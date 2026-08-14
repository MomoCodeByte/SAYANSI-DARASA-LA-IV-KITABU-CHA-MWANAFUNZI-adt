"""Audit the complete canonical ADT reading order."""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
pages = json.loads((ROOT / "content/pages.json").read_text(encoding="utf-8-sig"))
rows, issues = [], []
previous_section_id = 0
for position, entry in enumerate(pages, start=1):
    path = ROOT / entry["href"]
    source = path.read_text(encoding="utf-8-sig")
    images = re.findall(r'<img\b[^>]*src="([^"]+)"', source)
    missing = [src for src in images if not (ROOT / src).exists()]
    meta = re.search(r'<meta name="page-section-id" content="(\d+)"', source)
    if not meta:
        issues.append({"file": path.name, "issue": "missing_page_section_id"})
    elif int(meta.group(1)) <= previous_section_id:
        issues.append({"file": path.name, "issue": "reading_order_not_increasing"})
    else:
        previous_section_id = int(meta.group(1))
    for tag in re.findall(r"<img\b[^>]*>", source):
        if "alt=" not in tag:
            issues.append({"file": path.name, "issue": "image_missing_alt"})
    if source.count('id="content"') != 1:
        issues.append({"file": path.name, "issue": "content_id_count", "count": source.count('id="content"')})
    if "base.bundle.local.js" not in source:
        issues.append({"file": path.name, "issue": "missing_adt_runtime"})
    rows.append({
        "converted_page": position, "file": path.name,
        "source_page_number": entry.get("page_number"),
        "images": len(images), "missing_images": missing,
        "interactive": bool(re.search(r'<(?:input|textarea|button)\b', source)),
    })
result = {
    "scope": "canonical full book", "page_files": len(rows),
    "unique_files": len({row["file"] for row in rows}),
    "missing_images": sum(len(row["missing_images"]) for row in rows),
    "interactive_pages": sum(row["interactive"] for row in rows),
    "qa_issues": issues, "pages": rows,
}
(ROOT / "content/review-full-book.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({k: v for k, v in result.items() if k != "pages"}, ensure_ascii=False, indent=2))
