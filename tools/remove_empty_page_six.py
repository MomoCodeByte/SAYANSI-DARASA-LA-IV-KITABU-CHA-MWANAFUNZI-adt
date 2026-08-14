"""Remove all residual data for the intentionally deleted empty ADT page 6."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LANG = ROOT / "content" / "i18n" / "sw-TZ"
PREFIX = "pg006_"


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


texts_path = LANG / "texts.json"
audios_path = LANG / "audios.json"
timecodes_path = LANG / "timecode" / "timecode_output.json"

texts = load(texts_path)
audios = load(audios_path)
timecodes = load(timecodes_path)

keys = sorted({key for source in (texts, audios, timecodes) for key in source if key.startswith(PREFIX)})
removed_audio = []
for key in keys:
    audio_name = str(audios.get(key, "")).split("?")[0]
    if audio_name:
        audio_path = (LANG / "audio" / audio_name).resolve()
        audio_root = (LANG / "audio").resolve()
        if audio_path.parent == audio_root and audio_path.exists():
            audio_path.unlink()
            removed_audio.append(audio_path.name)
    texts.pop(key, None)
    audios.pop(key, None)
    timecodes.pop(key, None)

save(texts_path, texts)
save(audios_path, audios)
save(timecodes_path, timecodes)
print({"removed_ids": len(keys), "removed_audio_files": len(removed_audio)})
