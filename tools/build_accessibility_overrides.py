"""Build reviewed screen-reader supplements requested by the validation report."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

FIGURE_DESCRIPTIONS = {
    3: "Hatua za kufungua Paint: bofya Start au sehemu ya kutafutia, andika Paint, kisha chagua programu ya Paint. Kwa ufikivu, Quorum inaweza kutumiwa kama programu mbadala.",
    4: "Dirisha la programu lina sehemu za penseli, kifutio, rangi, brashi, maumbo na eneo la kuchorea. Mtumiaji wa kisoma skrini anaweza kutumia zana zinazolingana katika Quorum.",
    5: "Zana ya pembetatu mraba ipo katika sehemu ya maumbo; mshale unaelekeza mahali pa kuichagua.",
    6: "Mshale wa kipanya unawekwa katika eneo la kuchora, kisha unaburutwa kuelekea upande mwingine ili kuunda pembetatu mraba.",
    7: "Pembetatu mraba ina upande mmoja wa mteremko uliooneshwa kwa mshale mwekundu.",
    8: "Mchoro una pembetatu ya mteremko na miduara mitatu yenye ukubwa tofauti juu yake.",
    9: "Hatua za kuhifadhi kazi: chagua Faili, Hifadhi kama, aina ya picha, andika jina la faili, kisha chagua Hifadhi.",
    10: "Zana ya kujaza rangi na rangi zilizochaguliwa zinaelekezwa kwa mishale katika sehemu ya juu ya programu.",
    11: "Pembetatu mraba imejazwa rangi nyekundu.",
    12: "Pembetatu mraba nyekundu ina duara dogo la njano, duara la kati la zambarau na duara kubwa la pinki kwenye mteremko.",
    13: "Zana ya mstatili imechaguliwa kutoka katika sehemu ya maumbo.",
    14: "Tabaka la kwanza la ukuta lina matofali sita ya mstatili yaliyopangwa kwa upana.",
    15: "Matofali ya ukuta yamepangwa kwa mistari na kupakwa rangi za kijivu na njano.",
    16: "Tabaka nyingine za matofali zinaongezwa kwa kuiga, kubandika na kupanga mistatili.",
    17: "Ukuta uliokamilika una matofali yaliyopangwa kwa mpangilio wa rangi unaojirudia.",
    18: "Kufungua Scratch au Quorum: bonyeza Start, tafuta programu kwa jina, kisha uichague kutoka kwenye matokeo.",
    19: "Dirisha la Scratch lina bloku upande wa kushoto, eneo la kuandikia katikati, na jukwaa lenye Sprite upande wa kulia.",
    20: "Menyu ya lugha imefunguliwa na chaguo la Kiswahili limeoneshwa.",
    21: "Sehemu kuu ni bloku, eneo la kuandikia, jukwaa, orodha ya Sprite na aikoni ya kuchagua Sprite.",
    22: "Menyu ya Matukio imechaguliwa na bloku ya kuanza inaburutwa kwenda eneo la kuandikia.",
    23: "Bloku ya Mwendo ya kusonga hatua inaunganishwa chini ya bloku ya kuanza.",
    24: "Bendera ya kijani inaanzisha mchezo; Sprite huanza kusonga kwa idadi ya hatua iliyowekwa.",
    25: "Katika menyu ya Faili, chaguo la kuhifadhi kazi kwenye kompyuta limeoneshwa.",
}


def main() -> None:
    texts = json.loads((ROOT / "content/i18n/sw-TZ/texts.json").read_text(encoding="utf-8-sig"))
    overrides: dict[str, dict[str, object]] = {}
    for page in range(118, 169):
        key = f"{page:03d}"
        page_text = " ".join(
            value for item_id, value in texts.items()
            if item_id.startswith(f"pg{key}_") and isinstance(value, str)
        )
        supplements = [
            "Dokezo la ufikivu: mwanafunzi anayetumia kibodi au kisoma skrini anaweza kutumia Quorum kama programu fikivu mbadala, akiongozwa na mwalimu au mwezeshaji."
        ]
        for figure, description in FIGURE_DESCRIPTIONS.items():
            if re.search(rf"Kielelezo\s+namba\s+{figure}\b", page_text, flags=re.IGNORECASE):
                supplements.append(f"Maelezo fikivu ya Kielelezo namba {figure}: {description}")
        for caption in re.finditer(r"Kielelezo\s+namba\s+(\d+)\s*:\s*([^|.]{3,180})", page_text, flags=re.IGNORECASE):
            figure = int(caption.group(1))
            if figure in FIGURE_DESCRIPTIONS:
                continue
            description = caption.group(2).strip()
            generic = f"Maelezo fikivu ya Kielelezo namba {figure}: Kielelezo kinabainisha {description}."
            if generic not in supplements:
                supplements.append(generic)
        overrides[key] = {"supplements": supplements}

    mapping_path = ROOT / "content" / "validation-matrix-mapping.json"
    mapping = json.loads(mapping_path.read_text(encoding="utf-8"))
    matrix_supplements = 0
    for row in mapping["rows"]:
        pages = row.get("mapped_pdf_pages", [])
        category = row.get("category")
        joined = f'{row.get("issue", "")} {row.get("recommendation", "")}'.lower()
        supplement = None
        if category == "assistive_technology" and "quorum" not in joined:
            tools = ["programu saidizi inayolingana na kifaa cha mwanafunzi"]
            if "kipima joto" in joined or "kipimajoto" in joined:
                tools.append("kipimajoto chenye sauti")
            if "saa ya mtetemo" in joined:
                tools.append("saa yenye mtetemo")
            supplement = "Mahitaji ya ufikivu: " + ", pamoja na ".join(tools) + "."
        elif category == "inclusive_language":
            supplement = (
                "Maelekezo jumuishi: chunguza kwa kutumia njia inayokufaa, kwa mfano kuona, "
                "kusikiliza, kugusa, kuhisi, kupima au kueleza kwa msaada wa kifaa saidizi."
            )
        elif category == "figure_description":
            supplement = (
                "Maelezo fikivu ya kielelezo: kielelezo kinaonesha au kinabainisha jambo linalozungumziwa. "
                "Chunguza kwa kuona, kusikiliza maelezo, kugusa au kuhisi kwa kutumia njia inayokufaa."
            )
        if supplement:
            for page in pages:
                key = f"{int(page):03d}"
                entry = overrides.setdefault(key, {"supplements": []})
                if supplement not in entry["supplements"]:
                    entry["supplements"].append(supplement)
                    matrix_supplements += 1

    target = ROOT / "content" / "accessibility-overrides.json"
    target.write_text(json.dumps(overrides, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    described = sum(len(item["supplements"]) - 1 for item in overrides.values())
    print(f"Built overrides for {len(overrides)} pages; {described} figure descriptions; {matrix_supplements} matrix supplements")


if __name__ == "__main__":
    main()
