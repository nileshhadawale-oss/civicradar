#!/usr/bin/env python3
"""Reconcile hi/mr/gu i18n from clean git base + supplements + new-key translation."""
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
    for km in re.finditer(r"^\s+'([^']+)':\s*", block, re.M):
        key = km.group(1)
        pos = km.end()
        if block[pos] == "'":
            i = pos + 1
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
            out[key] = "".join(chars)
    return out


def is_corrupted(val: str) -> bool:
    if not val or val.strip() == "":
        return True
    if re.search(r"\?{3,}", val):
        return True
    if re.match(r"^[\?\s\.]+$", val):
        return True
    # Mostly question marks (legacy placeholder encoding)
    if len(val) > 4:
        q_ratio = val.count("?") / len(val)
        if q_ratio > 0.25 and not any("\u0900" <= c <= "\u097f" for c in val):
            if not any("\u0a80" <= c <= "\u0aff" for c in val):
                return True
    if "ï¿½" in val:
        return True
    return False


def fix_en_mojibake(val: str) -> str:
    return (
        val.replace("ï¿½", "—")
        .replace("â€™", "'")
        .replace("â€œ", '"')
        .replace("â€", '"')
        .replace("?? ", "🦟 ")
        .replace("??? ", "🌧️ ")
    )


def main():
    app_path = ROOT / "js" / "app.js"
    git_path = ROOT / "tests" / "_app_git.js"
    app = app_path.read_text(encoding="utf-8")
    git = git_path.read_text(encoding="utf-8")

    supplement = json.loads((ROOT / "tools" / "i18n-supplement.json").read_text(encoding="utf-8"))
    patch2 = json.loads((ROOT / "tools" / "i18n-patch2.json").read_text(encoding="utf-8"))

    en = parse_i18n_block(app, "en")
    for lang in ("hi", "mr", "gu"):
        git_lang = parse_i18n_block(git, lang)
        cur = parse_i18n_block(app, lang)
        sup = {**git_lang, **supplement.get(lang, {}), **patch2.get(lang, {})}
        missing = [k for k in en if k not in sup]
        corrupted = [k for k, v in cur.items() if is_corrupted(v)]
        print(f"\n=== {lang} ===")
        print(f"  en keys: {len(en)}, git: {len(git_lang)}, supplement total: {len(sup)}")
        print(f"  current corrupted: {len(corrupted)}")
        print(f"  still missing after merge: {len(missing)}")
        if missing:
            for k in missing[:40]:
                print(f"    - {k}: {en[k][:60]}...")
            if len(missing) > 40:
                print(f"    ... and {len(missing)-40} more")


if __name__ == "__main__":
    main()
