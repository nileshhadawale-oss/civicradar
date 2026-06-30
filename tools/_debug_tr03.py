#!/usr/bin/env python3
"""Replicate E2E TR03 flow exactly."""
import asyncio, json, sys, time
sys.path.insert(0, r'C:\civicradar\tests')
from e2e_comprehensive import new_ctx, goto_app, default_user, install_playwright, ensure_server, js_click

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
        hero_shown = await page.evaluate('() => !document.getElementById("homeHero").classList.contains("hidden")')
        print('hero_shown', hero_shown)
        if hero_shown:
            await js_click(page, '#btnHeroDismiss')
            await page.wait_for_timeout(1200)
        else:
            coach_shown = not await page.evaluate('() => document.getElementById("coachMark").classList.contains("hidden")')
            print('coach_shown', coach_shown)
            if coach_shown:
                await js_click(page, '#btnDismissCoach')
            await page.wait_for_timeout(1200)
        tour_open = not await page.evaluate('() => document.getElementById("tourOverlay").classList.contains("hidden")')
        step_txt = await page.evaluate('() => document.getElementById("tourStep").textContent || ""')
        print('tour_open', tour_open, 'step', repr(step_txt))
        print('TR03 pass', tour_open and step_txt.strip().startswith('1 /'))
        await ctx.close()
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
