from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
yellow = json.loads((ROOT / "reports/yellow-matrix-rows.json").read_text(encoding="utf-8"))[0]["yellow_rows"]
plan = {x["matrix_item"]: x for x in json.loads((ROOT / "content/validation-matrix-plan.json").read_text(encoding="utf-8"))["items"]}
status = {x["matrix_item"]: x for x in json.loads((ROOT / "content/matrix-implementation-status.json").read_text(encoding="utf-8"))["rows"]}

records = []
for row in yellow:
    item_number = row["row"] - 1  # Word table row 1 is the header.
    source = plan[item_number]
    implementation = status[item_number]
    records.append({
        "yellow_table_row": row["row"],
        "matrix_item": item_number,
        "area": source["area"],
        "page": source["reference"],
        "recommendation": source["recommendation"],
        "files": source["files"],
        "status": implementation["status"],
    })

summary = {}
for record in records:
    summary[record["status"]] = summary.get(record["status"], 0) + 1

result = {
    "source": "RIPOTI YA ADT VALIDATION SAYANSI 11.08.2026 (3).docx",
    "yellow_rows": len(records),
    "pending": sum(1 for r in records if r["status"].startswith("PENDING")),
    "summary": summary,
    "records": records,
}
(ROOT / "reports/yellow-matrix-audit.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

lines = [
    "# Ukaguzi wa maeneo ya njano ya matrix",
    "",
    f"- Mistari yenye njano: {len(records)}",
    f"- Mistari inayosubiri utekelezaji: {result['pending']}",
    "- Footer/ONLINE READING ONLY: imetengwa na audio",
    "- Namba: hubadilishwa na kutamkwa kwa Kiswahili",
    "- Audio na word-highlight: faili na timecode zimehakikiwa",
    "",
    "## Muhtasari wa utekelezaji",
    "",
]
lines.extend(f"- {key}: {value}" for key, value in sorted(summary.items()))
(ROOT / "reports/yellow-matrix-audit.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print(json.dumps({"yellow_rows": len(records), "pending": result["pending"], "summary": summary}, ensure_ascii=False))
