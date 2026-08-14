import json
from pathlib import Path

from lxml import etree, html


root = Path(__file__).resolve().parents[1]
page = root / "pg124_sec001.html"
texts_path = root / "content/i18n/sw-TZ/texts.json"
ids_path = root / "content/page125-documents-reference-audio-ids.json"
texts = json.loads(texts_path.read_text(encoding="utf-8"))
value = "Bofya au tumia mishale ‘Documents’ kama inavyoonekana au inavyobainishwa katika Kielelezo namba 9(b)."
ids = ["pg124_n0009", "pg124_n0009_easy_read"]
for text_id in ids:
    texts[text_id] = value
texts_path.write_text(json.dumps(texts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

tree = html.fromstring(page.read_text(encoding="utf-8-sig"))
node = tree.xpath('//*[@data-id="pg124_n0009"]')[0]
node.text = value
page.write_text(
    etree.tostring(tree, encoding="unicode", method="html", doctype="<!DOCTYPE html>"),
    encoding="utf-8",
)
ids_path.write_text(json.dumps(ids, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print({"updated": ids})
