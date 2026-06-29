#!/usr/bin/env python3
"""Quick smoke test: does app.js load and expose openReportModal?"""
import asyncio
import sys

async def main():
    from playwright.async_api import async_playwright
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 9080
    url = f"http://127.0.0.1:{port}/"
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.on("console", lambda m: errors.append(f"console.{m.type}: {m.text}") if m.type == "error" else None)
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_function('() => typeof window.openReportModal === "function"', timeout=60000)
            ver = await page.evaluate("() => window.CIVIC_APP_VERSION || 'unknown'")
            print(f"OK openReportModal ready, version={ver}")
        except Exception as e:
            print(f"FAIL: {e}")
            for err in errors[:20]:
                print(" ", err)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
