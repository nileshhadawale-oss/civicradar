"""One-shot merge: inject Reports Storage + Backend from tests/_chunk.js into js/app.js."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
chunk = (ROOT / "tests" / "_chunk.js").read_text(encoding="utf-8")
app = (ROOT / "js" / "app.js").read_text(encoding="utf-8")
lines = chunk.splitlines()

start = next(i for i, l in enumerate(lines) if l.strip() == "/* ---------- Reports Storage ---------- */")
end = next(i for i, l in enumerate(lines) if l.strip() == "window.Backend = Backend;")

block = "\n".join(lines[start : end + 1]) + "\n"

marker = "  window.Backend = Backend;"
if marker not in app:
    raise SystemExit("marker not found in app.js")
if "const Backend = {" in app:
    raise SystemExit("Backend already present in app.js")

app = app.replace(marker, block, 1)
(ROOT / "js" / "app.js").write_text(app, encoding="utf-8")
print(f"Inserted {end - start + 1} lines from _chunk.js into app.js")
