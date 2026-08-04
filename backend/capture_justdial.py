import asyncio
import sys
from pathlib import Path

if len(sys.argv) != 3:
    print("Usage: python capture_justdial.py <url> <output_file>")
    sys.exit(1)

URL = sys.argv[1]
SAVE_PATH = Path(sys.argv[2])
SAVE_PATH.parent.mkdir(parents=True, exist_ok=True)


async def capture():
    from playwright.async_api import async_playwright

    print("Opening:", URL)

    async with async_playwright() as p:

        browser = await p.chromium.launch(
            headless=False,
            channel="chrome",
            args=["--start-maximized"],
        )

        page = await browser.new_page(
            viewport={"width": 1280, "height": 800}
        )

        try:
            await page.goto(
                URL,
                wait_until="domcontentloaded",
                timeout=30000,
            )
        except Exception as e:
            print(e)

        await page.wait_for_timeout(5000)

        await page.screenshot(
            path=str(SAVE_PATH),
            full_page=False,
        )

        await browser.close()

    print("Saved:", SAVE_PATH)


asyncio.run(capture())