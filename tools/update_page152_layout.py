import json
from pathlib import Path

from lxml import etree, html


root = Path(__file__).resolve().parents[1]
page_path = root / "pg152_sec001.html"
texts_path = root / "content/i18n/sw-TZ/texts.json"
ids_path = root / "content/page152-layout-audio-ids.json"
updates = {
    "pg152_n0003": "Kielelezo namba 45: programu kwa ajili ya kishale juu na kishale chini.",
    "pg152_n0005": "Cheza mchezo wako kwa kutumia kitufe cha kwenda juu na kitufe cha kwenda chini.",
    "pg152_n0006": "Vitufe hivi vinapatikana katika kibodi cha kompyuta yako.",
    "pg152_n0007": "Je, umeona na kusikia nini?",
    "pg152_n0009": "Katika bloku ya ‘songa hatua’, badilisha kutoka hatua 10 kwenda hatua 50.",
    "pg152_n0011": "Badilisha bloku ya ‘zunguka digrii’, badilisha kutoka digrii 10 kwenda digrii 30.",
    "pg152_n0013": "Kisha rudia kucheza mchezo wako kwa kutumia vitufe vya kwenda juu na kwenda chini.",
    "pg152_n0014": "Je, nini utofauti wa matokeo unayoyaona au uliyoyabaini sasa na yale uliyoyaona au uliyoyabaini kabla ya kubadilisha hatua na digrii?",
    "pg152_im002_audio_desc": "Maelezo ya picha: Programu ya kishale juu ina bloku ya songa hatua kumi na bloku ya kucheza sauti hadi ikamilike. Programu ya kishale chini ina bloku ya zunguka digrii kumi na tano na bloku ya kucheza sauti hadi ikamilike.",
}

texts = json.loads(texts_path.read_text(encoding="utf-8"))
audio_ids = set()
for text_id, value in updates.items():
    texts[text_id] = value
    audio_ids.add(text_id)
    easy_id = f"{text_id}_easy_read"
    if easy_id in texts:
        texts[easy_id] = value
        audio_ids.add(easy_id)
texts_path.write_text(json.dumps(texts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

tree = html.fromstring(page_path.read_text(encoding="utf-8-sig"))
for text_id, value in updates.items():
    nodes = tree.xpath(f'//*[@data-id="{text_id}"]')
    if len(nodes) != 1:
        raise RuntimeError(f"Expected one node for {text_id}, found {len(nodes)}")
    nodes[0].text = value

image = tree.xpath('//*[@data-id="pg152_im002"]')[0]
image.set("src", "images/pg152_im002_v44.png")
image.set("alt", updates["pg152_im002_audio_desc"])

responses = {
    "pg152_n0007": "Sehemu ya kujibu: Je, umeona na kusikia nini?",
    "pg152_n0014": "Sehemu ya kujibu: Eleza utofauti wa matokeo baada ya kubadilisha hatua na digrii.",
}
for response_id, label in responses.items():
    candidates = tree.xpath(f'//*[@data-response-for="{response_id}"]')
    if not candidates:
        question = tree.xpath(f'//*[@data-id="{response_id}"]')[0]
        container = question.getparent().getparent()
        candidates = container.xpath('./textarea')
    if len(candidates) != 1:
        raise RuntimeError(f"Expected one response for {response_id}, found {len(candidates)}")
    candidates[0].set("data-response-for", response_id)
    candidates[0].set("aria-label", label)

page_path.write_text(
    etree.tostring(tree, encoding="unicode", method="html", doctype="<!DOCTYPE html>"),
    encoding="utf-8",
)
ids_path.write_text(json.dumps(sorted(audio_ids), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print({"updated": sorted(audio_ids)})
