# CivicRadar — Final Launch Checklist



**Audit date:** 21 June 2026 (re-audit)  

**Verdict:** **Ready with 8 founder steps** — app code is functional; founder must complete Supabase auth, config emails/URL, deploy, and legal review before real users.



---



## Must-do before launch



| Priority | Item | Where | Status |

|----------|------|-------|--------|

| P0 | Enable **Anonymous sign-ins** + **Email OTP** | Supabase → **Authentication → Sign In / Providers** | ⬜ **Founder only** — keys in config won't work until this is on |

| P0 | Run `supabase/schema.sql` in SQL Editor | Supabase → **SQL Editor → New query** | ⬜ Required for sync, roles, `delete_user_data` RPC |

| P0 | Set `publicUrl` to production HTTPS URL | `js/config.js` | ⬜ Empty — WhatsApp/deep links fall back to localhost |

| P0 | Set `legal.grievanceEmail` | `js/config.js` | ⬜ Placeholder shown on privacy/terms pages |

| P0 | Set `founder.email` + `founder.operatorEmail` | `js/config.js` | ⬜ About modal + legal contact |

| P0 | Deploy to HTTPS hosting | GitHub Pages (workflow ready) | ⬜ Camera + GPS require HTTPS |

| P0 | Counsel review of `privacy.html` + `terms.html` | Legal pages | ⬜ Draft complete; marked for counsel review |

| P1 | Replace emoji PWA icons with 512×512 PNG | `manifest.json` | ⬜ Optional for soft launch; required for store listings |

| P1 | Issue real NGO invite code in Supabase | `ngo_codes` table | ⬜ Demo codes in config for local only |

| P1 | Phone test (camera, GPS, WhatsApp, PWA) | Real Android device | ⬜ Founder only |



### Already done (agent / prior session)



| Item | Status |

|------|--------|

| `supabaseUrl` + `supabaseAnonKey` in `js/config.js` | ✅ Project `shrjkexfokootrzrpjsi` (Mumbai) |

| `founder.operatorName` | ✅ Nilesh Hadawale |

| GitHub Pages deploy workflow | ✅ `.github/workflows/deploy-pages.yml` |

| SW cache + network-first `config.js` | ✅ `civicradar-v42` |

| Backend.init error toast | ✅ User-visible on connect failure |

| Duplicate `resolutionBadgeHtml` JS bug | ✅ Fixed → `handleCommunityAutoResolve` (was blocking entire app) |



---



## Test results summary



| Suite | Result | Notes |

|-------|--------|-------|

| E2E comprehensive (this audit) | **83 / 87 PASS** | 4 expected fails with Supabase keys configured (see below) |

| E2E comprehensive (prior, local mode) | **109 / 109 PASS** | Empty Supabase keys → demo logins visible |

| HTTP smoke | **200 OK** | `/`, `/privacy.html`, `/terms.html` |

| i18n audit | **602 keys, 0 missing** | HI/MR/GU complete |



### E2E failures with Supabase configured (not launch blockers)



| Test | Reason |

|------|--------|

| C05 GPS consent on ToS accept | **By design** — GPS consent is unbundled from ToS (set on first report) |

| E09 Analytics after ToS | **By design** — analytics requires separate opt-in checkbox |

| NGO/Admin demo login suites | Demo logins hidden when Supabase connected; use real OTP + invite codes |



CI (GitHub Actions) runs E2E on push with whatever `config.js` is in the repo. For green CI with demo tests, use empty Supabase keys in CI or update tests for connected mode.



---



## Founder must-do list (copy-paste, ordered)



### 1. Supabase dashboard — project `shrjkexfokootrzrpjsi`



```

1. Open https://supabase.com/dashboard/project/shrjkexfokootrzrpjsi
   (If prompted, pick your Organization first, then this project.)

2. Left sidebar → SQL Editor → + New query
   Direct link: https://supabase.com/dashboard/project/shrjkexfokootrzrpjsi/sql/new
   Paste ALL of supabase/schema.sql → Run (or Ctrl+Enter)

3. Left sidebar → Authentication → Sign In / Providers
   Direct link: https://supabase.com/dashboard/project/shrjkexfokootrzrpjsi/auth/providers
   - Anonymous sign-ins → Enable
   - Email → Enable → expand Email settings:
     • Confirm email → OFF (OTP login without extra confirmation step)
     • Email OTP is the default passwordless method (no magic link needed)

4. (Optional verify) Left sidebar → Table Editor
   Direct link: https://supabase.com/dashboard/project/shrjkexfokootrzrpjsi/editor
   Confirm tables exist: reports, profiles, ngo_codes, analytics_events

5. Reload http://localhost:8095/ — expect toast: "Connected — reports sync across devices."

If you don't see "Sign In / Providers": look for "Providers" under Authentication (older UI).
If SQL Editor shows a blank page: refresh once, or use the direct /sql/new link above.

```



### 2. Fill remaining `js/config.js` fields



Edit `C:\civicradar\js\config.js`:



```js

publicUrl: 'https://YOUR-USER.github.io/civicradar',  // exact HTTPS deploy URL

legal: { grievanceEmail: 'privacy@yourdomain.com' },

founder: {

  email: 'nihira@yourdomain.com',

  operatorEmail: 'nilesh@yourdomain.com',

},

```



### 3. Deploy to GitHub Pages

> **Expanded walkthrough:** [GitHub Pages deploy (detailed)](#github-pages-deploy-detailed) — copy-paste commands, CI E2E gate workarounds, and verification.

```

1. Create public GitHub repo (e.g. civicradar)

2. Push code from C:\civicradar

3. Repo → Settings → Pages → Source: GitHub Actions

4. Wait for green "Deploy to GitHub Pages" workflow run

5. Copy the Pages URL → set as publicUrl in config.js → commit & push again

```

**CI gotcha:** The deploy workflow runs E2E tests first (`deploy` needs `test`). With Supabase keys in `config.js`, **4 scenarios fail by design** and block deploy. Workarounds: temporarily empty keys for first green deploy, fix the workflow/tests, or use Cloudflare Pages (`deploy-cloudflare.md`). See detailed section below.



### 4. Insert pilot NGO invite code (SQL Editor)



Open **SQL Editor → New query** (same path as step 1), then run:

```sql

insert into public.ngo_codes (code, ward, ngo_name, coordinator_scope)

values ('CLEAN-GN-2026', 'G/N Ward — Dadar, Shivaji Park', 'Your NGO Name', 'ward');

```



### 5. Legal counsel review



Send `privacy.html` and `terms.html` to qualified Indian DPDP counsel. Founder is 17; operator is parent contact.



### 6. Android phone smoke test



Open production HTTPS URL → ToS + analytics opt-in → ward onboarding → report with photo + GPS → WhatsApp share link uses `publicUrl` → Add to Home Screen.



### 7. Soft launch



One ward, 2–3 WhatsApp groups. Share `publicUrl` + NGO code with coordinator.



### 8. Optional later



- Replace emoji PWA icons (`manifest.json`)

- Custom domain on GitHub Pages

- `STORE_LAUNCH.md` for Play/App Store



---



## Code quality & security checks



| Check | Result |

|-------|--------|

| TODO / FIXME in app code | ✅ None |

| XSS sanitization | ✅ User inputs sanitized |

| Analytics + GPS consent unbundled | ✅ Separate from ToS accept |

| Service worker cache version | ✅ `civicradar-v42` |

| Legal page links | ✅ privacy ↔ terms ↔ index |

| Legal email placeholders | ⚠️ Shows "configure legal.grievanceEmail…" until founder fills config |



---



## Known limitations (not launch blockers)



- OG meta for individual reports: static defaults; per-report OG needs SSR at scale

- OG/Twitter image URLs are relative — fine for in-app; crawlers may need absolute URL after deploy

- NSFW moderation lazy-loads when online

- PWA offline: shell cached; map tiles need network

- Demo admin/NGO logins auto-hidden when Supabase configured (expected)



---



## Launch readiness verdict



### **Ready with 8 founder steps**



Application code loads and passes 83/87 E2E scenarios with Supabase keys configured. A critical JS bug (duplicate function declaration) was fixed during this audit.



**Do not send real users until:** Anonymous auth enabled, schema applied, production `publicUrl`, grievance/contact emails set, HTTPS deployed, and counsel has reviewed legal pages.



---



## GitHub Pages deploy (detailed)

Use this checklist item together with **LAUNCH-WALKTHROUGH.md** Phase C–D. The repo includes `.github/workflows/deploy-pages.yml` (workflow name: **Deploy to GitHub Pages**; jobs: `test` → `deploy`).

| Topic | Detail |
|-------|--------|
| Repo visibility | **Public** required for free Pages on personal GitHub accounts (or GitHub Pro for private) |
| Pages source | Settings → Pages → **GitHub Actions** (not “Deploy from branch”) |
| Live URL pattern | `https://YOUR-GITHUB-USERNAME.github.io/civicradar/` |
| Files deployed | `index.html`, legal pages, `manifest.json`, `sw.js`, `robots.txt`, `css/`, `js/`, `assets/` only |
| Excluded by workflow | `video/`, `tools/ffmpeg/`, `tests/`, `supabase/` SQL (also in `.gitignore` for large media) |
| CI gate | E2E on push; **83/87 pass** with Supabase configured — **4 failures block deploy** |
| Known failures | C05 (GPS unbundled from ToS), E09 (analytics separate opt-in), NGO/Admin demo suites (hidden when connected) |
| Workarounds | Empty Supabase keys for first deploy → set `publicUrl` → re-add keys; or edit workflow; or Cloudflare |
| After deploy | Hard refresh / clear site data (SW `civicradar-v42`); set `legal.grievanceEmail` before sharing legal pages |

**Git status (local):** `C:\civicradar` is **not** a git repo yet — run `git init` before first push.

For step-by-step commands, auth options, log reading, and phone verification, use the full **GitHub Pages deploy guide** from your launch session (founder copy-paste doc).

---



## Related docs



- `LAUNCH-WALKTHROUGH.md` — Step-by-step founder guide

- `BACKEND_SETUP.md` — Supabase roles, NGO codes, analytics

- `tests/TEST-RESULTS.md` — Latest E2E scenario table

- `STORE_LAUNCH.md` — App store submission checklist

- `js/config.example.js` — Safe template (no real secrets)



---



## Supabase dashboard quick reference (2025/2026 UI)



Project: `shrjkexfokootrzrpjsi` — base URL: `https://supabase.com/dashboard/project/shrjkexfokootrzrpjsi`



| Task | Left sidebar path | Direct link |
|------|-------------------|-------------|
| Run `schema.sql` | **SQL Editor** → **+ New query** | [/sql/new](https://supabase.com/dashboard/project/shrjkexfokootrzrpjsi/sql/new) |
| Enable Anonymous + Email OTP | **Authentication** → **Sign In / Providers** | [/auth/providers](https://supabase.com/dashboard/project/shrjkexfokootrzrpjsi/auth/providers) |
| Turn off Confirm email | Same page → **Email** → expand → **Confirm email** OFF | [/auth/providers](https://supabase.com/dashboard/project/shrjkexfokootrzrpjsi/auth/providers) |
| Copy Project URL + anon key | **Project Settings** → **API Keys** → **Legacy API Keys** tab | [/settings/api-keys](https://supabase.com/dashboard/project/shrjkexfokootrzrpjsi/settings/api-keys) |
| Project URL (alternate) | **Integrations** → **Data API** → Overview | [/integrations/data_api/overview](https://supabase.com/dashboard/project/shrjkexfokootrzrpjsi/integrations/data_api/overview) |
| Verify tables | **Table Editor** | [/editor](https://supabase.com/dashboard/project/shrjkexfokootrzrpjsi/editor) |
| Auth logs (debug OTP issues) | **Logs** → **Auth** | [/logs/auth-logs](https://supabase.com/dashboard/project/shrjkexfokootrzrpjsi/logs/auth-logs) |
| Rate limits (optional) | **Authentication** → **Rate Limits** | [/auth/rate-limits](https://supabase.com/dashboard/project/shrjkexfokootrzrpjsi/auth/rate-limits) |
| Site URL for production (later) | **Authentication** → **URL Configuration** | [/auth/url-configuration](https://supabase.com/dashboard/project/shrjkexfokootrzrpjsi/auth/url-configuration) |



**If you don't see a menu item:** Supabase occasionally rolls out UI changes. Try the direct link in the table above, or use the **Connect** button (top of project home) for URL + keys. Older projects may label **Sign In / Providers** as **Providers** only; **Project Settings → API Keys** may still show a legacy **API** tab with the same anon key.



**Key format note:** CivicRadar uses the legacy **anon public** JWT (`eyJ…`) from the **Legacy API Keys** tab. Newer projects may also offer a **Publishable key** (`sb_publishable_…`); either low-privilege key works. Do not paste **secret** or **service_role** keys into `config.js`.


