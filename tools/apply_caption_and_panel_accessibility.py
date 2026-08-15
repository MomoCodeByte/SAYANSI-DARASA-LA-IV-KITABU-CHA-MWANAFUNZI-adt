from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEXTS_PATH = ROOT / "content" / "i18n" / "sw-TZ" / "texts.json"
CAPTION = re.compile(
    r'(<(?P<tag>span|div|p|figcaption)\b[^>]*\bdata-id="[^"]+"[^>]*>\s*)'
    r'(?P<prefix>Kielelezo\s+namba\s+\d+(?:\s*\([^)]+\))?\s*:)', re.I)
DESC = re.compile(
    r'(?P<open><span\b[^>]*\bdata-id="(?P<id>[^"]+_audio_desc)"[^>]*\bimage-audio-description\b[^>]*>)'
    r'(?P<desc>[^<]*)(?P<close></span>)'
    r'(?P<between>(?:(?!<img\b)[\s\S]){0,1200}?)'
    r'(?P<label_element><(?:span|div|p)\b[^>]*\bdata-id="[^"]+"[^>]*>\s*\((?P<letter>[a-z])\)\s*(?P<label>[^<]+)</(?:span|div|p)>)', re.I)


def main() -> None:
    texts = json.loads(TEXTS_PATH.read_text(encoding="utf-8"))
    changed_pages = bolded = 0
    panel_ids: list[str] = []
    for path in sorted(ROOT.glob("pg*_sec*.html")):
        source = path.read_text(encoding="utf-8-sig")
        source, count = CAPTION.subn(
            lambda m: m.group(1) + '<strong data-figure-caption-prefix="true">' + m.group("prefix") + "</strong>",
            source,
        )
        bolded += count

        def panel_replacement(match: re.Match[str]) -> str:
            text_id = match.group("id")
            letter = match.group("letter").upper()
            label = match.group("label").strip().rstrip(".")
            current = match.group("desc").strip()
            if re.match(rf"^Picha\s+{letter}\b", current, re.I):
                return match.group(0)
            detail = re.sub(r"^Maelezo\s+ya\s+picha\s*:\s*", "", current, flags=re.I)
            updated = f"Picha {letter}, {label}. {detail}"
            texts[text_id] = updated
            panel_ids.append(text_id)
            return match.group("open") + updated + match.group("close") + match.group("between") + match.group("label_element")

        updated = DESC.sub(panel_replacement, source)
        if updated != path.read_text(encoding="utf-8-sig"):
            path.write_text(updated, encoding="utf-8")
            changed_pages += 1
    TEXTS_PATH.write_text(json.dumps(texts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    ids_path = ROOT / "tmp" / "caption-panel-audio-ids.txt"
    ids_path.parent.mkdir(exist_ok=True)
    ids_path.write_text("\n".join(panel_ids) + ("\n" if panel_ids else ""), encoding="utf-8")
    print(f"changed_pages={changed_pages} bolded_captions={bolded} panel_descriptions={len(panel_ids)}")


if __name__ == "__main__":
    main()
