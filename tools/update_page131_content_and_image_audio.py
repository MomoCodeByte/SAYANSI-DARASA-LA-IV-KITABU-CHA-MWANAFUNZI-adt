import json
import re
from pathlib import Path

from lxml import etree, html


root = Path(__file__).resolve().parents[1]
page = root / "pg130_sec001.html"
lang = root / "content/i18n/sw-TZ"
texts_path = lang / "texts.json"
audios_path = lang / "audios.json"
timecodes_path = lang / "timecode/timecode_output.json"
ids_path = root / "content/page131-content-audio-ids.json"

texts = json.loads(texts_path.read_text(encoding="utf-8"))
updates = {
    "pg130_n0004": "Usimbaji ni kuandika maelekezo kwenye kompyuta ili kufanya kazi maalum.",
    "pg130_n0005": "Katika sura hii utasimba kwa kutumia programu ya Scratch au Quorum.",
    "pg130_n0006": "Programu ya Scratch au Quorum inatumia lugha ya programu ya bloku kurahisisha uundaji wa michezo sahili.",
    "pg130_n0007": "Programu hii inaweza kupakuliwa kutoka https: au scratch au Quorum.mit.edu au download",
    "pg130_n0023": "Bofya au tumia mishale kwenye kitufe cha ‘Window’ kama inavyoonekana au inavyobainishwa kwenye Kielelezo namba 18.",
    "pg130_im001_audio_desc": "Maelezo ya picha: Menyu ya Windows imefunguliwa. Mshale namba moja unaelekeza kitufe cha Windows. Mshale namba mbili unaelekeza programu ya Scratch 3 iliyoandikwa Scratch 3, New.",
    "pg130_im002_audio_desc": "Maelezo ya picha: Sehemu ya utafutaji ya Windows ina maneno Scratch 3. Mshale namba moja unaelekeza sehemu ilipoandikwa Scratch 3. Mshale namba mbili unaelekeza programu ya Scratch 3 katika matokeo ya utafutaji.",
}

for text_id, value in updates.items():
    texts[text_id] = value
    easy_id = f"{text_id}_easy_read"
    if easy_id in texts and not text_id.endswith("_audio_desc"):
        texts[easy_id] = value

# This validator instruction must not appear or play as textbook content.
texts.pop("pg130_n0030", None)
texts_path.write_text(json.dumps(texts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

tree = html.fromstring(page.read_text(encoding="utf-8-sig"))
for node in tree.xpath('//*[@data-id="pg130_n0030"]'):
    node.getparent().remove(node)
for text_id, value in updates.items():
    nodes = tree.xpath(f'//*[@data-id="{text_id}"]')
    if nodes and len(nodes[0]) == 0:
        nodes[0].text = value
for paragraph in tree.xpath('//p[.//*[@data-id="pg130_n0004"]]'):
    spans = paragraph.xpath('./span[@data-id]')
    for span in spans[:-1]:
        span.tail = " "
page.write_text(
    etree.tostring(tree, encoding="unicode", method="html", doctype="<!DOCTYPE html>"),
    encoding="utf-8",
)

for json_path in (audios_path, timecodes_path):
    data = json.loads(json_path.read_text(encoding="utf-8"))
    data.pop("pg130_n0030", None)
    json_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

pattern = re.compile(r"\bhttps\b", re.I)
audio_ids = {text_id for text_id, value in texts.items() if pattern.search(str(value))}
audio_ids.update(updates)
audio_ids.update(
    f"{text_id}_easy_read" for text_id in updates
    if f"{text_id}_easy_read" in texts
)
ids_path.write_text(json.dumps(sorted(audio_ids), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print({"removed_visible_id": "pg130_n0030", "updated_ids": len(updates), "audio_ids": len(audio_ids)})
