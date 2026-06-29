#!/usr/bin/env python3
"""Validate app.js loads without syntax errors."""
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
app_path = ROOT / "js" / "app.js"
text = app_path.read_text(encoding="utf-8")

# Check I18N block string parsing
start = text.index("const I18N = {")
end = text.index("\n  };", start) + 5
block = text[start:end]

errors = []
for km in re.finditer(r"'([^']+)':\s*'", block):
    key = km.group(1)
    i = km.end()
    while i < len(block):
        c = block[i]
        if c == "\\" and i + 1 < len(block):
            i += 2
            continue
        if c == "'":
            break
        i += 1
    else:
        errors.append(f"Unclosed string for key: {key}")

print(f"I18N keys parsed, unclosed: {len(errors)}")
for e in errors[:10]:
    print(" ", e)

# Try node syntax check if available
for cmd in (["node", "--check", str(app_path)],):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        print(f"node --check: exit={r.returncode}")
        if r.stderr:
            print(r.stderr[:2000])
        break
    except FileNotFoundError:
        print("node not found, skipping syntax check")
