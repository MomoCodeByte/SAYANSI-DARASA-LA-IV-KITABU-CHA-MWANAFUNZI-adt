import json
from pathlib import Path
from lxml import html, etree

ROOT = Path(__file__).resolve().parents[1]
TEXT_PATH = ROOT / "content/i18n/sw-TZ/texts.json"
texts = json.loads(TEXT_PATH.read_text(encoding="utf-8-sig"))

updates = {
    "pg128_n0002": "Kielelezo namba 15 kinaonesha tabaka la kwanza la ukuta lililopakwa rangi.",
    "pg128_n0005": "Kielelezo namba 16 kinaonesha na kubainisha tabaka la pili la ukuta juu ya tabaka la kwanza.",
    "pg128_n0007": "Kielelezo namba 16 kinaonesha tabaka la kwanza na la pili la ukuta.",
    "pg128_n0012": "Kielelezo namba 17 kinaonesha ukuta uliokamilika wenye matabaka sita.",
    "pg130_n0029": "Kielelezo namba 18 kinaonesha hatua za kufungua programu ya Scratch/Quorum.",
    "pg131_n0012": "Kielelezo namba 19 kinaonesha programu ya Scratch/Quorum.",
    "pg131_n0018": "Kielelezo namba 20 kinaonesha kuchagua lugha ya Kiswahili katika Scratch/Quorum.",
    "pg132_n0007": "Kielelezo namba 21 kinaonesha sehemu za programu ya Scratch/Quorum.",
    "pg133_n0014": "Kielelezo namba 22 kinaonesha kuhamisha bloku ya ‘wakati inapobonyezwa’ kwenda eneo la kuandikia kwa kuburuta au kutumia mishale.",
    "pg134_n0002": "Kielelezo namba 23 kinaonesha kuburuta na kuunganisha bloku.",
    "pg134_n0007": "Kielelezo namba 24 kinaonesha namna ya kucheza mchezo wa kujongea.",
    "pg135_n0010": "Kielelezo namba 25 kinaonesha hatua za awali za kuhifadhi kazi yako kwenye kompyuta.",
    "pg135_n0016": "Kielelezo namba 26 kinaonesha hatua za mwisho za kuhifadhi kazi kwenye kompyuta.",
    "pg136_n0038": "Kielelezo namba 27 kinaonesha bloku ya zunguka digrii iliyounganishwa na bloku ya wakati inapobonyezwa.",
    "pg137_n0035": "Kielelezo namba 28 kinaonesha kuunganisha bloku ya enda mahali popote na bloku ya wakati inapobonyezwa.",
    "pg139_n0009": "Kielelezo namba 29 kinaonesha kuunganisha bloku mbalimbali za mwendo.",
    "pg139_n0016": "Kielelezo namba 30 kinaonesha programu iliyokamilika.",
    "pg140_n0028": "Kielelezo namba 31 kinaonesha kuunda programu ya sauti.",
    "pg141_n0005": "Kielelezo namba 32 kinaonesha bloku ya ‘cheza sauti’ iliyounganishwa na bloku ya ‘wakati inapobonyezwa’.",
    "pg142_n0011": "Kielelezo namba 33 kinaonesha mlolongo katika usimbaji.",
    "pg143_n0019": "Kielelezo namba 34 kinaonesha kutumia bloku ya rudia katika mchezo.",
    "pg143_n0026": "Chunguza Kielelezo namba 35 kinachoonesha namna ya kufanya.",
    "pg144_n0002": "Kielelezo namba 35 kinaonesha kuhamisha bloku ya sauti ndani ya bloku ya rudia.",
    "pg144_n0007": "Kielelezo namba 36 kinaonesha programu ya kucheza sauti inayojirudia.",
    "pg130_im001": "Sehemu ya kwanza inaonesha namna ya kutafuta Scratch/Quorum katika orodha ya programu za kompyuta.",
    "pg130_im002": "Sehemu ya pili inaonesha namna ya kutafuta Scratch/Quorum kwa kuandika jina lake ikiwa haipo kwenye orodha.",
    "pg137_im003": "Skrini ya Scratch/Quorum inaonesha bloku ya ‘enda mahali popote’ ikiunganishwa chini ya bloku ya ‘wakati inapobonyezwa’.",
}

texts.update(updates)
changed = []
for path in sorted(ROOT.glob("pg1??_sec001.html")):
    page_no = int(path.stem[2:5])
    if not 128 <= page_no <= 150:
        continue
    doc = html.fromstring(path.read_text(encoding="utf-8"))
    dirty = False

    # Restore clean source strings to leaf nodes; this removes mojibake while
    # retaining the page's layout and interactive structure.
    for node in doc.xpath('//*[@data-id]'):
        key = node.get("data-id")
        value = updates.get(key, texts.get(key))
        if value is None:
            continue
        if node.tag == "img":
            if key in updates and node.get("alt") != value:
                node.set("alt", value); dirty = True
        elif not node.xpath('.//*[@data-id]') and "".join(node.itertext()).strip() != value:
            for child in list(node): node.remove(child)
            node.text = value; dirty = True

    if dirty:
        path.write_text(etree.tostring(doc, encoding="unicode", method="html", doctype="<!DOCTYPE html>"), encoding="utf-8")
        changed.append(path.name)

TEXT_PATH.write_text(json.dumps(texts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("updated", len(changed), "pages", changed)
