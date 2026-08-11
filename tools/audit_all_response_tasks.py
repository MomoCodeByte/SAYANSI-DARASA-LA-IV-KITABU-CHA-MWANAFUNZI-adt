"""Find canonical book pages with answer-producing tasks but no interactivity.

This is deliberately a candidate audit: practical experiments and physical drawing
tasks are kept in the report for human review instead of being changed blindly.
"""

import json
import re
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = json.loads((ROOT / "content/pages.json").read_text(encoding="utf-8-sig"))
TEXTS = json.loads((ROOT / "content/i18n/sw-TZ/texts.json").read_text(encoding="utf-8-sig"))

MARKERS = re.compile(
    r"\b(?:Zoezi(?: la marudio)?|Kazi ya kufanya|Maswali|Jibu maswali|"
    r"Bainisha|Eleza|Taja|Orodhesha|Fafanua|Andika|Jaza|Chagua|Oanisha|"
    r"Pangilia|Toa sababu|Unaona nini|Umegundua nini)\b",
    re.I,
)

rows = []
for position, entry in enumerate(PAGES, start=1):
    if entry["section_id"].startswith("qz"):
        continue
    path = ROOT / entry["href"]
    source = path.read_text(encoding="utf-8-sig")
    ids = list(dict.fromkeys(re.findall(r'data-id="([^"]+)"', source)))
    visible = " ".join(str(TEXTS.get(data_id, "")) for data_id in ids)
    if not visible.strip():
        visible = unescape(re.sub(r"<[^>]+>", " ", source))
    visible = re.sub(r"\s+", " ", visible).strip()
    if not MARKERS.search(visible):
        continue
    controls = len(re.findall(r"<(?:textarea|input|select)\b", source, re.I))
    runtime_activity = bool(re.search(r'data-section-type="activity_', source))
    if controls == 0 and not runtime_activity:
        rows.append({
            "converted_page": position,
            "printed_page": entry.get("page_number"),
            "file": entry["href"],
            "text": visible[:1800],
        })

result = {"candidate_count": len(rows), "candidates": rows}
(ROOT / "content/all-response-task-candidates.json").write_text(
    json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)
print(json.dumps({"candidate_count": len(rows), "files": [r["file"] for r in rows]}, ensure_ascii=False, indent=2))
