from pathlib import Path

from lxml import etree, html


root = Path(__file__).resolve().parents[1]
page_path = root / "pg162_sec001.html"
captions = {
    "pg162_n0006": ("Kielelezo namba 60:", "bloku za elekeza kwa mwelekeo na songa hatua zikiwa zimeungwa."),
    "pg162_n0014": ("Kielelezo namba 61:", "bloku ya ikiwa basi imeungwa kwa mara ya pili."),
}

tree = html.fromstring(page_path.read_text(encoding="utf-8-sig"))
for text_id, (label, description) in captions.items():
    nodes = tree.xpath(f'//*[@data-id="{text_id}"]')
    if len(nodes) != 1:
        raise RuntimeError(f"Expected one node for {text_id}, found {len(nodes)}")
    node = nodes[0]
    node.set("class", node.get("class", "").replace(" italic", ""))
    node.text = None
    for child in list(node):
        node.remove(child)
    strong = etree.SubElement(node, "strong")
    strong.text = label
    strong.tail = " "
    emphasis = etree.SubElement(node, "em")
    emphasis.text = description

page_path.write_text(
    etree.tostring(tree, encoding="unicode", method="html", doctype="<!DOCTYPE html>"),
    encoding="utf-8",
)
print({"bold_captions": sorted(captions)})
