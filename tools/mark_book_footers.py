"""Mark printed production footers so they keep a small, consistent type size."""

import re
from pathlib import Path

from lxml import html


ROOT = Path(__file__).resolve().parents[1]
STAMP = re.compile(
    r"SAYANSI\s+DARASA\s+LA\s+IV|\.indd\b|"
    r"\b\d{1,2}/\d{1,2}/\d{4}\b|FOR\s+ONLINE\s+READING\s+ONLY",
    re.IGNORECASE,
)


def add_class(node, name: str) -> None:
    classes = node.get("class", "").split()
    if name not in classes:
        classes.append(name)
        node.set("class", " ".join(classes))


changed = 0
marked = 0
for path in sorted(ROOT.glob("*.html")):
    source = path.read_text(encoding="utf-8-sig")
    doctype = "<!DOCTYPE html>\n" if source.lstrip().lower().startswith("<!doctype html") else ""
    document = html.document_fromstring(source)
    page_marked = 0
    for node in document.xpath('//*[@data-id]'):
        text = " ".join(node.itertext()).strip()
        if not STAMP.search(text):
            continue
        node.set("aria-hidden", "true")
        add_class(node, "book-production-footer-text")
        parent = node.getparent()
        if parent is not None:
            add_class(parent, "book-production-footer")
        page_marked += 1
    if page_marked:
        rendered = html.tostring(document, encoding="unicode", method="html", pretty_print=False)
        if doctype and not rendered.lstrip().lower().startswith("<!doctype html"):
            rendered = doctype + rendered
        path.write_text(rendered, encoding="utf-8")
        changed += 1
        marked += page_marked

print({"changed_pages": changed, "marked_footer_items": marked})
