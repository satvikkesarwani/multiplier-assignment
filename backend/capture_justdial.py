"""
One-time script to capture the JustDial screenshot using the real Chrome browser.
Run once: python3 capture_justdial.py
"""
import asyncio
import hashlib
from pathlib import Path

URL = "https://google.com"

# Same hash logic as the main app
url_hash = hashlib.md5(URL.encode()).hexdigest()
SAVE_PATH = Path("app/static/previews") / f"{url_hash}.png"
SAVE_PATH.parent.mkdir(parents=True, exist_ok=True)

async def capture():
    from playwright.async_api import async_playwright

    print(f"Opening page: {URL}")
    async with async_playwright() as p:
        # Use real Chrome browser (NOT headless) — bypasses bot detection
        browser = await p.chromium.launch(
            headless=False,                  # Visible browser window
            channel="chrome",               # Use your installed Chrome
            args=["--start-maximized"]
        )
        page = await browser.new_page(
            viewport={"width": 1280, "height": 800}
        )
        print("Navigating... (waiting up to 30 seconds for page to fully load)")
        try:
            await page.goto(URL, wait_until="domcontentloaded", timeout=30000)
        except Exception as e:
            print(f"Navigation note: {e}")

        # Wait for content to render
        await asyncio.sleep(5)

        # Take screenshot
        await page.screenshot(path=str(SAVE_PATH), full_page=False)
        await browser.close()

    print(f"\n✅ Screenshot saved to: {SAVE_PATH}")
    print("Refresh your browser dashboard to see it!")

asyncio.run(capture())
