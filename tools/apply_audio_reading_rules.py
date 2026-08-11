"""Remove non-content audio mappings and print IDs needing honorific regeneration."""

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
I18N = ROOT / "content" / "i18n" / "sw-TZ"
texts = json.loads((I18N / "texts.json").read_text(encoding="utf-8"))
audio_path = I18N / "audios.json"
audios = json.loads(audio_path.read_text(encoding="utf-8"))

blocked = re.compile(
    r"FOR\s+ONLINE\s+(?:READING|USE)\s+ONLY|"
    r"SAYANSI\s+DARASA\s+LA\s+IV\s+KITABU\s+CHA\s+MWANAFUNZI(?:\.indd)?",
    re.IGNORECASE,
)
date_or_time = re.compile(r"^\s*\d{1,2}/\d{1,2}/\d{4}(?:\s+\d{1,2}:\d{2})?\s*$")
removed = [key for key in audios if blocked.search(str(texts.get(key, ""))) or date_or_time.match(str(texts.get(key, "")))]
for key in removed:
    audios.pop(key, None)
audio_path.write_text(json.dumps(audios, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

honorific = re.compile(r"(?<!\w)(?:Dkt\.?|Bi\.|Bw\.)", re.IGNORECASE)
ids = [key for key in audios if honorific.search(str(texts.get(key, "")))]
(I18N / "honorific-audio-ids.json").write_text(json.dumps(ids, indent=2) + "\n", encoding="utf-8")
print(f"removed={len(removed)} honorific_ids={len(ids)}")
