import asyncio
import hashlib
import urllib.request
from pathlib import Path
from typing import Optional
from concurrent.futures import ThreadPoolExecutor

# Directory where screenshots will be saved
SCREENSHOTS_DIR = Path(__file__).parent.parent / "static" / "previews"
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)


def get_screenshot_filename(url: str) -> str:
    """Generate a unique filename from the URL using MD5 hash."""
    url_hash = hashlib.md5(url.encode()).hexdigest()
    return f"{url_hash}.png"


def _download_screenshot_sync(url: str, filepath: str) -> bool:
    """
    Download a screenshot using thum.io (free screenshot API).
    Runs synchronously in a thread pool so it doesn't block the async event loop.
    """
    # thum.io generates screenshots of any public URL, no API key needed
    api_url = f"https://image.thum.io/get/width/1280/crop/800/{url}"
    try:
        req = urllib.request.Request(
            api_url,
            headers={"User-Agent": "Mozilla/5.0 (compatible; URLPreviewBot/1.0)"}
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            if resp.status == 200:
                content = resp.read()
                if len(content) > 1000:  # Must be a real image, not an error page
                    with open(filepath, "wb") as f:
                        f.write(content)
                    print(f"Screenshot saved: {filepath}")
                    return True
    except Exception as e:
        print(f"Screenshot API error for {url}: {e}")
    return False


async def take_screenshot(url: str) -> Optional[str]:
    """
    Capture a screenshot of the given URL using thum.io (free screenshot API).
    Returns the relative path to the saved screenshot, or None if it fails.
    """
    filename = get_screenshot_filename(url)
    filepath = SCREENSHOTS_DIR / filename

    # Reuse cached screenshot if already captured and is a valid file
    if filepath.exists() and filepath.stat().st_size > 1000:
        print(f"Reusing cached screenshot: {filepath}")
        return f"/static/previews/{filename}"

    # Run the blocking HTTP download in a thread pool (keeps FastAPI async-safe)
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor(max_workers=1) as executor:
        success = await loop.run_in_executor(
            executor, _download_screenshot_sync, url, str(filepath)
        )

    # Only return the path if the file was actually created
    if success and filepath.exists() and filepath.stat().st_size > 1000:
        return f"/static/previews/{filename}"

    print(f"Screenshot not available for: {url}")
    return None
