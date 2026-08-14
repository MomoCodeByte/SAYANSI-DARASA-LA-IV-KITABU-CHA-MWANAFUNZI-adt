import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEXTS_PATH = ROOT / "content" / "i18n" / "sw-TZ" / "texts.json"
CHAPTER_PAGES = [ROOT / f"pg{number:03d}_sec001.html" for number in range(118, 169)]


def make_inclusive(text: str) -> str:
    """Apply the chapter-six terminology requested by the validation matrix."""
    text = re.sub(r"\bPaint(?!/Quorum)", "Paint/Quorum", text)
    text = re.sub(r"\bpaint(?!/Quorum)", "paint/Quorum", text)
    text = re.sub(r"\bScratch(?!/Quorum)", "Scratch/Quorum", text)
    text = re.sub(r"\bscratch(?!/Quorum)", "scratch/Quorum", text)
    text = text.replace("Tazama Kielelezo", "Chunguza Kielelezo")
    text = text.replace("Angalia Kielelezo", "Angalia/chunguza Kielelezo")
    text = text.replace("angalia Kielelezo", "angalia/chunguza Kielelezo")
    text = re.sub(r"\bBofya(?! au tumia mishale)", "Bofya au tumia mishale", text)
    text = re.sub(r"\bbofya(?! au tumia mishale)", "bofya au tumia mishale", text)
    text = re.sub(
        r"\bBuruta(?:/tumia mishale)? na u?dondoshe",
        "Buruta au tumia mishale, kisha udondoshe",
        text,
    )
    text = re.sub(
        r"\bburuta(?:/tumia mishale)? na u?dondoshe",
        "buruta au tumia mishale, kisha udondoshe",
        text,
    )
    text = re.sub(
        r"\bBuruta(?:/tumia mishale)? na kudondosha",
        "Buruta au tumia mishale, kisha dondosha",
        text,
    )
    text = re.sub(
        r"\bburuta(?:/tumia mishale)? na kudondosha",
        "buruta au tumia mishale, kisha dondosha",
        text,
    )
    text = re.sub(
        r"\bKuburuta(?!/kutumia mishale) na kudondosha",
        "Kuburuta/kutumia mishale na kudondosha",
        text,
    )
    text = re.sub(
        r"\bkuburuta(?!/kutumia mishale) na kudondosha",
        "kuburuta/kutumia mishale na kudondosha",
        text,
    )
    text = re.sub(
        r"\binaburutwa(?! au inahamishwa kwa mishale)",
        "inaburutwa au inahamishwa kwa mishale",
        text,
    )
    text = re.sub(
        r"Weka mshale wa kipanya(?! au tumia mishale)",
        "Weka mshale wa kipanya au tumia mishale",
        text,
    )
    text = re.sub(
        r"Je, umeona nini(?!/)",
        "Je, umeona/umesikia/umehisi nini",
        text,
    )
    text = re.sub(r"\bUmesikia nini(?!/)", "Umesikia/umehisi nini", text)
    text = re.sub(r"\bumesikia nini(?!/)", "umesikia/umehisi nini", text)
    text = re.sub(r"\bUmeona nini(?!/)", "Umeona/umesikia/umehisi nini", text)
    text = re.sub(r"\bumeona nini(?!/)", "umeona/umesikia/umehisi nini", text)
    text = re.sub(r"kinaonesha(?!/kinabainisha)", "kinaonesha/kinabainisha", text)
    text = re.sub(r"kinavyoonesha(?!/kinavyobainisha)", "kinavyoonesha/kinavyobainisha", text)
    while "/kinabainisha/kinabainisha" in text:
        text = text.replace("/kinabainisha/kinabainisha", "/kinabainisha")
    while "/kinavyobainisha/kinavyobainisha" in text:
        text = text.replace("/kinavyobainisha/kinavyobainisha", "/kinavyobainisha")
    return text


def main() -> None:
    changed_files = []
    for path in CHAPTER_PAGES:
        if not path.exists():
            continue
        original = path.read_text(encoding="utf-8")
        updated = make_inclusive(original)
        if updated != original:
            path.write_text(updated, encoding="utf-8", newline="")
            changed_files.append(path.name)

    texts = json.loads(TEXTS_PATH.read_text(encoding="utf-8"))
    changed_ids = []
    for key, value in list(texts.items()):
        match = re.match(r"pg(\d{3})_", key)
        if not match or not 118 <= int(match.group(1)) <= 168 or not isinstance(value, str):
            continue
        updated = make_inclusive(value)
        if updated != value:
            texts[key] = updated
            changed_ids.append(key)

    texts["pg120_n0029"] = (
        "Kwa kutumia Quorum au kisoma skrini, tumia Tab na vitufe vya mishale kuchagua programu na kutekeleza hatua hizi."
    )
    texts["pg130_n0030"] = (
        "Kwa kutumia Quorum au kisoma skrini, tumia Tab na vitufe vya mishale badala ya kuburuta; thibitisha chaguo kwa Enter."
    )
    TEXTS_PATH.write_text(json.dumps(texts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"Updated {len(changed_files)} chapter files and {len(changed_ids)} existing text IDs")
    print("Files:", ", ".join(changed_files))


if __name__ == "__main__":
    main()
