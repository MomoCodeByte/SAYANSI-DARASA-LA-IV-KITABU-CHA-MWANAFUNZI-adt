"""Build one faithful ADT HTML page for each source PDF page."""

from __future__ import annotations

import html
import json
import re
from pathlib import Path

import pdfplumber


ROOT = Path(__file__).resolve().parents[1]
PDF = Path(r"C:\Users\Admin\Desktop\additionBooks\SAYANSI STD 4 PB\SAYANSI DARASA LA IV KITABU CHA MWANAFUNZI.pdf")
PAGE_COUNT = 168


ONES = ["sifuri", "moja", "mbili", "tatu", "nne", "tano", "sita", "saba", "nane", "tisa"]
TENS = ["", "kumi", "ishirini", "thelathini", "arobaini", "hamsini", "sitini", "sabini", "themanini", "tisini"]
ROMAN_SW = {"I": "moja", "II": "mbili", "III": "tatu", "IV": "nne", "V": "tano", "VI": "sita", "VII": "saba", "VIII": "nane", "IX": "tisa", "X": "kumi"}


def number_to_sw(number: int) -> str:
    """Return a screen-reader-friendly Kiswahili cardinal number."""
    if number < 10:
        return ONES[number]
    if number < 100:
        tens, ones = divmod(number, 10)
        return TENS[tens] + (f" na {ONES[ones]}" if ones else "")
    if number < 1_000:
        hundreds, rest = divmod(number, 100)
        return f"mia {ONES[hundreds]}" + (f" na {number_to_sw(rest)}" if rest else "")
    if number < 1_000_000:
        thousands, rest = divmod(number, 1_000)
        prefix = "elfu moja" if thousands == 1 else f"elfu {number_to_sw(thousands)}"
        return prefix + (f" na {number_to_sw(rest)}" if rest else "")
    millions, rest = divmod(number, 1_000_000)
    prefix = "milioni moja" if millions == 1 else f"milioni {number_to_sw(millions)}"
    return prefix + (f" na {number_to_sw(rest)}" if rest else "")


def normalize_accessible_text(value: str) -> str | None:
    """Apply matrix-wide speech/accessibility rules without altering the PDF image."""
    text = re.sub(r"\s+", " ", value).strip()
    upper = text.upper()
    if "FOR ONLINE READING ONLY" in upper:
        return None
    if ".INDD" in upper or re.fullmatch(r"\d{2}/\d{2}/\d{4}\s+\d{1,2}:\d{2}", text):
        return None
    text = re.sub(r"\bKamusi\b", "Farahasa", text, flags=re.IGNORECASE)
    abbreviations = {
        r"\bDkt\.?": "Daktari",
        r"\bBw\.?": "Bwana",
        r"\bBi\.?": "Bibi",
        r"\bTET\b": "Taasisi ya Elimu Tanzania",
        r"\bDUCE\b": "Chuo Kikuu Kishiriki cha Elimu Dar es Salaam",
        r"\bSUA\b": "Chuo Kikuu cha Sokoine cha Kilimo",
    }
    for pattern, spoken in abbreviations.items():
        text = re.sub(pattern, spoken, text)
    text = re.sub(r"\bUVIKO\s*[-–]?\s*19\b", "Uviko kumi na tisa", text, flags=re.IGNORECASE)
    text = re.sub(r"\bVVU\b", "Vivi U", text)
    text = re.sub(r"\(([a-z])\)", lambda match: f"(herufi {match.group(1).upper()})", text)
    text = re.sub(r"\b(.{3,80}?)\s*\(\1\)", r"\1", text)
    text = text.replace(
        "Chuo Kikuu cha Sokoine (Chuo Kikuu cha Sokoine cha Kilimo)",
        "Chuo Kikuu cha Sokoine cha Kilimo",
    )
    text = re.sub(
        r"(?<!\w)(VIII|VII|VI|IV|III|II|IX|X|V|I)(?!\w)",
        lambda match: ROMAN_SW[match.group()],
        text,
    )
    text = re.sub(r"\bAngalia\b", "Angalia au chunguza", text, flags=re.IGNORECASE)
    text = re.sub(r"\bKielelezo\s+namba\s+(\d+)\s+kinaonesha\b", r"Kielelezo namba \1 kinaonesha au kinabainisha", text, flags=re.IGNORECASE)
    text = re.sub(r"\bKielelezo\s+namba\s+(\d+)\s+inaonesha\b", r"Kielelezo namba \1 kinaonesha au kinabainisha", text, flags=re.IGNORECASE)
    text = re.sub(r"(?<![\w.-])\d+(?![\w.-])", lambda m: number_to_sw(int(m.group())), text)
    return text


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def href(number: int) -> str:
    return "index.html" if number == 1 else f"pg{number:03d}_sec001.html"


def page_html(number: int, words: list[dict], texts: dict[str, object], overrides: dict[str, object], width: float, height: float) -> str:
    prefix = f"pg{number:03d}_"
    transcript = []
    for key, value in texts.items():
        if (
            key.startswith(prefix)
            and re.fullmatch(rf"{prefix}n\d+", key)
            and isinstance(value, str)
            and value.strip()
        ):
            normalized = normalize_accessible_text(value)
            if normalized:
                transcript.append(
                    f'<span data-id="{html.escape(key, quote=True)}">{html.escape(normalized)}</span>'
                )

    word_layer = []
    for index, word in enumerate(words):
        left = float(word["x0"]) / width * 100
        top = float(word["top"]) / height * 100
        word_width = (float(word["x1"]) - float(word["x0"])) / width * 100
        word_height = (float(word["bottom"]) - float(word["top"])) / height * 100
        word_layer.append(
            '<span class="pdf-word" '
            f'data-word-index="{index}" '
            f'style="left:{left:.5f}%;top:{top:.5f}%;width:{word_width:.5f}%;height:{word_height:.5f}%">'
            f'{html.escape(str(word["text"]))}</span>'
        )

    section = f"pg{number:03d}_sec001"
    supplement_items = []
    page_override = overrides.get(f"{number:03d}", {})
    if isinstance(page_override, dict):
        for item in page_override.get("supplements", []):
            if isinstance(item, str) and item.strip():
                supplement_items.append(f"<p>{html.escape(item.strip())}</p>")
    supplement = ""
    if supplement_items:
        supplement = '      <aside class="accessible-transcript" aria-label="Maelezo ya ziada ya ufikivu">' + " ".join(supplement_items) + "</aside>"
    return f'''<!DOCTYPE html>
<html lang="sw-TZ">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Sayansi Darasa la IV - Ukurasa {number}</title>
  <meta name="title-id" content="{section}" />
  <meta name="page-section-id" content="{number}" />
  <link href="./content/tailwind_output.css" rel="stylesheet" />
  <link href="./assets/libs/fontawesome/css/all.min.css" rel="stylesheet" />
  <link href="./assets/fonts.css" rel="stylesheet" />
  <style>
    html, body {{ margin: 0; min-height: 100%; background: #d8dde2; }}
    body {{ display: flex; justify-content: center; align-items: flex-start; }}
    main {{ width: 100%; padding: 20px 12px 112px; box-sizing: border-box; }}
    #content {{ opacity: 1 !important; width: min(100%, 902px); margin: 0 auto; }}
    .pdf-page {{ position: relative; margin: 0 auto; background: #fff; box-shadow: 0 8px 30px rgba(0,0,0,.22); }}
    .pdf-page img {{ display: block; width: 100%; height: auto; }}
    .pdf-text-layer {{ position: absolute; inset: 0; pointer-events: none; overflow: hidden; }}
    .pdf-word {{ position: absolute; display: block; overflow: hidden; color: transparent; font-size: 1px; line-height: 1; }}
    .pdf-word.is-reading-word {{ background: rgba(255, 235, 59, .72); outline: 2px solid rgba(255, 152, 0, .9); border-radius: 3px; mix-blend-mode: multiply; }}
    .accessible-transcript {{ position: absolute !important; width: 1px !important; height: 1px !important; padding: 0 !important; margin: -1px !important; overflow: hidden !important; clip: rect(0,0,0,0) !important; white-space: nowrap !important; border: 0 !important; }}
    @media (max-width: 640px) {{ main {{ padding: 0 0 96px; }} .pdf-page {{ box-shadow: none; }} }}
  </style>
</head>
<body>
  <main>
    <h1 class="accessible-transcript">Sayansi Darasa la IV, ukurasa wa PDF {number}</h1>
    <div id="content">
      <article class="pdf-page" data-section-type="image" data-section-id="{section}">
        <img src="./images/pdf-pages/page-{number:03d}.jpg" alt="Ukurasa wa {number} wa kitabu cha Sayansi Darasa la IV" />
        <div class="pdf-text-layer" aria-hidden="true">{' '.join(word_layer)}</div>
      </article>
      <div class="accessible-transcript" aria-label="Maandishi ya ukurasa">{' '.join(transcript)}</div>
{supplement}
    </div>
  </main>
  <div class="relative z-50" id="interface-container"></div>
  <div class="relative z-50" id="nav-container"></div>
  <script src="./assets/scorm.js"></script>
  <script src="./assets/base.bundle.local.js"></script>
  <script src="./assets/read-along.js"></script>
</body>
</html>
'''


def main() -> None:
    texts = load_json(ROOT / "content/i18n/sw-TZ/texts.json")
    overrides_path = ROOT / "content/accessibility-overrides.json"
    overrides = load_json(overrides_path) if overrides_path.is_file() else {}
    pages = []
    with pdfplumber.open(PDF) as pdf:
        if len(pdf.pages) != PAGE_COUNT:
            raise ValueError(f"Expected {PAGE_COUNT} pages, found {len(pdf.pages)}")
        for number, page in enumerate(pdf.pages, 1):
            image = ROOT / f"images/pdf-pages/page-{number:03d}.jpg"
            if not image.is_file():
                raise FileNotFoundError(image)
            words = page.extract_words(use_text_flow=True, keep_blank_chars=False)
            (ROOT / href(number)).write_text(
                page_html(number, words, texts, overrides, float(page.width), float(page.height)),
                encoding="utf-8",
                newline="\n",
            )
            pages.append({"section_id": f"pg{number:03d}_sec001", "href": href(number), "page_number": number})

    (ROOT / "content/pages.json").write_text(
        json.dumps(pages, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    toc = load_json(ROOT / "content/toc.json")
    revised = []
    seen = set()
    for entry in toc:
        match = re.fullmatch(r"pg(\d{3})_sec\d{3}", str(entry.get("section_id", "")))
        if not match:
            continue
        number = int(match.group(1))
        if not 1 <= number <= PAGE_COUNT or number in seen:
            continue
        seen.add(number)
        updated = dict(entry)
        updated["section_id"] = f"pg{number:03d}_sec001"
        updated["href"] = href(number)
        revised.append(updated)
    (ROOT / "content/toc.json").write_text(
        json.dumps(revised, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    manifest_path = ROOT / "imsmanifest.xml"
    manifest = manifest_path.read_text(encoding="utf-8-sig")
    files = [href(n) for n in range(1, PAGE_COUNT + 1)]
    files += [f"images/pdf-pages/page-{n:03d}.jpg" for n in range(1, PAGE_COUNT + 1)]
    file_block = "\n".join(f'      <file href="{item}"/>' for item in files)
    manifest = re.sub(
        r"(?s)(<resource\b[^>]*>).*?(\n\s*</resource>)",
        lambda match: match.group(1) + "\n" + file_block + match.group(2),
        manifest,
        count=1,
    )
    manifest_path.write_text(manifest, encoding="utf-8", newline="\n")
    print(f"Built {PAGE_COUNT} PDF-faithful ADT pages")


if __name__ == "__main__":
    main()
