# Changelog

All notable changes to CivicRadar are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project aims to follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Release process and environment details live in [`RELEASE.md`](./RELEASE.md).

## [Unreleased]

### Added
- **Society / neighbourhood layer (MVP, v86)** — optional society/neighbourhood on onboarding
  (after ward) and Profile: searchable text + datalist from config suggestions + free-text
  fallback. Stored on user profile (`society`) and attached to new reports; shown on map
  popup when set. Profile link-out to National Cooperative Database (Maharashtra state list).
  Schema: additive `society` on `profiles` and `reports`. Localized en/hi/mr/gu. E2E SO01–SO04.
- **i18n audit complete (v86)** — `rerenderDynamicViews()` re-localizes open modals in place
  (success, community, profile, about, tour); `refreshSuccessModalStrings()` for success modal;
  map "You are here" localized. E2E I06–I08 (child screens in mr/hi).
- **Official grievance channel integration (Tier 1–3)** — city-aware panels linking to
  verified government resources without API partnerships: **MyBMC MARG**, **PMC CARE**,
  **Swachhata-MoHUA**, and **Aaple Sarkar** (plus existing BMC 1916/WhatsApp/portal and
  TMC helpline). Surfaces: report success modal (“Also file officially”), Community and
  Profile “Official grievance channels”, escalation extras (Swachhata + category hints), and
  escalation-ladder quick links. Smart routing by city + hazard (garbage → Swachhata;
  stagnant water → corp pest-control/drainage hints). One-tap open copies a structured
  summary (ward, hazard, CivicRadar report ID, category hint, photo guidance) to clipboard.
  Complaint-number save (Tier 3) unchanged. Analytics: `official_channel_open`. Config in
  `js/config.js` → `officialChannels`. Localized en/hi/mr/gu. Cache bumped to v84
  (E2E OC01–OC05).
- **Launch differentiation vs helpline routers (Majha Ward positioning)** — hero, empty-map CTA,
  and About modal now lead with community ward map + Me too corroboration + optional official filing,
  not "anonymous complaint to helpline." New **"What makes CivicRadar different"** section (4 bullets)
  in About, localized en/hi/mr/gu (`about.different*`). Hero reframed as "Community ward map" with
  trust strip "Add to Home Screen · 4 languages." Cache bumped to v84 (E2E DF01–DF02, RP16–RP18).
- **Four hazard types live at launch** — garbage/solid waste, potholes, and broken streetlights join
  stagnant water. All tiles selectable (no "Coming soon" locks). Share templates, copy1916 categories,
  map markers, and report flow handle all four. E2E RP01/RP02 updated for multi-hazard launch.
- **Dismissible location banner with a compact "Locate me" affordance** — the
  "Turn on location" map banner now has an accessible **×** dismiss control. Closing
  it **snoozes** the banner for 7 days (`civicradar_locbanner_snooze`) and collapses
  it into a small, unobtrusive **"Locate me"** pill on the map. While snoozed the
  full banner no longer reappears on every map load; the pill lets users re-enable
  location in one tap (which bypasses the snooze and re-runs the enable-location
  flow). Granting location, or any explicit tap, clears the snooze and hides both
  the banner and the pill. All banner copy is now localized via `t()`
  (`location.banner` / `location.bannerNearby` / `location.unavailable` /
  `location.withdrawn` / `location.dismiss` / `location.locate` /
  `location.locateAria`) in en/hi/mr/gu — replacing the previously hardcoded English
  strings. The snooze key is cleared on "delete my data". Keyboard operable,
  `focus-visible` rings, role/aria preserved, and motion respects
  `prefers-reduced-motion`. Cache bumped to v81 (E2E LB01–LB06).
- **First-run interactive guided tour** — after the onboarding explainer/coach tip,
  brand-new citizens get a short, skippable coach-mark spotlight tour that teaches
  the key navigation by highlighting the real UI: **Map = your ward** → **Report**
  (the camera FAB) → **Me too** (explained generically so it never points at a
  missing pin) → **Profile / Civic Points** (bottom-nav). It is sequenced right
  after the existing v79 `coachSpotTip` so users never see two stacked first-run
  pop-ups. The spotlight and tooltip are positioned from live bounding rects (mobile
  viewport safe), every step has visible **Skip** + **Next/Got it** controls, and
  **Esc**/backdrop tap dismiss it. Fully keyboard operable (Tab is trapped, Enter
  advances), focus is managed (and restored on exit), `aria` dialog semantics, and
  it respects `prefers-reduced-motion`. Shown **once** (`civicradar_tour_seen`) and
  never auto-shown for demo (`?demo=`), referral (`?ref=`), or returning users. A
  **"Replay app tour"** entry in Profile restarts it on demand. All copy localized
  in en/hi/mr/gu (`tour.*`). Cache bumped to v80.
- **Clearer onboarding — "what / why / how"** — the first-run onboarding modal now
  carries a compact explainer above the city/ward fields: a one-line *why*
  ("Stagnant water breeds dengue & malaria. Your report puts the spot on your ward
  map and into the BMC queue — and alerts neighbours."), a numbered 3-step *how it
  works* (Spot → Pin & snap on the spot → Submit & earn Civic Points), and a short
  "best reported on the spot" note. The first-run coach mark adds an explicit
  report-on-the-spot guidance line ("No need to report right now. When you pass
  stagnant water… open CivicRadar and pin it on the spot so the location is
  accurate."). All copy localized in en/hi/mr/gu; respects reduced-motion.
- **Opt-in "report stagnant water nearby" reminders** — a new Profile toggle
  ("Remind me to report stagnant water nearby") lets users opt into a gentle
  monsoon-season nudge. Enabling it requests notification permission; when granted,
  a foreground-triggered reminder (on load / tab focus, on a ~2-day cadence with
  snooze) is delivered via the service-worker registration or a page `Notification`.
  **Honest about platform limits:** there is *no* background push or geofencing —
  reminders fire only while the app is open. On iOS, unsupported browsers, or when
  permission is denied, it degrades gracefully to the existing in-app reminder card
  and never errors (feature-detected). Stored under
  `civicradar_report_reminder_optin`; easy to turn off.
- **Location-aware in-app nudge** — when the app is open and GPS is already granted,
  CivicRadar reuses the current position (never re-prompting, never persisting
  coordinates) to check proximity to known *pending* hazards via the existing
  haversine helper. Within ~150 m of a pending spot it surfaces the existing
  staleCheck reminder ("Spot near {ward} — still stagnant?") with "Still there" /
  "Add a photo" actions, routed through the same reminder queue so it respects
  `MAX_SESSION_REMINDERS`, snooze keys, and priority ordering. Foreground only.
  All new copy localized in en/hi/mr/gu. Cache bumped to v79.
- **Warmer post-report success experience** — every successful report now shows
  an encouraging line in the success modal, not just on milestone reports.
  Non-milestone reports rotate through a small set of warm "kudos" messages
  (deterministic by report count) so the praise never feels repetitive, while the
  special first-report and milestone messages still take priority. A new compact
  progress-to-next-badge nudge (`#successProgress`) tells the user how close they
  are to their next milestone (e.g. "Just 1 more report to your next badge"),
  switches to a celebratory "Badge unlocked!" variant right after a milestone, and
  becomes a sustained "{n} reports and counting — a true Monsoon Guardian" line
  once they pass the top milestone. All new copy localized in en/hi/mr/gu; points
  animation, confetti, badge toasts, and the share block are unchanged. Cache
  bumped to v78.
- **Coordinator access requests + approval workflow** — BMC officials and
  NGO/community coordinators can now request elevated access in-app (entry points
  in Profile, the partner portal, and the About modal). A low-friction request
  form (name, role, ward/city, one contact required; organization, proof photo,
  and note optional) submits even without logging in. The CivicRadar team reviews
  requests in an admin-only "Access requests" screen (reachable from the BMC
  queue) and approves/rejects with one tap; approving issues a one-time **claim
  code** the applicant enters to unlock their role. New `access_requests` table
  with RLS (anon/auth may INSERT a pending request only; admin-only read/update),
  an `admin` super-admin role on `profiles`, and `request_access` /
  `approve_access_request` / `reject_access_request` / `claim_access` RPCs. Works
  fully in local/no-Supabase mode (on-device queue). All UI strings localized in
  en/hi/mr/gu. **Requires re-running `supabase/schema.sql` and bootstrapping one
  super-admin.**
- Multi-city support for **Mumbai, Pune, and Thane** — per-city map centers,
  bounds, ward detection, and corporation channels (BMC / PMC CARE / TMC).
- Environment-aware configuration in `js/config.js` (and `js/config.example.js`):
  hostname-based `dev` / `staging` / `prod` detection that resolves
  `supabaseUrl`, `supabaseAnonKey`, and `publicUrl` per environment, with a safe
  fallback to production for unknown hosts.
- Release scaffolding: `RELEASE.md` runbook, PR-triggered E2E gate workflow
  (`.github/workflows/pr-checks.yml`), and an optional secret-guarded Cloudflare
  Pages preview workflow (`.github/workflows/preview-cloudflare.yml`).
- Admin proof-photo scan when resolving reports (resolution requires a proof
  photo).
- Soft photo-relevance confirmation prompt on report submission.
- Image-safety test scenarios in the E2E suite.

### Changed
- Anonymized founder identity across the public UI — no personal names shown
  ("The CivicRadar team"); contact via project email only.
- Migrated to a name-free public URL on the **civicradarNH** GitHub org
  (`https://civicradarnh.github.io/civicradar`).
- PWA icons moved from vector to raster for broader install/launch compatibility.
- Navigation Phase 1 improvements.
- E2E coverage expanded from **234 to 243** passing checks.

### Fixed
- Referral welcome banner behavior (shows on `?ref=`, hides after dismiss, stays
  hidden in demo tour).
- Single-language WhatsApp share — shared messages no longer duplicate content
  across multiple languages.
- Accessibility fixes.
- Offline / service-worker reliability fixes.
- Coordinator access copy no longer promises email when the applicant only
  provides a phone number; claim-code copy toast no longer references the team
  inbox instead of the applicant.
- BMC OTP fallback now accepts `admin` super-admin profiles (was signing them out).
- Magic-link callback hash errors routed through `formatAuthError` (no raw `{}`).
- Bottom-nav ghost taps ignored while the native camera / file picker is active.
- Twitter share no longer duplicates hashtag lines already in the template.

[Unreleased]: https://github.com/civicradarnh/civicradar/commits/main
