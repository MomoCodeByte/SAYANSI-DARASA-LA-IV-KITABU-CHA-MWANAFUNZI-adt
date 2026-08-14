"""Apply the targeted corrections transcribed from matrix photos 1 and 2."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LANG = ROOT / "content" / "i18n" / "sw-TZ"

# Production marks must remain visible where the original page contains them,
# but they must never enter the read-aloud sequence.
SILENT_IDS = {
    "pg001_n0005", "pg001_n0023", "pg001_n0025",
    "pg002_n0019", "pg002_n0021", "pg002_n0022",
    "pg003_n0034", "pg003_n0036", "pg003_n0037",
}

# Rehema audio that must be regenerated with Swahili number handling and the
# pronunciation overrides in generate_matrix_audio.py.
AUDIO_IDS = [
    "pg001_n0011", "pg001_n0015",
    "pg002_n0002", "pg002_n0004", "pg002_n0006",
    "pg003_n0006", "pg003_n0009",
    "pg009_n0005", "pg009_n0007",
    "pg010_n0010", "pg010_n0013", "pg010_n0015",
    "pg011_n0021",
    "pg012_n0012", "pg012_n0017", "pg012_n0022",
]


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def save(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


audios_path = LANG / "audios.json"
audios = load(audios_path)
for text_id in SILENT_IDS:
    audios.pop(text_id, None)
for text_id in AUDIO_IDS:
    if text_id in audios:
        audios[text_id] = str(audios[text_id]).split("?")[0] + "?v=matrix-p12-1"
save(audios_path, audios)

timecodes_path = LANG / "timecode" / "timecode_output.json"
if timecodes_path.exists():
    timecodes = load(timecodes_path)
    for text_id in SILENT_IDS:
        timecodes.pop(text_id, None)
    save(timecodes_path, timecodes)

ids_path = ROOT / "content" / "matrix-photos-1-2-audio-ids.json"
ids_path.write_text(json.dumps(AUDIO_IDS, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"silent={len(SILENT_IDS)} regenerate={len(AUDIO_IDS)}")
