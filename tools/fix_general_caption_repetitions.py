import json
from pathlib import Path
from lxml import html, etree

ROOT = Path(__file__).resolve().parents[1]
TEXT_PATH = ROOT / "content/i18n/sw-TZ/texts.json"
texts = json.loads(TEXT_PATH.read_text(encoding="utf-8-sig"))
updates = {
    "pg025_n0003": "Chunguza Kielelezo namba 15 kinachoonesha na kubainisha mifano ya alama za dharura.",
    "pg026_n0008": "Chunguza Kielelezo namba 16 kinachoonesha na kubainisha mifano ya alama za lazima au amri.",
    "pg040_n0031": "Chunguza Kielelezo namba 3 kinachoonesha na kubainisha mgonjwa wa tetekuwanga.",
    "pg050_n0004": "Chunguza Kielelezo namba 6 kinachoonesha na kubainisha hatua za ukuaji wa nzi.",
    "pg053_n0007": "Chunguza Kielelezo namba 7 kinachoonesha na kubainisha hatua za ukuaji wa mende.",
    "pg094_n0026": "Chunguza Kielelezo namba 6 kinachoonesha na kubainisha vyanzo vya nishati ya mwanga.",
}
for key, value in updates.items():
    page = ROOT / f"{key[:5]}_sec001.html"
    doc = html.fromstring(page.read_text(encoding="utf-8"))
    node = doc.xpath(f'//*[@data-id="{key}"]')[0]
    for child in list(node): node.remove(child)
    node.text = value
    page.write_text(etree.tostring(doc, encoding="unicode", method="html", doctype="<!DOCTYPE html>"), encoding="utf-8")
    texts[key] = value
TEXT_PATH.write_text(json.dumps(texts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("updated", len(updates))
