"""Rebuild word-highlight display indexes from the current visible textbook text."""

from __future__ import annotations

import json
from pathlib import Path

from generate_matrix_audio import spoken


ROOT = Path(__file__).resolve().parents[1]
LANG = ROOT / "content" / "i18n" / "sw-TZ"


def main() -> None:
    texts = json.loads((LANG / "texts.json").read_text(encoding="utf-8"))
    timecode_path = LANG / "timecode" / "timecode_output.json"
    timecodes = json.loads(timecode_path.read_text(encoding="utf-8"))
    updated_entries = 0
    updated_words = 0
    skipped = []

    for text_id, entry in timecodes.items():
        shown = str(texts.get(text_id, "")).strip()
        if not shown or not isinstance(entry, dict):
            continue
        _, display_map = spoken(shown)
        timestamps = [
            word
            for group in entry.get("timecodes", [])
            if isinstance(group, dict)
            for word in group.get("word_timestamps", [])
        ]
        if not display_map or not timestamps:
            skipped.append(text_id)
            continue
        changed = False
        for index, word in enumerate(timestamps):
            mapped = display_map[min(index, len(display_map) - 1)]
            if word.get("display_index") != mapped:
                word["display_index"] = mapped
                updated_words += 1
                changed = True
        if changed:
            updated_entries += 1

    timecode_path.write_text(
        json.dumps(timecodes, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        f"updated_entries={updated_entries} updated_words={updated_words} "
        f"skipped={len(skipped)}"
    )


if __name__ == "__main__":
    main()
