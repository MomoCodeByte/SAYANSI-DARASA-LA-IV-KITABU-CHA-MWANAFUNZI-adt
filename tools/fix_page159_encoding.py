import json
from pathlib import Path

from lxml import etree, html


root = Path(__file__).resolve().parents[1]
page_path = root / "pg159_sec001.html"
texts_path = root / "content/i18n/sw-TZ/texts.json"
ids_path = root / "content/page159-encoding-audio-ids.json"
updates = {
    "pg159_n0002": "Kielelezo namba 55: baada ya kuongeza ‘Sprite’ wa pili.",
    "pg159_n0005": "Kumwondoa ‘Sprite’ mmoja, bofya au tumia mishale kwenye Sprite ‘Cat’ kisha bofya au tumia mishale alama ya kufuta kama inavyoonekana katika Kielelezo namba 56.",
    "pg159_n0008": "Kielelezo namba 56: kumwondoa ‘Sprite’ ‘Cat’.",
    "pg159_n0011": "Baada ya hapo, utabaki na ‘Sprite’ mmoja anayeitwa ‘City Bus’ kama inavyoonekana katika Kielelezo namba 57.",
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
