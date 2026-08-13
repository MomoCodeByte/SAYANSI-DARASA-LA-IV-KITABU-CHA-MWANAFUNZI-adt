"""Apply the highlighted validation-matrix corrections for printed pages 51-100."""

from __future__ import annotations

import json
import re
from pathlib import Path

from lxml import html


ROOT = Path(__file__).resolve().parents[1]

REPLACEMENTS = {
    "pg050_sec001.html": {
        "Lenzi ya mkononi, kipande cha nyama mbichi, karatasi ya plastiki, pini na sahani": "Lenzi ya mkononi, kipande cha nyama mbichi, karatasi ya plastiki, pini, sahani na programu saidizi",
        "Je, umeona nini?": "Je, umeona au umehisi nini?",
    },
    "pg051_sec001.html": {
        "(c) Je, umeviona viumbe gani vingine kwenye sahani?": "(c) Je, umeviona, umevigusa au umevihisi viumbe gani vingine kwenye sahani?",
        "Lenzi ya mkononi, maji yaliyotuama kwa mda mrefu, chupa au kifuu cha nazi na wavu wenye matundu madogo": "Lenzi ya mkononi, maji yaliyotuama kwa muda mrefu, chupa au kifuu cha nazi, wavu wenye matundu madogo na programu saidizi",
    },
    "pg052_sec001.html": {
        "1. Je, umeona nini wakati wa uchunguzi?": "1. Je, umeona au umehisi nini wakati wa uchunguzi?",
        "2. Chora mchoro wa hatua za ukuaji wa mbu.": "2. Chora au eleza hatua za ukuaji wa mbu.",
    },
    "pg058_sec001.html": {
        "Vipande sita vya barafu vyenye ukubwa sawa, sufuria, deli la kutunzia barafu, kitu chenye uso ulionyooka kama vile sinia, jagi na jiko au chanzo chochote cha moto": "Vipande sita vya barafu vyenye ukubwa sawa, sufuria, deli la kutunzia barafu, kitu chenye uso ulionyooka kama vile sinia, jagi, jiko au chanzo chochote cha moto na programu saidizi",
    },
    "pg059_sec001.html": {
        "Inamisha meza taratibu na chunguza matokeo.": "Inamisha meza taratibu na chunguza matokeo unayoyaona au unayoyahisi.",
    },
    "pg060_sec001.html": {
        "Jagi, sufuria, maji safi na salama, mfuko wa plastiki na kikombe safi": "Jagi, sufuria, maji safi na salama, mfuko wa plastiki, kikombe safi na programu saidizi",
    },
    "pg061_sec001.html": {
        "Maji, sufuria, kioo, kipimajoto na chanzo cha moto (jiko)": "Maji, sufuria, kioo, kipimajoto, chanzo cha moto (jiko) na programu saidizi",
        "Chunguza unachokiona maji yanapoanza kuchemka.": "Chunguza unachokiona au unachokihisi maji yanapoanza kuchemka.",
    },
    "pg062_sec001.html": {
        "Kioo, glasi, maji, birika na chanzo cha moto (jiko)": "Kioo, glasi, maji, birika, chanzo cha moto (jiko) na programu saidizi",
        "Chunguza kinachoonekana kwenye mdomo wa birika maji yanapoanza kuchemka.": "Chunguza kinachoonekana au unachohisi kwenye mdomo wa birika maji yanapoanza kuchemka.",
    },
    "pg063_sec001.html": {
        "Kielelezo namba 4 kinaonesha kubadilisha gesi kuwa kimiminika.": "Kielelezo namba 4 kinaonesha na kinabainisha kubadilisha gesi kuwa kimiminika.",
        "Chunguza kinachoonekana kwenye kioo.": "Chunguza kinachoonekana au unachohisi kwenye kioo.",
        "Hii inaonyesha kwamba mvuke": "Hii inaonesha kwamba mvuke",
        "Jaribio linaonyesha mchakato": "Jaribio linaonesha mchakato",
    },
    "pg065_sec001.html": {
        "Jokofu, meza, kipimajoto, maji na kikombe cha plastiki": "Jokofu, meza, kipimajoto, kipimajoto sauti, maji, kikombe cha plastiki na programu saidizi",
    },
    "pg067_sec001.html": {
        "Chanzo cha moto (jiko), maji, sufuria na kipimajoto": "Chanzo cha moto (jiko), maji, sufuria, kipimajoto, kipimajoto sauti na programu saidizi",
    },
    "pg073_sec001.html": {
        "Kiberiti, mishumaa miwili, chombo angavu chenye uwazi upande mmoja au jagi lenye kuzuia hewa kupita, saa na meza": "Kiberiti, mishumaa miwili, chombo angavu chenye uwazi upande mmoja au jagi lenye kuzuia hewa kupita, saa, meza na programu saidizi",
    },
    "pg074_sec001.html": {
        "Kuni, majani makavu au vipande vya karatasi, chanzo cha moto na eneo la wazi": "Kuni, majani makavu au vipande vya karatasi, chanzo cha moto, eneo la wazi na programu saidizi",
        "Jaribio linaonyesha kwamba oksijeni": "Jaribio linaonesha na linabainisha kwamba oksijeni",
    },
    "pg075_sec001.html": {
        "Chunguza nini kimetokea baada ya kuni kuungua.": "Chunguza na eleza kilichotokea au ulichohisi baada ya kuni kuungua.",
    },
    "pg076_sec001.html": {
        "Kuni, majani makavu au vipande vya karatasi, chanzo cha moto, chombo kikubwa cha chuma, eneo la wazi, na kifaa cha kutifulia udongo.": "Kuni, majani makavu au vipande vya karatasi, chanzo cha moto, chombo kikubwa cha chuma, eneo la wazi, kifaa cha kutifulia udongo na programu saidizi.",
        "Chochea moto hadi kuni zishike moto kisawasawa.": "Chochea moto hadi kuni zishike moto kisawasawa, kisha chunguza unachokiona au unachohisi.",
    },
    "pg086_sec001.html": {
        "Je, nini kinatokea kwenye nta?": "Je, nini kinatokea au kinaweza kuhisiwa kwenye nta?",
    },
    "pg088_sec001.html": {
        "Sufuria, jiko, kibiriti, maji, vipande vidogo vya karatasi ya A4 na kipimajoto": "Sufuria, jiko, kibiriti, maji, vipande vidogo vya karatasi ya A4, kipimajoto, kipimajoto sauti na programu saidizi",
    },
    "pg090_sec001.html": {
        "Je, kitambaa kinaonekanaje?": "Je, kitambaa kinaonekanaje au kinahisikaje?",
    },
    "pg091_sec001.html": {
        "mnururisho": "mnunurisho",
    },
    "pg095_sec001.html": {
        "Chora mifano hiyo uliyoorodhesha kwenye namba 1 hapo juu": "Chora au eleza mifano hiyo uliyoorodhesha kwenye namba 1 hapo juu",
        "chunguza vitu katika Jedwali namba 3": "chunguza au tambua vitu katika Jedwali namba 3",
    },
    "pg097_sec001.html": {
        "umeona jinsi mwanga unavyopita": "umetambua jinsi mwanga unavyopita",
        "Kuonesha uwezo wa vitu mbalimbali kupitisha mwanga": "Kutambua uwezo wa vitu mbalimbali kupitisha mwanga",
        "glasi iliyojaa maji na kitabu": "glasi iliyojaa maji, kitabu na programu saidizi",
    },
    "pg098_sec001.html": {
        "andika matokeo uliyoyaona.": "andika au eleza matokeo uliyotambua.",
        "Andika matokeo ya kila kimoja kadiri ulivyoona": "Andika matokeo ya kila kimoja kadiri ulivyotambua",
        "Glasi yenye maji, karatasi ngumu isiyo pitisha mwanga, karatasi ngumu yenye tobo, kurunzi na maji": "Glasi yenye maji, karatasi ngumu isiyopitisha mwanga, karatasi ngumu yenye tobo, kurunzi, maji na programu saidizi",
    },
    "pg099_sec001.html": {
        "Je, unaweza kuona mwanga wa kurunzi katika karatasi ngumu isiyo na tobo?": "Je, unaweza kutambua mwanga wa kurunzi katika karatasi ngumu isiyo na tobo?",
    },
}

SCRIPT_VERSION_PAGES = {
    "pg050_sec001.html", "pg051_sec001.html", "pg052_sec001.html", "pg056_sec001.html",
    "pg060_sec001.html", "pg061_sec001.html", "pg064_sec001.html", "pg068_sec001.html",
    "pg072_sec001.html", "pg074_sec001.html", "pg076_sec001.html", "pg082_sec001.html",
    "pg086_sec001.html", "pg089_sec001.html", "pg093_sec001.html", "pg094_sec001.html",
    "pg095_sec001.html", "pg096_sec001.html", "pg097_sec001.html", "pg098_sec001.html",
    "pg099_sec001.html",
}


def main() -> None:
    for filename, replacements in REPLACEMENTS.items():
        path = ROOT / filename
        source = path.read_text(encoding="utf-8-sig")
        for old, new in replacements.items():
            if old not in source:
                if new in source:
                    continue
                raise RuntimeError(f"Missing expected text in {filename}: {old}")
            source = source.replace(old, new)
        path.write_text(source, encoding="utf-8")

    for filename in SCRIPT_VERSION_PAGES:
        path = ROOT / filename
        source = path.read_text(encoding="utf-8-sig")
        source = re.sub(r'(matrix-accessibility\.js\?v=)[^"\']+', r'\1matrix3-77', source)
        path.write_text(source, encoding="utf-8")

    texts_path = ROOT / "content" / "i18n" / "sw-TZ" / "texts.json"
    texts = json.loads(texts_path.read_text(encoding="utf-8-sig"))
    changed_ids: set[str] = set()
    for filename, replacements in REPLACEMENTS.items():
        source = (ROOT / filename).read_text(encoding="utf-8")
        document = html.fromstring(source)
        for element in document.xpath('//*[@data-id and not(self::img) and not(.//*[@data-id])]'):
            text_id = element.get("data-id")
            plain = " ".join(element.text_content().split())
            if (text_id in texts and any(new in plain for new in replacements.values())) or text_id.startswith("pg097_fix_n"):
                texts[text_id] = plain
                changed_ids.add(text_id)
    texts_path.write_text(json.dumps(texts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    audios_path = ROOT / "content" / "i18n" / "sw-TZ" / "audios.json"
    audios = json.loads(audios_path.read_text(encoding="utf-8-sig"))
    for text_id in changed_ids:
        audios.setdefault(text_id, f"{text_id}.mp3")
    audios_path.write_text(json.dumps(audios, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"updated_files={len(REPLACEMENTS)} synced_text_ids={len(changed_ids)}")


if __name__ == "__main__":
    main()
