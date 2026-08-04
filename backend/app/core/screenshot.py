import asyncio
import hashlib
import logging
import urllib.request
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse, urlunparse

from playwright.async_api import (
    BrowserContext,
    Error as PlaywrightError,
    TimeoutError as PlaywrightTimeoutError,
    async_playwright,
)

logger = logging.getLogger(__name__)

APP_DIR = Path(__file__).resolve().parent.parent

SCREENSHOTS_DIR = APP_DIR / "static" / "previews"
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

# Separate browser profile made only for this application.
# Do not point this at your personal Chrome profile.
BROWSER_PROFILE_DIR = APP_DIR / "browser_profile"
BROWSER_PROFILE_DIR.mkdir(parents=True, exist_ok=True)

# A persistent Chrome profile cannot safely be opened multiple times
# simultaneously, so serialize screenshot jobs.
_screenshot_lock = asyncio.Lock()

MIN_SCREENSHOT_SIZE = 1_000
NAVIGATION_TIMEOUT_MS = 30_000
SCREENSHOT_TIMEOUT_MS = 15_000


def normalize_url(url: str) -> str:
    """
    Normalize a URL so equivalent inputs produce the same cache file.

    Example:
        google.com -> https://google.com/
    """
    url = url.strip()

    if not url:
        raise ValueError("URL cannot be empty")

    if "://" not in url:
        url = f"https://{url}"

    parsed = urlparse(url)

    if parsed.scheme not in {"http", "https"}:
        raise ValueError("Only HTTP and HTTPS URLs are supported")

    if not parsed.hostname:
        raise ValueError("Invalid URL")

    # Fragments do not affect the downloaded page.
    parsed = parsed._replace(fragment="")

    return urlunparse(parsed)


def get_screenshot_filename(url: str) -> str:
    """
    Generate a stable screenshot filename from the normalized URL.

    SHA-256 is used for cache identity. This is not password hashing.
    """
    normalized_url = normalize_url(url)
    url_hash = hashlib.sha256(normalized_url.encode("utf-8")).hexdigest()
    return f"{url_hash}.png"


def is_valid_cached_file(filepath: Path) -> bool:
    """Return True only when a usable cached screenshot exists."""
    return filepath.is_file() and filepath.stat().st_size > MIN_SCREENSHOT_SIZE


async def block_unnecessary_resources(route) -> None:
    """
    Block only heavy media resources.

    Do not block CSS or images because that would make screenshots visually
    incomplete.
    """
    resource_type = route.request.resource_type

    if resource_type in {"media"}:
        await route.abort()
    else:
        await route.continue_()


async def launch_context(playwright) -> BrowserContext:
    """
    Launch installed Google Chrome when available.

    If Chrome is not installed, fall back to Playwright Chromium.
    """
    common_options = {
        "user_data_dir": str(BROWSER_PROFILE_DIR),
        "headless": True,
        "viewport": {"width": 1280, "height": 800},
        "screen": {"width": 1280, "height": 800},
        "locale": "en-IN",
        "timezone_id": "Asia/Kolkata",
        "ignore_https_errors": True,
        "java_script_enabled": True,
        "color_scheme": "light",
        "args": [
            "--disable-dev-shm-usage",
            "--disable-background-networking",
            "--disable-background-timer-throttling",
            "--disable-renderer-backgrounding",
            "--disable-features=Translate",
            "--hide-scrollbars",
            "--mute-audio",
        ],
    }

    try:
        logger.info("Launching installed Google Chrome")

        return await playwright.chromium.launch_persistent_context(
            channel="chrome",
            **common_options,
        )

    except PlaywrightError as chrome_error:
        logger.warning(
            "Installed Chrome could not be launched; falling back to "
            "Playwright Chromium: %s",
            chrome_error,
        )

        return await playwright.chromium.launch_persistent_context(
            **common_options,
        )


async def prepare_page(page) -> None:
    """Configure headers, timeouts and request handling."""
    page.set_default_navigation_timeout(NAVIGATION_TIMEOUT_MS)
    page.set_default_timeout(SCREENSHOT_TIMEOUT_MS)

    await page.set_extra_http_headers(
        {
            "Accept-Language": "en-IN,en-US;q=0.9,en;q=0.8",
            "Upgrade-Insecure-Requests": "1",
        }
    )

    await page.route("**/*", block_unnecessary_resources)


async def navigate_and_render(page, url: str) -> None:
    """
    Navigate without depending on networkidle.

    Many real websites continuously make analytics, ads or websocket requests,
    so networkidle may never occur.
    """
    response = None

    try:
        response = await page.goto(
            url,
            wait_until="domcontentloaded",
            timeout=NAVIGATION_TIMEOUT_MS,
        )

    except PlaywrightTimeoutError:
        # The document may already have rendered useful content even when some
        # background request caused navigation to time out.
        logger.warning("Navigation timed out for %s; attempting screenshot", url)

    if response is not None and response.status >= 400:
        logger.warning(
            "Target returned HTTP %s for %s",
            response.status,
            url,
        )

    # Let client-side rendering, images and lazy content settle.
    try:
        await page.wait_for_load_state("load", timeout=8_000)
    except PlaywrightTimeoutError:
        pass

    await page.wait_for_timeout(2_500)

    # Scroll once to trigger common lazy-loaded content, then return to top.
    try:
        await page.evaluate(
            """
            async () => {
                window.scrollTo(0, Math.min(document.body.scrollHeight, 700));
                await new Promise(resolve => setTimeout(resolve, 500));
                window.scrollTo(0, 0);
            }
            """
        )
    except PlaywrightError:
        pass

    await page.wait_for_timeout(700)


async def capture_with_playwright(url: str, filepath: Path) -> bool:
    """Capture the URL using local Chrome/Chromium."""
    context: Optional[BrowserContext] = None

    try:
        async with async_playwright() as playwright:
            context = await launch_context(playwright)

            # Persistent contexts sometimes open an initial blank page.
            page = context.pages[0] if context.pages else await context.new_page()

            await prepare_page(page)
            await navigate_and_render(page, url)

            await page.screenshot(
                path=str(filepath),
                full_page=False,
                type="png",
                animations="disabled",
                timeout=SCREENSHOT_TIMEOUT_MS,
            )

            if not is_valid_cached_file(filepath):
                filepath.unlink(missing_ok=True)
                return False

            logger.info("Playwright screenshot saved: %s", filepath)
            return True

    except Exception:
        logger.exception("Playwright screenshot failed for %s", url)
        filepath.unlink(missing_ok=True)
        return False

    finally:
        if context is not None:
            try:
                await context.close()
            except Exception:
                logger.exception("Failed to close browser context")


def _download_thum_fallback(url: str, filepath: Path) -> bool:
    """
    Optional fallback for cases where the local browser cannot start.

    This does not guarantee success on bot-protected websites.
    """
    api_url = f"https://image.thum.io/get/width/1280/crop/800/noanimate/{url}"

    try:
        request = urllib.request.Request(
            api_url,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (compatible; URLPreviewApplication/1.0)"
                )
            },
        )

        with urllib.request.urlopen(request, timeout=30) as response:
            if response.status != 200:
                return False

            content = response.read()

        if len(content) <= MIN_SCREENSHOT_SIZE:
            return False

        filepath.write_bytes(content)

        return is_valid_cached_file(filepath)

    except Exception:
        logger.exception("thum.io fallback failed for %s", url)
        filepath.unlink(missing_ok=True)
        return False


async def capture_with_thum_fallback(url: str, filepath: Path) -> bool:
    """Run the blocking fallback request without blocking FastAPI."""
    return await asyncio.to_thread(
        _download_thum_fallback,
        url,
        filepath,
    )


async def take_screenshot(url: str) -> Optional[str]:
    """
    Capture and cache a website preview.

    Order:
    1. Validate and normalize the URL
    2. Return cached screenshot when available
    3. Try local Playwright with Chrome
    4. Try thum.io only if local capture fails
    """
    normalized_url = normalize_url(url)
    filename = get_screenshot_filename(normalized_url)
    filepath = SCREENSHOTS_DIR / filename
    public_path = f"/static/previews/{filename}"

    if is_valid_cached_file(filepath):
        logger.info("Reusing cached screenshot: %s", filepath)
        return public_path

    async with _screenshot_lock:
        # Another request might have created it while this request waited.
        if is_valid_cached_file(filepath):
            return public_path

        playwright_success = await capture_with_playwright(
            normalized_url,
            filepath,
        )

        if playwright_success:
            return public_path

        logger.warning(
            "Local browser capture failed for %s; trying fallback",
            normalized_url,
        )

        fallback_success = await capture_with_thum_fallback(
            normalized_url,
            filepath,
        )

        if fallback_success:
            return public_path

    return None