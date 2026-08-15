"""Version the offline preloader reference on every canonical reading page."""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
pages = json.loads((ROOT / "content/pages.json").read_text(encoding="utf-8-sig"))
CACHE_VERSION = "page-frame-94"
updated = 0
reading_paths = [ROOT / entry["href"] for entry in pages]
reading_paths.extend(sorted(ROOT.glob("pg*_sec*.html")))
for path in dict.fromkeys(reading_paths):
    source = path.read_text(encoding="utf-8-sig")
    normalized = re.sub(
        r'(<script\s+src="\./assets/offline-preloader\.js)(?:\?v=[^"]*)?("[^>]*></script>)',
        rf'\1?v={CACHE_VERSION}\2', source,
    )
    normalized = re.sub(
        r'(<link\s+href="\./assets/fonts\.css)(?:\?v=[^"]*)?("[^>]*>)',
        rf'\1?v={CACHE_VERSION}\2', normalized,
    )
    normalized = re.sub(
        r'(<script\s+src="\./assets/matrix-accessibility\.js)(?:\?v=[^"]*)?("[^>]*></script>)',
        rf'\1?v={CACHE_VERSION}\2', normalized,
    )
    normalized = re.sub(
        r'(<script\s+src="\./assets/base\.bundle\.local\.js)(?:\?v=[^"]*)?("[^>]*></script>)',
        rf'\1?v={CACHE_VERSION}\2', normalized,
    )
    if normalized != source:
        path.write_text(normalized, encoding="utf-8")
        updated += 1
print(f"cache_busted_pages={updated}")
