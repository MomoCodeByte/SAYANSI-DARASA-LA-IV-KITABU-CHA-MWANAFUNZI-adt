"""Audit converted pages 51-100 against matrix scope and ADT interaction rules."""

import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
plan = json.loads((ROOT / "content/validation-matrix-plan.json").read_text(encoding="utf-8"))
status_path = ROOT / "content/matrix-implementation-status.json"
statuses = json.loads(status_path.read_text(encoding="utf-8")) if status_path.exists() else {}
status_by_item = {
    int(item.get("matrix_item", 0)): item.get("status", "UNKNOWN")
    for item in (statuses.get("rows", []) if isinstance(statuses, dict) else statuses)
}

rows = []
for path in sorted(ROOT.glob("*.html")):
    source = path.read_text(encoding="utf-8")
    meta = re.search(r'<meta name="page-section-id" content="(\d+)"', source)
    if not meta or not 51 <= int(meta.group(1)) <= 100:
        continue
    images = re.findall(r'<img\b[^>]*src="([^"]+)"', source)
    rows.append({
        "converted_page": int(meta.group(1)),
        "file": path.name,
        "section_type": (re.search(r'data-section-type="([^"]+)"', source) or [None, "unknown"])[1],
        "images": len(images),
        "missing_images": [src for src in images if not (ROOT / src).exists()],
        "inputs": len(re.findall(r'<input\b', source)),
        "textareas": len(re.findall(r'<textarea\b', source)),
        "buttons": len(re.findall(r'<button\b', source)),
        "matrix_script": "matrix-accessibility.js" in source,
    })

scope_files = {row["file"] for row in rows}
matrix_items = []
for item in plan["items"]:
    if scope_files.intersection(item.get("files", [])):
        enriched = dict(item)
        enriched["implementation_status"] = status_by_item.get(int(item["matrix_item"]), "UNKNOWN")
        matrix_items.append(enriched)

issues = []
for row in rows:
    source = (ROOT / row["file"]).read_text(encoding="utf-8")
    for tag in re.findall(r"<img\b[^>]*>", source):
        if "alt=" not in tag:
            issues.append({"file": row["file"], "issue": "image_missing_alt"})
    if source.count('id="content"') != 1:
        issues.append({"file": row["file"], "issue": "content_id_count", "count": source.count('id="content"')})
    if "base.bundle.local.js" not in source:
        issues.append({"file": row["file"], "issue": "missing_adt_runtime"})

result = {
    "scope": "converted pages 51-100",
    "page_files": len(rows),
    "matrix_items": len(matrix_items),
    "matrix_statuses": dict(sorted(Counter(item["implementation_status"] for item in matrix_items).items())),
    "missing_images": sum(len(row["missing_images"]) for row in rows),
    "interactive_pages": sum(bool(row["inputs"] or row["textareas"] or row["buttons"]) for row in rows),
    "pages": sorted(rows, key=lambda row: (row["converted_page"], row["file"])),
    "matrix": matrix_items,
    "qa_issues": issues,
}
(ROOT / "content/review-pages-051-100.json").write_text(
    json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)
print(json.dumps({key: value for key, value in result.items() if key not in {"pages", "matrix"}}, ensure_ascii=False, indent=2))
