"""Measure text coverage for every physical PDF page against canonical ADT sections."""

import json
import re
import unicodedata
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parents[1]
PDF = Path(r"C:\Users\Admin\Desktop\additionBooks\SAYANSI STD 4 PB\SAYANSI DARASA LA IV KITABU CHA MWANAFUNZI.pdf")
TEXTS = json.loads((ROOT / "content/i18n/sw-TZ/texts.json").read_text(encoding="utf-8-sig"))
PAGES = json.loads((ROOT / "content/pages.json").read_text(encoding="utf-8-sig"))

def words(value: str) -> set[str]:
    value = unicodedata.normalize("NFKC", value).lower()
    return {word for word in re.findall(r"[^\W_]+", value, flags=re.UNICODE) if len(word) > 1}

sources = []
for entry in PAGES:
    if entry["section_id"].startswith("qz"):
        continue
    path = ROOT / entry["href"]
    source = path.read_text(encoding="utf-8-sig")
    ids = list(dict.fromkeys(re.findall(r'data-id="([^"]+)"', source)))
    covered = {int(n) for n in re.findall(r'data-id="pg(\d{3})_', source)}
    text = " ".join(str(TEXTS.get(data_id, "")) for data_id in ids)
    sources.append((path.name, covered, text))

doc = fitz.open(PDF)
records = []
for physical in range(1, len(doc) + 1):
    matches = [(name, text) for name, covered, text in sources if physical in covered]
    html_words = words(" ".join(text for _, text in matches))
    pdf_words = words(doc[physical - 1].get_text("text", sort=True))
    shared = html_words & pdf_words
    recall = len(shared) / len(pdf_words) if pdf_words else 1.0
    precision = len(shared) / len(html_words) if html_words else 0.0
    records.append({
        "physical_pdf_page": physical,
        "files": [name for name, _ in matches],
        "pdf_words": len(pdf_words), "adt_words": len(html_words),
        "recall": round(recall, 3), "precision": round(precision, 3),
        "missing_sample": sorted(pdf_words - html_words)[:30],
    })
result = {
    "pdf_pages": len(doc),
    "pages_below_070_recall": [r["physical_pdf_page"] for r in records if r["recall"] < 0.70],
    "pages_below_040_recall": [r["physical_pdf_page"] for r in records if r["recall"] < 0.40],
    "unmapped_pdf_pages": [r["physical_pdf_page"] for r in records if not r["files"]],
    "pages": records,
}
(ROOT / "content/pdf-html-text-coverage.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({k: v for k, v in result.items() if k != "pages"}, ensure_ascii=False, indent=2))
