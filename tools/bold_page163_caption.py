from pathlib import Path

from lxml import etree, html


root = Path(__file__).resolve().parents[1]
page_path = root / "pg163_sec001.html"
tree = html.fromstring(page_path.read_text(encoding="utf-8-sig"))
nodes = tree.xpath('//*[@data-id="pg163_n0010"]')
if len(nodes) != 1:
    raise RuntimeError(f"Expected one caption, found {len(nodes)}")
node = nodes[0]
node.set("class", node.get("class", "").replace(" italic", ""))
node.text = None
for child in list(node):
    node.remove(child)
strong = etree.SubElement(node, "strong")
strong.text = "Kielelezo namba 62:"
strong.tail = " "
emphasis = etree.SubElement(node, "em")
emphasis.text = "bloku ya ikiwa basi imeungwa kwa mara ya pili."
page_path.write_text(
    etree.tostring(tree, encoding="unicode", method="html", doctype="<!DOCTYPE html>"),
    encoding="utf-8",
)
print("pg163_n0010 updated")
