"""Version the offline preloader reference on every canonical reading page."""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
pages = json.loads((ROOT / "content/pages.json").read_text(encoding="utf-8-sig"))
CACHE_VERSION = "matrix-final-59"
updated = 0
for entry in pages:
    path = ROOT / entry["href"]
    source = path.read_text(encoding="utf-8-sig")
    normalized = re.sub(
        r'(<script\s+src="\./assets/offline-preloader\.js)(?:\?v=[^"]*)?("[^>]*></script>)',
        rf'\1?v={CACHE_VERSION}\2', source,
    )
    normalized = re.sub(
        r'(<script\s+src="\./assets/matrix-accessibility\.js)(?:\?v=[^"]*)?("[^>]*></script>)',
        rf'\1?v={CACHE_VERSION}\2', normalized,
    )
    if normalized != source:
        path.write_text(normalized, encoding="utf-8")
        updated += 1
print(f"cache_busted_pages={updated}")
