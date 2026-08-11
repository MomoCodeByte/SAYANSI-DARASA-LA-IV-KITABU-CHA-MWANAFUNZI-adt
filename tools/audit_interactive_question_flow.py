"""Find interactive pages whose question text IDs are duplicated in the same page."""

import collections
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
pages = json.loads((ROOT / "content/pages.json").read_text(encoding="utf-8-sig"))
texts = json.loads((ROOT / "content/i18n/sw-TZ/texts.json").read_text(encoding="utf-8-sig"))
rows = []
for position, entry in enumerate(pages, start=1):
    path = ROOT / entry["href"]
    source = path.read_text(encoding="utf-8-sig")
    if "<textarea" not in source:
        continue
    counts = collections.Counter(re.findall(r'data-id="([^"]+)"', source))
    duplicates = {key: value for key, value in counts.items() if value > 1 and not key.endswith("_easy_read")}
    ids = list(dict.fromkeys(re.findall(r'data-id="([^"]+)"', source)))
    values = collections.defaultdict(list)
    for data_id in ids:
        value = " ".join(str(texts.get(data_id, "")).split()).casefold()
        if len(value) >= 30:
            values[value].append(data_id)
    repeated_text = {value: data_ids for value, data_ids in values.items() if len(data_ids) > 1}
    rows.append({
        "converted_page": position,
        "file": path.name,
        "textareas": source.count("<textarea"),
        "duplicate_ids": duplicates,
        "repeated_text": repeated_text,
    })
result = {
    "pages_with_textareas": len(rows),
    "pages_with_duplicate_ids": sum(bool(row["duplicate_ids"]) for row in rows),
    "pages_with_repeated_text": sum(bool(row["repeated_text"]) for row in rows),
    "pages": rows,
}
(ROOT / "content/interactive-flow-audit.json").write_text(
    json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)
print(json.dumps({key: value for key, value in result.items() if key != "pages"}, indent=2))
for row in rows:
    if row["duplicate_ids"] or row["repeated_text"]:
        print(row)
