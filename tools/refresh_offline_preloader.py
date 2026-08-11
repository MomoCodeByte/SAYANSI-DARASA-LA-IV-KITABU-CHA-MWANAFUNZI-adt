"""Rebuild offline resources from canonical files and pages.json reading order."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRELOADER = ROOT / "assets/offline-preloader.js"
MARKER = "  var INLINE = "

def load(path: Path):
    text = path.read_text(encoding="utf-8-sig")
    return json.loads(text) if path.suffix.lower() == ".json" else text

source = PRELOADER.read_text(encoding="utf-8-sig")
start = source.index(MARKER) + len(MARKER)
old, consumed = json.JSONDecoder().raw_decode(source[start:])
pages = json.loads((ROOT / "content/pages.json").read_text(encoding="utf-8-sig"))
keys = [key for key in old if not key.lower().endswith(".html")]
keys.extend("./" + entry["href"].lstrip("./") for entry in pages)
inline, missing = {}, []
for key in dict.fromkeys(keys):
    path = ROOT / key.removeprefix("./")
    if path.is_file():
        inline[key] = load(path)
    else:
        missing.append(key)
if missing:
    raise SystemExit(f"Missing offline resources: {missing}")
payload = json.dumps(inline, ensure_ascii=False, separators=(",", ":"))
PRELOADER.write_text(source[:start] + payload + source[start + consumed :], encoding="utf-8")
print(json.dumps({"inline_resources": len(inline), "reading_pages": len(pages), "missing": 0}, indent=2))
