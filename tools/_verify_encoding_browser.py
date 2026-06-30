#!/usr/bin/env python3
"""Browser verify: no mojibake in key UI strings (v99)."""
import asyncio
import subprocess
import sys
import socket
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MOJIBAKE = "ï¿½"


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
    issues = []
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.goto(f"http://127.0.0.1:{port}/index.html", wait_until="networkidle", timeout=60000)
            await page.wait_for_function('() => typeof window.openReportModal === "function"', timeout=60000)

            checks = await page.evaluate(
                f"""() => {{
                const MOJ = '{MOJIBAKE}';
                const ids = [
                  'onboardCityHint', 'homeHeroTitle', 'headerContext',
                  'homeHeroSub', 'homeHeroTrust'
                ];
                const out = {{ bodyMojibake: (document.body.innerText.match(/ï¿½/g) || []).length, items: [] }};
                for (const id of ids) {{
                  const el = document.getElementById(id);
                  if (el) out.items.push({{ id, text: el.textContent }});
                }}
                out.items.push({{ id: 'data-i18n-onboard.subtitle', text: document.querySelector('[data-i18n=\"onboard.subtitle\"]')?.textContent }});
                return out;
            }}"""
            )
            for item in checks.get("items", []):
                if item.get("text") and MOJIBAKE in item["text"]:
                    issues.append(item)
            print(f"body_mojibake_count: {checks.get('bodyMojibake', -1)}")
            for item in checks.get("items", []):
                print(f"  {item['id']}: {item['text']!r}")
            print(f"issues: {len(issues)}")
            await browser.close()
    finally:
        proc.terminate()
        proc.wait(timeout=5)
    return 1 if issues or checks.get("bodyMojibake") else 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
