import json
from pathlib import Path

from lxml import etree, html


ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "pg120_sec001.html"
LANG = ROOT / "content/i18n/sw-TZ"

REPAIRS = {
    "pg120_n0020": "Bofya au tumia mishale kwenye kitufe cha ‘Windows Start’ kama inavyoonesha au inavyobainishwa katika Kielelezo namba 3.",
    "pg120_n0023": "Andika ‘Paint au Quorum’ katika upau wa utafutaji.",
    "pg120_n0026": "Bofya au tumia mishale kwenye ‘Paint au Quorum’.",
    "pg120_im001": (
        "Maelezo ya picha: Skrini ya Windows 11 inaonesha hatua tatu za kufungua programu ya Paint au Quorum. "
        "Namba 1 inaonesha upau wa utafutaji chini ya skrini. Namba 2 inaonesha neno Paint lililoandikwa "
        "kwenye upau wa utafutaji. Namba 3 inaonesha programu ya Paint iliyochaguliwa kwenye matokeo ya utafutaji."
    ),
}


def main():
    tree = html.fromstring(PAGE.read_text(encoding="utf-8-sig"))
    for text_id, clean_text in REPAIRS.items():
        nodes = tree.xpath(f'//*[@data-id="{text_id}"]')
        if not nodes:
            raise RuntimeError(f"Missing {text_id}")
        node = nodes[0]
        if node.tag.lower() == "img":
            node.set("alt", clean_text)
        else:
            node.text = clean_text

    PAGE.write_text(
        etree.tostring(tree, encoding="unicode", method="html", doctype="<!DOCTYPE html>"),
        encoding="utf-8",
    )

    texts_path = LANG / "texts.json"
    texts = json.loads(texts_path.read_text(encoding="utf-8"))
    texts.update(REPAIRS)
    texts_path.write_text(json.dumps(texts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    ids_path = ROOT / "content/page121-encoding-repair-audio-ids.json"
    ids_path.write_text(json.dumps(sorted(REPAIRS), indent=2) + "\n", encoding="utf-8")
    print({"repaired_ids": sorted(REPAIRS)})


if __name__ == "__main__":
    main()
