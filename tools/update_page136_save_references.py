import json
from pathlib import Path

from lxml import etree, html


root = Path(__file__).resolve().parents[1]
page = root / "pg135_sec001.html"
texts_path = root / "content/i18n/sw-TZ/texts.json"
ids_path = root / "content/page136-save-reference-audio-ids.json"
texts = json.loads(texts_path.read_text(encoding="utf-8"))
updates = {
    "pg135_n0007": "Chagua ‘Hifadhi kwa kompyuta yako’ kama inavyoonekana au inavyobainishwa kwenye Kielelezo namba 25.",
    "pg135_n0013": "Kisanduku cha ‘Save As’ kitajitokeza kama inavyoonekana au inavyobainishwa katika Kielelezo namba 26.",
}
ids = set()
for text_id, value in updates.items():
    texts[text_id] = value
    ids.add(text_id)
    easy_id = f"{text_id}_easy_read"
    if easy_id in texts:
        texts[easy_id] = value
        ids.add(easy_id)
texts_path.write_text(json.dumps(texts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

tree = html.fromstring(page.read_text(encoding="utf-8-sig"))
for text_id, value in updates.items():
    tree.xpath(f'//*[@data-id="{text_id}"]')[0].text = value
page.write_text(
    etree.tostring(tree, encoding="unicode", method="html", doctype="<!DOCTYPE html>"),
    encoding="utf-8",
)
ids_path.write_text(json.dumps(sorted(ids), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print({"updated": sorted(ids)})
