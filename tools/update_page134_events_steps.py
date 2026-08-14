import json
from pathlib import Path

from lxml import etree, html


root = Path(__file__).resolve().parents[1]
page = root / "pg133_sec001.html"
texts_path = root / "content/i18n/sw-TZ/texts.json"
ids_path = root / "content/page134-events-audio-ids.json"
texts = json.loads(texts_path.read_text(encoding="utf-8"))
updates = {
    "pg133_n0008": "Bofya au tumia mishale menyu ya bloku za ‘Matukio’ kama inavyoonekana au inavyobainishwa katika Kielelezo namba 22.",
    "pg133_n0011": "Buruta au tumia mishale, kisha udondoshe bloku ya ‘wakati inapobonyezwa’ kwenye eneo la kuandikia kama inavyoonekana au inavyobainishwa katika Kielelezo namba 22.",
    "pg133_n0014": "Kielelezo namba 22: Kuburuta au kutumia mishale na kudondosha bloku ya wakati inapobonyezwa kwenye eneo la kuandikia.",
    "pg133_im001_audio_desc": "Maelezo ya picha: Menyu ya Matukio imechaguliwa kwenye Scratch au Quorum. Bloku ya ‘wakati inapobonyezwa’ inaburutwa au inahamishwa kwa mishale na kudondoshwa kwenye eneo la kuandikia.",
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
image = tree.xpath('//*[@data-id="pg133_im001"]')[0]
image.set("alt", updates["pg133_im001_audio_desc"])
page.write_text(
    etree.tostring(tree, encoding="unicode", method="html", doctype="<!DOCTYPE html>"),
    encoding="utf-8",
)
ids_path.write_text(json.dumps(sorted(ids), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print({"updated": sorted(ids)})
