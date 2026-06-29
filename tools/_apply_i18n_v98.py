#!/usr/bin/env python3
"""Apply v98 i18n fixes: en ? placeholders + hi/mr/gu official hints."""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _apply_i18n_v94 import (
    parse_i18n_block,
    fix_mojibake,
    js_escape,
    format_locale_block,
    is_corrupted,
)

ROOT = Path(__file__).resolve().parent.parent

# Targeted hi/mr/gu fixes for untranslated official hints and any remaining garbage
LOCALE_FIXES = {
    "en": {
        "shareWin.instagramHint": "Save image → post to Instagram Stories",
        "esc.tmc.portalHint": "On thanecity.gov.in: login → Online citizen services → File a complaint. Paste details below.",
        "esc.portalHint": "On the portal or MARG app: choose Public Health → Pest Control → stagnant water. Paste the details below.",
        "official.hint.marg.stagnant-water": "Public Health → Pest Control → stagnant water / mosquito breeding",
        "official.hint.marg.garbage": "Solid Waste Management → garbage / drainage",
        "official.hint.aaple": "Select {corp} as local body → Health / Water supply",
        "toast.installHint": "Browser menu → Add to Home screen.",
        "coord.workflow": "Dispatch volunteers → log cleanup → confirm supplies → verify hours (+200 pts)",
        "share.appMsg": "🦟 {city} monsoon map — pin stagnant water, tap Me too, beat rival wards!\n{link}\n{hashtags}",
        "share.wardMapMsg": "🗺️ {ward}: {pending} open dengue-risk spots — beat us on CivicRadar!\n{link}\n{hashtags}",
        "confirm.shareMsg": "✅ Hazard I flagged in {ward} is FIXED on CivicRadar! Community pressure works:\n{link}\n{hashtags}",
        "about.sharePitch": "Free {city} monsoon map — pin stagnant water in 30 sec, say Me too, beat rival wards.\nBuilt for Mumbai, Pune & Thane. No login, 4 languages.\n{link}\nForward to your RWA / society WhatsApp group 👋",
    },
    "hi": {
        "official.hint.marg.stagnant-water": "सार्वजनिक स्वास्थ्य → कीट नियंत्रण → stagnant water / मच्छर प्रजनन",
        "official.hint.marg.garbage": "ठोस अपशिष्ट प्रबंधन → कचरा / नाली",
        "official.hint.swachhata.garbage": "कचरा डंप",
        "official.hint.pmc.garbage": "ठोस अपशिष्ट / कचरा",
        "onboard.subtitle": "तीन टैप — वार्ड, फोटो, पड़ोसियों को सूचना।",
        "report.hazardHint": "खतरे का प्रकार चुनें",
        "report.photoHint": "मौके की फ़ोटो — पिन सटीक रहेगा",
        "report.photoNext": "{hazard} चुना — अब फ़ोटो लें",
        "report.retake": "फिर से लें",
    },
    "mr": {
        "official.hint.marg.stagnant-water": "सार्वजनिक आरोग्य → कीटक नियंत्रण → stagnant water / डास प्रजनन",
        "official.hint.marg.garbage": "घन कचरा व्यवस्थापन → कचरा / नाला",
        "official.hint.swachhata.garbage": "कचरा डंप",
        "official.hint.pmc.garbage": "घन कचरा / कचरा",
        "onboard.subtitle": "तीन टॅप — ward, फोटो, शेजाऱ्यांना कळवा.",
        "home.hero.tour": "छोटा टूर",
        "home.hero.trust": "मोफत · ऑफलाइन · 3 शहरे · 4 भाषा",
        "report.hazardHint": "धोक्याचा प्रकार निवडा",
        "report.photoHint": "जागेचा फोटो — पिन अचूक राहील",
        "report.photoNext": "{hazard} निवडले — आता फोटो काढा",
        "report.retake": "पुन्हा काढा",
    },
    "gu": {
        "official.hint.marg.stagnant-water": "જાહેર આરોગ્ય → કીટ નિયંત્રણ → stagnant water / મચ્છર પ્રજનન",
        "official.hint.marg.garbage": "ઘન કચરો વ્યવસ્થાપન → કચરો / ગટર",
        "official.hint.swachhata.garbage": "કચરો ડંપ",
        "official.hint.pmc.garbage": "ઘન કચરો / કચરો",
        "onboard.subtitle": "ત્રણ tap — ward, ફોટો, પડોશીઓને ચેતવણી.",
        "home.hero.cta": "હમણાં રિપોર્ટ",
        "home.hero.tour": "ટૂંકો ટૂર",
        "home.hero.trust": "મફત · ઑફલાઇન · 3 શહેર · 4 ભાષા",
        "report.hazardHint": "જોખમનો પ્રકાર પસંદ કરો",
        "report.photoHint": "જગ્યાનો ફોટો — પિન સચોટ રહેશે",
        "report.photoNext": "{hazard} પસંદ — હવે ફોટો લો",
        "report.retake": "ફરી લો",
    },
}


def main():
    app_path = ROOT / "js" / "app.js"
    app = app_path.read_text(encoding="utf-8")

    en = parse_i18n_block(app, "en")
    key_order = list(en.keys())
    stats = {"en": 0, "hi": 0, "mr": 0, "gu": 0}

    locales = {"en": dict(en)}
    for lang in ("en", "hi", "mr", "gu"):
        if lang == "en":
            cur = dict(en)
        else:
            cur = parse_i18n_block(app, lang)
        fixes = LOCALE_FIXES.get(lang, {})
        out = {}
        for key in key_order:
            base = cur.get(key, en[key])
            val = fix_mojibake(base)
            if key in fixes:
                val = fixes[key]
                stats[lang] += 1
            elif lang == "en":
                val = fix_mojibake(val)
                if val != base:
                    stats[lang] += 1
            out[key] = val
        locales[lang] = out

    i18n_start = app.index("  const I18N = {")
    i18n_end = app.index("\n  };", i18n_start) + len("\n  };")

    new_i18n = "  const I18N = {\n\n"
    new_i18n += format_locale_block("en", locales["en"], key_order)
    new_i18n += "\n"
    for lang in ("hi", "mr", "gu"):
        new_i18n += format_locale_block(lang, locales[lang], key_order)
    new_i18n += "  };"

    app = app[:i18n_start] + new_i18n + app[i18n_end:]
    app = re.sub(r"const CIVIC_APP_VERSION = 'v\d+';", "const CIVIC_APP_VERSION = 'v98';", app)
    app_path.write_text(app, encoding="utf-8")

    sw_path = ROOT / "sw.js"
    sw = sw_path.read_text(encoding="utf-8")
    sw = re.sub(r"const CACHE = 'civicradar-v\d+';", "const CACHE = 'civicradar-v98';", sw)
    sw_path.write_text(sw, encoding="utf-8")

    # index.html SW06 comment
    idx_path = ROOT / "index.html"
    idx = idx_path.read_text(encoding="utf-8")
    idx = re.sub(r"<!-- SW\d+ -->", "<!-- SW98 -->", idx)
    idx = re.sub(r"civicradar-v\d+", "civicradar-v98", idx)
    idx_path.write_text(idx, encoding="utf-8")

    # e2e cache version
    e2e_path = ROOT / "tests" / "e2e_comprehensive.py"
    e2e = e2e_path.read_text(encoding="utf-8")
    e2e = re.sub(r"civicradar-v\d+", "civicradar-v98", e2e)
    e2e_path.write_text(e2e, encoding="utf-8")

    print("Keys fixed:", stats)
    for lang in ("hi", "mr", "gu"):
        cur = parse_i18n_block(app_path.read_text(encoding="utf-8"), lang)
        corrupted = sum(1 for k, v in cur.items() if is_corrupted(v))
        print(f"{lang}: corrupted remaining: {corrupted}")


if __name__ == "__main__":
    main()
