# CivicRadar — Shared Backend Setup (Supabase)

CivicRadar runs in two modes:

- **Local / demo mode (default):** no setup, data lives in the browser only. Reports are *not* shared between devices.
- **Connected mode:** reports & pledges sync across all devices in real time, so a citizen's report shows up on the BMC admin's map instantly.

Connected mode uses [Supabase](https://supabase.com) (free tier is enough to start).

> **Free tier limits & scale plan:** Supabase free includes ~500 MB database, 1 GB
> Storage, 5 GB/month egress, and 50K MAU. CivicRadar's main risk is hazard photos
> stored as data URLs in Postgres. See [`ARCHITECTURE.md`](ARCHITECTURE.md) for India
> NFRs, cost triggers, and staged upgrades (Storage migration at ~1K–10K users).

---

## 1. Create the project

1. Go to <https://supabase.com> → **New project**.
2. Pick a name, a strong database password, and a region close to your users
   (e.g. **South Asia (Mumbai)** `ap-south-1` for India — keeps data in-country).
3. Wait ~2 minutes for it to provision.

## 2. Create the tables & security rules

1. Left sidebar → **SQL Editor** → **+ New query**
   - Example: `https://supabase.com/dashboard/project/YOUR-PROJECT-REF/sql/new`
2. Copy the entire contents of [`supabase/schema.sql`](supabase/schema.sql) and **Run** it (Ctrl+Enter).
   - This creates the `reports` and `pledges` tables, row-level security (RLS)
     policies, and enables realtime.
3. **Verify:** Left sidebar → **Table Editor** — confirm `reports`, `profiles`, `ngo_codes` exist.

## 3. Turn on anonymous sign-in and email OTP

The app gives every visitor an anonymous account so reports can be tied to an owner
without forcing a login. BMC/NGO staff sign in with email OTP.

1. Left sidebar → **Authentication** → **Sign In / Providers**
   - Example: `https://supabase.com/dashboard/project/YOUR-PROJECT-REF/auth/providers`
2. **Anonymous sign-ins** → **Enable**
3. **Email** → **Enable** → expand Email settings:
   - **Confirm email** → **OFF** (OTP login without a separate confirmation step)
   - Email OTP is the default passwordless method (no magic link setup needed)

> **If you don't see "Sign In / Providers":** look for **Providers** under Authentication (older UI).

## 4. Paste your keys

1. Left sidebar → **Project Settings** → **API Keys**
   - Example: `https://supabase.com/dashboard/project/YOUR-PROJECT-REF/settings/api-keys`
2. Copy **Project URL** (top of page, or **Integrations → Data API → Overview**)
3. Open **Legacy API Keys** tab → copy **anon public** key (`eyJ…`)
   - Newer projects may show a **Publishable key** (`sb_publishable_…`) instead — either works
4. Open [`js/config.js`](js/config.js) and fill them in:

   ```js
   window.CIVICRADAR_CONFIG = {
     supabaseUrl: 'https://YOUR-PROJECT.supabase.co',
     supabaseAnonKey: 'eyJhbGciOi...your anon key...',
   };
   ```

5. Reload the app. You should see a toast: **"Connected — reports now sync across devices."**

> The anon key is **safe to ship in the browser** — RLS (step 2) is what protects
> your data, not the key. Never put **secret** or **service_role** keys in `config.js`.

> **If API Keys looks different:** use the **Connect** button on the project home page, or the legacy **API** tab under Project Settings.

---

## How it behaves

- **Offline / flaky network:** writes always save to `localStorage` first, then sync.
  If sync fails the report still appears locally and you'll see a "will retry" notice.
- **Realtime:** when any device adds or resolves a report, every open client updates
  automatically (map markers, profile stats, community counts).
- **Ownership:** reports/pledges created before you connected are re-keyed to your
  anonymous account on first connect and pushed up (best effort).

## Roles & elevated access (BMC / NGO)

CivicRadar has three roles, enforced by the database (`profiles.role` + RLS):

| Role | How it's granted | Can do |
| --- | --- | --- |
| `citizen` (default) | Anonymous sign-in | Report, file with BMC, self-confirm own resolved reports |
| `bmc` | **Official gov email** (OTP). Auto-granted to allowlisted domains (`mcgm.gov.in`, `gov.in`, `*.gov.in`, `maharashtra.gov.in`) by a signup trigger | Hazard Queue dashboard, resolve any report |
| `ngo_lead` | **Email OTP + NGO invite code**. Redeeming a code (`redeem_ngo_code` RPC) grants the role and assigns a ward | Coordinator Hub: dispatch volunteers, log community cleanups, verify pledge hours |

**To onboard a BMC official:** they simply sign in with their `@mcgm.gov.in` email and enter the emailed code. The trigger grants `bmc` automatically.

**To onboard an NGO coordinator:** insert an invite code, then share it with them:

```sql
-- Ward-wide lead (sees all volunteers & hazards in the ward)
insert into public.ngo_codes (code, ward, ngo_name, coordinator_scope)
values ('CLEAN-HW-2026', 'H/W Ward — Bandra West, Khar West', 'Bandra Cares', 'ward');

-- Neighbourhood / RWA lead (narrower scope — matches neighbourhood tags)
insert into public.ngo_codes (code, ward, ngo_name, neighbourhood, coordinator_scope)
values (
  'NBH-WORLI-2026',
  'G/S Ward — Worli, Lower Parel',
  'Worli West RWA',
  'Worli West — Phoenix Mills area',
  'neighbourhood'
);
```

They sign in with their email + this code. The RPC grants `ngo_lead`, assigns the ward, and stores
`coordinator_scope` + `neighbourhood_label` on their profile.

**Demo codes (local mode, no Supabase):** see `demoNgoCodes` in [`js/config.js`](js/config.js), or use demo logins:
`lead` / `password` (ward lead) and `lead-nbh` / `password` (neighbourhood lead, Worli demo).

---

## Volunteer self-help & neighbourhood leads (v34+)

Citizens can sign up to volunteer in their ward (Community tab → **Volunteer in my ward**). Data lives in
`volunteer_signups` (localStorage + Supabase when connected). Optional phone/WhatsApp is **never** auto-dialled —
coordinators see it only in the hub if the citizen entered it (DPDP-friendly).

**Citizen loop**

1. Set ward in onboarding.
2. Community → Volunteer signup (neighbourhood/society, hours, skills).
3. On a pending hazard pin → **I can help clean this** (creates `volunteer_tasks` row).
4. Neighbourhood/ward lead marks task complete → `community_cleared` on the report + reporter toast.

**Coordinator scopes**

| Scope | Sees |
| --- | --- |
| `ward` | All volunteer signups, tasks, pledges, and open hazards in that ward |
| `neighbourhood` | Same tables, filtered to matching `neighbourhood` text (RWA/society/lane) |

BMC filing remains separate — community cleanup is **not** official BMC resolution.

### Launch checklist — designating leads

1. Run the latest [`supabase/schema.sql`](supabase/schema.sql) (volunteer tables + `ngo_codes.neighbourhood`).
2. Pick scope: one **ward lead** per BMC ward, or multiple **neighbourhood leads** (RWAs/societies) within a ward.
3. Insert invite code(s) in **SQL Editor → New query**.
4. Email the code + CivicRadar URL to the lead; they use **Volunteer / NGO login** → email OTP + code.
5. Lead opens **Coordinator hub** — volunteers, cleanup offers, pledges, hazards in scope.
6. Optional: add demo codes to `js/config.js` → `demoNgoCodes` for dry runs without email OTP.

### Analytics events (new)

| Event | When |
| --- | --- |
| `volunteer_signup_created` | Citizen saves volunteer signup |
| `volunteer_task_offered` | Citizen taps “I can help clean this” |
| `volunteer_task_completed` | Lead marks volunteer task done |

> Enable **Anonymous** and **Email (OTP)** at **Authentication → Sign In / Providers** ([docs](https://supabase.com/docs/guides/auth/general-configuration)).

In **local/demo mode** (no Supabase), the BMC/NGO logins fall back to labelled demo credentials (`admin`/`password`, `lead`/`password`, `lead-nbh`/`password`) so you can explore dashboards without setup.

## Official BMC channels (citizen filing)

CivicRadar deep-links to real BMC channels; it does **not** submit complaints on your behalf.

| Channel | Use for | URL / contact |
| --- | --- | --- |
| **1916** | Stagnant water / pest control complaints | `tel:1916` |
| **MyBMC WhatsApp** | Chatbot complaint filing | `+91 8999228999` |
| **MyBMC portal** | Online complaint registration (CCRS) | [portal.mcgm.gov.in](https://portal.mcgm.gov.in/irj/portal/anonymous/qlcomplaintreg?guest_user=english) |
| **@mybmc** | Public follow-up on X | `@mybmc` |
| **Aaple Sarkar** | State grievance after ~30 days | [aaplesarkar.mahaonline.gov.in](https://aaplesarkar.mahaonline.gov.in/) |
| **Participate Mumbai** | Volunteering, CSR, ward project proposals — **not** complaint filing | [participatemumbai.mcgm.gov.in](https://participatemumbai.mcgm.gov.in/) (override in `js/config.js` → `bmcChannels.participateMumbaiUrl`) |

There is no public API for Participate Mumbai or CCRS complaint submission; integration is deep-link + UX copy only unless BMC provides a partnership/API later.

## Super-user dashboards

- **BMC Hazard Queue:** filterable (by ward) and sortable (oldest / newest / overdue) list of pending reports, with summary stats (pending, overdue 7d+, resolved, average age) and resolve-with-confirmation. Opens from the BMC badge after login.
- **NGO Coordinator Hub:** open-hazard list for the coordinator's scope (ward or neighbourhood) with one-tap **Log cleanup**, volunteer signups, volunteer cleanup offers, pledge delivery/verification, and stats.

## Production hardening (before a real launch)

The connected build now enforces roles server-side (gov-domain trigger, invite-code
RPC, role-based RLS). Remaining items to address before a public launch:

1. **Domain allowlist is broad.** Auto-granting `bmc` to any `*.gov.in` is convenient
   but generous. For production, restrict to specific verified addresses or add a
   manual approval step (e.g. an `bmc` approval queue an existing admin confirms).
2. **NGO codes are shared secrets.** Rotate/expire them, set sensible `max_uses`, and
   consider per-coordinator invites instead of a shared ward code.
3. **Images are stored as data URLs in a `text` column.** For scale, upload photos
   to **Supabase Storage** and store only the URL.
4. **Photo moderation (client-side).** Reports run through `js/image-moderation.js`:
   file-type/size checks, EXIF stripping, blank/document/selfie heuristics, and
   optional NSFW scanning (lazy-loaded when online). Tune thresholds in
   `js/config.js` → `moderation`. For production, add server-side review (Supabase
   Edge Function + Vision API) before images are published to the map.
5. **Rate limiting / abuse:** add per-user insert limits and admin flagging before
   opening to the public. Supabase auth rate limits: **Authentication → Rate Limits**
   ([`/auth/rate-limits`](https://supabase.com/dashboard/project/_/auth/rate-limits)); auth event logs: **Logs → Auth**
   ([`/logs/auth-logs`](https://supabase.com/dashboard/project/_/logs/auth-logs)).
6. **HTTPS:** serve the app over HTTPS (required for camera + geolocation in the field).
7. **Demo logins:** the `DEMO_CREDENTIALS` fallback only applies in local mode (no
   backend). Ensure production always ships with Supabase configured so demo creds are
   never shown.

---

## Free tier limits (Supabase)

| Resource | Free allowance | CivicRadar note |
| --- | --- | --- |
| Database | 500 MB | JPEG data URLs in `reports.image` fill this first |
| Storage | 1 GB | Use after migrating photos (see `supabase/storage-migration.sql`) |
| Bandwidth | 5 GB/month | Full sync + images; paginated sync in app reduces this |
| Auth MAU | 50,000 | Anonymous + email OTP users |
| Region | Pick **Mumbai (`ap-south-1`)** | Lower latency for India; data residency expectations |

**Tune without code changes:** `js/config.js` → `scale` (batch size, image size, local report cap).

**When to upgrade:** DB > ~400 MB, bandwidth warnings, or > ~150 simultaneous Realtime
connections. Full staging guide: [`ARCHITECTURE.md`](ARCHITECTURE.md).

---

## Analytics (app health & impact)

CivicRadar ships a lightweight client analytics layer (`js/analytics.js`). It runs after
Terms acceptance and records **anonymous** events only:

| Event | Purpose |
| --- | --- |
| `session_start`, `tab_view` | Traffic / navigation |
| `report_submitted`, `report_corroborated`, `bmc_filed`, `report_resolved`, `community_cleanup`, `whatsapp_share` | Civic impact funnel |
| `volunteer_signup_created`, `volunteer_task_offered`, `volunteer_task_completed` | Volunteer self-help loop |
| `error` | Client crashes & failed paths (no photos/GPS in payload) |
| `perf` | Load times, map init, report submit, sync duration |

**Privacy:** random session UUID in `sessionStorage`; ward **code** only (e.g. `G/N Ward`);
no email, display name, photos, or coordinates. Events batch locally and flush to
Supabase when configured. Analytics never blocks the app.

**Database:** the analytics block at the bottom of [`supabase/schema.sql`](supabase/schema.sql)
creates `analytics_events` with RLS (anonymous insert, no direct read). Run it after the
main schema if upgrading an existing project.

**Dashboards in-app:**

- **Community tab** — public report impact (all-time + “this week” from local reports).
- **BMC Admin → Hazard Queue → App health** — last 7 days from device buffer + cloud
  aggregate via `get_analytics_summary()` RPC when Supabase is connected.

Tune sampling in `js/config.js` → `analytics` (`sampleRate`, `batchSize`, `flushIntervalMs`).
Set `debug: true` to log events to the console in local mode.

**Consent:** analytics runs only after the user opts in at Terms acceptance (separate checkbox).
Withdraw via Profile → Withdraw analytics consent.

---

## DPDP / account erasure

**In-app:** Profile → Delete my data clears local storage and calls `delete_user_data()` RPC.

**RPC** (bottom of `schema.sql`, migration v23) deletes for `auth.uid()`:

- `reports`, `pledges`, `volunteer_signups`, `report_confirmations`, linked `volunteer_tasks`
- `analytics_events` rows matching the current session UUID (if passed)

Re-run the SQL block on existing Supabase projects after upgrading the app.

**Legal config** (`js/config.js`):

```js
legal: {
  grievanceEmail: 'privacy@yourdomain.com',  // DPDP grievance officer — required before launch
},
founder: {
  operatorEmail: 'nilesh@example.com',       // fallback if grievanceEmail empty
},
```

Review `privacy.html` and `terms.html` with qualified Indian counsel before public launch.
