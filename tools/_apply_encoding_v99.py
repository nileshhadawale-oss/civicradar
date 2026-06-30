#!/usr/bin/env python3
"""v99: Fix all mojibake (ï¿½) in app.js + restore apostrophes mangled by v98."""
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
MOJIBAKE = "ï¿½"
EM = "—"
EN = "–"  # en dash for ranges
MID = "·"
APOS = "'"


def fix_apostrophe_em_dashes(text: str) -> str:
    """Undo v98 over-replacement: em dash used where apostrophe belongs."""
    fixes = [
        (r"You—re\b", "You're"),
        (r"that—s\b", "that's"),
        (r"doesn—t\b", "doesn't"),
        (r"it—s\b", "it's"),
        (r"we—ll\b", "we'll"),
        (r"you—ll\b", "you'll"),
        (r"BMC—s\b", "BMC's"),
        (r"ward—s\b", "ward's"),
        (r"Monsoon—s\b", "Monsoon's"),
        (r"how you—ll\b", "how you'll"),
    ]
    for pat, rep in fixes:
        text = re.sub(pat, rep, text)
    return text


def fix_body_mojibake(text: str) -> str:
    """Fix mojibake outside I18N block with context-aware rules."""
    if MOJIBAKE not in text:
        return text

    # Apostrophe contractions (before generic replace)
    text = (
        text.replace(f"BMC{MOJIBAKE}s", f"BMC{APOS}s")
        .replace(f"we{MOJIBAKE}ll", f"we{APOS}ll")
        .replace(f"doesn{MOJIBAKE}t", f"doesn{APOS}t")
        .replace(f"it{MOJIBAKE}s", f"it{APOS}s")
        .replace(f"you{MOJIBAKE}ll", f"you{APOS}ll")
        .replace(f"Monsoon{MOJIBAKE}s", f"Monsoon{APOS}s")
        .replace(f"ward{MOJIBAKE}s", f"ward{APOS}s")
    )

    # Date range
    text = text.replace(f"Nov{MOJIBAKE}Apr", f"Nov{EN}Apr")

    # Bullet lists (impact summary etc.)
    text = re.sub(rf"`{MOJIBAKE} ", f"`{MID} ", text)
    text = re.sub(rf"\n\s*'{MOJIBAKE} ", f"\n      '{MID} ", text)
    text = re.sub(rf"'{MOJIBAKE} PWA", f"'{MID} PWA", text)
    text = re.sub(rf" \? {MOJIBAKE} ", f" {MID} ", text)

    # split/join delimiters — must match ward data (js/wards/*.js uses em dash)
    text = text.replace(f"split('{MOJIBAKE}')", f"split('{EM}')")
    text = text.replace(f"join(' {MOJIBAKE} ')", f"join(' {EM} ')")
    text = text.replace(f" ` {MOJIBAKE} `", f" ` {EM} `")

    # Standalone placeholder glyphs
    text = text.replace(f"'{MOJIBAKE}'", f"'{EM}'")
    text = re.sub(
        rf'<div class="proof-compare__placeholder">{MOJIBAKE}</div>',
        f'<div class="proof-compare__placeholder">{EM}</div>',
        text,
    )

    # Remaining mojibake → em dash (ward separators, punctuation)
    text = text.replace(MOJIBAKE, EM)

    return fix_apostrophe_em_dashes(text)


def fix_i18n_value(val: str) -> str:
    v = fix_mojibake(val)
    v = fix_apostrophe_em_dashes(v)
    # Trailing ellipsis on placeholders (typing/detecting)
    v = re.sub(r"ward—$", "ward…", v)
    v = re.sub(r"location—$", "location…", v)
    v = re.sub(r"landmark—$", "landmark…", v)
    v = re.sub(r"Select ward—$", "Select ward…", v)
    v = re.sub(r"Checking photo—$", "Checking photo…", v)
    v = re.sub(r"coming \?🦟", "coming 🦟", v)
    return v


def bump_version(content: str, old_ver: str, new_ver: str) -> str:
    return (
        content.replace(f"const CIVIC_APP_VERSION = '{old_ver}';", f"const CIVIC_APP_VERSION = '{new_ver}';")
        .replace(f"const CACHE = 'civicradar-{old_ver}';", f"const CACHE = 'civicradar-{new_ver}';")
        .replace(f"civicradar-{old_ver}", f"civicradar-{new_ver}")
    )


def main():
    app_path = ROOT / "js" / "app.js"
    app = app_path.read_text(encoding="utf-8")
    before_count = app.count(MOJIBAKE)

    # --- I18N block ---
    en = parse_i18n_block(app, "en")
    key_order = list(en.keys())
    i18n_start = app.index("  const I18N = {")
    i18n_end = app.index("\n  };", i18n_start) + len("\n  };")
    body_before = app[:i18n_start]
    body_after = app[i18n_end:]

    i18n_fixes = 0
    locales = {}
    for lang in ("en", "hi", "mr", "gu"):
        cur = parse_i18n_block(app, lang) if lang != "en" else dict(en)
        out = {}
        for key in key_order:
            base = cur.get(key, en.get(key, ""))
            fixed = fix_i18n_value(base)
            if fixed != base:
                i18n_fixes += 1
            out[key] = fixed
        locales[lang] = out

    new_i18n = "  const I18N = {\n\n"
    new_i18n += format_locale_block("en", locales["en"], key_order)
    new_i18n += "\n"
    for lang in ("hi", "mr", "gu"):
        new_i18n += format_locale_block(lang, locales[lang], key_order)
    new_i18n += "  };"

    # Escape apostrophes in JS single-quoted string literals (body code only)
    def escape_js_apostrophes_in_strings(text: str) -> str:
        out = []
        i = 0
        in_str = False
        while i < len(text):
            c = text[i]
            if c == "'" and (i == 0 or text[i - 1] != "\\"):
                if not in_str:
                    in_str = True
                    out.append(c)
                else:
                    # closing quote if next char suggests end of literal
                    j = i + 1
                    while j < len(text) and text[j] in " \t":
                        j += 1
                    if j < len(text) and text[j] in ",}]:;\n":
                        in_str = False
                        out.append(c)
                    else:
                        out.append("\\'")
                i += 1
                continue
            out.append(c)
            i += 1
        return "".join(out)

    body_before = escape_js_apostrophes_in_strings(fix_body_mojibake(body_before))
    body_after = escape_js_apostrophes_in_strings(fix_body_mojibake(body_after))
    app = body_before + new_i18n + body_after
    app = fix_apostrophe_em_dashes(app)
    app = bump_version(app, "v98", "v99")
    app_path.write_text(app, encoding="utf-8")

    after_count = app.count(MOJIBAKE)
    body_fixes = before_count - after_count

    # --- sw.js ---
    sw_path = ROOT / "sw.js"
    sw = bump_version(sw_path.read_text(encoding="utf-8"), "v98", "v99")
    sw_path.write_text(sw, encoding="utf-8")

    # --- e2e ---
    e2e_path = ROOT / "tests" / "e2e_comprehensive.py"
    e2e = bump_version(e2e_path.read_text(encoding="utf-8"), "v98", "v99")
    e2e_path.write_text(e2e, encoding="utf-8")

    # --- CHANGELOG ---
    cl_path = ROOT / "CHANGELOG.md"
    cl = cl_path.read_text(encoding="utf-8")
    entry = (
        "- **Encoding fix (v99)** — eliminated remaining `ï¿½` mojibake across app.js "
        "(ward separators, split/join, user-facing strings); restored apostrophes mangled "
        "by v98 em-dash over-replacement (`You—re` → `You're`, etc.); cache v99.\n"
    )
    if "Encoding fix (v99)" not in cl:
        cl = cl.replace("### Fixed\n", "### Fixed\n" + entry, 1)
        cl_path.write_text(cl, encoding="utf-8")

    # --- audit ---
    app_final = app_path.read_text(encoding="utf-8")
    corrupted = {}
    for lang in ("en", "hi", "mr", "gu"):
        cur = parse_i18n_block(app_final, lang)
        corrupted[lang] = sum(1 for v in cur.values() if is_corrupted(v))

    report = {
        "mojibake_before": before_count,
        "mojibake_after": after_count,
        "body_fixes_approx": body_fixes,
        "i18n_key_fixes": i18n_fixes,
        "corrupted_remaining": corrupted,
        "apostrophe_fixes": len(re.findall(r"You—re|doesn—t|BMC—s|ward—s|it—s|we—ll", app_final)),
    }
    (ROOT / "tools" / "_encoding_v99_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
