"""Remove standalone qz001-qz038 pages and their orphaned i18n/audio data."""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUIZ_FILE = re.compile(r"qz\d{3}\.html$")
QUIZ_KEY = re.compile(r"qz\d{3}(?:_|$)")


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def save_json(path: Path, value) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


quiz_pages = sorted(path for path in ROOT.glob("qz*.html") if QUIZ_FILE.fullmatch(path.name))
if len(quiz_pages) != 38:
    raise SystemExit(f"Expected 38 quiz pages, found {len(quiz_pages)}; no files removed.")

pages_path = ROOT / "content" / "pages.json"
pages = load_json(pages_path)
kept_pages = [entry for entry in pages if not QUIZ_FILE.fullmatch(entry.get("href", ""))]
removed_entries = len(pages) - len(kept_pages)
if removed_entries != 38:
    raise SystemExit(f"Expected 38 pages.json entries, found {removed_entries}; no files removed.")
save_json(pages_path, kept_pages)

i18n_root = ROOT / "content" / "i18n" / "sw-TZ"
json_counts = {}
for relative in ("texts.json", "audios.json", "timecode/timecode_output.json"):
    path = i18n_root / relative
    data = load_json(path)
    if not isinstance(data, dict):
        continue
    quiz_keys = [key for key in data if QUIZ_KEY.match(key)]
    for key in quiz_keys:
        del data[key]
    save_json(path, data)
    json_counts[relative] = len(quiz_keys)

audio_files = sorted((i18n_root / "audio").glob("qz*.mp3"))
for path in audio_files:
    path.unlink()

for path in quiz_pages:
    path.unlink()

print(json.dumps({
    "quiz_html_removed": len(quiz_pages),
    "pages_entries_removed": removed_entries,
    "remaining_pages": len(kept_pages),
    "audio_files_removed": len(audio_files),
    "json_keys_removed": json_counts,
}, ensure_ascii=False, indent=2))
