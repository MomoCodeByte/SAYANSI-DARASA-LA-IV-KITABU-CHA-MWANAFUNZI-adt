import json
from pathlib import Path

from lxml import etree, html


root = Path(__file__).resolve().parents[1]
page_path = root / "pg148_sec001.html"
texts_path = root / "content/i18n/sw-TZ/texts.json"
ids_path = root / "content/page148-step11-audio-ids.json"
text_id = "pg148_n0014"
value = "Buruta na dondosha bloku ya ‘cheza sauti hadi ikamilike’ ndani ya bloku ya ‘ikiwa basi’ kama inavyoonekana au inavyobainishwa kwenye Kielelezo namba 40."

texts = json.loads(texts_path.read_text(encoding="utf-8"))
audio_ids = {text_id}
texts[text_id] = value
easy_id = f"{text_id}_easy_read"
if easy_id in texts:
    texts[easy_id] = value
    audio_ids.add(easy_id)
texts_path.write_text(json.dumps(texts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

tree = html.fromstring(page_path.read_text(encoding="utf-8-sig"))
nodes = tree.xpath(f'//*[@data-id="{text_id}"]')
if len(nodes) != 1:
    raise RuntimeError(f"Expected one node for {text_id}, found {len(nodes)}")
nodes[0].text = value
page_path.write_text(
    etree.tostring(tree, encoding="unicode", method="html", doctype="<!DOCTYPE html>"),
    encoding="utf-8",
)
(root / "content/page148-step11-audio-ids.json").write_text(
    json.dumps(sorted(audio_ids), ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)
print({"updated": sorted(audio_ids)})
