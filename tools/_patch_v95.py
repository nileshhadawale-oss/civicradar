"""One-shot patch for v95 UX — do not commit."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# sw.js
sw = ROOT / 'sw.js'
sw.write_text(sw.read_text(encoding='utf-8').replace('civicradar-v94', 'civicradar-v95'), encoding='utf-8')

# e2e
e2e = ROOT / 'tests' / 'e2e_comprehensive.py'
t = e2e.read_text(encoding='utf-8')
t = t.replace('civicradar-v94', 'civicradar-v95')
old_tr03 = """    coach_shown = not await page.evaluate(

        '() => document.getElementById("coachMark").classList.contains("hidden")'

    )

    if coach_shown:

        await page.click('#btnDismissCoach')

    await page.wait_for_timeout(700)"""
new_tr03 = """    hero_shown = not await page.evaluate(
        '() => !document.getElementById("homeHero").classList.contains("hidden")'
    )
    if hero_shown:
        await page.click('#btnHeroDismiss')
        await page.wait_for_timeout(700)
    else:
        coach_shown = not await page.evaluate(
            '() => document.getElementById("coachMark").classList.contains("hidden")'
        )
        if coach_shown:
            await page.click('#btnDismissCoach')
        await page.wait_for_timeout(700)"""
if old_tr03 in t:
    t = t.replace(old_tr03, new_tr03)
old_tr05 = """    if not await page.evaluate('() => document.getElementById("coachMark").classList.contains("hidden")'):

        await page.click('#btnDismissCoach')

    await page.wait_for_timeout(700)

    skipped = False"""
new_tr05 = """    hero_up = not await page.evaluate('() => !document.getElementById("homeHero").classList.contains("hidden")')
    if hero_up:
        await page.click('#btnHeroDismiss')
    elif not await page.evaluate('() => document.getElementById("coachMark").classList.contains("hidden")'):
        await page.click('#btnDismissCoach')
    await page.wait_for_timeout(700)

    skipped = False"""
if old_tr05 in t:
    t = t.replace(old_tr05, new_tr05)
e2e.write_text(t, encoding='utf-8')

app_path = ROOT / 'js' / 'app.js'
s = app_path.read_text(encoding='utf-8')

s = s.replace(
    "'report.hazardHint': 'तुम्ही नोंदवत असलेला धोका nivडa'",
    "'report.hazardHint': 'तुम्ही नोंदवत असलेला धोका निवडा'",
)
s = s.replace(
    "'report.hazardHint': 'तुम्ही नोंदवत असलेला धोका nivडा'",
    "'report.hazardHint': 'तुम्ही नोंदवत असलेला धोका निवडा'",
)

patches = [
    (
        "  function showLocationBanner(message) {\n\n    if (isLocBannerSnoozed()) {",
        "  function showLocationBanner(message) {\n\n    if (shouldDeferFirstRunNudges()) return;\n\n    if (isLocBannerSnoozed()) {",
    ),
    (
        "  function renderSeasonalHook() {\n\n    const el = $('#seasonHook');\n\n    if (!el) return;\n\n    const hook = getSeasonalHook();",
        "  function renderSeasonalHook() {\n\n    const el = $('#seasonHook');\n\n    if (!el) return;\n\n    if (shouldDeferFirstRunNudges()) {\n\n      el.classList.add('hidden');\n\n      return;\n\n    }\n\n    const hook = getSeasonalHook();",
    ),
    (
        "  function maybeShowPwaNudge(trigger) {\n\n    if (!canShowPwaNudge()) return;\n\n    const visits = parseInt(localStorage.getItem(VISIT_COUNT_KEY) || '0', 10);",
        "  function maybeShowPwaNudge(trigger) {\n\n    if (!canShowPwaNudge()) return;\n\n    if (shouldDeferFirstRunNudges() && trigger === 'visit') return;\n\n    const visits = parseInt(localStorage.getItem(VISIT_COUNT_KEY) || '0', 10);",
    ),
    (
        """      updateProfileUI();

      updatePersonaUI();

      setTimeout(showCoachMark, 600);

      setTimeout(() => { checkResolvedWins(); checkConfirmedResolved(); updateCommunityWinBadge(); }, 1200);

      setTimeout(processBootReminders, 1800);

      setTimeout(maybeShowReportReminder, 2400);

      updateMapEmptyCta();

      updateHomeHero();

      handleReportDeepLink();""",
        """      updateProfileUI();

      updatePersonaUI();

      updateHomeHero();

      updateMapEmptyCta();

      if (!shouldShowHomeHero()) setTimeout(showCoachMark, 600);

      if (!shouldDeferFirstRunNudges()) {

        setTimeout(() => { checkResolvedWins(); checkConfirmedResolved(); updateCommunityWinBadge(); }, 1200);

        setTimeout(processBootReminders, 1800);

        setTimeout(maybeShowReportReminder, 2400);

      }

      handleReportDeepLink();""",
    ),
    (
        """      showToast(t('toast.welcome').replace('{name}', name), 'success', 4500);

      setTimeout(showCoachMark, 500);

    });""",
        """      showToast(t('toast.welcome').replace('{name}', name), 'success', 4500);

      if (!shouldShowHomeHero()) setTimeout(showCoachMark, 500);

    });""",
    ),
    (
        """    window.addEventListener('popstate', () => {

      if (isReportPhotoPickerActive()) {

        reportPhotoFlowActive = false;

        ensureReportModalOpen();

        reportPhotoDismissGuard = Date.now();

        return;

      }""",
        """    window.addEventListener('popstate', () => {

      if (isReportPhotoPickerActive() || hasReportPhotoPreview()) {

        reportPhotoFlowActive = false;

        syncReportPhotoReturn();

        return;

      }""",
    ),
    (
        """    window.addEventListener('pageshow', (e) => {

      if (e.persisted && $('#imageCanvas')?.classList.contains('visible')) {

        ensureReportModalOpen();

        updateReportFlowSteps('submit');

      }

    });""",
        """    window.addEventListener('pageshow', () => {

      if (hasReportPhotoPreview() || isReportPhotoPickerActive()) syncReportPhotoReturn();

    });""",
    ),
    (
        "if (name === 'report' && isReportPhotoPickerActive()) return;",
        "if (name === 'report' && (isReportPhotoPickerActive() || hasReportPhotoPreview())) return;",
    ),
]

for old, new in patches:
    if old not in s:
        print('WARN missing patch block:', old[:60])
    else:
        s = s.replace(old, new, 1)

# English tagline
if "'tagline.threeBeat'" not in s:
    s = s.replace(
        "      'coach.step': '#MonsoonGuardian — 30 sec',",
        """      'tagline.threeBeat': 'Map it · Snap it · Report it',
      'tagline.subline': 'Three taps — your ward, a photo, neighbours alerted.',
      'tagline.beatMap': 'Map it',
      'tagline.beatSnap': 'Snap it',
      'tagline.beatReport': 'Report it',

      'coach.step': '#MonsoonGuardian — 30 sec',""",
        1,
    )

en_repls = {
    "'coach.title': 'Spot stagnant water? Pin it.'": "'coach.title': 'Map it · Snap it · Report it'",
    "'coach.body': 'Tap Report, snap a photo — we pin your ward map.'": "'coach.body': 'Three taps — your ward, a photo, neighbours alerted.'",
    "'tour.map.title': 'Your ward map'": "'tour.map.title': 'Map it'",
    "'tour.map.body': 'Hazard pins show here — tap Me too to back neighbours.'": "'tour.map.body': 'Your ward map — hazard pins and Me too show here.'",
    "'tour.report.title': 'Report in 30 sec'": "'tour.report.title': 'Snap it'",
    "'tour.report.body': 'Tap here when you spot stagnant water.'": "'tour.report.body': 'Tap Report and snap a photo on the spot.'",
    "'tour.profile.title': 'Profile'": "'tour.profile.title': 'Report it'",
    "'tour.profile.body': 'Civic Points and your reports live here.'": "'tour.profile.body': 'Submit — neighbours see the pin. Track Civic Points in Profile.'",
    "'onboard.subtitle': 'Pin hazards on your ward map in 30 sec.'": "'onboard.subtitle': 'Three taps — your ward, a photo, neighbours alerted.'",
    "'home.hero.headline': 'Pin stagnant water on your ward map'": "'home.hero.headline': 'Map it · Snap it · Report it'",
    "'home.hero.subline': 'Monsoon is here — pin stagnant water on the spot: snap a photo, neighbours Me too.'": "'home.hero.subline': 'Three taps — your ward, a photo, neighbours alerted.'",
    "'home.hero.benefit1': '30 sec'": "'home.hero.benefit1': 'Map it'",
    "'home.hero.benefit2': 'Me too'": "'home.hero.benefit2': 'Snap it'",
    "'home.hero.benefit3': 'Track fixes'": "'home.hero.benefit3': 'Report it'",
    "'about.subtitle': 'Community-powered ward map for Mumbai, Pune & Thane — not an anonymous helpline router.'": "'about.subtitle': 'Map it · Snap it · Report it — community ward map for Mumbai, Pune & Thane.'",
    "'success.tagline': 'On your ward map'": "'success.tagline': 'Report it — pinned on your ward map'",
    "'map.emptyHint': 'Photo on the spot · ~30 sec'": "'map.emptyHint': 'Map it · Snap it · Report it'",
}
for a, b in en_repls.items():
    s = s.replace(a, b)

# Insert tagline keys for hi/mr/gu before coach.step in each locale block
locales = [
    ("'lang.native': 'हिन्दी'", """      'tagline.threeBeat': 'नक्शे पर · फोटो · रिपोर्ट',
      'tagline.subline': 'तीन टैप — आपका वार्ड, एक फोटो, पड़ोसियों को सूचना।',
      'tagline.beatMap': 'नक्शे पर',
      'tagline.beatSnap': 'फोटो',
      'tagline.beatReport': 'रिपोर्ट',

"""),
    ("'lang.native': 'मराठी'", """      'tagline.threeBeat': 'नकाशावर · फोटो · नोंदवा',
      'tagline.subline': 'तीन टॅप — तुमचा ward, एक फोटो, शेजाऱ्यांना कळवा.',
      'tagline.beatMap': 'नकाशावर',
      'tagline.beatSnap': 'फोटो',
      'tagline.beatReport': 'नोंदवा',

"""),
    ("'lang.native': 'ગુજરાતી'", """      'tagline.threeBeat': 'નકશા પર · ફોટો · રિપોર્ટ',
      'tagline.subline': 'ત્રણ tap — તમારું ward, એક ફોટો, પડોશીઓને ચેતવણી.',
      'tagline.beatMap': 'નકશા પર',
      'tagline.beatSnap': 'ફોટો',
      'tagline.beatReport': 'રિપોર્ટ',

"""),
]
for marker, insert in locales:
    idx = s.find(marker)
    if idx < 0:
        print('WARN locale', marker)
        continue
    coach_idx = s.find("      'coach.step':", idx)
    if coach_idx < 0 or insert.strip() in s[idx:idx + 8000]:
        continue
    s = s[:coach_idx] + insert + s[coach_idx:]

hi_repls = {
    "'home.hero.headline': 'अपने वार्ड नक्शे पर रुका पानी पिन करें'": "'home.hero.headline': 'नक्शे पर · फोटो · रिपोर्ट'",
    "'home.hero.subline': 'मानसून आ गया — मौके पर रुका पानी पिन करें: फ़ोटो लें, पड़ोसी Me too।'": "'home.hero.subline': 'तीन टैप — आपका वार्ड, एक फोटो, पड़ोसियों को सूचना।'",
    "'home.hero.benefit1': '30 सेक'": "'home.hero.benefit1': 'नक्शे पर'",
    "'home.hero.benefit2': 'Me too'": "'home.hero.benefit2': 'फोटो'",
    "'home.hero.benefit3': 'ठीक ट्रैक'": "'home.hero.benefit3': 'रिपोर्ट'",
}
for a, b in hi_repls.items():
    s = s.replace(a, b)

mr_repls = {
    "'home.hero.headline': 'तुमच्या वॉर्ड नकाशावर साचलेले पाणी pin करा'": "'home.hero.headline': 'नकाशावर · फोटो · नोंदवा'",
    "'home.hero.subline': 'मान्सून आला — जागेवर साचलेले पाणी pin: फोटो, शेजारी Me too.'": "'home.hero.subline': 'तीन टॅप — तुमचा ward, एक फोटो, शेजाऱ्यांना कळवा.'",
    "'home.hero.benefit1': '30 सेक'": "'home.hero.benefit1': 'नकाशावर'",
    "'home.hero.benefit2': 'Me too'": "'home.hero.benefit2': 'फोटो'",
    "'home.hero.benefit3': 'दुरुस्ती track'": "'home.hero.benefit3': 'नोंदवा'",
}
for a, b in mr_repls.items():
    s = s.replace(a, b)

gu_repls = {
    "'home.hero.headline': 'તમારા ward map પર ભરાયેલું પાણી pin કરો'": "'home.hero.headline': 'નકશા પર · ફોટો · રિપોર્ટ'",
    "'home.hero.subline': 'માન્સૂન આવ્યો — જગ્યાએ pin: ફોટો, પડોશી Me too.'": "'home.hero.subline': 'ત્રણ tap — તમારું ward, એક ફોટો, પડોશીઓને ચેતવણી.'",
    "'home.hero.benefit1': '30 sec'": "'home.hero.benefit1': 'નકશા પર'",
    "'home.hero.benefit2': 'Me too'": "'home.hero.benefit2': 'ફોટો'",
    "'home.hero.benefit3': 'Fix track'": "'home.hero.benefit3': 'રિપોર્ટ'",
}
for a, b in gu_repls.items():
    s = s.replace(a, b)

app_path.write_text(s, encoding='utf-8')
print('Done')
