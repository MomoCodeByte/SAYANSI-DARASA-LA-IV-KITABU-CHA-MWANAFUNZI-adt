"""Make every active HTML page use its canonical pages.json reading position."""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
pages = json.loads((ROOT / "content/pages.json").read_text(encoding="utf-8-sig"))
updated = []
for position, entry in enumerate(pages, start=1):
    path = ROOT / entry["href"]
    source = path.read_text(encoding="utf-8-sig")
    normalized = re.sub(
        r'(<meta\s+name="page-section-id"\s+content=")[^"]+("\s*/?>)',
        rf'\g<1>{position}\2', source, count=1,
    )
    if normalized != source:
        path.write_text(normalized, encoding="utf-8")
        updated.append(path.name)
print(f"reading_entries={len(pages)} metadata_updated={len(updated)}")
