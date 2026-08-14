import json
from pathlib import Path

from lxml import etree, html


root = Path(__file__).resolve().parents[1]
page_path = root / "pg150_sec001.html"
texts_path = root / "content/i18n/sw-TZ/texts.json"
ids_path = root / "content/page150-steps-audio-ids.json"
updates = {
    "pg150_n0009": "Kisha iunganishe bloku ya ‘songa hatua’ kwenye bloku ya ‘wakati kitufe cha kinapobonyezwa’ kama inavyoonekana au inavyobainishwa katika Kielelezo namba 43.",
    "pg150_n0017": "Kisha unganisha bloku hiyo kwenye bloku ya ‘songa hatua’ kama inavyoonekana au inavyobainishwa katika Kielelezo namba 43.",
    "pg150_n0030": "Buruta na dondosha bloku ya ‘wakati kitufe cha kinapobonyezwa’ kwenye eneo la kuandikia kama inavyoonekana au inavyobainishwa katika Kielelezo namba 44.",
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

# Preserve readable spacing where consecutive spans form one numbered instruction.
for text_id in ("pg150_n0008", "pg150_n0016", "pg150_n0030", "pg150_n0031"):
    nodes = tree.xpath(f'//*[@data-id="{text_id}"]')
    if nodes:
        nodes[0].tail = " "

page_path.write_text(
    etree.tostring(tree, encoding="unicode", method="html", doctype="<!DOCTYPE html>"),
    encoding="utf-8",
)
ids_path.write_text(json.dumps(sorted(audio_ids), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print({"updated": sorted(audio_ids)})
