import json
from pathlib import Path

from lxml import etree, html


root = Path(__file__).resolve().parents[1]
page = root / "pg125_sec001.html"
texts_path = root / "content/i18n/sw-TZ/texts.json"
ids_path = root / "content/page126-red-reference-audio-ids.json"
texts = json.loads(texts_path.read_text(encoding="utf-8"))
value = "Bofya au tumia mishale kwenye rangi nyekundu ‘Red’ kama inavyoonekana au inavyobainishwa katika Kielelezo namba 10."
ids = ["pg125_n0012"]
texts["pg125_n0012"] = value
if "pg125_n0012_easy_read" in texts:
    texts["pg125_n0012_easy_read"] = value
    ids.append("pg125_n0012_easy_read")
texts_path.write_text(json.dumps(texts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

tree = html.fromstring(page.read_text(encoding="utf-8-sig"))
tree.xpath('//*[@data-id="pg125_n0012"]')[0].text = value
page.write_text(
    etree.tostring(tree, encoding="unicode", method="html", doctype="<!DOCTYPE html>"),
    encoding="utf-8",
)
ids_path.write_text(json.dumps(ids, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print({"updated": ids})
