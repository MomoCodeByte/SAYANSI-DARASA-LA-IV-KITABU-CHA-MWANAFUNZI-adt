from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LANG = ROOT / "content" / "i18n" / "sw-TZ"
PATTERN = re.compile(r"kinaonesha\s+au\s+kinabainisha", re.I)


def main() -> None:
    texts_path = LANG / "texts.json"
    texts = json.loads(texts_path.read_text(encoding="utf-8"))
    changed_ids: list[str] = []
    for text_id, value in texts.items():
        updated, count = PATTERN.subn("kinaonesha", str(value))
        if count:
            texts[text_id] = updated
            changed_ids.append(text_id)
    texts_path.write_text(json.dumps(texts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    changed_pages = 0
    for path in [ROOT / "index.html", *sorted(ROOT.glob("pg*_sec*.html"))]:
        source = path.read_text(encoding="utf-8-sig")
        updated = PATTERN.sub("kinaonesha", source)
        if updated != source:
            path.write_text(updated, encoding="utf-8")
            changed_pages += 1

    ids_path = ROOT / "tmp" / "restore-kinaonesha-audio-ids.json"
    ids_path.parent.mkdir(exist_ok=True)
    ids_path.write_text(json.dumps(changed_ids, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print({"changed_text_ids": len(changed_ids), "changed_pages": changed_pages, "ids_file": str(ids_path)})


if __name__ == "__main__":
    main()
