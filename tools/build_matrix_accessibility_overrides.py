"""Build non-visual, screen-reader supplements from reviewed matrix rows."""

from __future__ import annotations

import html
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
plan = json.loads((ROOT / "content" / "validation-matrix-plan.json").read_text(encoding="utf-8"))
overrides: dict[str, list[dict[str, object]]] = {}
allowed = {"inclusive_language", "figure_accessibility", "assistive_technology"}
reference_fallbacks = {
    85: ["pg043_sec001.html"],
    120: ["pg076_sec001.html"],
}
# These rows are implemented directly in the page content/figure, so repeating
# the matrix recommendation as hidden prose would create confusing narration.
directly_implemented = {10, 14, 26}
for item in plan["items"]:
    if item["category"] not in allowed or item["status"] != "pending":
        continue
    if item["matrix_item"] in directly_implemented:
        continue
    recommendation = re.sub(r"\s+", " ", item["recommendation"]).strip()
    if not recommendation:
        continue
    if item["category"] == "inclusive_language":
        prefix = "Maelekezo jumuishi"
    elif item["category"] == "figure_accessibility":
        prefix = "Maelezo fikivu ya kielelezo"
    else:
        prefix = "Teknolojia saidizi"
    supplement = f"{prefix}: {recommendation}"
    filenames = item["files"] or reference_fallbacks.get(item["matrix_item"], [])
    for filename in filenames:
        if filename.lower().startswith("qz"):
            continue
        overrides.setdefault(filename, []).append({
            "matrix_item": item["matrix_item"],
            "category": item["category"],
            "text": supplement,
        })

for filename, entries in overrides.items():
    seen = set()
    overrides[filename] = [entry for entry in entries if not (entry["text"] in seen or seen.add(entry["text"]))]

(ROOT / "content" / "accessibility-overrides.json").write_text(
    json.dumps(overrides, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)

script_tag = '    <script src="./assets/matrix-accessibility.js?v=matrix-v1-1" defer></script>\n'
changed = 0
for page in sorted(ROOT.glob("*.html")):
    source = page.read_text(encoding="utf-8")
    if page.name.lower().startswith("qz"):
        cleaned = source.replace(script_tag, "")
        if cleaned != source:
            page.write_text(cleaned, encoding="utf-8")
        continue
    if "matrix-accessibility.js" in source:
        continue
    marker = "</body>"
    if marker in source:
        page.write_text(source.replace(marker, script_tag + marker), encoding="utf-8")
        changed += 1
print(f"override_files={len(overrides)} injected_html={changed}")
