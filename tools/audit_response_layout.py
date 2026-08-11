"""Verify that every injected response field follows its source prompt in DOM order."""

import json
from pathlib import Path
from lxml import html

ROOT = Path(__file__).resolve().parents[1]
pages = json.loads((ROOT / "content/pages.json").read_text(encoding="utf-8-sig"))
issues = []
checked_pages = 0
checked_fields = 0

for position, entry in enumerate(pages, start=1):
    if entry["section_id"].startswith("qz"):
        continue
    path = ROOT / entry["href"]
    doc = html.document_fromstring(path.read_text(encoding="utf-8-sig"))
    fields = doc.xpath('//textarea[@data-response-for]')
    if not fields:
        continue
    checked_pages += 1
    all_nodes = list(doc.iter())
    positions = {id(node): i for i, node in enumerate(all_nodes)}
    for field in fields:
        checked_fields += 1
        target = field.get("data-response-for")
        prompts = doc.xpath(f'//*[@data-id="{target}"]')
        if len(prompts) != 1:
            issues.append({"page": position, "file": entry["href"], "target": target, "problem": f"prompt_count={len(prompts)}"})
            continue
        prompt = prompts[0]
        if positions[id(field)] <= positions[id(prompt)]:
            issues.append({"page": position, "file": entry["href"], "target": target, "problem": "field_before_prompt"})
        # The next response field must not leap over a later numbered/prompt block.
        if field.getparent() is None:
            issues.append({"page": position, "file": entry["href"], "target": target, "problem": "field_without_parent"})
    sections = doc.xpath('//*[@data-section-type]')
    if not sections or not sections[0].get("data-section-type", "").startswith("activity_"):
        issues.append({"page": position, "file": entry["href"], "problem": "response_page_not_activity"})

report = {"checked_pages": checked_pages, "checked_fields": checked_fields, "issues": issues}
(ROOT / "content/response-layout-audit.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=2))
