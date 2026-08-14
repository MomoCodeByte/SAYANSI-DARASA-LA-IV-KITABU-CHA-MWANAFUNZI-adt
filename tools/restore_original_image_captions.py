import json
import re
from pathlib import Path

from lxml import etree, html


ROOT = Path(__file__).resolve().parents[1]
TEXTS_PATH = ROOT / "content/i18n/sw-TZ/texts.json"
IDS_PATH = ROOT / "content/original-image-caption-audio-ids.json"
PATTERN = re.compile(
    r"(Kielelezo\s+namba\s+\d+(?:\s*\([a-z]\))?)\s+"
    r"kina(?:onesha|onyesha)\s+(?:au|/)\s+kinabainisha\s+"
    r"(?:na\s+kinaeleza\s+)?",
    re.IGNORECASE,
)


def classes(node):
    return set((node.get("class") or "").split())


def has_class_fragment(node, fragment):
    return any(fragment in item for item in classes(node))


def is_image_caption(node):
    if node.tag.lower() == "figcaption":
        return True
    ancestors = list(node.iterancestors())[:3]
    for ancestor in [node, *ancestors]:
        if has_class_fragment(ancestor, "text-center"):
            return True
        if ancestor.xpath("./img"):
            return True
    parent = node.getparent()
    if parent is not None and parent.xpath(".//img"):
        compact = " ".join(parent.text_content().split())
        if len(compact) <= 350:
            return True
    if has_class_fragment(node, "italic") or has_class_fragment(node, "font-medium"):
        for previous in list(node.itersiblings(preceding=True))[:2]:
            if previous.xpath("self::img | .//img"):
                return True
    return False


def simplify(value):
    return PATTERN.sub(r"\1: ", value)


def main():
    texts = json.loads(TEXTS_PATH.read_text(encoding="utf-8"))
    changed_ids = set()
    changed_pages = []

    for page in sorted(ROOT.glob("pg*_sec*.html")):
        tree = html.fromstring(page.read_text(encoding="utf-8-sig"))
        dirty = False
        for node in tree.xpath('//*[@data-id]'):
            if len(node) or not is_image_caption(node):
                continue
            current = " ".join(node.text_content().split())
            updated = simplify(current)
            if updated == current:
                continue
            text_id = node.get("data-id")
            node.text = updated
            texts[text_id] = updated
            changed_ids.add(text_id)
            easy_id = f"{text_id}_easy_read"
            if easy_id in texts:
                easy_updated = simplify(str(texts[easy_id]))
                if easy_updated != texts[easy_id]:
                    texts[easy_id] = easy_updated
                    changed_ids.add(easy_id)
            dirty = True
        if dirty:
            page.write_text(
                etree.tostring(tree, encoding="unicode", method="html", doctype="<!DOCTYPE html>"),
                encoding="utf-8",
            )
            changed_pages.append(page.name)

    TEXTS_PATH.write_text(json.dumps(texts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    IDS_PATH.write_text(json.dumps(sorted(changed_ids), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print({"changed_pages": changed_pages, "changed_ids": len(changed_ids)})


if __name__ == "__main__":
    main()
