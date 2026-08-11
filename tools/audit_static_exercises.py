"""List canonical pages that contain Zoezi text but no answer controls."""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
pages = json.loads((ROOT / "content/pages.json").read_text(encoding="utf-8-sig"))
texts = json.loads((ROOT / "content/i18n/sw-TZ/texts.json").read_text(encoding="utf-8-sig"))
rows = []
for position, entry in enumerate(pages, start=1):
    if entry["section_id"].startswith("qz"):
        continue
    source = (ROOT / entry["href"]).read_text(encoding="utf-8-sig")
    ids = list(dict.fromkeys(re.findall(r'data-id="([^"]+)"', source)))
    visible = " ".join(str(texts.get(data_id, "")) for data_id in ids)
    has_exercise = bool(re.search(r"\bZoezi\b", visible, flags=re.I))
    controls = len(re.findall(r'<(?:textarea|input|select)\b', source))
    runtime_activity = bool(re.search(r'data-section-type="activity_', source))
    if has_exercise and controls == 0 and not runtime_activity:
        rows.append({"converted_page": position, "file": entry["href"], "exercise_text": visible[:500]})
result = {"static_exercise_pages": len(rows), "pages": rows}
(ROOT / "content/static-exercise-audit.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, ensure_ascii=False, indent=2))
