import asyncio
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tests'))

from e2e_comprehensive import BASE, WARD, default_user, goto_app, new_ctx  # noqa: E402
from playwright.async_api import async_playwright  # noqa: E402

BASE = 'http://127.0.0.1:9080/'


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        ctx = await new_ctx(browser, storage={
            'civicradar_user': default_user(id='oc-copy'),
            'civicradar_coach_seen': '1',
            'civicradar_tour_seen': '1',
            'mosquiTrackReports': json.dumps([{
                'id': 'oc-copy-report',
                'reporterId': 'oc-copy',
                'hazard': 'stagnant-water',
                'ward': WARD,
                'city': 'mumbai',
                'reporter': 'Test',
                'lat': 19.076,
                'lng': 72.8777,
                'status': 'pending',
                'timestamp': '2026-06-01T00:00:00.000Z',
            }]),
        })
        page = await ctx.new_page()
        await goto_app(page, wait_map=True)
        result = await page.evaluate("""() => {
          const r = { id: 'oc-copy-report', hazard: 'stagnant-water', ward: 'G/N Ward — Dadar, Shivaji Park',
            city: 'mumbai', lat: 19.076, lng: 72.8777, timestamp: '2026-06-01T00:00:00.000Z' };
          const hasFn = typeof buildOfficialSummaryText === 'function';
          let txt = '';
          let err = '';
          try { txt = hasFn ? buildOfficialSummaryText(r, 'marg') : ''; }
          catch (e) { err = String(e); }
          return {
            hasFn,
            err,
            idOk: txt.includes('oc-copy-report'),
            civicOk: txt.includes('CivicRadar'),
            head: txt.slice(0, 500),
          };
        }""")
        print(result)
        await ctx.close()
        await browser.close()

asyncio.run(main())
