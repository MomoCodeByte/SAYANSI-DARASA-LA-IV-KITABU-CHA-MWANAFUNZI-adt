"""Audit per-PDF-page text order and media presence against canonical ADT HTML."""

import json
import re
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parents[1]
PDF = Path(r"C:\Users\Admin\Desktop\additionBooks\SAYANSI STD 4 PB\SAYANSI DARASA LA IV KITABU CHA MWANAFUNZI.pdf")
TEXTS = json.loads((ROOT / "content/i18n/sw-TZ/texts.json").read_text(encoding="utf-8-sig"))
PAGES = json.loads((ROOT / "content/pages.json").read_text(encoding="utf-8-sig"))


def tokens(value):
    value = unicodedata.normalize("NFKC", value).lower()
    return [w for w in re.findall(r"[^\W_]+", value, flags=re.UNICODE) if len(w) > 1]


sources = []
for entry in PAGES:
    if entry["section_id"].startswith("qz"):
        continue
    source = (ROOT / entry["href"]).read_text(encoding="utf-8-sig")
    ids = list(dict.fromkeys(re.findall(r'data-id="([^"]+)"', source)))
    ids_by_page = {}
    for item_id in ids:
        match = re.match(r"pg(\d{3})_", item_id)
        if match:
            ids_by_page.setdefault(int(match.group(1)), []).append(item_id)

    primary_match = re.match(r"pg(\d{3})_", entry["section_id"])
    primary_page = int(primary_match.group(1)) if primary_match else None
    runtime_controls = sum(
        int(value) for value in re.findall(r'data-runtime-controls="(\d+)"', source)
    )
    image_tags = re.findall(r"<img\b[^>]*>", source, re.I)
    visible_image_tags = [
        tag for tag in image_tags
        if not re.search(
            r'\bhidden\b|style="[^"]*display\s*:\s*none|alt="Zoezi\s+namba|data-vector-reconstruction="true"',
            tag,
            re.I,
        )
    ]
    image_pages = [
        int(match.group(1))
        for tag in visible_image_tags
        if (match := re.search(r'data-id="pg(\d{3})_[^"]+"', tag, re.I))
    ]
    total_images = len(visible_image_tags)
    unassigned_images = max(0, total_images - len(image_pages))

    # A converted file may contain a continuation belonging to the next PDF
    # page.  Emit one scoped fragment per data-id prefix instead of attaching
    # the complete file text/media to every page mentioned in that file.
    for covered_page, page_ids in ids_by_page.items():
        sources.append({
            "file": entry["href"],
            "covered": {covered_page},
            "text": " ".join(str(TEXTS.get(i, "")) for i in page_ids),
            "images": image_pages.count(covered_page)
            + (unassigned_images if covered_page == primary_page else 0),
            "controls": (len(re.findall(r"<(?:textarea|input|select)\b", source, re.I)) + runtime_controls)
            if covered_page == primary_page else 0,
            "tables": len(re.findall(r"<table\b", source, re.I))
            if covered_page == primary_page else 0,
        })

doc = fitz.open(PDF)
rows = []
for physical, page in enumerate(doc, start=1):
    matched = [s for s in sources if physical in s["covered"]]
    pdf_tokens = tokens(page.get_text("text", sort=True))
    adt_tokens = tokens(" ".join(s["text"] for s in matched))
    ratio = SequenceMatcher(None, pdf_tokens, adt_tokens, autojunk=False).ratio() if pdf_tokens or adt_tokens else 1.0
    rows.append({
        "physical_pdf_page": physical,
        "files": list(dict.fromkeys(s["file"] for s in matched)),
        "order_similarity": round(ratio, 3),
        "pdf_tokens": len(pdf_tokens),
        "adt_tokens": len(adt_tokens),
        "pdf_images": len(page.get_images(full=True)),
        "adt_images": sum(s["images"] for s in matched),
        "adt_controls": sum(s["controls"] for s in matched),
        "adt_tables": sum(s["tables"] for s in matched),
    })

report = {
    "pdf_pages": len(rows),
    "unmapped": [r["physical_pdf_page"] for r in rows if not r["files"]],
    "order_below_050": [
        r["physical_pdf_page"] for r in rows
        if r["order_similarity"] < 0.5
        and not (r["adt_tables"] > 0 and r["adt_controls"] > 0)
    ],
    "image_presence_mismatch": [r["physical_pdf_page"] for r in rows if (r["pdf_images"] > 0) != (r["adt_images"] > 0)],
    "pages": rows,
}
(ROOT / "content/pdf-adt-arrangement-audit.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({k: v for k, v in report.items() if k != "pages"}, ensure_ascii=False, indent=2))
