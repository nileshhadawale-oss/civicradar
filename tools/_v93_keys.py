import sys
sys.path.insert(0, r"C:\civicradar\tools")
from _apply_i18n_v94 import parse_i18n_block
from pathlib import Path
app=Path(r"C:\civicradar\js\app.js").read_text(encoding="utf-8")
git=Path(r"C:\civicradar\tests\_app_git.js").read_text(encoding="utf-8")
en=parse_i18n_block(app,'en')
en_git=parse_i18n_block(git,'en')
prefixes=('home.','coach.','tour.','persona.','success.','map.empty','report.photo','report.retake','header.','fab.')
changed=[k for k in en if k in en_git and en[k]!=en_git[k] and k.startswith(prefixes)]
Path(r"C:\civicradar\tools\_v93_changed.txt").write_text("\n".join(f"{k}\n  NEW: {en[k]}\n  OLD: {en_git[k]}\n" for k in sorted(changed)), encoding="utf-8")
print(len(changed))
