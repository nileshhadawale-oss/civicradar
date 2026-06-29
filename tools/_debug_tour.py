#!/usr/bin/env python3
import asyncio, json, time
from playwright.async_api import async_playwright

WARD = 'G/N Ward — Dadar, Shivaji Park'

async def main():
    user = json.dumps({
        'id': 'tour02',
        'tosAccepted': True,
        'gpsConsent': True,
        'city': 'mumbai',
        'ward': WARD,
        'displayName': 'TestCitizen',
        'pledges': [],
    })
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context()
        await ctx.add_init_script(f"""
            localStorage.setItem('civicradar_user', {json.dumps(user)});
        """)
        page = await ctx.new_page()
        page.on('pageerror', lambda e: print('PAGEERROR:', e))
        page.on('console', lambda m: print(f'CONSOLE {m.type}:', m.text) if m.type == 'error' else None)
        await page.goto('http://127.0.0.1:9080/', wait_until='domcontentloaded', timeout=30000)
        await page.wait_for_function('() => typeof window.openReportModal === "function"', timeout=60000)
        await page.wait_for_timeout(1500)
        state = await page.evaluate("""() => ({
          heroHidden: document.getElementById('homeHero').classList.contains('hidden'),
          coachHidden: document.getElementById('coachMark').classList.contains('hidden'),
          tourHidden: document.getElementById('tourOverlay').classList.contains('hidden'),
          coachKey: localStorage.getItem('civicradar_coach_seen'),
          tourKey: localStorage.getItem('civicradar_tour_seen'),
          heroDismissKey: localStorage.getItem('civicradar_hero_dismissed'),
          btnCamera: !!document.getElementById('btnCamera'),
          btnCameraRect: (() => { const r = document.getElementById('btnCamera')?.getBoundingClientRect(); return r ? {w:r.width,h:r.height} : null; })(),
        })""")
        print('Before dismiss:', state)
        if not state['heroHidden']:
            await page.click('#btnHeroDismiss')
            await page.wait_for_timeout(1500)
        state2 = await page.evaluate("""() => ({
          heroHidden: document.getElementById('homeHero').classList.contains('hidden'),
          tourHidden: document.getElementById('tourOverlay').classList.contains('hidden'),
          tourStep: document.getElementById('tourStep')?.textContent || '',
          coachKey: localStorage.getItem('civicradar_coach_seen'),
          tourKey: localStorage.getItem('civicradar_tour_seen'),
          heroDismissKey: localStorage.getItem('civicradar_hero_dismissed'),
        })""")
        print('After dismiss:', state2)
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
