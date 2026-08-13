from pathlib import Path
import json, re
from lxml import html, etree

root = Path(__file__).resolve().parents[1]
text_path = root / "content/i18n/sw-TZ/texts.json"
texts = json.loads(text_path.read_text(encoding="utf-8"))
changed = []

exact = {
    "pg007_n0024": "Kielelezo namba 1 kinaonesha/kinabainisha na kinaeleza mifano ya kanuni za afya.",
    "pg008_n0005": "Kielelezo namba 1 kinaonesha/kinabainisha uzingatiaji wa kanuni za afya.",
    "pg008_n0017": "Kielelezo namba 2 kinaonesha/kinabainisha mfano wa makundi makuu ya vyakula katika mlo kamili.",
    "pg011_n0014": "Kwa mfano, umeng’enywaji wa chakula na ufyonzwaji mzuri wa virutubisho kutoka kwenye vyakula.",
    "pg016_n0006": "Kielelezo namba 10 kinaonesha/kinabainisha na kinaeleza mlo kamili wa mgonjwa.",
}

for n in range(7, 17):
    p = root / f"pg{n:03d}_sec001.html"
    doc = html.fromstring(p.read_text(encoding="utf-8"))
    dirty = False
    for el in doc.xpath('//*[@data-id]'):
        did = el.get("data-id")
        old = " ".join(el.text_content().split())
        new = exact.get(did, old)
        if did not in exact and "Kielelezo namba" in old and ":" not in old and "kinaonesha" in old and "kinabainisha" not in old:
            new = old.replace("kinaonesha", "kinaonesha/kinabainisha", 1)
        if new != old and len(el) == 0:
            el.text = new
            texts[did] = new
            dirty = True
    if dirty:
        p.write_text(etree.tostring(doc, encoding="unicode", method="html", doctype="<!DOCTYPE html>"), encoding="utf-8")
        changed.append(p.name)

text_path.write_text(json.dumps(texts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("updated", len(changed), "pages", changed)
