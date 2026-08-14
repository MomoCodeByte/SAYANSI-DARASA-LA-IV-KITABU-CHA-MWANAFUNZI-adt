import json
from pathlib import Path

from lxml import etree, html


root = Path(__file__).resolve().parents[1]
page_path = root / "pg149_sec001.html"
texts_path = root / "content/i18n/sw-TZ/texts.json"
ids_path = root / "content/page149-steps-audio-ids.json"
updates = {
    "pg149_n0007": "Je, nini umesikia, umeona au umehisi katika hatua hii?",
    "pg149_n0014": "Je, umesikia, umeona au umehisi nini katika hatua hii?",
    "pg149_n0027": "Buruta na dondosha bloku ya ‘wakati kitufe cha kinapobonyezwa’ kwenye eneo la kuandikia kama inavyoonekana au kinavyobainishwa katika Kielelezo namba 42.",
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

aria_updates = {
    "pg149_n0007": "Sehemu ya kujibu: Je, nini umesikia, umeona au umehisi katika hatua hii?",
    "pg149_n0014": "Sehemu ya kujibu: Je, umesikia, umeona au umehisi nini katika hatua hii?",
}
for response_id, label in aria_updates.items():
    nodes = tree.xpath(f'//*[@data-response-for="{response_id}"]')
    if nodes:
        nodes[0].set("aria-label", label)

page_path.write_text(
    etree.tostring(tree, encoding="unicode", method="html", doctype="<!DOCTYPE html>"),
    encoding="utf-8",
)
ids_path.write_text(json.dumps(sorted(audio_ids), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print({"updated": sorted(audio_ids)})
