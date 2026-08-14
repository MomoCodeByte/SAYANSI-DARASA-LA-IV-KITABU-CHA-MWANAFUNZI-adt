import json
import re
from pathlib import Path

from lxml import etree, html


root = Path(__file__).resolve().parents[1]
page = root / "pg127_sec001.html"
texts_path = root / "content/i18n/sw-TZ/texts.json"
ids_path = root / "content/page128-content-audio-ids.json"
texts = json.loads(texts_path.read_text(encoding="utf-8"))

updates = {
    "pg127_n0007": "Unaweza kutumia rangi kutengeneza miundo kwenye ukuta kama ilivyooneshwa au ilivyobainishwa katika Kazi ya kufanya namba 3.",
    "pg127_n0015": "Chagua zana ya mstatili kwa kubofya kwenye zana ya pembenne ‘Rectangle’.",
    "pg127_n0016": "Angalia au chunguza Kielelezo namba 13.",
}
for text_id, value in updates.items():
    texts[text_id] = value
    easy_id = f"{text_id}_easy_read"
    if easy_id in texts:
        texts[easy_id] = value
texts_path.write_text(json.dumps(texts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

tree = html.fromstring(page.read_text(encoding="utf-8-sig"))
for text_id, value in updates.items():
    node = tree.xpath(f'//*[@data-id="{text_id}"]')[0]
    node.text = value

# Ensure adjacent sentences render with visible spaces.
for paragraph in tree.xpath('//p[.//*[@data-id="pg127_n0004"]] | //p[.//*[@data-id="pg127_n0015"]]'):
    spans = paragraph.xpath('./span[@data-id]')
    for span in spans[:-1]:
        span.tail = " "

page.write_text(
    etree.tostring(tree, encoding="unicode", method="html", doctype="<!DOCTYPE html>"),
    encoding="utf-8",
)

pattern = re.compile(r"\bRectangle\b", re.I)
audio_ids = {
    text_id for text_id, value in texts.items() if pattern.search(str(value))
}
audio_ids.update(updates)
audio_ids.update(f"{text_id}_easy_read" for text_id in updates if f"{text_id}_easy_read" in texts)
ids_path.write_text(json.dumps(sorted(audio_ids), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print({"updated": sorted(updates), "audio_ids": len(audio_ids)})
