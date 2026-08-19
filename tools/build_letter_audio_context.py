"""Classify parenthesized A-H labels as image panels or answer choices."""

from __future__ import annotations

import json
import re
from pathlib import Path

from lxml import html


ROOT = Path(__file__).resolve().parents[1]
TEXTS = ROOT / "content" / "i18n" / "sw-TZ" / "texts.json"
OUTPUT = ROOT / "content" / "letter-audio-context.json"
REGEN_OUTPUT = ROOT / "content" / "letter-audio-regeneration-ids.json"
LETTER = re.compile(r"^\s*\(([a-h])\)", re.I)
LETTER_ANYWHERE = re.compile(r"(?<!\w)\([a-h]\)", re.I)


def main() -> None:
    texts = json.loads(TEXTS.read_text(encoding="utf-8"))
    candidates = {
        text_id
        for text_id, value in texts.items()
        if not text_id.endswith("_easy_read") and LETTER.match(str(value))
    }
    picture: set[str] = set()
    choice: set[str] = set()

    for page in ROOT.glob("pg*_sec*.html"):
        document = html.fromstring(page.read_text(encoding="utf-8-sig"))
        for element in document.xpath("//*[@data-id]"):
            text_id = element.get("data-id")
            if text_id not in candidates:
                continue
            ancestors = list(element.iterancestors())
            section = next((node for node in ancestors if node.tag == "section"), None)
            section_type = section.get("data-section-type", "") if section is not None else ""
            in_option = element.get("data-activity-item") is not None or any(
                node.tag == "label" and "activity-option" in node.get("class", "").split()
                for node in ancestors
            )
            in_activity_table = any(node.tag == "table" for node in ancestors) and section_type.startswith("activity_")
            if in_option or in_activity_table or section_type in {"activity_multiple_choice", "activity_true_false"}:
                choice.add(text_id)
                continue
            # Captions normally share a small image/card container with <img>.
            local_ancestors = []
            for node in ancestors:
                if node.tag == "section":
                    break
                local_ancestors.append(node)
            if element.tag == "img" or any(node.xpath(".//img") for node in local_ancestors[:2]):
                picture.add(text_id)
                continue

    result = {"picture": sorted(picture), "choice": sorted(choice)}
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    audios = json.loads((ROOT / "content" / "i18n" / "sw-TZ" / "audios.json").read_text(encoding="utf-8"))
    regeneration_ids = sorted(
        text_id for text_id in audios
        if LETTER_ANYWHERE.search(str(texts.get(text_id, "")))
    )
    REGEN_OUTPUT.write_text(
        json.dumps(regeneration_ids, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        f"picture={len(picture)} choice={len(choice)} "
        f"plain={len(candidates - picture - choice)} regenerate={len(regeneration_ids)}"
    )


if __name__ == "__main__":
    main()
