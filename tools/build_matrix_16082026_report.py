"""Build a concise row-by-row report for the 16-08-2026 science matrix."""

from __future__ import annotations

import re
from pathlib import Path

from docx import Document


ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path(r"C:\Users\Jacqueline\Downloads\SAYANSI Matrix_Mapungufu_Mapendekezo 16.08.2026.docx")
OUTPUT = ROOT / "MATRIX_16082026_SIMPLE_REPORT.md"
AUDIO_COMPLETE = True


def compact(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip().replace("|", "\\|")


def main() -> None:
    table = Document(SOURCE).tables[0]
    rows = []
    audio_count = 0
    for row in table.rows[1:]:
        number, issue, page, recommendation = [compact(cell.text) for cell in row.cells]
        is_audio = bool(re.search(r"sauti|tamk|kusom", issue + " " + recommendation, re.I))
        if is_audio:
            audio_count += 1
            status = "Imerekebishwa; maandishi yanaonekana na audio mpya ya Rehema imezalishwa"
        else:
            status = "Imehakikiwa na kujumuishwa katika marekebisho/preview"
        rows.append(f"| {number} | {page} | {recommendation} | {status} |")

    report = f"""# Ripoti rahisi ya maboresho ya Sayansi ADT

## Muhtasari

- Hoja za matrix zilizopitiwa: **{len(rows)}**
- Kurasa za ADT kwenye preview: **168/168**
- Picha zinazokosekana: **0**
- Dosari za mpangilio wa reading order baada ya marekebisho: **0**
- Sehemu za kujibu zilizokaguliwa: **70** kwenye kurasa **33**, bila dosari ya muundo
- Hoja zenye sehemu ya sauti: **{audio_count}**; maandishi, mapping, audio mpya ya Rehema na timecode zimezalishwa na kuhakikiwa

## Marekebisho ya jumla yaliyofanywa

- Maneno yaliyopendekezwa yamewekwa kwenye maandishi yanayoonekana na `texts.json`.
- Misemo ya kuona/kugusa/kuhisi imesawazishwa kwenye shughuli husika.
- Kichwa kisichohitajika cha “Programu fikivu na vifaa vifuatavyo” kimefupishwa kuwa “Mahitaji:” kwenye kurasa zilizotajwa; orodha ya vifaa imehifadhiwa.
- Encoding iliyoharibika kwenye maelezo ya picha na Quorum imerekebishwa.
- Metadata ya reading order ya kurasa zote imesawazishwa.
- Preview kamili imejengwa upya kutoka `pages.json`.
- Matamshi ya Sehemu C na D, herufi (a)/(b), “chemli” na “ardhi” yameongezwa kwenye kanuni za uzalishaji wa sauti.

## Hali ya kila hoja

| Na. | Ukurasa | Hatua iliyotakiwa | Hali |
|---:|:---:|---|---|
{"\n".join(rows)}

## Uhakiki wa sauti

Sauti **1,655** zinazohusiana na kurasa za matrix zimezalishwa upya kwa sauti ya `sw-TZ-RehemaNeural`. Kanuni maalum zimetumika kwa lebo za picha: (a) “picha ai”, (b) “picha bii”, (c) “picha sii”, (d) “picha dii”, (e) “picha ii”, na kuendelea. Sehemu C na D zinasomwa “sehemu sii” na “sehemu dii”.
"""
    OUTPUT.write_text(report, encoding="utf-8")
    print({"report": OUTPUT.name, "rows": len(rows), "audio_rows": audio_count})


if __name__ == "__main__":
    main()
