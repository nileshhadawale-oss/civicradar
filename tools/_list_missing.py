import json, sys
sys.path.insert(0, r"C:\civicradar\tools")
from _apply_i18n_v94 import parse_i18n_block, is_corrupted
from pathlib import Path

ROOT = Path(r"C:\civicradar")
app = (ROOT / "js/app.js").read_text(encoding="utf-8")
git = (ROOT / "tests/_app_git.js").read_text(encoding="utf-8")
supplement = json.loads((ROOT / "tools/i18n-supplement.json").read_text(encoding="utf-8"))
patch2 = json.loads((ROOT / "tools/i18n-patch2.json").read_text(encoding="utf-8"))
en = parse_i18n_block(app, "en")
missing = {}
for lang in ("hi", "mr", "gu"):
    merged = {}
    merged.update(parse_i18n_block(git, lang))
    merged.update(supplement.get(lang, {}))
    merged.update(patch2.get(lang, {}))
    missing[lang] = sorted(k for k in en if k not in merged or is_corrupted(merged.get(k, "")))
all_m = sorted(set(missing["hi"]) | set(missing["mr"]) | set(missing["gu"]))
Path(r"C:\civicradar\tools\_truly_missing.txt").write_text("\n".join(all_m), encoding="utf-8")
print("truly missing unique:", len(all_m))
for k in all_m:
    print(k)
