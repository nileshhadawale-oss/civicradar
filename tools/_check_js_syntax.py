#!/usr/bin/env python3
"""Quick check app.js loads without syntax errors via Playwright."""
import asyncio
import http.server
import socket
import subprocess
import sys
import threading
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


async def main():
    from playwright.async_api import async_playwright

    port = free_port()
    proc = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(port), "--bind", "127.0.0.1"],
        cwd=str(ROOT),
    )
    errors = []
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            page.on("pageerror", lambda e: errors.append(str(e)))
            page.on("console", lambda m: errors.append(f"console:{m.type}:{m.text}") if m.type == "error" else None)
            await page.goto(f"http://127.0.0.1:{port}/index.html", wait_until="networkidle", timeout=60000)
            await page.wait_for_timeout(3000)
            ok = await page.evaluate("() => typeof window.openReportModal === 'function'")
            ver = await page.evaluate("() => window.CIVIC_APP_VERSION || 'missing'")
            mojibake = await page.evaluate(
                "() => (document.body.innerText.match(/ï¿½/g) || []).length"
            )
            onboard = await page.evaluate(
                "() => document.getElementById('onboardCityHint')?.textContent || ''"
            )
            print(f"openReportModal: {ok}")
            print(f"version: {ver}")
            print(f"mojibake_count_in_body: {mojibake}")
            print(f"onboardCityHint: {onboard!r}")
            if errors:
                print("ERRORS:")
                for e in errors[:20]:
                    print(" ", e)
            await browser.close()
    finally:
        proc.terminate()
        proc.wait(timeout=5)


if __name__ == "__main__":
    asyncio.run(main())
