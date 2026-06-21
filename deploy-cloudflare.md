# Deploy CivicRadar to Cloudflare Pages (alternative)

**Recommended path for first launch:** GitHub Pages — see `LAUNCH-WALKTHROUGH.md` Phase C.

Use Cloudflare Pages if you prefer Cloudflare DNS, custom domain, or already use Cloudflare for your domain.

---

## Prerequisites **[YOU]**

- Cloudflare account: [dash.cloudflare.com](https://dash.cloudflare.com)
- Repo pushed to GitHub (or GitLab)
- `js/config.js` filled with Supabase keys and emails

---

## Option A — Dashboard (no CLI)

1. Cloudflare dashboard → **Workers & Pages** → **Create** → **Pages** → **Connect to Git**
2. Select your `civicradar` repository
3. Build settings:
   - **Framework preset:** None
   - **Build command:** *(leave empty)*
   - **Build output directory:** `/` (repo root)
4. **Save and Deploy**
5. Your site URL: `https://civicradar.pages.dev` (or similar)
6. Set `publicUrl` in `js/config.js` to that URL → commit → push (auto-redeploys)

### Custom domain **[OPTIONAL]**

Pages project → **Custom domains** → add e.g. `civicradar.app`  
Update DNS at your registrar per Cloudflare instructions.

---

## Option B — Wrangler CLI

Install Node.js, then:

```powershell
npm install -g wrangler
wrangler login
```

From repo root:

```powershell
cd C:\civicradar
wrangler pages project create civicradar
wrangler pages deploy . --project-name=civicradar
```

Output shows the preview URL. For production:

```powershell
wrangler pages deploy . --project-name=civicradar --branch=main
```

Set `publicUrl` to the assigned `*.pages.dev` URL (or custom domain).

---

## Notes

- No build step required — static HTML/CSS/JS at repo root
- HTTPS is automatic (required for camera + GPS)
- The anon Supabase key in `config.js` is safe to deploy (RLS protects data)
- Large folders (`video/`, `tools/ffmpeg/`) deploy too — trim repo or add `.cfignore` later if deploy size matters

---

## Compare: GitHub Pages vs Cloudflare Pages

| | GitHub Pages | Cloudflare Pages |
|---|-------------|------------------|
| Setup | Workflow already in repo | Dashboard or Wrangler |
| HTTPS | Yes | Yes |
| Custom domain | Yes (CNAME) | Yes |
| Best if | Already on GitHub | Domain already on Cloudflare |

See `LAUNCH-WALKTHROUGH.md` for the full launch sequence.
