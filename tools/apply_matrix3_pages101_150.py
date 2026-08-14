from pathlib import Path
import json, re
from lxml import html, etree

ROOT = Path(__file__).resolve().parents[1]
TEXTS = ROOT / "content/i18n/sw-TZ/texts.json"
texts = json.loads(TEXTS.read_text(encoding="utf-8"))
AUDIO_MAP = ROOT / "content/i18n/sw-TZ/audios.json"
audios = json.loads(AUDIO_MAP.read_text(encoding="utf-8"))

replacements = {
    "pg102_n0023": "Je, unatambua nini kuhusu umbo la kivuli kutokana na Kielelezo namba 10?",
    "pg104_n0017": "Mahitaji: Bakuli angavu au bika, maji safi ndani ya jagi, penseli, programu saidizi na kipimajoto sauti.",
    "pg108_n0030": "Je, unasikia, kuhisi au kutambua nini?",
    "pg109_n0019": "Mahitaji: Ndoo, maji, kengele au kitu chochote kinachoweza kutoa sauti, na programu saidizi.",
    "pg110_n0020": "Je, unasikia, kuhisi au kutambua nini?",
    "pg110_n0030": "Mahitaji: Kipande kirefu cha chuma, meza, rula, saa ya mtetemo na programu saidizi.",
    "pg111_n0013": "Muulize alichosikia, alichohisi au alichotambua, kisha uandike jibu lake.",
    "pg117_n0070": "Ombwe",
}

append_after = {}

def clean_mojibake(s: str) -> str:
    # Repair only the common mangled smart quotes, without guessing other content.
    s = re.sub(r"(?:Ãƒ|Ã¢|Â|â)[^A-Za-z0-9<]{1,80}(?=[A-Za-z])", "‘", s)
    return s

changed = []
for n in range(100, 151):
    path = ROOT / f"pg{n:03d}_sec001.html"
    if not path.exists():
        continue
    doc = html.fromstring(path.read_text(encoding="utf-8"))
    dirty = False
    for did, new_text in replacements.items():
        found = doc.xpath(f'//*[@data-id="{did}"]')
        el = found[0] if found else None
        if el is not None and " ".join(el.text_content().split()) != new_text:
            el.text = new_text
            for child in list(el): el.remove(child)
            texts[did] = new_text
            dirty = True
    for anchor_id, (did, desc) in append_after.items():
        af = doc.xpath(f'//*[@data-id="{anchor_id}"]')
        anchor = af[0] if af else None
        if anchor is not None and not doc.xpath(f'//*[@data-id="{did}"]'):
            p = etree.Element("p", {"data-id": did, "class": "matrix-audio-description mt-3 rounded-lg bg-sky-50 p-3 text-[0.95rem] leading-relaxed"})
            p.text = desc
            base = anchor.getparent() if anchor.tag == "img" else anchor
            base.addnext(p)
            texts[did] = desc
            dirty = True
        if anchor is not None:
            texts[did] = desc
            audios.setdefault(did, f"{did}.mp3")
    # Image descriptions must be available to Rehema, not only to visual alt text.
    for img in doc.xpath('//img[@data-id][@alt]'):
        alt = (img.get("alt") or "").strip()
        if alt and len(alt) > 12:
            texts[img.get("data-id")] = alt
    # Inclusive terminology requested throughout this batch.
    for el in doc.xpath('//*[@data-id]'):
        value = " ".join("".join(el.itertext()).split())
        if value and el.get("data-id") in texts:
            audios.setdefault(el.get("data-id"), f'{el.get("data-id")}.mp3')
        new = value
        if 130 <= n <= 150:
            new = re.sub(r"\bTazama\b", "Chunguza", new)
            new = re.sub(r"\btazama\b", "chunguza", new)
        if new != value and len(el) == 0:
            el.text = new
            texts[el["data-id"]] = new
            dirty = True
    # Ensure the latest duplicate-submit and read-aloud runtime is used.
    output = etree.tostring(doc, encoding="unicode", method="html", doctype="<!DOCTYPE html>")
    newer = re.sub(r"assets/matrix-accessibility\.js(?:\?v=[^\"']*)?", "assets/matrix-accessibility.js?v=matrix3-78", output)
    if newer != output:
        output = newer
        dirty = True
    if dirty:
        path.write_text(output, encoding="utf-8")
        changed.append(path.name)

# Correct scientific meaning explicitly, preserving the existing heading.
p = ROOT / "pg117_sec001.html"
doc = html.fromstring(p.read_text(encoding="utf-8"))
hf = doc.xpath('//*[@data-id="pg117_n0070"]')
heading = hf[0] if hf else None
if heading is not None:
    targets = heading.xpath('following::p[1]')
    target = targets[0] if targets else None
    definition = "Nafasi isiyo na mada, hivyo haina hewa wala kitu kingine kinachoweza kusafirisha sauti."
    if target is not None and "Nafasi isiyo na mada" not in target.text_content():
        target.text = definition
        for child in list(target): target.remove(child)
        if target.get("data-id"):
            texts[target.get("data-id")] = definition
        p.write_text(etree.tostring(doc, encoding="unicode", method="html", doctype="<!DOCTYPE html>"), encoding="utf-8")
        if p.name not in changed: changed.append(p.name)

TEXTS.write_text(json.dumps(texts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
AUDIO_MAP.write_text(json.dumps(audios, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"Updated {len(changed)} HTML pages")
print("\n".join(changed))
