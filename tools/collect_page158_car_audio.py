import json
import re
from pathlib import Path


root = Path(__file__).resolve().parents[1]
texts_path = root / "content/i18n/sw-TZ/texts.json"
ids_path = root / "content/page158-car-audio-ids.json"
texts = json.loads(texts_path.read_text(encoding="utf-8"))
pattern = re.compile(r"\bcar\b", re.IGNORECASE)
ids = sorted(
    text_id
    for text_id, value in texts.items()
    if isinstance(value, str)
    and pattern.search(value)
    and text_id.startswith("pg158_")
)
if not ids:
    raise RuntimeError("No page 158 car text IDs found")
ids_path.write_text(json.dumps(ids, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print({"ids": ids})
