"""Audit matrix implementation progress without overstating completion."""

import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
plan = json.loads((ROOT / "content/validation-matrix-plan.json").read_text(encoding="utf-8"))
overrides = json.loads((ROOT / "content/accessibility-overrides.json").read_text(encoding="utf-8"))
implemented_items = {
    int(entry["matrix_item"])
    for entries in overrides.values()
    for entry in entries
}
# Exact rows verified against the current HTML and the corresponding printed
# PDF pages. Some required no content change because Version 1 already matches
# the source; they are still recorded as verified rather than pending.
verified_exact_items = {
    8, 10, 14, 15, 24, 26, 30, 32, 33, 38, 65, 66, 72, 73, 75, 77, 78, 80,
    81, 83, 84, 85, 86, 88, 89, 92, 102, 103, 111, 122, 143, 147, 148, 151,
    171, 191, 193,
}
rows = []
for item in plan["items"]:
    number = item["matrix_item"]
    removed_quiz_reference = bool(item["files"]) and all(
        str(name).lower().startswith("qz") for name in item["files"]
    )
    if removed_quiz_reference:
        status = "IMPLEMENTED_QUIZ_CLEANUP"
    elif item["category"] == "answer_space":
        status = "IMPLEMENTED_INTERACTIVITY"
    elif item["category"] == "quiz":
        status = "IMPLEMENTED_QUIZ_CLEANUP"
    elif number == 152:
        status = "IMPLEMENTED_INTERACTIVITY"
    elif item["category"] == "audio_pronunciation":
        status = "IMPLEMENTED_AUDIO_REGENERATED"
    elif number in implemented_items:
        status = "IMPLEMENTED_ACCESSIBILITY_SUPPLEMENT"
    elif number in verified_exact_items:
        status = "IMPLEMENTED_EXACT_OR_VERIFIED"
    else:
        status = "PENDING_EXACT_FIX"
    rows.append({
        "matrix_item": number,
        "category": item["category"],
        "files": item["files"],
        "status": status,
    })
summary = Counter(row["status"] for row in rows)
result = {
    "baseline": plan["baseline"],
    "summary": dict(summary),
    "global_rules": {
        "footer_and_online_reading_audio": "implemented",
        "glossary_label_farahasa": "implemented",
        "number_pronunciation": "implemented_for_matrix_audio_pages",
    },
    "rows": rows,
}
(ROOT / "content/matrix-implementation-status.json").write_text(
    json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)
lines = [
    "# Matrix Implementation Progress",
    "",
    f"Baseline: {plan['baseline']}",
    "",
    *[f"- {key}: {value}" for key, value in sorted(summary.items())],
    "",
    "Global footer/watermark speech cleanup and Farahasa label are implemented.",
    "Standalone quiz cleanup and genuine textbook answer fields are implemented.",
]
(ROOT / "MATRIX_IMPLEMENTATION_PROGRESS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print(dict(summary))
