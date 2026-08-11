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
    8, 10, 14, 26, 30, 32, 33, 65, 66, 75, 77, 78, 80, 81, 84, 102, 103, 148, 182,
}
rows = []
for item in plan["items"]:
    number = item["matrix_item"]
    if item["status"] == "hold_user_instruction":
        status = "HOLD_ANSWER_SPACE"
    elif item["status"] == "conflict_needs_user_decision":
        status = "HOLD_QUIZ_CONFLICT"
    elif number == 152:
        status = "HOLD_ANSWER_CHOICE"
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
    "Quiz conflicts and answer-field/answer-choice changes remain on hold by user instruction.",
]
(ROOT / "MATRIX_IMPLEMENTATION_PROGRESS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print(dict(summary))
