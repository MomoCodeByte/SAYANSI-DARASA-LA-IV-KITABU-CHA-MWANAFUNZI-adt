import json
from pathlib import Path

from lxml import etree, html


root = Path(__file__).resolve().parents[1]
page_path = root / "pg151_sec001.html"
texts_path = root / "content/i18n/sw-TZ/texts.json"
ids_path = root / "content/page151-layout-audio-ids.json"
updates = {
    "pg151_n0002": "Kielelezo namba 44: kuchagua ‘kishale chini’.",
    "pg151_n0006": "Bofya au tumia mishale menyu ya bloku za ‘Mwendo’.",
    "pg151_n0009": "Buruta na dondosha bloku ya ‘zunguka digrii’ kwenye eneo la kuandikia.",
    "pg151_n0010": "Kisha, iunganishe bloku ya ‘zunguka digrii’ kwenye bloku ya ‘wakati kitufe cha kinapobonyezwa’ kama inavyoonekana au inavyobainishwa katika Kielelezo namba 45.",
    "pg151_n0013": "Bofya au tumia mishale menyu ya bloku za ‘Sauti’.",
    "pg151_n0016": "Buruta na dondosha bloku ya ‘cheza sauti hadi ikamilike’ kwenye eneo la kuandikia.",
    "pg151_n0017": "Kisha, unganisha bloku hiyo kwenye bloku ya ‘zunguka digrii’ kama inavyoonekana au inavyobainishwa katika Kielelezo namba 45.",
    "pg151_im002_audio_desc": "Maelezo ya picha: Juu kuna programu ya kishale juu yenye bloku za songa hatua kumi na cheza sauti hadi ikamilike. Chini kuna bloku ya wakati kitufe cha kishale chini kinapobonyezwa pamoja na menyu ya kuchagua vishale.",
}

texts = json.loads(texts_path.read_text(encoding="utf-8"))
audio_ids = set()
for text_id, value in updates.items():
    texts[text_id] = value
    audio_ids.add(text_id)
    easy_id = f"{text_id}_easy_read"
    if easy_id in texts:
        texts[easy_id] = value
        audio_ids.add(easy_id)
texts_path.write_text(json.dumps(texts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

tree = html.fromstring(page_path.read_text(encoding="utf-8-sig"))
for text_id, value in updates.items():
    nodes = tree.xpath(f'//*[@data-id="{text_id}"]')
    if len(nodes) != 1:
        raise RuntimeError(f"Expected one node for {text_id}, found {len(nodes)}")
    nodes[0].text = value

image = tree.xpath('//*[@data-id="pg151_im002"]')[0]
image.set("src", "images/pg151_im002_v43.png")
image.set("alt", updates["pg151_im002_audio_desc"])

page_path.write_text(
    etree.tostring(tree, encoding="unicode", method="html", doctype="<!DOCTYPE html>"),
    encoding="utf-8",
)
ids_path.write_text(json.dumps(sorted(audio_ids), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print({"updated": sorted(audio_ids)})
