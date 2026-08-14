import json
import re
from pathlib import Path

from lxml import etree, html


root = Path(__file__).resolve().parents[1]
page = root / "pg136_sec001.html"
texts_path = root / "content/i18n/sw-TZ/texts.json"
ids_path = root / "content/page137-rotation-audio-ids.json"
texts = json.loads(texts_path.read_text(encoding="utf-8"))
updates = {
    "pg136_n0036": "Unganisha bloku ya ‘zunguka digrii au nyuzi ↻(15)’ na bloku ya ‘wakati inapobonyezwa’ kama inavyoonekana au inavyobainishwa katika Kielelezo namba 27.",
    "pg136_im001_audio_desc": "Maelezo ya picha: Bloku ya ‘wakati bendera ya kijani inapobonyezwa’ imeunganishwa na bloku ya ‘zunguka digrii 15’. Namba ya digrii inaweza kubadilishwa.",
    "pg136_im002_audio_desc": "Maelezo ya picha: Hatua za kutengeneza programu ya kumzungusha Sprite kwenye Scratch au Quorum. Bloku za Matukio na Mwendo zimechaguliwa, kisha bloku ya ‘wakati inapobonyezwa’ imeunganishwa na bloku ya ‘zunguka digrii 15’.",
}
for text_id, value in updates.items():
    texts[text_id] = value
    easy_id = f"{text_id}_easy_read"
    if easy_id in texts and not text_id.endswith("_audio_desc"):
        texts[easy_id] = value
texts_path.write_text(json.dumps(texts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

tree = html.fromstring(page.read_text(encoding="utf-8-sig"))
for text_id, value in updates.items():
    nodes = tree.xpath(f'//*[@data-id="{text_id}"]')
    if nodes and len(nodes[0]) == 0:
        nodes[0].text = value
for image_id, desc_id in (("pg136_im001", "pg136_im001_audio_desc"), ("pg136_im002", "pg136_im002_audio_desc")):
    tree.xpath(f'//*[@data-id="{image_id}"]')[0].set("alt", updates[desc_id])
page.write_text(
    etree.tostring(tree, encoding="unicode", method="html", doctype="<!DOCTYPE html>"),
    encoding="utf-8",
)

pattern = re.compile(r"\b(?:Desktop|Save)\b", re.I)
ids = {text_id for text_id, value in texts.items() if pattern.search(str(value))}
ids.update(updates)
ids.update(
    f"{text_id}_easy_read" for text_id in updates
    if f"{text_id}_easy_read" in texts
)
ids_path.write_text(json.dumps(sorted(ids), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print({"updated_ids": len(updates), "audio_ids": len(ids)})
