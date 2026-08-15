import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEXTS_PATH = ROOT / "content" / "i18n" / "sw-TZ" / "texts.json"
QUORUM_DESCRIPTION = (
    "Quorum ni programu fikivu ya kuandika, kuhariri na kuendesha msimbo wa "
    "programu kwa kutumia maandishi."
)
CACHE_VERSION = "chapter6-quorum-images-80"


def append_description(text: str) -> str:
    text = text.strip()
    if QUORUM_DESCRIPTION in text:
        return text
    separator = " " if text.endswith((".", "!", "?")) else ". "
    return f"{text}{separator}{QUORUM_DESCRIPTION}"


texts = json.loads(TEXTS_PATH.read_text(encoding="utf-8"))
changed_ids: set[str] = set()

for page_number in range(120, 129):
    page_path = ROOT / f"pg{page_number:03d}_sec001.html"
    if not page_path.exists():
        continue

    source = page_path.read_text(encoding="utf-8")

    def update_span(match: re.Match[str]) -> str:
        prefix, item_id, body, suffix = match.groups()
        changed_ids.add(item_id)
        return f"{prefix}{item_id}{body[0:0]}{append_description(body)}{suffix}"

    span_pattern = re.compile(
        r'(<span\s+data-id=")([^"]+)("\s+class="sr-only image-audio-description">)(.*?)(</span>)',
        re.DOTALL,
    )

    def update_span_safe(match: re.Match[str]) -> str:
        opening, item_id, middle, body, closing = match.groups()
        changed_ids.add(item_id)
        return f"{opening}{item_id}{middle}{append_description(body)}{closing}"

    source = span_pattern.sub(update_span_safe, source)

    def update_alt(match: re.Match[str]) -> str:
        before, item_id, between, alt_text, after = match.groups()
        changed_ids.add(item_id)
        return f'{before}{item_id}{between}{append_description(alt_text)}{after}'

    image_pattern = re.compile(
        r'(<img\s+[^>]*?data-id=")([^"]+)("[^>]*?alt=")([^"]*)("[^>]*>)',
        re.DOTALL,
    )
    source = image_pattern.sub(update_alt, source)
    source = re.sub(
        r'(\./assets/(?:offline-preloader|base\.bundle\.local|matrix-accessibility)\.js)\?v=[^"]+',
        rf'\1?v={CACHE_VERSION}',
        source,
    )
    page_path.write_text(source, encoding="utf-8")

for item_id in sorted(changed_ids):
    if item_id in texts:
        texts[item_id] = append_description(texts[item_id])

TEXTS_PATH.write_text(
    json.dumps(texts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)

print(json.dumps({"updated_ids": sorted(changed_ids), "count": len(changed_ids)}, ensure_ascii=False))
