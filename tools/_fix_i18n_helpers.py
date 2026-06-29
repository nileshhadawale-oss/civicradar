"""Insert missing i18n helpers + utilities after I18N block in app.js."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
chunk = (ROOT / "tests" / "_chunk.js").read_text(encoding="utf-8")
app_path = ROOT / "js" / "app.js"
app = app_path.read_text(encoding="utf-8")

lines = chunk.splitlines()
start = next(i for i, l in enumerate(lines) if l.strip().startswith("const LANG_ORDER"))
end = next(i for i, l in enumerate(lines) if l.strip() == "/* ---------- Reports Storage ---------- */")

block = "\n".join(lines[start:end]) + "\n\n"

marker = "  };\n\n  /* ---------- Reports Storage ---------- */"
if "const LANG_ORDER" in app.split(marker)[0].split("const I18N =")[-1]:
    print("LANG_ORDER already present after I18N")
else:
    if marker not in app:
        raise SystemExit("marker not found")
    app = app.replace(marker, "  };\n\n" + block + "  /* ---------- Reports Storage ---------- */", 1)
    app_path.write_text(app, encoding="utf-8")
    print(f"Inserted {end - start} i18n helper lines")
