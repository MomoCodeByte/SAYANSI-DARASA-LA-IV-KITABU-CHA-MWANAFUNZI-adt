import json, re
from pathlib import Path
from lxml import html, etree

ROOT = Path(__file__).resolve().parents[1]
TEXT_PATH = ROOT / "content/i18n/sw-TZ/texts.json"
texts = json.loads(TEXT_PATH.read_text(encoding="utf-8-sig"))
changed_ids = set()
changed_pages = []

blank_captions = {
    "pg040_n0033": "Kielelezo namba 3 kinaonesha/kinabainisha mgonjwa wa tetekuwanga.",
    "pg084_n0017": "Kielelezo namba 1 kinaonesha/kinabainisha namna joto linavyosafiri.",
    "pg101_n0033": "Kielelezo namba 9 kinaonesha/kinabainisha namna mwanga unavyotengeneza kivuli.",
}

for path in sorted(ROOT.glob("pg*_sec*.html")):
    doc = html.fromstring(path.read_text(encoding="utf-8"))
    dirty = False

    for node in doc.xpath('//*[@data-id]'):
        key = node.get("data-id")
        shown = " ".join("".join(node.itertext()).split())

        # General suggestion 1: every requirements block in chapters 3-6
        # explicitly includes assistive software.
        if shown.startswith("Mahitaji:") and "programu saidizi" not in shown.lower():
            if shown == "Mahitaji:":
                new = "Mahitaji: Programu saidizi na vifaa vifuatavyo:"
            else:
                rest = shown[len("Mahitaji:"):].strip()
                new = f"Mahitaji: Programu saidizi, {rest}"
            node.text = new
            for child in list(node): node.remove(child)
            texts[key] = new; changed_ids.add(key); dirty = True
            shown = new

        # General suggestions 9 and 13: every caption must explain/bainisha.
        if re.match(r"^Kielelezo (?:namba|na\.)\s*\d+", shown, re.I) and not re.search(r"kinaonesha|kinabainisha", shown, re.I):
            if key in blank_captions:
                new = blank_captions[key]
            else:
                m = re.match(r"^(Kielelezo (?:namba|na\.)\s*[^:]+):?\s*(.*)$", shown, re.I)
                if not m:
                    continue
                label, desc = m.group(1), m.group(2).strip().rstrip(".")
                if not desc:
                    desc = "maudhui yaliyo katika picha"
                desc = desc[0].lower() + desc[1:] if desc else desc
                new = f"{label} kinaonesha/kinabainisha {desc}."
            node.text = new
            for child in list(node): node.remove(child)
            texts[key] = new; changed_ids.add(key); dirty = True

        # General suggestion 7: accessible Quorum descriptions for every
        # illustration in chapter six. Image IDs are read by Rehema.
        if path.name.startswith(tuple(f"pg{n:03d}" for n in range(118, 165))) and node.tag == "img":
            alt = " ".join((node.get("alt") or texts.get(key, "")).split())
            if alt and not alt.lower().startswith("maelezo ya programu fikivu ya quorum"):
                new_alt = f"Maelezo ya programu fikivu ya Quorum: {alt}"
                node.set("alt", new_alt)
                texts[key] = new_alt; changed_ids.add(key); dirty = True

    if dirty:
        path.write_text(etree.tostring(doc, encoding="unicode", method="html", doctype="<!DOCTYPE html>"), encoding="utf-8")
        changed_pages.append(path.name)

TEXT_PATH.write_text(json.dumps(texts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
(ROOT / "content/general-suggestions-updated-ids.json").write_text(
    json.dumps(sorted(changed_ids), ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)
print({"changed_pages": len(changed_pages), "changed_ids": len(changed_ids)})
