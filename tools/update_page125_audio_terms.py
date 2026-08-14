import json
from pathlib import Path

from lxml import etree, html


root = Path(__file__).resolve().parents[1]
page = root / "pg124_sec001.html"
texts_path = root / "content/i18n/sw-TZ/texts.json"
ids_path = root / "content/page125-audio-term-ids.json"
texts = json.loads(texts_path.read_text(encoding="utf-8"))

updates = {
    "pg124_n0004": "Angalia au Chagua ‘PNG picture’.",
    "pg124_n0005": "Pia, unaweza kuchagua ‘JPEG picture’ au ‘BMP picture’.",
    "pg124_n0006": "Chunguza Kielelezo namba 9(a).",
    "pg124_n0004_easy_read": "Angalia au Chagua ‘PNG picture’.",
    "pg124_n0005_easy_read": "Pia, unaweza kuchagua ‘JPEG picture’ au ‘BMP picture’.",
    "pg124_n0006_easy_read": "Chunguza Kielelezo namba 9(a).",
}
texts.update(updates)
texts_path.write_text(json.dumps(texts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

tree = html.fromstring(page.read_text(encoding="utf-8-sig"))
for text_id, value in updates.items():
    if text_id.endswith("_easy_read"):
        continue
    nodes = tree.xpath(f'//*[@data-id="{text_id}"]')
    if nodes and len(nodes[0]) == 0:
        nodes[0].text = value

page.write_text(
    etree.tostring(tree, encoding="unicode", method="html", doctype="<!DOCTYPE html>"),
    encoding="utf-8",
)

audio_ids = sorted(set(updates) | {
    "pg124_n0013", "pg124_n0013_easy_read",
    "pg124_im001_audio_desc", "pg124_im002_audio_desc",
})
ids_path.write_text(json.dumps(audio_ids, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print({"updated_text_ids": len(updates), "audio_ids": len(audio_ids)})
