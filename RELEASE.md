# CivicRadar — Release & Environments Runbook

This is the founder-friendly guide for testing changes on **staging** and shipping
them safely to **production**. CivicRadar is a static PWA (no build step) deployed to
GitHub Pages for production and Cloudflare Pages for staging/previews.

> TL;DR flow: `feature/*` → open PR (E2E gate + Cloudflare preview) → merge to
> `staging` (test on a real phone) → merge to `main` (auto-deploys to prod) → verify.

---

## 1. Environments

| Env | Where it runs | Host(s) | Supabase project | publicUrl |
|-----|---------------|---------|------------------|-----------|
| **dev** (local) | Your laptop | `localhost`, `127.0.0.1` | none — **pure local mode** (no remote read/write) | empty (links use current origin) |
| **staging** | Cloudflare Pages | `*.pages.dev`, `*civicradar-staging*` | **staging** project (separate from prod) | `https://civicradar-staging.pages.dev` |
| **prod** | GitHub Pages | `civicradarnh.github.io` | **production** (`shrjkexfokootrzrpjsi`) | `https://civicradarnh.github.io/civicradar` |

Environment is detected automatically by hostname in `js/config.js`
(`detectEnvironment()`). **Any unknown host falls back to production values**, so a
misconfigured or new host can never silently break the live site. The resolved
environment is exposed as `window.CIVICRADAR_CONFIG.environment` for debugging, and
dev/staging print `CivicRadar env: <env>` to the console (prod stays silent).

> **Why local dev uses no backend:** local mode keeps your laptop from reading or
> writing the shared databases. To exercise cross-device sync locally, temporarily
> paste the `staging` Supabase values into the `dev` block in `js/config.js` (never
> commit that change).

---

## 2. Branch & release flow

```
feature/my-change ──PR──▶ staging ──PR──▶ main ──▶ (GitHub Actions) ──▶ prod
        │                    │                │
   E2E gate +           phone smoke        E2E gate
   CF preview            test on CF        then deploy
```

### Start a feature

```bash
git checkout main
git pull
git checkout -b feature/short-description
# ...make changes...
git add -A
git commit -m "feat: short description"
git push -u origin feature/short-description
```

Open a PR against `staging` (or `main`). The **PR Checks** workflow runs the full
E2E suite as a required gate, and Cloudflare Pages posts a per-PR preview URL.

### Promote to staging

```bash
# Merge the PR into staging via the GitHub UI (preferred), or:
git checkout staging
git pull
git merge --no-ff feature/short-description
git push origin staging
```

Cloudflare auto-builds `https://staging.civicradar-staging.pages.dev` (branch
preview). Run the **phone smoke test** below against staging.

### Promote to production

```bash
# Open a PR from staging → main, let E2E pass, then merge.
git checkout main
git pull
git merge --no-ff staging
git push origin main
```

Pushing to `main` triggers `.github/workflows/deploy-pages.yml`, which **re-runs the
E2E suite as a gate and only then deploys** to GitHub Pages.

---

## 3. Test a release on staging (phone smoke test)

Do this on a **real phone** against the staging URL before promoting to prod. These
mirror the existing smoke-test items:

- [ ] **Camera** — capture a report photo (requires HTTPS; works on staging).
- [ ] **GPS** — allow location; ward auto-detects for Mumbai / Pune / Thane.
- [ ] **WhatsApp share (single language)** — share a report; confirm the message is
      in **one** language only (no duplicated multi-language block) and the
      `?report=` deep link uses the **staging** `publicUrl`.
- [ ] **PWA install** — "Add to Home Screen" works; app launches standalone.
- [ ] **Cross-device sync** — submit on one device, confirm it appears on another
      (validates the **staging Supabase** project, not prod).
- [ ] **Language switch** — toggle English / Hindi / Marathi / Gujarati; UI strings
      update everywhere.
- [ ] **Offline** — load once, go offline, confirm the app still opens (service
      worker cache).

If anything fails on staging, fix on the feature branch and re-PR. Never promote a
red smoke test.

---

## 4. Versioning

- **Git tags** — tag each production release:

  ```bash
  git tag -a v1.4.0 -m "Multi-city + navigation Phase 1"
  git push origin v1.4.0
  ```

- **Service worker cache bump** — the SW cache constant in `sw.js` is currently
  `const CACHE = 'civicradar-v67';`. **Bump this number on every production release**
  that changes cached assets (HTML/CSS/JS), so returning users get the new files
  instead of a stale cache. (Owned by the app agent — coordinate the bump as part of
  the release; see Follow-ups.)
- **CHANGELOG** — move items from `[Unreleased]` into a dated version section in
  `CHANGELOG.md` for each release.

---

## 5. Rollback

If a bad deploy reaches prod:

```bash
git checkout main
git pull
git revert <bad-commit-sha>     # or: git revert <oldest>..<newest> for a range
git push origin main            # re-runs E2E gate, then redeploys the reverted state
```

Notes:
- Reverting on `main` re-triggers the deploy workflow automatically.
- **Service worker:** after a revert, **bump the `CACHE` version again** (a new
  number, do not reuse an old one) so clients drop the bad cached assets. Reusing a
  previous version string can leave users on stale files.
- For an emergency, you can also re-run the last good deploy from the Actions tab
  (`Deploy to GitHub Pages` → Re-run) — but a git revert is the durable fix.

---

## 6. Setup checklist to ACTIVATE this process

These are one-time founder tasks. Until they are done, staging falls back to
placeholders and the optional Cloudflare CI workflow stays a safe no-op.

- [ ] **Create a staging Supabase project** (separate from prod
      `shrjkexfokootrzrpjsi`). Run `supabase/schema.sql` in its SQL Editor.
- [ ] **Fill staging values in `js/config.js`** — replace the `staging` block
      placeholders (`YOUR-STAGING-PROJECT`, `YOUR_STAGING_ANON_KEY`, and the
      `publicUrl`) with the staging project's URL + anon key and your Cloudflare
      staging domain. (Do **not** touch the `prod` block.)
- [ ] **Connect Cloudflare Pages** (see next section) for per-branch / per-PR
      previews.
- [ ] **Create a `staging` branch** in GitHub if it does not exist.
- [ ] **Enable branch protection** on `main` (and `staging`): require the
      **PR Checks / e2e** status check to pass before merge.

---

## 7. Cloudflare Pages preview (staging)

### Primary — dashboard, zero secrets (recommended)

1. [dash.cloudflare.com](https://dash.cloudflare.com) → **Workers & Pages** →
   **Create** → **Pages** → **Connect to Git**.
2. Select the `civicradar` repository.
3. Build settings:
   - **Framework preset:** None
   - **Build command:** *(leave empty — static site, no build)*
   - **Build output directory:** `/` (repo root)
4. Name the project `civicradar-staging` and **Save and Deploy**.
5. Cloudflare now builds:
   - **Production branch** (set this to `staging`, *not* `main`, so Cloudflare
     mirrors staging — prod stays on GitHub Pages).
   - **Per-branch previews:** `https://<branch>.civicradar-staging.pages.dev`
   - **Per-PR previews:** a unique URL commented on each pull request.
6. Set the `staging.publicUrl` in `js/config.js` to the staging domain Cloudflare
   assigns.

No secrets live in the repo with this path — Cloudflare pulls from GitHub directly.

### Optional — GitHub Action variant

`.github/workflows/preview-cloudflare.yml` can drive previews from CI instead. It is
**guarded**: if `CLOUDFLARE_API_TOKEN` / `CLOUDFLARE_ACCOUNT_ID` secrets are absent,
the run is a successful no-op (never red). To enable it, follow the comments at the
top of that file (create the Pages project + add the two repo secrets).

### Why Cloudflare for previews (GitHub Pages limitation)

GitHub Pages serves **one site per repository** (the production branch only) — it has
no per-branch or per-PR preview URLs. Cloudflare Pages gives a unique URL for every
branch and every PR, which is exactly what staging review needs. So: **prod →
GitHub Pages, staging/previews → Cloudflare Pages.**

---

## 8. Deferred follow-ups (require editing in-flight files)

These were intentionally **not** changed to avoid conflicting with the app agent
currently editing `js/app.js`, `index.html`, `sw.js`, etc. Do them as a small,
separate change once that work lands:

- **SW cache bump on release** — `sw.js` `const CACHE` must be incremented per
  production release (and per rollback). Owned by `sw.js`; not edited here.
- **Show the environment badge (optional)** — `js/app.js` could surface
  `window.CIVICRADAR_CONFIG.environment` (e.g. a small "STAGING" ribbon) so testers
  never confuse staging with prod. Hook point: read `CFG.environment` near the
  existing `const CFG = window.CIVICRADAR_CONFIG || {}` usage.
- **Tag analytics with environment (optional)** — pass `environment` into the
  analytics payload so staging traffic can be filtered out of prod metrics.
