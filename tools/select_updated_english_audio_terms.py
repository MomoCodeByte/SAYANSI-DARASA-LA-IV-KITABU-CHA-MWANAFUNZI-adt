import json
import re
from pathlib import Path


root = Path(__file__).resolve().parents[1]
texts = json.loads((root / "content/i18n/sw-TZ/texts.json").read_text(encoding="utf-8"))
pattern = re.compile(r"\b(?:PNG|JPEG|BMP|Shape|Save)\b", re.IGNORECASE)
ids = sorted(text_id for text_id, value in texts.items() if pattern.search(str(value)))
path = root / "content/updated-english-audio-term-ids.json"
path.write_text(json.dumps(ids, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print({"selected_ids": len(ids), "ids": ids})
