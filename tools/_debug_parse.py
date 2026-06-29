import re
from pathlib import Path

text = Path(r"C:\civicradar\tests\_app_git.js").read_text(encoding="utf-8")
start = text.index("hi: {")
end = text.index("mr: {")
block = text[start:end]
keys = re.findall(r"'([^']+)':", block)
print("block count", len(keys), "unique", len(set(keys)))
print("esc.subtitle in", "esc.subtitle" in set(keys))
