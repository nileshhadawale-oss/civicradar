#!/usr/bin/env python3
import asyncio, json, sys
sys.path.insert(0, r'C:\civicradar\tests')
from e2e_comprehensive import new_ctx, goto_app, default_user, install_playwright, ensure_server

async def main():
    ensure_server()
    await install_playwright()
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx = await new_ctx(browser, storage={'civicradar_user': default_user(id='tour02')})
        page = await ctx.new_page()
        await goto_app(page, wait_map=True)
        await page.wait_for_timeout(900)
        diag = await page.evaluate("""() => ({
          heroHidden: document.getElementById('homeHero').classList.contains('hidden'),
          coachHidden: document.getElementById('coachMark').classList.contains('hidden'),
          tourHidden: document.getElementById('tourOverlay').classList.contains('hidden'),
          tourStep: document.getElementById('tourStep')?.textContent,
          bodyHero: document.body.classList.contains('home-hero-visible'),
          userReports: (() => { try { return JSON.parse(localStorage.getItem('civicradar_reports')||'[]').length; } catch(e){ return -1;} })(),
          heroDismiss: localStorage.getItem('civicradar_hero_dismissed'),
          firstReport: localStorage.getItem('civicradar_first_report_done'),
          coach: localStorage.getItem('civicradar_coach_seen'),
          tour: localStorage.getItem('civicradar_tour_seen'),
          visit: localStorage.getItem('civicradar_visit_count'),
          user: JSON.parse(localStorage.getItem('civicradar_user')||'{}'),
        })""")
        for k,v in diag.items():
            print(k, ':', v)
        await ctx.close()
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
