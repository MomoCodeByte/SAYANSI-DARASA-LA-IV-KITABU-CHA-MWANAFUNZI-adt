"""Apply safe book-wide validation rules without changing visible textbook text."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LANG = ROOT / "content" / "i18n" / "sw-TZ"
texts = json.loads((LANG / "texts.json").read_text(encoding="utf-8"))
audio_path = LANG / "audios.json"
audios = json.loads(audio_path.read_text(encoding="utf-8"))

# Keep printed content intact, but never offer production footer/watermark audio.
blocked = re.compile(
    r"FOR\s+ONLINE\s+(?:READING|USE)\s+ONLY|"
    r"SAYANSI\s+DARASA\s+LA\s+IV\s+KITABU\s+CHA\s+MWANAFUNZI(?:\.indd)?",
    re.IGNORECASE,
)
production_stamp = re.compile(r"^\s*(?:\d{1,2}/\d{1,2}/\d{4}|\d{1,2}:\d{2})\s*$")
removed = []
blocked_ids = []
for key, value in texts.items():
    if blocked.search(str(value)) or production_stamp.match(str(value)):
        blocked_ids.append(key)
for key in list(audios):
    value = str(texts.get(key, ""))
    if blocked.search(value) or production_stamp.match(value):
        removed.append(key)
        audios.pop(key)
audio_path.write_text(json.dumps(audios, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

interface_path = ROOT / "assets" / "interface_translations" / "sw-TZ" / "interface_translations.json"
interface = json.loads(interface_path.read_text(encoding="utf-8"))
replacements = 0
for key, value in list(interface.items()):
    if isinstance(value, str) and ("Kamusi" in value or "kamusi" in value):
        interface[key] = value.replace("Kamusi", "Farahasa").replace("kamusi", "farahasa")
        replacements += 1
interface_path.write_text(json.dumps(interface, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

report = {
    "removed_audio_mappings": len(removed),
    "removed_ids": removed,
    "blocked_text_ids": blocked_ids,
    "blocked_text_ids_without_audio": sum(key not in audios for key in blocked_ids),
    "interface_farahasa_replacements": replacements,
    "visible_text_changed": False,
}
(ROOT / "content" / "matrix-global-rules-report.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)
print(json.dumps(report, ensure_ascii=False))
