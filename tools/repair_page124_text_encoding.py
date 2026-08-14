import json
from pathlib import Path

from lxml import etree, html


root = Path(__file__).resolve().parents[1]
page = root / "pg123_sec001.html"
texts = json.loads((root / "content/i18n/sw-TZ/texts.json").read_text(encoding="utf-8"))
texts["pg123_n0019"] = "Kuhifadhi kazi yako kupitia programu ya ‘Paint au Quorum’, fuata hatua zifuatazo:"
if "pg123_n0019_easy_read" in texts:
    texts["pg123_n0019_easy_read"] = "Kuhifadhi kazi yako kupitia programu ya ‘Paint au Quorum’, fuata hatua zifuatazo:"
(root / "content/i18n/sw-TZ/texts.json").write_text(
    json.dumps(texts, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)
tree = html.fromstring(page.read_text(encoding="utf-8-sig"))
changed = []

for node in tree.xpath('//*[@data-id]'):
    text_id = node.get("data-id")
    if len(node) or node.tag.lower() in {"img", "audio"} or text_id not in texts:
        continue
    clean = str(texts[text_id])
    if (node.text or "") != clean:
        node.text = clean
        changed.append(text_id)

page.write_text(
    etree.tostring(tree, encoding="unicode", method="html", doctype="<!DOCTYPE html>"),
    encoding="utf-8",
)
print({"changed_ids": changed})
