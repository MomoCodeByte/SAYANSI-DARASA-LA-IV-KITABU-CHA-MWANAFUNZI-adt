import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LANG = ROOT / "content/i18n/sw-TZ"
texts = json.loads((LANG / "texts.json").read_text(encoding="utf-8"))
audios = json.loads((LANG / "audios.json").read_text(encoding="utf-8"))
ids = sorted(
    text_id
    for text_id, text in texts.items()
    if text_id in audios
    and not text_id.endswith("_easy_read")
    and re.search(r"(?i)\bRight\s+angled\s+triangle\b", str(text))
)
path = ROOT / "content/right-angled-triangle-audio-ids.json"
path.write_text(json.dumps(ids, indent=2) + "\n", encoding="utf-8")
print({"selected_audio_ids": ids})
