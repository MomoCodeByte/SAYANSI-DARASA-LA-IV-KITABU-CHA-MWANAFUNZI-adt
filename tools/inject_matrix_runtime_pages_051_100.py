"""Ensure the scoped quiz/activity pages receive matrix UI accessibility rules."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
report = json.loads((ROOT / "content/review-pages-051-100.json").read_text(encoding="utf-8"))
tag = '<script src="./assets/matrix-accessibility.js?v=matrix-v1-2"></script>'
updated = []
for row in report["pages"]:
    path = ROOT / row["file"]
    source = path.read_text(encoding="utf-8")
    if "matrix-accessibility.js" in source:
        continue
    source = source.replace("</body>", f"    {tag}\n</body>")
    path.write_text(source, encoding="utf-8")
    updated.append(path.name)
print(f"updated={len(updated)} files={updated}")
