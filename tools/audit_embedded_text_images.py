"""Find images likely to repeat nearby HTML instructional content."""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = json.loads((ROOT / "content/pages.json").read_text(encoding="utf-8-sig"))
TEXTS = json.loads((ROOT / "content/i18n/sw-TZ/texts.json").read_text(encoding="utf-8-sig"))
KEYWORDS = re.compile(r"\b(?:kazi ya kufanya|zoezi|jaribio|maswali|hatua|lengo|mahitaji)\b", re.I)

rows = []
seen = set()
for position, entry in enumerate(PAGES, start=1):
    if entry["section_id"].startswith("qz") or entry["href"] in seen:
        continue
    seen.add(entry["href"])
    source = (ROOT / entry["href"]).read_text(encoding="utf-8-sig")
    for match in re.finditer(r"<img\b[^>]*>", source, re.I):
        tag = match.group(0)
        src = re.search(r'src="([^"]+)"', tag)
        data_id = re.search(r'data-id="([^"]+)"', tag)
        alt = re.search(r'alt="([^"]*)"', tag)
        alt_text = alt.group(1) if alt else ""
        localized = str(TEXTS.get(data_id.group(1), "")) if data_id else ""
        description = localized or alt_text
        if not KEYWORDS.search(description):
            continue
        classes = (re.search(r'class="([^"]*)"', tag) or [None, ""])[1]
        rows.append({
            "converted_page": position,
            "file": entry["href"],
            "image": src.group(1) if src else None,
            "data_id": data_id.group(1) if data_id else None,
            "hidden": "hidden" in classes.split(),
            "description": description,
        })

result = {"candidate_count": len(rows), "candidates": rows}
(ROOT / "content/embedded-text-image-audit.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, ensure_ascii=False, indent=2))
