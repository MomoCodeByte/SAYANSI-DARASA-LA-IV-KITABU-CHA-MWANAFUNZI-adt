"""Audit converted pages 1–50 against matrix scope and ADT interaction rules."""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
plan = json.loads((ROOT / "content/validation-matrix-plan.json").read_text(encoding="utf-8"))
rows = []
for path in sorted(ROOT.glob("*.html")):
    html = path.read_text(encoding="utf-8")
    meta = re.search(r'<meta name="page-section-id" content="(\d+)"', html)
    if not meta or not 1 <= int(meta.group(1)) <= 50:
        continue
    images = re.findall(r'<img\b[^>]*src="([^"]+)"', html)
    rows.append({
        "converted_page": int(meta.group(1)),
        "file": path.name,
        "section_type": (re.search(r'data-section-type="([^"]+)"', html) or [None, "unknown"])[1],
        "images": len(images),
        "missing_images": [src for src in images if not (ROOT / src).exists()],
        "inputs": len(re.findall(r'<input\b', html)),
        "textareas": len(re.findall(r'<textarea\b', html)),
        "buttons": len(re.findall(r'<button\b', html)),
        "matrix_script": "matrix-accessibility.js" in html,
    })

scope_files = {row["file"] for row in rows}
matrix_items = [
    item for item in plan["items"]
    if scope_files.intersection(item.get("files", []))
]
result = {
    "scope": "converted pages 1-50",
    "page_files": len(rows),
    "matrix_items": len(matrix_items),
    "missing_images": sum(len(row["missing_images"]) for row in rows),
    "interactive_pages": sum(bool(row["inputs"] or row["textareas"] or row["buttons"]) for row in rows),
    "pages": sorted(rows, key=lambda row: (row["converted_page"], row["file"])),
    "matrix": matrix_items,
}
issues = []
for row in rows:
    source = (ROOT / row["file"]).read_text(encoding="utf-8")
    for tag in re.findall(r"<img\\b[^>]*>", source):
        if "alt=" not in tag:
            issues.append({"file": row["file"], "issue": "image_missing_alt"})
    if source.count('id="content"') != 1:
        issues.append({"file": row["file"], "issue": "content_id_count", "count": source.count('id="content"')})
    if "base.bundle.local.js" not in source:
        issues.append({"file": row["file"], "issue": "missing_adt_runtime"})
result["qa_issues"] = issues
(ROOT / "content/review-pages-001-050.json").write_text(
    json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)
print(json.dumps({key: value for key, value in result.items() if key not in {"pages", "matrix"}}, ensure_ascii=False, indent=2))
