#!/usr/bin/env python3
"""Audit current app.js i18n for issues."""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _apply_i18n_v94 import parse_i18n_block, is_corrupted

ROOT = Path(__file__).resolve().parent.parent
app = (ROOT / "js/app.js").read_text(encoding="utf-8")
en = parse_i18n_block(app, "en")
out = []

for lang in ("en", "hi", "mr", "gu"):
    cur = parse_i18n_block(app, lang)
    for k, v in cur.items():
        flags = []
        if is_corrupted(v):
            flags.append("corrupted")
        if re.search(r"\?\?+", v):
            flags.append("multi-?")
        if re.search(r" \? ", v) or re.search(r"→", v) and lang != "en" and "→" in v and "garbage" in v.lower():
            flags.append("arrow-placeholder")
        if lang != "en":
            if v == en.get(k, ""):
                flags.append("same-as-en")
            if re.search(r"Garbage dump|Solid waste / garbage|Solid Waste →", v):
                flags.append("untranslated-en-fragment")
        if flags:
            out.append({"lang": lang, "key": k, "flags": flags, "val": v})

report = {
    "total_issues": len(out),
    "by_lang": {l: sum(1 for r in out if r["lang"] == l) for l in ("en", "hi", "mr", "gu")},
    "issues": out,
}
(ROOT / "tools/_audit_i18n_report.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
)
print(json.dumps({"total": len(out), "by_lang": report["by_lang"]}, indent=2))
