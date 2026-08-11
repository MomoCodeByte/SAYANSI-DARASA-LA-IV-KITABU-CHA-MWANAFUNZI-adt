"""Synchronize the canonical interface translation into the offline bundle cache."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRELOADER = ROOT / "assets/offline-preloader.js"
KEY = "./assets/interface_translations/sw-TZ/interface_translations.json"
MARKER = "  var INLINE = "

source = PRELOADER.read_text(encoding="utf-8-sig")
start = source.index(MARKER) + len(MARKER)
inline, consumed = json.JSONDecoder().raw_decode(source[start:])
inline[KEY] = json.loads((ROOT / KEY.removeprefix("./")).read_text(encoding="utf-8-sig"))
payload = json.dumps(inline, ensure_ascii=False, separators=(",", ":"))
PRELOADER.write_text(source[:start] + payload + source[start + consumed :], encoding="utf-8")
print(f"synced={KEY} glossary-label={inline[KEY].get('glossary-label')}")
