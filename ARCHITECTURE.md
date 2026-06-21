# CivicRadar — Architecture & Scale Plan

This document describes how CivicRadar is built today on **$0 infrastructure**, what breaks first as usage grows, and a staged path to scale for **Mumbai / India** without over-investing early.

For Supabase setup steps, see [`BACKEND_SETUP.md`](BACKEND_SETUP.md).

---

## Free tier stack today (costs $0)

| Layer | Choice | Cost | Notes |
| --- | --- | --- | --- |
| **App shell** | Vanilla PWA (HTML/CSS/JS) | $0 | No build toolchain required; works on basic Android browsers |
| **Hosting** | GitHub Pages or Cloudflare Pages | $0 | Static files only; HTTPS included |
| **Local dev** | `serve.ps1` + service worker | $0 | Offline cache via `sw.js` |
| **Backend (optional)** | Supabase free tier | $0 | Mumbai region (`ap-south-1`) recommended |
| **Maps** | Leaflet + OpenStreetMap tiles | $0 | Tile usage policy: fair use; heavy traffic may need a tile CDN later |
| **Auth** | Supabase anonymous + email OTP | $0 | 50K MAU on free tier |
| **Realtime** | Supabase Realtime | $0 | Included; watch connection counts at scale |
| **Moderation** | Client-side heuristics + optional NSFW model | $0 | Model loaded from CDN when online |

### Supabase free tier limits (watch these)

| Resource | Free limit | CivicRadar impact |
| --- | --- | --- |
| Database | 500 MB | **Main risk:** JPEG data URLs stored in `reports.image` text column |
| Storage | 1 GB | Unused until Stage 1 migration |
| Bandwidth | 5 GB/month (egress) | Full-table sync + large images burn this quickly |
| Auth MAU | 50,000 | Fine for early launch |
| Edge Functions | 500K invocations | Not used yet |
| Realtime | 200 concurrent connections | ~200 simultaneous open tabs city-wide |

**Region:** create the project in **South Asia (Mumbai)** so latency and DPDP data-locality expectations are met.

---

## India-specific non-functional requirements

| NFR | Reality in India | How CivicRadar addresses it | Gaps |
| --- | --- | --- | --- |
| **Low bandwidth (2G/3G)** | 1–5 Mbps, high latency | PWA cache, compressed JPEG uploads (320px / q=0.52), paginated sync, deferred leaderboard init | Full hazard photos still heavy until Storage + thumbnails |
| **Intermittent connectivity** | Drops on trains, monsoon outages | localStorage-first writes, sync retry toasts, service worker shell cache | No background sync API yet |
| **Languages** | Hindi, Marathi, Gujarati + English | 4-language UI (`i18n` in `app.js`) | No runtime locale bundles; all strings ship in one file |
| **DPDP (2023)** | Consent, purpose limitation, erasure | ToS GPS consent, EXIF strip on upload, delete-my-data flow | Privacy policy should name Supabase sub-processor; DPIA for minors |
| **Monsoon spikes** | June–Sept hazard surge | Local-first; recent-window sync (`syncRecentDays`) | No autoscale — upgrade Supabase tier before peak |
| **Basic Android phones** | 2–3 GB RAM, older WebView | No React bundle; map marker cap (150); viewport-only markers | NSFW model is heavy on low-end devices |
| **Battery / GPS** | Users disable location | Throttled geolocation (15s min interval) | High-accuracy GPS still used when reporting |

---

## Current bottlenecks

1. **Images as data URLs in Postgres** — a single 320px JPEG can be 30–80 KB as base64 in a `text` column. Thousands of reports → hundreds of MB DB + slow `SELECT *`.
2. **Sync pulled entire tables** — fixed with batched pull (recent N days + user's own rows). Admin/coordinator views still use local merged data.
3. **No server-side pagination API** — client limits rows; BMC queue may miss very old pending items until Stage 2 ward-scoped queries.
4. **Leaderboard computed client-side** — O(n) over all loaded reports each refresh. Acceptable under ~500 local rows; move aggregation to SQL/views at Stage 2.
5. **NSFW model from CDN** — first scan downloads ~MB of WASM; slow on 2G. `requireOnlineNsfw: true` blocks upload when offline (configurable).
6. **Map markers** — capped at 150 in viewport with pending-first priority. Stage 2: Leaflet.markercluster or vector tiles.

---

## Scale path by growth stage

### Stage 0 — Now (0 → ~1K users)

**Stack:** Static PWA + Supabase free + localStorage merge.

**Already implemented:**

- Config knobs in `js/config.js` → `scale`: `maxReportsPerDevice`, `syncBatchSize`, `syncRecentDays`, `imageMaxWidth`, `jpegQuality`, `maxMapMarkers`
- Paginated `Backend.pullAll()` — recent window + own reports
- Viewport-limited map markers with debounced refresh
- Throttled GPS; deferred leaderboard render
- DB indexes on `status`, `ward`, `created_at`, `reporter_id`, `(status, created_at)`

**You should:**

- Deploy to GitHub/Cloudflare Pages with HTTPS
- Supabase project in Mumbai; run `supabase/schema.sql`
- Keep `scale` defaults unless you hit limits
- Monitor Supabase dashboard: DB size, API requests, bandwidth

---

### Stage 1 — 1K → 10K users

**Trigger:** DB > 300 MB, sync slow on 3G, or bandwidth warnings.

| Change | Why |
| --- | --- |
| **Supabase Storage for photos** | Move blobs out of Postgres; store `image_url` only |
| **Thumbnails** | Map/list uses 200px thumb; full image on detail tap |
| **Tighter sync** | Lower `syncBatchSize` to 100; `syncRecentDays` to 60 |
| **Indexes** | Already in schema; add partial index on pending per ward if needed |
| **Run** | `supabase/storage-migration.sql` + app upload path |

**Cost:** Still likely $0 on Supabase free if images leave the DB.

---

### Stage 2 — 10K → 100K users

**Trigger:** Free tier exceeded, Realtime connection limits, abuse/spam.

| Change | Why |
| --- | --- |
| **Supabase Pro** (~$25/mo) | More DB, bandwidth, daily backups |
| **RLS hardening** | Narrow `reports_select_all`; ward-scoped reads for citizens |
| **Read replicas** | Analytics / leaderboard without hitting primary (Supabase Pro+) |
| **CDN for static** | Cloudflare in front of Pages; cache `js/`, `css/` aggressively |
| **Edge Functions** | Server-side moderation, rate limits, signed upload URLs |
| **Rate limits** | e.g. 5 reports/user/day; RPC counters |
| **Marker clustering** | Leaflet.markercluster or MapLibre vector layers |

---

### Stage 3 — 100K+ users

**Trigger:** Single-city report volume overwhelms one Postgres instance or BMC partnership needs API integration.

| Change | Why |
| --- | --- |
| **Ward sharding** | Partition hot wards or separate read models per zone |
| **BMC read API** | If MCGM exposes CCRS status webhooks, replace manual complaint ID entry |
| **Dedicated object storage** | Compare **Cloudflare R2** ($0.015/GB/mo, no egress to CF) vs Supabase Storage ($0.021/GB + egress) |
| **Managed auth** | Stricter BMC/NGO verification workflow |
| **Observability** | Sentry, Supabase logs, uptime checks |

---

## Cost table — free vs paid trigger points

| Metric | Stay free | Upgrade signal | Typical next step |
| --- | --- | --- | --- |
| DB size | < 400 MB | > 400 MB sustained | Storage migration + Pro if still growing |
| Storage | < 800 MB | Image bucket filling | R2 or resize/thumbnail pipeline |
| Bandwidth | < 4 GB/mo | API egress alerts | CDN, smaller payloads, pagination |
| MAU | < 40K | Approaching 50K | Pro or optimize anonymous session churn |
| Realtime | < 150 concurrent | Connection errors | Reduce full-table refresh; ward channels |
| Moderation | Client-only | Abuse reports | Edge Function + Vision API (~pay per call) |

---

## NFR checklist

| Area | Target | Done today | Gap |
| --- | --- | --- | --- |
| **Performance** | Map usable on 3G | SW cache, compressed images, lazy markers, idle leaderboard | Clustering at high density |
| **Availability** | Works offline for report draft | localStorage + SW shell | No Background Sync for failed uploads |
| **Security** | Role-based admin actions | RLS + gov-domain trigger + NGO codes | Broad `*.gov.in` auto-grant; no rate limits |
| **Privacy** | DPDP-aligned consent | GPS ToS, EXIF strip, delete data | Document subprocessors; retention policy |
| **Offline** | Core flows without network | Report saved locally; map cached | NSFW scan optional offline |
| **Accessibility** | WCAG basics | Semantic modals, i18n | Full audit not done |
| **i18n** | EN / HI / MR / GU | In-app translations | RTL not needed; no server locale |
| **Scalability** | 10K without rewrite | Stage 0 optimizations | Storage migration required for 10K+ photos |

---

## Cache bust strategy

The service worker cache name (`civicradar-v18` in `sw.js`) is bumped whenever shipped JS/CSS changes. On activate, old caches are deleted. After deploy:

1. Users get new SW on next visit (or force refresh).
2. Optional: add `?v=18` query params to script tags if you need immediate bust before SW update.

---

## Configuration reference

All scale knobs live in `js/config.js`:

```js
scale: {
  maxReportsPerDevice: 500,
  syncBatchSize: 200,
  syncRecentDays: 90,
  imageMaxWidth: 320,
  jpegQuality: 0.52,
  maxMapMarkers: 150,
  mapMarkerDebounceMs: 250,
  geoThrottleMs: 15000,
}
```

Tune down `syncBatchSize` / `imageMaxWidth` on free tier pressure; tune up only after Storage migration and Pro tier.

---

## Related files

| File | Purpose |
| --- | --- |
| [`BACKEND_SETUP.md`](BACKEND_SETUP.md) | Supabase setup, roles, BMC channels |
| [`supabase/schema.sql`](supabase/schema.sql) | Tables, RLS, indexes |
| [`supabase/storage-migration.sql`](supabase/storage-migration.sql) | Stage 1 Storage bucket + `image_url` column |
| [`js/config.js`](js/config.js) | Runtime config including `scale` |
| [`sw.js`](sw.js) | PWA asset cache version |
