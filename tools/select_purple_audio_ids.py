import json
import re
from pathlib import Path


root = Path(__file__).resolve().parents[1]
texts = json.loads((root / "content/i18n/sw-TZ/texts.json").read_text(encoding="utf-8"))
ids = sorted(text_id for text_id, value in texts.items() if re.search(r"\bPurple\b", str(value), re.I))
(root / "content/purple-audio-ids.json").write_text(
    json.dumps(ids, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)
print({"selected_ids": len(ids), "ids": ids})
