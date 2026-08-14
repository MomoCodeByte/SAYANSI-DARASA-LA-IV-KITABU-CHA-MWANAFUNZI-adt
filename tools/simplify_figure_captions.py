import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEXTS_PATH = ROOT / "content/i18n/sw-TZ/texts.json"
IDS_PATH = ROOT / "content/simplified-figure-caption-ids.json"
PATTERN = re.compile(
    r"(Kielelezo\s+namba\s+[^<\n]+?)\s+"
    r"kina(?:onesha|onyesha)\s+(?:au|/)\s+kinabainisha\s+"
    r"(?:na\s+kinaeleza\s+)?",
    re.IGNORECASE,
)


def simplify(value: str) -> str:
    return PATTERN.sub(r"\1: ", value)


def main():
    texts = json.loads(TEXTS_PATH.read_text(encoding="utf-8"))
    changed_ids = set()
    changed_pages = []

    for text_id, value in list(texts.items()):
        updated = simplify(str(value))
        if updated != value:
            texts[text_id] = updated
            changed_ids.add(text_id)

    for page in sorted(ROOT.glob("pg*_sec*.html")):
        source = page.read_text(encoding="utf-8-sig")
        updated = simplify(source)
        if updated != source:
            page.write_text(updated, encoding="utf-8")
            changed_pages.append(page.name)

    TEXTS_PATH.write_text(
        json.dumps(texts, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    IDS_PATH.write_text(
        json.dumps(sorted(changed_ids), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print({"changed_pages": len(changed_pages), "changed_ids": len(changed_ids)})


if __name__ == "__main__":
    main()
