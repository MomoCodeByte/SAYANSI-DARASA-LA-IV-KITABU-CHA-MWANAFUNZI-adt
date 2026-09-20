"""Rebuild offline resources from canonical files and pages.json reading order."""

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRELOADER = ROOT / "assets/offline-preloader.js"
MARKER = "  var INLINE = "

def load(path: Path):
    text = path.read_text(encoding="utf-8-sig")
    return json.loads(text) if path.suffix.lower() == ".json" else text

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--all-active", action="store_true",
                    help="Also refresh the preloaders referenced by reading pages.")
args = parser.parse_args()
pages = json.loads((ROOT / "content/pages.json").read_text(encoding="utf-8-sig"))
preloaders = {PRELOADER}
if args.all_active:
    for entry in pages:
        html = (ROOT / entry["href"]).read_text(encoding="utf-8-sig")
        preloaders.update(ROOT / name for name in re.findall(
            r'src="\./(assets/offline-preloader[^"?]*\.js)', html))

updates = []
for preloader in sorted(preloaders):
    source = preloader.read_text(encoding="utf-8-sig")
    start = source.index(MARKER) + len(MARKER)
    old, consumed = json.JSONDecoder().raw_decode(source[start:])
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
        raise SystemExit(f"Missing offline resources in {preloader.name}: {missing}")
    payload = json.dumps(inline, ensure_ascii=False, separators=(",", ":"))
    updates.append((preloader, source[:start] + payload + source[start + consumed :]))

for preloader, source in updates:
    preloader.write_text(source, encoding="utf-8")
print(json.dumps({"preloaders": len(updates), "reading_pages": len(pages), "missing": 0}, indent=2))
