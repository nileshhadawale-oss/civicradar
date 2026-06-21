# CivicRadar — First-Time Launch Walkthrough

**For:** Nihira Hadawale (founder) + Nilesh Hadawale (parent / legal operator)  
**Prepared:** 21 June 2026  
**Verdict:** App code is **GO with conditions** — complete the steps below before real users.

Legend for each step:
- **[YOU]** — only a human can do this (accounts, emails, legal, phone test, outreach)
- **[AGENT/DONE]** — already verified or prepared in this session
- **[OPTIONAL]** — nice to have; not a launch blocker

---

## Quick start — do this next (ordered)

### Today (~2 hours)

| # | Step | Who |
|---|------|-----|
| 1 | ~~Create Supabase project~~ → **Run schema + enable auth** (project `shrjkexfokootrzrpjsi` exists; keys in config) | **[YOU]** |
| 2 | Run `supabase/schema.sql` in **SQL Editor → New query** | **[YOU]** |
| 3 | Enable **Anonymous** + **Email (OTP)** in **Authentication → Sign In / Providers** | **[YOU]** — *required; app shows connect error until Anonymous is on* |
| 4 | ~~Paste Supabase keys~~ → **Verify "Connected" toast** on reload | **[YOU]** |
| 5 | Fill real emails: `grievanceEmail`, `founder.email`, `founder.operatorEmail` | **[YOU]** |
| 6 | Push repo to GitHub + enable Pages (see Phase C) | **[YOU]** |
| 7 | Set `publicUrl` to your live HTTPS URL | **[YOU]** |
| 8 | Open site on Android phone — camera, GPS, WhatsApp share | **[YOU]** |

### This week

| # | Step | Who |
|---|------|-----|
| 9 | Send `privacy.html` + `terms.html` to Indian legal counsel | **[YOU]** |
| 10 | Insert one real NGO invite code for your pilot ward | **[YOU]** |
| 11 | Soft launch: 1 ward, 2–3 WhatsApp groups | **[YOU]** |
| 12 | Install Python on deploy machine; re-run E2E suite | **[YOU]** |
| 13 | Replace emoji PWA icons with 512×512 PNG | **[OPTIONAL]** |
| 14 | Custom domain (e.g. civicradar.app) on GitHub Pages or Cloudflare | **[OPTIONAL]** |

---

## What was automated / verified this session

| Item | Result |
|------|--------|
| Supabase project + keys in `js/config.js` | **[AGENT/DONE]** Project `shrjkexfokootrzrpjsi` (Mumbai); URL + anon key filled |
| Critical JS bug (`resolutionBadgeHtml` duplicate) | **[AGENT/DONE]** Fixed — app was failing to load |
| `sw.js` cache version | **[AGENT/DONE]** `civicradar-v42`, network-first `config.js` |
| Local server (`serve.ps1 -Port 8095`) | **[AGENT/DONE]** HTTP 200 on `/`, `/privacy.html`, `/terms.html` |
| i18n audit (`tools/i18n-audit.ps1`) | **[AGENT/DONE]** 602 EN keys; 0 missing in HI/MR/GU |
| E2E comprehensive (this audit) | **83/87 PASS** — 4 expected fails with Supabase on (unbundled consent + hidden demo logins). Prior local-mode run: 109/109 |
| GitHub Pages workflow | **[AGENT/DONE]** Created `.github/workflows/deploy-pages.yml` |
| Config template | **[AGENT/DONE]** Created `js/config.example.js` (example values only, no real secrets) |
| `founder.operatorName` | **[AGENT/DONE]** Pre-filled: Nilesh Hadawale |
| Email placeholder comments in `js/config.js` | **[AGENT/DONE]** Marked **[YOU]** fields |

---

## Blockers needing your input

Answer these before going live:

1. **Supabase auth** — Enable Anonymous sign-ins at **Authentication → Sign In / Providers** (keys are already in `js/config.js`; sync won't work until this is on).
2. **Email addresses** — What real emails for `legal.grievanceEmail`, `founder.email`, `founder.operatorEmail`?
3. **GitHub repo / Pages URL** — Repo name and user for `publicUrl` (e.g. `https://<user>.github.io/civicradar/`).
4. **Pilot ward** — Which BMC ward for soft launch (e.g. G/N Ward — Dadar)?
5. **Legal counsel** — Indian privacy/DPDP lawyer to review `privacy.html` and `terms.html`?

---

## Phase A — Configure `js/config.js`

**Goal:** Connect the app to Supabase and set public contact details.

### A1. Open the config file **[YOU]**

Edit `js/config.js` (or copy from template):

```powershell
copy js\config.example.js js\config.js
# then edit js\config.js with your real values
```

### A2. Required fields (must fill before launch)

| Field | Example (not real) | Where it appears |
|-------|-------------------|------------------|
| `supabaseUrl` | `https://abcdefgh.supabase.co` | Backend sync |
| `supabaseAnonKey` | `eyJhbGciOiJIUzI1NiIs…` | Backend sync |
| `publicUrl` | `https://youruser.github.io/civicradar` | WhatsApp shares, `?report=` deep links |
| `legal.grievanceEmail` | `privacy@yourdomain.com` | Privacy + Terms pages |
| `founder.email` | `nihira@yourdomain.com` | About modal, partner inquiries |
| `founder.operatorEmail` | `nilesh@yourdomain.com` | Legal fallback contact |

### A3. Already pre-filled **[AGENT/DONE]**

- `founder.name`, `founder.role`, `founder.school`, `founder.story`, `founder.highlights`
- `founder.operatorName`: **Nilesh Hadawale**
- BMC channel URLs, scale/moderation defaults, demo NGO codes (local testing only)

### A4. Optional overrides **[OPTIONAL]**

| Field | When to change |
|-------|----------------|
| `monetization.sponsors` | Real local business partners |
| `monetization.partnerInquiryEmail` | Separate partners inbox |
| `bmcChannels.*` | If BMC publishes new app store links |
| `demoNgoCodes` | Local dry-runs only — production codes live in Supabase |

### A5. Where to get Supabase keys **[YOU]**

1. Open your project: [supabase.com/dashboard/project/shrjkexfokootrzrpjsi](https://supabase.com/dashboard/project/shrjkexfokootrzrpjsi)
2. Left sidebar → **Project Settings** → **API Keys**
   - Direct link: [settings/api-keys](https://supabase.com/dashboard/project/shrjkexfokootrzrpjsi/settings/api-keys)
3. Copy **Project URL** (shown at top, or **Integrations → Data API → Overview**)
4. Open the **Legacy API Keys** tab → copy **anon public** key (`eyJ…`) → paste as `supabaseAnonKey`

> **If you don't see Legacy API Keys:** use the **Connect** button on the project home page, or the **Publishable key** (`sb_publishable_…`) on the **API Keys** tab. Either low-privilege key works. Never paste **secret** or **service_role** keys into the browser config.

> The anon key is safe in the browser. Row-level security (RLS) in `schema.sql` protects your data.

### A6. Verify locally **[YOU]**

```powershell
powershell -File serve.ps1 -Port 8095
```

Open `http://localhost:8095/`. After Supabase keys are set, you should see a toast: **"Connected — reports now sync across devices."**

Demo logins (`admin/password`, `lead/password`) **disappear** once Supabase is configured.

---

## Phase B — Supabase setup (Mumbai)

**Goal:** Database tables, security rules, and auth providers for cross-device sync.

### B1. Create project **[YOU]**

1. [supabase.com](https://supabase.com) → **New project**
2. Name: e.g. `civicradar-prod`
3. Strong database password (save in a password manager)
4. Region: **South Asia (Mumbai)** — `ap-south-1`
5. Wait ~2 minutes for provisioning

### B2. Run the schema **[YOU]**

1. Left sidebar → **SQL Editor** → **+ New query**
   - Direct link: [sql/new](https://supabase.com/dashboard/project/shrjkexfokootrzrpjsi/sql/new)
2. Open `supabase/schema.sql` from this repo
3. Select **all** (~616 lines) → paste → **Run** (or Ctrl+Enter)

**Path:** `C:\civicradar\supabase\schema.sql`

The file is **safe to re-run** (uses `IF NOT EXISTS` / `OR REPLACE`). For a **brand-new** project, run the **entire file once**.

**Verify:** Left sidebar → **Table Editor** ([editor](https://supabase.com/dashboard/project/shrjkexfokootrzrpjsi/editor)) — confirm `reports`, `profiles`, `ngo_codes`, and `analytics_events` appear.

#### If upgrading an existing Supabase project

Run the **full file** again, or at minimum these migration blocks:

| Migration | Lines (approx.) | What it adds |
|-----------|-----------------|--------------|
| v22 — Analytics | ~383–439 | `analytics_events` table, `get_analytics_summary()` |
| v23 — Account erasure | ~442–469 | `delete_user_data()` RPC (DPDP deletion) |
| v39 — Community fix verification | ~472–615 | `report_fix_confirmations`, `confirm_fix()`, updated `delete_user_data()` + analytics summary |

For a fresh launch, just run everything — no need to cherry-pick.

### B3. Enable auth providers **[YOU]**

Left sidebar → **Authentication** → **Sign In / Providers**:
- Direct link: [auth/providers](https://supabase.com/dashboard/project/shrjkexfokootrzrpjsi/auth/providers)

| Provider | Setting |
|----------|---------|
| **Anonymous sign-ins** | **Enable** (citizens get auto accounts) |
| **Email** | **Enable** → expand Email settings → **Confirm email** **OFF**; Email OTP is the default passwordless method |

> **If you don't see "Sign In / Providers":** look for **Providers** under Authentication (older UI label). OTP emails require Email enabled; Confirm email should stay off so BMC/NGO login isn't blocked by a separate confirmation step.

> **Optional (production):** After deploy, set **Authentication → URL Configuration** → Site URL to your `publicUrl` and add redirect URLs for localhost + production.

### B4. Paste keys into config **[YOU]**

See Phase A5. Reload the app and confirm the "Connected" toast.

### B5. Issue NGO invite codes (before coordinators join) **[YOU]**

In **SQL Editor → New query** ([sql/new](https://supabase.com/dashboard/project/shrjkexfokootrzrpjsi/sql/new)), after schema is applied:

```sql
-- Ward-wide lead (pilot ward — edit ward name)
insert into public.ngo_codes (code, ward, ngo_name, coordinator_scope)
values ('CLEAN-GN-2026', 'G/N Ward — Dadar, Shivaji Park', 'Your NGO Name', 'ward');
```

Share the code + your `publicUrl` with the coordinator. They use **Volunteer / NGO login** → email OTP + code.

**[OPTIONAL]** Neighbourhood-scoped leads: see examples in `BACKEND_SETUP.md`.

---

## Phase C — Deploy static site (recommended: GitHub Pages)

**Why GitHub Pages:** CivicRadar is a static PWA (HTML/CSS/JS at repo root). No build step. Free HTTPS. Works with the workflow already created.

**Alternative:** Cloudflare Pages — see `deploy-cloudflare.md`.

### C1. Create GitHub repo **[YOU]**

1. [github.com/new](https://github.com/new) → name e.g. `civicradar`
2. Keep repo **public** (required for free GitHub Pages on personal accounts) **or** use GitHub Pro for private Pages

### C2. Push code **[YOU]**

From `C:\civicradar`:

```powershell
git init
git add .
git commit -m "Initial CivicRadar launch"
git branch -M main
git remote add origin https://github.com/YOUR-USER/civicradar.git
git push -u origin main
```

> **Before pushing:** Confirm `js/config.js` has your Supabase keys and emails. If the repo is public, consider using GitHub **Secrets** + a future build step — for now, the anon key is designed to be public (RLS protects data).

### C3. Enable GitHub Pages **[YOU]**

1. Repo → **Settings** → **Pages**
2. **Source:** GitHub Actions (not "Deploy from branch")
3. Push to `main` triggers `.github/workflows/deploy-pages.yml` **[AGENT/DONE]**

### C4. Confirm deploy **[YOU]**

1. Repo → **Actions** tab → wait for green "Deploy to GitHub Pages"
2. Settings → Pages shows URL, typically:
   `https://YOUR-USER.github.io/civicradar/`

### C5. Smoke test production **[YOU]**

Open in browser:
- `https://YOUR-USER.github.io/civicradar/`
- `…/privacy.html`
- `…/terms.html`

Confirm "Connected" toast if Supabase keys are in the deployed `config.js`.

---

## Phase D — Set `publicUrl` to match deploy URL

**Critical:** WhatsApp share links and `?report=` deep links use `publicUrl`. If empty, they fall back to `localhost`.

### D1. Edit config **[YOU]**

In `js/config.js`:

```js
publicUrl: 'https://YOUR-USER.github.io/civicradar',
```

Use your **exact** deployed URL. Trailing slash is OK.

### D2. Redeploy **[YOU]**

```powershell
git add js/config.js
git commit -m "Set production publicUrl"
git push
```

Wait for GitHub Actions to finish (~1–2 min).

### D3. Test a deep link **[YOU]**

1. Submit a test report on your phone
2. Tap **Share on WhatsApp**
3. Confirm the link starts with your `publicUrl`, not `localhost`

**[OPTIONAL]** Custom domain: GitHub Pages → Settings → Custom domain → add DNS CNAME. Then update `publicUrl` to `https://civicradar.app` (or your domain).

---

## Phase E — Test on a real phone

Use **Android Chrome** first (camera + PWA install work well). iOS Safari also works.

### Checklist **[YOU]**

| # | Test | Pass? |
|---|------|-------|
| 1 | Open production HTTPS URL (not localhost) | ☐ |
| 2 | Accept Terms + Privacy; analytics opt-in works | ☐ |
| 3 | Select ward + display name in onboarding | ☐ |
| 4 | Allow location when prompted | ☐ |
| 5 | Report → take photo → GPS pin → submit | ☐ |
| 6 | Report appears on map + in Profile | ☐ |
| 7 | **Me too** on another device / account corroborates | ☐ |
| 8 | WhatsApp share link opens correct report | ☐ |
| 9 | **Add to Home Screen** (PWA install) | ☐ |
| 10 | Profile → Delete my data (if Supabase connected) | ☐ |
| 11 | 1916 / MyBMC links open correctly | ☐ |
| 12 | Hindi / Marathi / Gujarati UI switches | ☐ |

**[OPTIONAL]** Test NGO login with real invite code + BMC official with `@mcgm.gov.in` email.

---

## Phase F — Soft launch (1 ward)

**Goal:** Real users in one ward before city-wide promotion.

### F1. Pick pilot ward **[YOU]**

Choose a ward where you have family, an NGO contact, or WhatsApp group access.

### F2. Onboard one NGO coordinator **[YOU]**

1. Insert invite code in Supabase (Phase B5)
2. Email/WhatsApp the code + URL to the lead
3. They sign in → open **Coordinator Hub** → verify volunteers/hazards show

### F3. WhatsApp outreach **[YOU]**

Share in 2–3 trusted groups:

> CivicRadar — free ward hazard map for monsoon stagnant water. Report with photo + pin, neighbours can corroborate, optional BMC filing. Not official BMC. [your publicUrl]

### F4. Monitor first week **[YOU]**

- BMC Admin → App health (if you have a BMC test account)
- Watch for abusive uploads (client-side moderation is enabled)
- Respond to grievance emails promptly

**[OPTIONAL]** Disable demo sponsor in config (`monetization.sponsors` with `active: false`).

---

## Phase G — Legal

### G1. Counsel review **[YOU]**

Send to qualified **Indian** privacy/DPDP counsel:
- `privacy.html`
- `terms.html`
- Note: founder is 17; `operatorEmail` is parent/legal operator

### G2. Grievance officer **[YOU]**

Set `legal.grievanceEmail` to a monitored inbox. Required under DPDP for data-principal complaints.

### G3. Disclaimers **[AGENT/DONE]**

App already states: independent community tool, not official BMC/MCGM. Do not change copy to imply government affiliation.

---

## Phase H — App stores (optional, later)

CivicRadar works as a **PWA today** — "Add to Home Screen" is the recommended path for launch.

| Platform | Recommendation |
|----------|----------------|
| Google Play | **[OPTIONAL]** TWA via Bubblewrap — see `STORE_LAUNCH.md` |
| Apple App Store | **[OPTIONAL]** Higher rejection risk for WebView-only — prefer PWA |

Before store submission:
- Replace emoji icons in `manifest.json` with 512×512 PNG
- Complete Data safety / App Privacy forms honestly
- Ensure demo logins are hidden (Supabase configured)

---

## Supabase SQL reference

| File | Purpose |
|------|---------|
| `supabase/schema.sql` | **Run once** for new projects — tables, RLS, RPCs, realtime |
| `supabase/storage-migration.sql` | **[OPTIONAL]** Later — move photos from DB to Storage at scale |

### Key RPCs created by schema.sql

| Function | Purpose |
|----------|---------|
| `delete_user_data(session_id)` | Profile → Delete my data (DPDP erasure) |
| `confirm_fix(report_id, …)` | Community "looks fixed" verification (v39) |
| `redeem_ngo_code(…)` | NGO coordinator onboarding |
| `get_analytics_summary(days)` | BMC App health dashboard |

---

## Local development commands

```powershell
# Start local server
powershell -File serve.ps1 -Port 8095

# i18n audit
powershell -File tools\i18n-audit.ps1

# E2E tests (requires Python 3)
python tests\e2e_comprehensive.py
```

---

## Related docs

| Doc | Contents |
|-----|----------|
| `LAUNCH_CHECKLIST.md` | Pre-launch gate audit |
| `BACKEND_SETUP.md` | Supabase roles, NGO codes, analytics |
| `STORE_LAUNCH.md` | Play Store / App Store checklist |
| `js/config.example.js` | Safe template with example values |
| `deploy-cloudflare.md` | Alternative deploy via Cloudflare Pages |
| `.github/workflows/deploy-pages.yml` | GitHub Pages CI |

---

## Launch readiness checklist (final gate)

Before sending to real users outside your pilot:

- [ ] `supabaseUrl` + `supabaseAnonKey` set
- [ ] `publicUrl` matches live HTTPS deploy
- [ ] `grievanceEmail`, `founder.email`, `operatorEmail` are real monitored inboxes
- [ ] `supabase/schema.sql` run via **SQL Editor → New query**
- [ ] Anonymous + Email OTP enabled at **Authentication → Sign In / Providers**
- [ ] Phone test passed (camera, GPS, WhatsApp, PWA)
- [ ] Legal counsel reviewed privacy + terms
- [ ] At least one real NGO invite code for pilot ward
- [ ] Demo admin/NGO logins not visible (Supabase connected)

**When all boxes are checked → GO for soft launch.**
