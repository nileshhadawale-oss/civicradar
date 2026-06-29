#!/usr/bin/env python3
"""Apply v94 i18n fix: restore clean translations + new keys + fix en mojibake."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def parse_i18n_block(text: str, lang: str) -> dict[str, str]:
    m = re.search(rf"    {lang}: \{{\n", text)
    if not m:
        return {}
    rest = text[m.start() :]
    depth = 0
    end = 0
    for i, ch in enumerate(rest):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    block = rest[:end]
    out: dict[str, str] = {}
    for km in re.finditer(r"'([^']+)':\s*'", block):
        key = km.group(1)
        i = km.end()
        chars = []
        while i < len(block):
            c = block[i]
            if c == "\\" and i + 1 < len(block):
                chars.append(block[i : i + 2])
                i += 2
                continue
            if c == "'":
                break
            chars.append(c)
            i += 1
        raw = "".join(chars)
        out[key] = raw.replace("\\'", "'").replace("\\\\", "\\").replace("\\n", "\n")
    return out


def is_corrupted(val: str) -> bool:
    if not val or val.strip() == "":
        return True
    if re.search(r"\?{3,}", val):
        return True
    if re.match(r"^[\?\s\.]+$", val):
        return True
    if len(val) > 4:
        q_ratio = val.count("?") / len(val)
        if q_ratio > 0.25 and not any("\u0900" <= c <= "\u097f" for c in val):
            if not any("\u0a80" <= c <= "\u0aff" for c in val):
                return True
    if "ï¿½" in val:
        return True
    return False


def fix_mojibake(val: str) -> str:
    v = (
        val.replace("ï¿½", "—")
        .replace("â€™", "'")
        .replace("â€œ", '"')
        .replace("â€", '"')
        .replace("â\u0080\u0094", "—")
        .replace("â\u0080\u0099", "'")
    )
    v = re.sub(r"\?\? ", "🦟 ", v)
    v = re.sub(r"\?\?\? ", "🌧️ ", v)
    v = re.sub(r" \?\?(\s|$)", " 👋\\1", v)
    v = re.sub(r" \?\?\?(\s|$)", " 🌧️\\1", v)
    v = v.replace("Before ? After", "Before → After")
    v = v.replace("Before ? after", "Before → after")
    v = v.replace("login ? Online", "login → Online")
    v = v.replace("Public Health ? Pest", "Public Health → Pest")
    v = v.replace("? GPS", "⚠ GPS")
    v = v.replace("? FIXED", "✅ FIXED")
    v = v.replace("loading metricsï¿½", "loading metrics…")
    v = v.replace("Loading metricsï¿½", "Loading metrics…")
    v = v.replace("Submittingï¿½", "Submitting…")
    v = v.replace("wardï¿½", "ward…")
    v = v.replace("typing your wardï¿½", "typing your ward…")
    v = v.replace("locationï¿½", "location…")
    v = v.replace("doesnï¿½t", "doesn't")
    v = v.replace("itï¿½s", "it's")
    v = v.replace("Monsoonï¿½s", "Monsoon's")
    v = v.replace("youï¿½ll", "you'll")
    v = v.replace("wardï¿½s", "ward's")
    v = v.replace("BMCï¿½s", "BMC's")
    v = v.replace("24ï¿½7", "24×7")
    v = v.replace("1 ï¿½ File", "1 — File")
    v = v.replace("2 ï¿½ Day", "2 — Day")
    v = v.replace("3 ï¿½ Day", "3 — Day")
    v = v.replace("4 ï¿½ Day", "4 — Day")
    v = v.replace("Monsoon is here â", "Monsoon is here —")
    v = re.sub(
        r"Free — offline — 3 cities — 4 langs",
        "Free · offline · 3 cities · 4 langs",
        v,
    )
    return v


def js_escape(s: str) -> str:
    return (
        s.replace("\\", "\\\\")
        .replace("'", "\\'")
        .replace("\n", "\\n")
        .replace("\r", "")
    )


def format_locale_block(lang: str, data: dict[str, str], key_order: list[str]) -> str:
    lines = [f"    {lang}: {{"]
    for key in key_order:
        if key not in data:
            continue
        val = js_escape(data[key])
        lines.append(f"      '{key}': '{val}',")
    lines.append("    },")
    return "\n\n".join(lines) + "\n"


def main():
    app_path = ROOT / "js" / "app.js"
    git_path = ROOT / "tests" / "_app_git.js"
    new_keys_path = ROOT / "tools" / "i18n-v94-new-keys.json"
    polish_path = ROOT / "tools" / "i18n-v94-v93-polish.json"

    app = app_path.read_text(encoding="utf-8")
    git = git_path.read_text(encoding="utf-8")

    supplement = json.loads((ROOT / "tools" / "i18n-supplement.json").read_text(encoding="utf-8"))
    patch2 = json.loads((ROOT / "tools" / "i18n-patch2.json").read_text(encoding="utf-8"))
    new_keys = {}
    if new_keys_path.exists():
        new_keys = json.loads(new_keys_path.read_text(encoding="utf-8"))
    polish = {}
    if polish_path.exists():
        polish = json.loads(polish_path.read_text(encoding="utf-8"))

    en = parse_i18n_block(app, "en")
    key_order = list(en.keys())

    # Fix English
    en_fixed = {k: fix_mojibake(v) for k, v in en.items()}

    stats = {"en": 0, "hi": 0, "mr": 0, "gu": 0}
    locales = {}
    for lang in ("hi", "mr", "gu"):
        merged = {}
        merged.update(parse_i18n_block(git, lang))
        merged.update(supplement.get(lang, {}))
        merged.update(patch2.get(lang, {}))
        merged.update(new_keys.get(lang, {}))
        merged.update(polish.get(lang, {}))

        cur = parse_i18n_block(app, lang)
        out = {}
        for key in key_order:
            en_val = en_fixed[key]
            if key in merged and not is_corrupted(merged[key]):
                out[key] = fix_mojibake(merged[key])
            elif key in cur and not is_corrupted(cur[key]):
                out[key] = fix_mojibake(cur[key])
            else:
                out[key] = en_val  # last resort
                stats[lang] += 1
            if key in cur and cur[key] != out[key]:
                stats[lang] += 1
        locales[lang] = out

    # Replace I18N section
    i18n_start = app.index("  const I18N = {")
    i18n_end = app.index("\n  };", i18n_start) + len("\n  };")

    new_i18n = "  const I18N = {\n\n"
    new_i18n += format_locale_block("en", en_fixed, key_order)
    new_i18n += "\n"
    for lang in ("hi", "mr", "gu"):
        new_i18n += format_locale_block(lang, locales[lang], key_order)
    new_i18n += "  };"

    app = app[:i18n_start] + new_i18n + app[i18n_end:]

    # Bump version
    app = re.sub(r"const CIVIC_APP_VERSION = 'v\d+';", "const CIVIC_APP_VERSION = 'v94';", app)
    app_path.write_text(app, encoding="utf-8")

    sw_path = ROOT / "sw.js"
    sw = sw_path.read_text(encoding="utf-8")
    sw = re.sub(r"const CACHE = 'civicradar-v\d+';", "const CACHE = 'civicradar-v94';", sw)
    sw_path.write_text(sw, encoding="utf-8")

    e2e_path = ROOT / "tests" / "e2e_comprehensive.py"
    e2e = e2e_path.read_text(encoding="utf-8")
    e2e = e2e.replace("civicradar-v93", "civicradar-v94")
    e2e_path.write_text(e2e, encoding="utf-8")

    print("Stats (keys changed/fallback):", stats)
    for lang in ("hi", "mr", "gu"):
        corrupted = sum(1 for k, v in locales[lang].items() if is_corrupted(v))
        print(f"{lang}: {len(locales[lang])} keys, still corrupted: {corrupted}, fallback: {stats[lang]}")


if __name__ == "__main__":
    main()
