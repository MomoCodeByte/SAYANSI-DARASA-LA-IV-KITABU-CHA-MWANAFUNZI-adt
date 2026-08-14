import json
from pathlib import Path

from lxml import etree, html


root = Path(__file__).resolve().parents[1]
page_path = root / "pg157_sec001.html"
texts_path = root / "content/i18n/sw-TZ/texts.json"
ids_path = root / "content/page157-diagram-audio-ids.json"
updates = {
    "pg157_n0006": "15. Unaweza kuanza kucheza mchezo wako kwa kutumia vitufe vya ‘kwenda juu’, ‘kwenda chini’, ‘kwenda kushoto’ na ‘kwenda kulia’ vilivyopo katika kibodi ya kompyuta yako.",
    "pg157_n0009": "Je, umeweza kumpeleka ‘Sprite’ pande ngapi?",
    "pg157_n0011": "17. Unaweza kuongeza hatua katika bloku ya ‘songa hatua’, kisha ukacheza tena mchezo.",
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

image = tree.xpath('//*[@data-id="pg157_im002"]')[0]
image.set("src", "images/pg157_im002_v49.png")
page_path.write_text(
    etree.tostring(tree, encoding="unicode", method="html", doctype="<!DOCTYPE html>"),
    encoding="utf-8",
)
ids_path.write_text(json.dumps(sorted(audio_ids), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print({"updated": sorted(audio_ids), "image": image.get("src")})
