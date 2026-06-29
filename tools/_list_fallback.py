import sys
sys.path.insert(0, r"C:\civicradar\tools")
from _apply_i18n_v94 import parse_i18n_block
from pathlib import Path
app = Path(r"C:\civicradar\js\app.js").read_text(encoding="utf-8")
en = parse_i18n_block(app, "en")
for lang in ("hi", "mr", "gu"):
    d = parse_i18n_block(app, lang)
    fb = sorted(k for k, v in d.items() if v == en.get(k))
    print(lang, len(fb))
    for k in fb:
        print(" ", k)
