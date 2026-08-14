import json
import re
from pathlib import Path

from lxml import etree, html


root = Path(__file__).resolve().parents[1]
texts_path = root / "content/i18n/sw-TZ/texts.json"
ids_path = root / "content/remove-bainishwa-audio-ids.json"
pattern = re.compile(r"\s+au\s+(?:inavyobainishwa|zinazobainishwa)", re.IGNORECASE)

texts = json.loads(texts_path.read_text(encoding="utf-8"))
audio_ids = set()
for text_id, value in list(texts.items()):
    if not isinstance(value, str):
        continue
    cleaned = pattern.sub("", value)
    if cleaned != value:
        texts[text_id] = cleaned
        audio_ids.add(text_id)

caption_updates = {
    "pg156_n0010": "Kielelezo namba 51: programu iliyotolewa nakala na kubadilishwa.",
    "pg156_n0011": "nyuzi na hatua.",
}
for text_id, value in caption_updates.items():
    texts[text_id] = value
    audio_ids.add(text_id)
    easy_id = f"{text_id}_easy_read"
    if easy_id in texts:
        texts[easy_id] = value
        audio_ids.add(easy_id)

texts_path.write_text(json.dumps(texts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

changed_files = []
for page_path in root.glob("*.html"):
    if page_path.name.startswith("preview-"):
        continue
    source = page_path.read_text(encoding="utf-8-sig")
    cleaned = pattern.sub("", source)
    if cleaned != source:
        page_path.write_text(cleaned, encoding="utf-8")
        changed_files.append(page_path.name)

page156 = root / "pg156_sec001.html"
tree = html.fromstring(page156.read_text(encoding="utf-8-sig"))
for text_id, value in caption_updates.items():
    nodes = tree.xpath(f'//*[@data-id="{text_id}"]')
    if len(nodes) != 1:
        raise RuntimeError(f"Expected one node for {text_id}, found {len(nodes)}")
    nodes[0].text = value
page156.write_text(
    etree.tostring(tree, encoding="unicode", method="html", doctype="<!DOCTYPE html>"),
    encoding="utf-8",
)
if page156.name not in changed_files:
    changed_files.append(page156.name)

ids_path.write_text(json.dumps(sorted(audio_ids), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print({"changed_files": len(changed_files), "audio_ids": len(audio_ids)})
