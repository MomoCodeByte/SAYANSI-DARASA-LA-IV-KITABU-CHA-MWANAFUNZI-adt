"""Add answer fields to genuine static response prompts in canonical book pages."""

from pathlib import Path
from lxml import html, etree

ROOT = Path(__file__).resolve().parents[1]

# One field per learner response. Pure procedural steps are intentionally absent.
TARGETS = {
    "pg008_sec001.html": ["pg008_n0024"],
    "pg009_sec001.html": ["pg009_n0011", "pg009_n0014"],
    "pg015_sec001.html": ["pg015_n0009"],
    "pg019_sec001.html": ["pg019_n0035"],
    "pg023_sec001.html": ["pg023_n0021", "pg023_n0022"],
    "pg025_sec001.html": ["pg025_n0016", "pg025_n0018"],
    "pg026_sec001.html": ["pg026_n0021"],
    "pg060_sec001.html": ["pg060_n0016", "pg060_n0020"],
    "pg061_sec001.html": ["pg061_n0035", "pg061_n0039", "pg061_n0042"],
    "pg063_sec001.html": ["pg063_n0008"],
    "pg074_sec001.html": ["pg074_n0007", "pg074_n0011"],
    "pg076_sec001.html": ["pg076_n0033", "pg076_n0038", "pg076_n0041"],
    "pg082_sec001.html": ["pg082_n0013", "pg082_n0016", "pg082_n0019", "pg082_n0022", "pg082_n0025", "pg082_n0028", "pg082_n0031"],
    "pg085_sec001.html": ["pg085_n0004", "pg085_n0013"],
    "pg086_sec001.html": ["pg086_n0030", "pg086_n0034"],
    "pg087_sec001.html": ["pg087_n0023"],
    "pg098_sec001.html": ["pg098_n0004", "pg098_n0014", "pg098_n0017", "pg098_n0020"],
    "pg099_sec001.html": ["pg099_n0017", "pg099_n0025", "pg099_n0030"],
    "pg100_sec001.html": ["pg100_n0018", "pg100_n0021"],
    "pg102_sec001.html": ["pg102_n0003", "pg102_n0023", "pg102_n0026"],
    "pg103_sec001.html": ["pg103_n0031", "pg103_n0032"],
    "pg117_sec001.html": ["pg117_n0006", "pg117_n0009", "pg117_n0012", "pg117_n0015", "pg117_n0018", "pg117_n0021", "pg117_n0024"],
    "pg119_sec001.html": ["pg119_fix_n0010"],
    "pg120_sec001.html": ["pg120_n0004"],
    "pg129_sec001.html": ["pg129_n0004"],
    "pg134_sec001.html": ["pg134_n0012"],
    "pg138_sec001.html": ["pg138_n0007"],
    "pg140_sec001.html": ["pg140_n0004"],
    "pg146_sec001.html": ["pg146_n0005"],
    "pg149_sec001.html": ["pg149_n0007", "pg149_n0014"],
}

FIELD_CLASS = (
    "mt-3 block w-full rounded-md border border-sky-400 bg-white px-3 py-2 "
    "min-h-20 resize-y focus:outline-none focus:ring-2 focus:ring-sky-300"
)


def response_container(node):
    current = node
    if current.tag == "span" and current.getparent() is not None:
        current = current.getparent()
    parent = current.getparent()
    if parent is not None and parent.tag == "div":
        classes = parent.get("class", "")
        if any(token in classes for token in ("flex", "grid", "items-start")):
            current = parent
    return current


changed = []
inserted_total = 0
for filename, ids in TARGETS.items():
    path = ROOT / filename
    source = path.read_text(encoding="utf-8-sig")
    doctype = "<!DOCTYPE html>\n" if source.lstrip().lower().startswith("<!doctype html") else ""
    document = html.document_fromstring(source)
    inserted = 0
    for data_id in ids:
        nodes = document.xpath(f'//*[@data-id="{data_id}"]')
        if not nodes:
            raise RuntimeError(f"Missing {data_id} in {filename}")
        node = nodes[0]
        container = response_container(node)
        parent = container.getparent()
        if parent is None:
            raise RuntimeError(f"No insertion parent for {data_id} in {filename}")
        existing = parent.xpath(f'.//textarea[@data-response-for="{data_id}"]')
        if existing:
            continue
        field = etree.Element("textarea")
        field.set("class", FIELD_CLASS)
        field.set("data-response-for", data_id)
        field.set("data-aria-id", f"aria-response-{data_id}")
        field.set("aria-label", f"Sehemu ya kujibu: {''.join(node.itertext()).strip()[:120]}")
        field.set("tabindex", "0")
        parent.insert(parent.index(container) + 1, field)
        inserted += 1
    if inserted:
        sections = document.xpath('//*[@data-section-type]')
        if sections and not sections[0].get("data-section-type", "").startswith("activity_"):
            sections[0].set("data-section-type", "activity_open_ended_answer")
        rendered = html.tostring(document, encoding="unicode", method="html", pretty_print=False)
        if doctype and not rendered.lstrip().lower().startswith("<!doctype html"):
            rendered = doctype + rendered
        path.write_text(rendered, encoding="utf-8")
        changed.append({"file": filename, "fields": inserted})
        inserted_total += inserted

print({"changed_pages": len(changed), "inserted_fields": inserted_total, "pages": changed})
