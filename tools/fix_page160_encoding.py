import json
from pathlib import Path

from lxml import etree, html


root = Path(__file__).resolve().parents[1]
page_path = root / "pg160_sec001.html"
texts_path = root / "content/i18n/sw-TZ/texts.json"
ids_path = root / "content/page160-encoding-audio-ids.json"
updates = {
    "pg160_n0002": "Kielelezo namba 57: ‘Sprite’ ‘City Bus’ akiwa amebaki.",
    "pg160_n0006": "Bofya au tumia mishale menyu ya bloku za ‘Matukio’.",
    "pg160_n0009": "Buruta na dondosha bloku ya ‘wakati inapobonyezwa’ kwenye eneo la kuandikia.",
    "pg160_n0012": "Bofya au tumia mishale menyu ya bloku za ‘Mwendo’.",
    "pg160_n0015": "Buruta na dondosha bloku ya ‘weka mtindo wa mzunguko’ kwenye eneo la kuandikia.",
    "pg160_n0016": "Kisha iunganishe kwenye bloku ya ‘wakati inapobonyezwa’.",
    "pg160_n0019": "Kielelezo namba 58: bloku ya ‘weka mtindo wa mzunguko’.",
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

# Regenerate the image description too so City Bus uses the siti basi pronunciation.
for text_id in ("pg160_im001", "pg160_im001_audio_desc"):
    if text_id in texts:
        audio_ids.add(text_id)

texts_path.write_text(json.dumps(texts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

tree = html.fromstring(page_path.read_text(encoding="utf-8-sig"))
for text_id, value in updates.items():
    nodes = tree.xpath(f'//*[@data-id="{text_id}"]')
    if len(nodes) != 1:
        raise RuntimeError(f"Expected one node for {text_id}, found {len(nodes)}")
    nodes[0].text = value
page_path.write_text(
    etree.tostring(tree, encoding="unicode", method="html", doctype="<!DOCTYPE html>"),
    encoding="utf-8",
)
ids_path.write_text(json.dumps(sorted(audio_ids), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print({"updated": sorted(audio_ids)})
