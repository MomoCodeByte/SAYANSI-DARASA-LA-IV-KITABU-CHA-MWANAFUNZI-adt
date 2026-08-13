import json
from pathlib import Path
from lxml import html, etree

ROOT = Path(__file__).resolve().parents[1]
TEXT_PATH = ROOT / "content/i18n/sw-TZ/texts.json"
texts = json.loads(TEXT_PATH.read_text(encoding="utf-8-sig"))

updates = {
    "pg102_n0017": "Kielelezo namba 10 kinaonesha kutokea kwa vivuli.",
    "pg103_n0008": "Kielelezo namba 11 kinaonesha kutokea kwa taswira katika kioo bapa.",
    "pg104_n0011": "Kielelezo namba 12 kinaonesha matokeo ya kupinda kwa miale ya mwanga.",
    "pg107_n0005": "Chunguza Kielelezo namba 13 kinachoonesha vitendo vya kutoa sauti.",
    "pg107_n0013": "Kielelezo namba 13 kinaonesha vitendo vya kutoa sauti.",
    "pg108_n0030": "Je, unasikia, unahisi au unatambua nini?",
    "pg109_n0002": "Kielelezo namba 14 kinaonesha mwangwi unavyotokea.",
    "pg109_n0019": "Mahitaji: Ndoo, maji, kengele au kitu chochote kinachoweza kutoa sauti na programu saidizi.",
    "pg110_n0002": "Kielelezo namba 15 kinaonesha kusafiri kwa sauti katika maji.",
    "pg110_n0020": "Je, unasikia, unahisi au unatambua nini? Andika matokeo.",
    "pg110_n0030": "Mahitaji: Kipande kirefu cha chuma, meza, rula, saa ya mtetemo na programu saidizi.",
    "pg111_n0007": "Kielelezo namba 16 kinaonesha kusafiri kwa sauti kwenye chuma.",
    "pg111_n0013": "Muulize mwenzako anachosikia, anachohisi au anachotambua, kisha andika jibu.",
    "pg111_n0019": "Andika unachosikia, unachohisi au unachotambua.",
    "pg112_n0015": "Chunguza Kielelezo namba 17(b).",
    "pg112_n0021": "Kielelezo namba 17 kinaonesha baadhi ya vifaa vinavyotumia nishati ya sauti.",
    "pg113_n0014": "Kielelezo namba 18 kinaonesha matumizi ya nishati ya mwanga, sauti na joto.",
    "pg119_n0006": "Kielelezo namba 1 kinaonesha mifano ya miundo.",
    "pg119_n0016": "Kielelezo namba 2 kinaonesha maumbo tofauti yaliyopangiliwa kimantiki kuwa muundo.",
    "pg120_n0028": "Kielelezo namba 3 kinaonesha kufungua programu ya Paint/Quorum.",
    "pg121_n0005": "Kielelezo namba 4 kinaonesha vipengele vya programu ya Paint/Quorum.",
    "pg121_n0015": "Kielelezo namba 5 kinaonesha kuchagua zana ya pembetatu mraba.",
    "pg122_n0012": "Kielelezo namba 6 kinaonesha kuchora umbo la pembetatu mraba.",
    "pg122_n0014": "Kielelezo namba 7 kinaonesha pembetatu mraba inayounda mteremko.",
    "pg123_n0015": "Kielelezo namba 8 kinaonesha pembetatu mraba na maduara.",
    "pg124_n0006": "Chunguza Kielelezo namba 9(a).",
    "pg124_n0018": "Kielelezo namba 9(a) kinaonesha hatua za awali za kuhifadhi kazi yako.",
    "pg124_n0020": "Kielelezo namba 9(b) kinaonesha hatua za mwisho za kuhifadhi kazi yako.",
    "pg125_n0021": "Kielelezo namba 10 kinaonesha hatua za kupaka rangi maumbo.",
    "pg126_n0002": "Kielelezo namba 11 kinaonesha pembetatu mraba iliyopakwa rangi nyekundu.",
    "pg126_n0015": "Kielelezo namba 12 kinaonesha pembetatu mraba na maduara yaliyopakwa rangi.",
    "pg127_n0016": "Chunguza Kielelezo namba 13.",
    "pg127_n0018": "Kielelezo namba 13 kinaonesha kuchagua umbo la mstatili.",
    "pg127_n0023": "Kielelezo namba 14 kinaonesha tabaka la kwanza la ukuta.",
}

# Replace damaged visible strings from the clean language map too.
for key in ("pg103_n0004", "pg103_n0005", "pg120_n0020", "pg124_n0004", "pg124_n0005",
            "pg124_n0009", "pg124_n0013", "pg124_n0016"):
    updates.setdefault(key, texts[key])

texts.update(updates)
changed = []
for page_no in range(101, 128):
    path = ROOT / f"pg{page_no:03d}_sec001.html"
    if not path.exists():
        continue
    doc = html.fromstring(path.read_text(encoding="utf-8"))
    dirty = False
    for key, value in updates.items():
        if not key.startswith(f"pg{page_no:03d}_"):
            continue
        for node in doc.xpath(f'//*[@data-id="{key}"]'):
            if node.tag == "img":
                if node.get("alt") != value:
                    node.set("alt", value); dirty = True
            elif "".join(node.itertext()).strip() != value:
                for child in list(node): node.remove(child)
                node.text = value; dirty = True

    # Page 112 contained the opening paragraph twice.
    if page_no == 112:
        nodes = doc.xpath('//*[@data-id="pg112_n0007"]')
        if len(nodes) > 1:
            duplicate_parent = nodes[0].getparent()
            duplicate_parent.getparent().remove(duplicate_parent)
            dirty = True

    # Matrix requires visible Kiswahili choices, not unexplained T/F or 1/2.
    if page_no == 115:
        for div in doc.xpath('//div[contains(@class,"after:content-")]'):
            label = div.getparent()
            hidden = label.xpath('.//span[contains(@class,"sr-only")]/text()')
            if hidden:
                div.attrib["class"] = "min-w-[110px] rounded-full border border-slate-300 bg-white/80 px-4 py-2 text-center font-semibold transition-colors peer-checked:bg-blue-500 peer-checked:text-white peer-focus:ring-2 peer-focus:ring-blue-400 peer-focus:ring-offset-2"
                div.text = hidden[0].strip().capitalize()
                dirty = True
    if page_no == 116:
        for label in doc.xpath('//label[contains(@class,"activity-option")]')[:2]:
            inp = label.xpath('.//input[@aria-label]')
            target = label.xpath('.//div[contains(@class,"flex-grow")]')
            if inp and target and not target[0].xpath('./span[contains(@class,"matrix-choice-label")]'):
                span = etree.Element("span", {"class": "matrix-choice-label block text-xl font-semibold text-gray-800"})
                span.text = inp[0].get("aria-label")
                target[0].insert(0, span); dirty = True

    if dirty:
        path.write_text(etree.tostring(doc, encoding="unicode", method="html", doctype="<!DOCTYPE html>"), encoding="utf-8")
        changed.append(path.name)

TEXT_PATH.write_text(json.dumps(texts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("updated", len(changed), "pages", changed)
