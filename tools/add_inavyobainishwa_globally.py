import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEXTS_PATH = ROOT / "content/i18n/sw-TZ/texts.json"
IDS_PATH = ROOT / "content/inavyooneshwa-inavyobainishwa-audio-ids.json"


def update(value: str) -> str:
    value = re.sub(
        r"\binavyooneshwa\s+au\s+inavyo\s+bainishwa\b",
        "inavyooneshwa au inavyobainishwa",
        value,
        flags=re.IGNORECASE,
    )
    return re.sub(
        r"\binavyooneshwa\b(?!\s+au\s+inavyobainishwa)",
        "inavyooneshwa au inavyobainishwa",
        value,
        flags=re.IGNORECASE,
    )


def main():
    texts = json.loads(TEXTS_PATH.read_text(encoding="utf-8"))
    changed_ids = set()
    changed_pages = []
    for text_id, text in list(texts.items()):
        revised = update(str(text))
        if revised != text:
            texts[text_id] = revised
            changed_ids.add(text_id)

    for page in sorted(ROOT.glob("pg*_sec*.html")):
        source = page.read_text(encoding="utf-8-sig")
        revised = update(source)
        if revised != source:
            page.write_text(revised, encoding="utf-8")
            changed_pages.append(page.name)

    TEXTS_PATH.write_text(json.dumps(texts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    IDS_PATH.write_text(json.dumps(sorted(changed_ids), indent=2) + "\n", encoding="utf-8")
    print({"changed_pages": changed_pages, "changed_ids": sorted(changed_ids)})


if __name__ == "__main__":
    main()
