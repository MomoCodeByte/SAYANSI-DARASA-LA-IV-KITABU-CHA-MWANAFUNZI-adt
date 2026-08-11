"""Build the authoritative physical-PDF-page to ADT-section review map."""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
pages = json.loads((ROOT / "content/pages.json").read_text(encoding="utf-8"))
mapped = []
for position, entry in enumerate(pages, 1):
    section = entry["section_id"]
    match = re.match(r"pg(\d{3})_", section)
    source = (ROOT / entry["href"]).read_text(encoding="utf-8") if (ROOT / entry["href"]).exists() else ""
    covered = sorted({int(n) for n in re.findall(r'data-id="pg(\d{3})_', source)})
    mapped.append({
        "reading_order": position,
        "section_id": section,
        "href": entry["href"],
        "printed_page": entry.get("page_number"),
        "pdf_physical_page": int(match.group(1)) if match else None,
        "covered_pdf_pages": covered,
        "kind": "quiz" if section.startswith("qz") else "book_page",
        "exists": (ROOT / entry["href"]).exists(),
    })

book_pages = [row for row in mapped if row["kind"] == "book_page"]
physical = {n for row in book_pages for n in row["covered_pdf_pages"]}
result = {
    "source_pdf_pages": 168,
    "adt_reading_entries": len(mapped),
    "adt_book_sections": len(book_pages),
    "adt_quiz_entries": len(mapped) - len(book_pages),
    "missing_physical_pages": sorted(set(range(1, 169)) - physical),
    "duplicate_physical_pages": sorted(n for n in physical if sum(n in r["covered_pdf_pages"] for r in book_pages) > 1),
    "missing_files": [row["href"] for row in mapped if not row["exists"]],
    "pages": mapped,
}
(ROOT / "content/pdf-adt-review-map.json").write_text(
    json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)
print(json.dumps({key: value for key, value in result.items() if key != "pages"}, ensure_ascii=False, indent=2))
