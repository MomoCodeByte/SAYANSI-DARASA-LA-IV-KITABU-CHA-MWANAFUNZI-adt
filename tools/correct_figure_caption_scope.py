import json
import re
from pathlib import Path

from lxml import etree, html


ROOT = Path(__file__).resolve().parents[1]
TEXTS_PATH = ROOT / "content/i18n/sw-TZ/texts.json"
CHANGED_PATH = ROOT / "content/simplified-figure-caption-ids.json"
AUDIO_IDS_PATH = ROOT / "content/figure-caption-scope-audio-ids.json"
COLON_PATTERN = re.compile(r"^(Kielelezo\s+namba\s+[^:]+):\s+", re.IGNORECASE)
SPECIAL_EXPLAINS = {"pg007_n0024", "pg016_n0006"}


def classes(node):
    return set((node.get("class") or "").split())


def has_class_fragment(node, fragment):
    return any(fragment in item for item in classes(node))


def is_caption(node):
    if node.tag.lower() == "figcaption":
        return True
    ancestors = list(node.iterancestors())[:2]
    for ancestor in [node, *ancestors]:
        if has_class_fragment(ancestor, "text-center"):
            return True
    if has_class_fragment(node, "italic"):
        previous = node.getprevious()
        if previous is not None and previous.xpath("self::img | .//img"):
            return True
    parent = node.getparent()
    if parent is not None and parent.xpath(".//img"):
        compact_text = " ".join(parent.text_content().split())
        if len(compact_text) <= 300:
            return True
    return False


def restore(text_id, value):
    connector = " kinaonesha au kinabainisha"
    if text_id in SPECIAL_EXPLAINS:
        connector += " na kinaeleza"
    return COLON_PATTERN.sub(rf"\1{connector} ", value, count=1)


def main():
    candidate_ids = set(json.loads((ROOT / "content/figure-caption-scope-audio-ids.json").read_text(encoding="utf-8")))
    candidate_ids.update({"pg121_n0003_easy_read", "pg143_n0026_easy_read"})
    texts = json.loads(TEXTS_PATH.read_text(encoding="utf-8"))
    caption_ids = set()
    restored_ids = set()

    for page in sorted(ROOT.glob("pg*_sec*.html")):
        tree = html.fromstring(page.read_text(encoding="utf-8-sig"))
        dirty = False
        for node in tree.xpath('//*[@data-id]'):
            text_id = node.get("data-id")
            if text_id not in candidate_ids:
                continue
            if is_caption(node):
                caption_ids.add(text_id)
                continue
            current = " ".join(node.text_content().split())
            restored = restore(text_id, current)
            if restored != current and len(node) == 0:
                node.text = restored
                texts[text_id] = restored
                restored_ids.add(text_id)
                dirty = True
        if dirty:
            page.write_text(
                etree.tostring(tree, encoding="unicode", method="html", doctype="<!DOCTYPE html>"),
                encoding="utf-8",
            )

    unresolved = candidate_ids - caption_ids - restored_ids
    AUDIO_IDS_PATH.write_text(
        json.dumps(sorted(caption_ids | restored_ids), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    CHANGED_PATH.write_text(
        json.dumps(sorted(caption_ids), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    TEXTS_PATH.write_text(
        json.dumps(texts, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print({
        "caption_ids": len(caption_ids),
        "restored_content_ids": len(restored_ids),
        "unresolved_ids": sorted(unresolved),
    })


if __name__ == "__main__":
    main()
