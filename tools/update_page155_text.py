import json
from pathlib import Path

from lxml import etree, html


root = Path(__file__).resolve().parents[1]
page_path = root / "pg155_sec001.html"
texts_path = root / "content/i18n/sw-TZ/texts.json"
ids_path = root / "content/page155-text-audio-ids.json"
updates = {
    "pg155_n0002": "inavyoonekana au inavyobainishwa katika Kielelezo namba 49.",
    "pg155_n0004": "Kielelezo namba 49: programu ya kumfanya ‘Sprite’ aende juu.",
    "pg155_n0006": "10. Chagua ‘Toa Nakala Nyingine’, kisha peleka kipanya upande wa chini na ubofye kitufe cha kushoto mara moja.",
    "pg155_n0007": "Utakuwa umeunda program ya pili kwa kutoa nakala ya programu ya kwanza kama inavyoonekana au inavyobainishwa katika Kielelezo namba 50.",
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
page_path.write_text(
    etree.tostring(tree, encoding="unicode", method="html", doctype="<!DOCTYPE html>"),
    encoding="utf-8",
)
ids_path.write_text(json.dumps(sorted(audio_ids), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print({"updated": sorted(audio_ids)})
