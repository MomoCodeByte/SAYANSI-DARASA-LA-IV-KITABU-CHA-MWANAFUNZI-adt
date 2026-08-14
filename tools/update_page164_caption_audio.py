import json
import re
from pathlib import Path

from lxml import etree, html


root = Path(__file__).resolve().parents[1]
page_path = root / "pg164_sec001.html"
texts_path = root / "content/i18n/sw-TZ/texts.json"
ids_path = root / "content/page164-citybus-audio-ids.json"

tree = html.fromstring(page_path.read_text(encoding="utf-8-sig"))
nodes = tree.xpath('//*[@data-id="pg164_n0004"]')
if len(nodes) != 1:
    raise RuntimeError(f"Expected one caption, found {len(nodes)}")
node = nodes[0]
node.text = None
for child in list(node):
    node.remove(child)
strong = etree.SubElement(node, "strong")
strong.text = "Kielelezo namba 63:"
strong.tail = " "
emphasis = etree.SubElement(node, "em")
emphasis.text = "bloku ya ikiwa basi imeungwa kwa mara ya pili."
page_path.write_text(
    etree.tostring(tree, encoding="unicode", method="html", doctype="<!DOCTYPE html>"),
    encoding="utf-8",
)

texts = json.loads(texts_path.read_text(encoding="utf-8"))
pattern = re.compile(r"\bCity\s+Bus\b", re.IGNORECASE)
ids = sorted(
    text_id
    for text_id, value in texts.items()
    if text_id.startswith("pg164_")
    and isinstance(value, str)
    and pattern.search(value)
)
if not ids:
    raise RuntimeError("No page 164 City Bus text IDs found")
ids_path.write_text(json.dumps(ids, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print({"caption": "pg164_n0004", "audio_ids": ids})
