#!/usr/bin/env python3
"""Select numbered procedure steps and give their number audio explicit context."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEXTS = ROOT / "content" / "i18n" / "sw-TZ" / "texts.json"
OVERRIDES = ROOT / "content" / "audio-spoken-overrides.json"
IDS = ROOT / "content" / "step-number-audio-ids.json"
NUMBER = re.compile(r"\s*(\d+)[.)]?\s*(.*)", re.DOTALL)
PAGE = re.compile(r"^(pg\d{3})_")
STOP = re.compile(
    r"^(?:matokeo|hitimisho|maswali?|zoezi|kazi ya kufanya|tahadhari|"
    r"majadiliano|sehemu\s+[a-d])\b",
    re.IGNORECASE,
)


def main() -> None:
    texts: dict[str, str] = json.loads(TEXTS.read_text(encoding="utf-8"))
    items = list(texts.items())
    selected: dict[str, str] = {}

    for index, (heading_id, heading_text) in enumerate(items):
        if heading_text.strip().casefold() != "hatua" or heading_id.endswith("_easy_read"):
            continue
        if not PAGE.match(heading_id):
            continue
        expected = 1
        started = False
        for text_id, value in items[index + 1 :]:
            clean = value.strip()
            if clean.casefold() == "hatua" or (started and STOP.match(clean)):
                break
            if text_id.endswith("_easy_read") or not PAGE.match(text_id):
                continue
            number_match = NUMBER.fullmatch(clean)
            if not number_match:
                continue
            number = int(number_match.group(1))
            if number == expected:
                remainder = number_match.group(2).strip()
                selected[text_id] = f"Hatua namba {number}" + (f". {remainder}" if remainder else "")
                expected += 1
                started = True
            elif started and number < expected:
                # A reset marks a different numbered list. Larger stray numbers
                # can be page furniture or values mentioned between steps.
                break

    existing = json.loads(OVERRIDES.read_text(encoding="utf-8")) if OVERRIDES.exists() else {}
    old_step_ids = set(json.loads(IDS.read_text(encoding="utf-8"))) if IDS.exists() else set()
    existing = {key: value for key, value in existing.items() if key not in old_step_ids}
    existing.update(selected)
    OVERRIDES.write_text(json.dumps(existing, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    IDS.write_text(json.dumps(sorted(selected), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"step headings scanned: {sum(v.strip().casefold() == 'hatua' for v in texts.values())}")
    print(f"step number audio overrides: {len(selected)}")
    for text_id, speech in selected.items():
        print(f"{text_id}\t{speech}")


if __name__ == "__main__":
    main()
