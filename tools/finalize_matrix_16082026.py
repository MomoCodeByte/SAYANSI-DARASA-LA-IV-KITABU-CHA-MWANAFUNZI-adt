"""Final deterministic cleanup for the 16-08-2026 Sayansi review matrix."""

from __future__ import annotations

import json
import re
from pathlib import Path

from lxml import etree, html


ROOT = Path(__file__).resolve().parents[1]
LANG = ROOT / "content/i18n/sw-TZ"
TEXTS_PATH = LANG / "texts.json"

# Matrix pages containing audio/content observations. Keeping the list here
# also makes the exact TTS regeneration scope reproducible.
MATRIX_REFERENCE_PAGES = {
    7, 23, 24, 26, 27, 31, 32, 33, 37, 40, 45, 51, 52, 54, 57,
    59, 61, 62, 63, 66, 68, 69, 73, 82, 83, 84, 85, 88, 90, 93,
    94, 95, 98, 99, 101, 102, 103, 104, 108, 109, 110, 113, 114,
    117, 118, 119, 121, 134,
}
MATRIX_PAGES = MATRIX_REFERENCE_PAGES | {number - 1 for number in MATRIX_REFERENCE_PAGES}

TEXT_REPAIRS = {
    # Suggested inclusive wording must be visible as well as spoken.
    "pg051_n0018": (
        "Endelea kuchunguza mabuu, kisha andika unachokiona au unachokigusa "
        "kwa kuongozwa na maswali yafuatayo:"
    ),
    "pg100_n0018": "Je, umeona au umehisi nini?",
    "pg100_n0021": "Weka kumbukumbu ya kile unachokiona au unachokihisi.",
    "pg101_n0016": "Je, umeona au umehisi nini?",
    "pg101_n0022": "Angalia au gusa chini ya meza na kiti.",
    "pg101_n0023": "Je, unaona au unahisi nini?",
    "pg101_n0028": "Je, unaona au unahisi nini?",
    "pg101_n0031": (
        "Andika matokeo ya unachokiona au unachokihisi katika hatua ya 1, 3 na 4."
    ),
    "pg101_n0033": "Kielelezo namba 9.",
    "pg133_im001": (
        "Maelezo ya programu fikivu ya Quorum: Menyu ya Matukio imechaguliwa "
        "kwenye Scratch au Quorum. Bloku ya ‘wakati inapobonyezwa’ inaburutwa "
        "au inahamishwa kwa mishale na kuwekwa kwenye eneo la kuandikia."
    ),
    "pg133_im001_audio_desc": (
        "Maelezo ya picha: Menyu ya Matukio imechaguliwa kwenye Scratch au Quorum. "
        "Bloku ya ‘wakati inapobonyezwa’ inaburutwa au inahamishwa kwa mishale na "
        "kudondoshwa kwenye eneo la kuandikia."
    ),
    "pg134_im001": (
        "Maelezo ya programu fikivu ya Quorum: Chagua bloku ya Mwendo ya ‘songa "
        "hatua 10’ na uiweke chini ya bloku ya kuanza. Unaweza kubadilisha namba "
        "10 kuwa idadi nyingine ya hatua."
    ),
    "pg134_im001_audio_desc": (
        "Maelezo ya picha: Bloku ya Mwendo ‘songa hatua 10’ imeunganishwa chini ya "
        "bloku ya kuanza. Namba 10 inaweza kubadilishwa kuwa idadi nyingine ya hatua."
    ),
    "pg136_im001": (
        "Maelezo ya programu fikivu ya Quorum: Bloku ya ‘wakati bendera ya kijani "
        "inapobonyezwa’ imeunganishwa na bloku ya ‘zunguka digrii 15’. Namba ya "
        "digrii inaweza kubadilishwa."
    ),
    "pg136_im002": (
        "Maelezo ya programu fikivu ya Quorum: Hatua za kutengeneza programu ya "
        "kumzungusha Sprite kwenye Scratch au Quorum. Chagua bloku za Matukio na "
        "Mwendo, kisha unganisha ‘wakati inapobonyezwa’ na ‘zunguka digrii 15’."
    ),
    "pg140_im001": (
        "Maelezo ya programu fikivu ya Quorum: Menyu ya Sauti imefunguliwa. Bloku "
        "ya ‘wakati inapobonyezwa’ imeunganishwa na bloku ya ‘cheza sauti Meow hadi "
        "ikamilike’. Namba 1, 2 na 3 zinaonesha hatua za kuunda programu ya sauti."
    ),
    "pg140_im001_audio_desc": (
        "Maelezo ya programu fikivu ya Quorum: Menyu ya Sauti imefunguliwa. Bloku "
        "ya ‘wakati inapobonyezwa’ imeunganishwa na bloku ya ‘cheza sauti Meow hadi "
        "ikamilike’. Namba 1, 2 na 3 zinaonesha hatua za kuunda programu ya sauti."
    ),
    "pg145_im001": (
        "Maelezo ya programu fikivu ya Quorum: Programu ya Scratch au Quorum ina "
        "bloku ya ‘wakati inapobonyezwa’ na ndani yake bloku ya ‘milele’ yenye amri "
        "ya kucheza sauti hadi ikamilike. Mshale unaonesha kitufe cha kusimamisha mchezo."
    ),
    "pg145_im001_audio_desc": (
        "Maelezo ya programu fikivu ya Quorum: Programu ya Scratch au Quorum ina "
        "bloku ya ‘wakati inapobonyezwa’ na ndani yake bloku ya ‘milele’ yenye amri "
        "ya kucheza sauti hadi ikamilike. Mshale unaonesha kitufe cha kusimamisha mchezo."
    ),
    "pg149_im001": (
        "Maelezo ya programu fikivu ya Quorum: Kwenye Scratch au Quorum, kitufe cha "
        "‘kishale juu’ kinapobonyezwa. Kwenye orodha, ‘kishale juu’ kimechaguliwa."
    ),
    "pg149_im001_audio_desc": (
        "Maelezo ya programu fikivu ya Quorum: Kwenye Scratch au Quorum, kitufe cha "
        "‘kishale juu’ kinapobonyezwa. Kwenye orodha, ‘kishale juu’ kimechaguliwa."
    ),
}


def main() -> None:
    texts = json.loads(TEXTS_PATH.read_text(encoding="utf-8"))
    texts.update(TEXT_REPAIRS)

    # The matrix requests removal of the redundant phrase while retaining the
    # visible heading and the actual list of required materials.
    material_pages = {51, 58, 60, 61, 62, 65, 67, 74, 77, 84, 87, 90, 97, 98, 101}
    for key, value in list(texts.items()):
        match = re.match(r"pg(\d{3})_", key)
        if not match or int(match.group(1)) not in material_pages or not isinstance(value, str):
            continue
        if value.strip().casefold() == "mahitaji: programu fikivu na vifaa vifuatavyo:".casefold():
            texts[key] = "Mahitaji:"
    TEXTS_PATH.write_text(
        json.dumps(texts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    synced_files: list[str] = []
    synced_nodes = 0
    # Sync fallback HTML with canonical i18n content. Only leaf nodes are
    # replaced, so semantic wrappers and interactive controls stay intact.
    for page in sorted(ROOT.glob("pg*_sec*.html")):
        number = int(page.name[2:5])
        tree = html.fromstring(page.read_text(encoding="utf-8-sig"))
        changed = False
        for node in tree.xpath('//*[@data-id]'):
            text_id = node.get("data-id")
            if text_id not in texts:
                continue
            canonical = str(texts[text_id])
            if node.tag.lower() == "img":
                if node.get("alt", "") != canonical:
                    node.set("alt", canonical)
                    changed = True
                    synced_nodes += 1
            elif len(node) == 0 and node.tag.lower() not in {"audio", "input", "textarea"}:
                if (node.text or "") != canonical:
                    node.text = canonical
                    changed = True
                    synced_nodes += 1
        if changed:
            page.write_text(
                etree.tostring(tree, encoding="unicode", method="html", doctype="<!DOCTYPE html>"),
                encoding="utf-8",
            )
            synced_files.append(page.name)

    audio_ids = sorted(
        key for key in texts
        if (match := re.match(r"pg(\d{3})_", key))
        and int(match.group(1)) in MATRIX_PAGES
        and not key.endswith("_easy_read")
    )
    ids_path = ROOT / "content/matrix-16082026-audio-ids.json"
    ids_path.write_text(json.dumps(audio_ids, indent=2) + "\n", encoding="utf-8")
    print({
        "text_repairs": len(TEXT_REPAIRS),
        "html_files_synced": len(synced_files),
        "html_nodes_synced": synced_nodes,
        "matrix_audio_ids": len(audio_ids),
    })


if __name__ == "__main__":
    main()
