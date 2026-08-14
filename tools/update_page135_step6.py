import json
from pathlib import Path

from lxml import etree, html


root = Path(__file__).resolve().parents[1]
page = root / "pg134_sec001.html"
texts_path = root / "content/i18n/sw-TZ/texts.json"
ids_path = root / "content/page135-step6-audio-ids.json"
texts = json.loads(texts_path.read_text(encoding="utf-8"))
updates = {
    "pg134_n0002": "Kielelezo namba 23: kuburuta na kuunganisha bloku.",
    "pg134_n0005": "Bofya au tumia mishale kibendera cha kijani ‘Anza’ kama inavyoonekana au inavyobainishwa katika Kielelezo namba 24 ili kuchezesha Sprite.",
    "pg134_n0007": "Kielelezo namba 24: namna ya kucheza mchezo wa kujongea.",
    "pg134_im001_audio_desc": "Maelezo ya picha: Bloku ya Mwendo ‘songa hatua 10’ imeunganishwa chini ya bloku ya kuanza. Namba 10 inaweza kubadilishwa kuwa idadi nyingine ya hatua.",
}
ids = set()
for text_id, value in updates.items():
    texts[text_id] = value
    ids.add(text_id)
    easy_id = f"{text_id}_easy_read"
    if easy_id in texts and not text_id.endswith("_audio_desc"):
        texts[easy_id] = value
        ids.add(easy_id)
texts_path.write_text(json.dumps(texts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

tree = html.fromstring(page.read_text(encoding="utf-8-sig"))
for text_id, value in updates.items():
    nodes = tree.xpath(f'//*[@data-id="{text_id}"]')
    if nodes and len(nodes[0]) == 0:
        nodes[0].text = value
tree.xpath('//*[@data-id="pg134_im001"]')[0].set("alt", updates["pg134_im001_audio_desc"])
page.write_text(
    etree.tostring(tree, encoding="unicode", method="html", doctype="<!DOCTYPE html>"),
    encoding="utf-8",
)
ids_path.write_text(json.dumps(sorted(ids), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print({"updated": sorted(ids)})
