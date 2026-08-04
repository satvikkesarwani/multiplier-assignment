import asyncio
import os
import hashlib
from pathlib import Path
from typing import Optional

# Directory where screenshots will be saved
SCREENSHOTS_DIR = Path(__file__).parent.parent / "static" / "previews"
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

def get_screenshot_filename(url: str) -> str:
    """Generate a unique filename from the URL using MD5 hash."""
    url_hash = hashlib.md5(url.encode()).hexdigest()
    return f"{url_hash}.png"

async def take_screenshot(url: str) -> Optional[str]:
    """
    Use Playwright (headless browser) to capture a screenshot of the given URL.
    Returns the relative path to the saved screenshot, or None if it fails.
    """
    filename = get_screenshot_filename(url)
    filepath = SCREENSHOTS_DIR / filename
    
    # Reuse existing screenshot if already captured
    if filepath.exists():
        return f"/static/previews/{filename}"
    
    try:
        from playwright.async_api import async_playwright
        
        async with async_playwright() as p:
            # Launch Chromium with disabled HTTP/2
            browser = await p.chromium.launch(
                headless=True,
                args=["--disable-http2"]
            )
            # Use custom context options (User Agent, bypass HTTP/2 errors if any)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 800},
                ignore_https_errors=True
            )
            page = await context.new_page()
            
            # Try navigating with a very short timeout and minimal wait criteria
            try:
                # Wait for load event or domcontentloaded with a 20s timeout
                await page.goto(url, wait_until="load", timeout=20000)
            except Exception as goto_err:
                print(f"Navigation error (ignored to capture page content): {goto_err}")
                try:
                    await page.goto(url, wait_until="commit", timeout=10000)
                except Exception:
                    pass
            
            # Wait a small delay for rendering to finish
            await asyncio.sleep(4)
            
            # Take a screenshot, passing a high timeout (25s) and ignoring standard font wait blocks if any
            try:
                await page.screenshot(path=str(filepath), full_page=False, animations="disabled", timeout=25000)
            except Exception as ss_err:
                print(f"Screenshot capture error: {ss_err}")
            await browser.close()
        
        return f"/static/previews/{filename}"
    
    except Exception as e:
        print(f"Screenshot failed for {url}: {e}")
        return None
