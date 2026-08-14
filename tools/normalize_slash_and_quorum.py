"""Normalize reader-facing slash and Quorum wording across the complete ADT."""

import json
import re
from pathlib import Path
from lxml import etree, html

ROOT = Path(__file__).resolve().parents[1]
TEXTS_PATH = ROOT / "content" / "i18n" / "sw-TZ" / "texts.json"
UPDATED_PATH = ROOT / "content" / "slash-quorum-updated-ids.json"


def normalize(value: str) -> str:
    value = re.sub(r"\s*/\s*", " au ", value)
    return re.sub(r" {2,}", " ", value)


texts = json.loads(TEXTS_PATH.read_text(encoding="utf-8-sig"))
changed_ids = set()
changed_pages = []

for page in sorted(ROOT.glob("pg*_sec*.html")):
    tree = html.fromstring(page.read_text(encoding="utf-8-sig"))
    dirty = False
    for node in tree.xpath('//*[@data-id]'):
        key = node.get("data-id")
        before = " ".join(node.text_content().split())

        for element in node.iter():
            if element.text:
                new = normalize(element.text)
                if new != element.text:
                    element.text = new
                    dirty = True
            if element.tail:
                new = normalize(element.tail)
                if new != element.tail:
                    element.tail = new
                    dirty = True

        for attribute in ("alt", "aria-label", "title"):
            if node.get(attribute):
                new = normalize(node.get(attribute))
                if new != node.get(attribute):
                    node.set(attribute, new)
                    dirty = True

        after = " ".join(node.text_content().split())
        if node.tag == "img":
            after = node.get("alt") or after
        if after != before or normalize(str(texts.get(key, ""))) != str(texts.get(key, "")):
            texts[key] = normalize(after or str(texts.get(key, "")))
            changed_ids.add(key)

    if dirty:
        page.write_text(
            etree.tostring(tree, encoding="unicode", method="html", doctype="<!DOCTYPE html>"),
            encoding="utf-8",
        )
        changed_pages.append(page.name)

for key, value in list(texts.items()):
    new = normalize(str(value))
    if new != value:
        texts[key] = new
        changed_ids.add(key)
    if re.search(r"(?i)\bQuorum\b", new):
        changed_ids.add(key)

TEXTS_PATH.write_text(json.dumps(texts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
UPDATED_PATH.write_text(json.dumps(sorted(changed_ids), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print({"changed_pages": len(changed_pages), "changed_ids": len(changed_ids)})
