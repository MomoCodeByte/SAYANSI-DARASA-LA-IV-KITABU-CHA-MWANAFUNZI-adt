"""Normalize multi-panel figure narration: caption, then Picha A/B/C descriptions."""

from __future__ import annotations

import html
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEXTS_PATH = ROOT / "content" / "i18n" / "sw-TZ" / "texts.json"
IDS_PATH = ROOT / "content" / "multi-panel-image-audio-ids.json"

NODE = re.compile(
    r'<(?P<tag>span|div|p|figcaption)\b(?P<attrs>[^>]*\bdata-id="(?P<id>[^"]+)"[^>]*)>'
    r'(?P<body>[\s\S]*?)</(?P=tag)>',
    re.I,
)
DESC_SPAN = re.compile(
    r'(?P<open><span\b[^>]*\bdata-id="(?P<id>[^"]+)"[^>]*\bimage-audio-description\b[^>]*>)'
    r'(?P<body>[^<]*)(?P<close></span>)',
    re.I,
)
CAPTION = re.compile(r'^Kielelezo\s+namba\s+\d+(?:\s*\([^)]+\))?', re.I)
PREFIX = re.compile(
    r'^(?:Maelezo\s+ya\s+)?Picha\s+(?P<letter>[A-Z])(?:\s*[,.:;-]\s*|\s+)',
    re.I,
)


def plain(value: str) -> str:
    value = re.sub(r'<[^>]+>', ' ', value)
    return re.sub(r'\s+', ' ', html.unescape(value)).strip()


def normalize_description(value: str, letter: str) -> str:
    detail = PREFIX.sub('', value.strip()).strip()
    detail = re.sub(r'^Maelezo\s+ya\s+picha\s*:\s*', '', detail, flags=re.I)
    return f"Picha {letter}. {detail}" if detail else f"Picha {letter}."


def main() -> None:
    texts = json.loads(TEXTS_PATH.read_text(encoding='utf-8'))
    existing_ids = set(json.loads(IDS_PATH.read_text(encoding='utf-8'))) if IDS_PATH.exists() else set()
    changed_ids: set[str] = set()
    changed_pages: set[str] = set()
    figures = 0

    for path in sorted(ROOT.glob('pg*_sec*.html')):
        source = path.read_text(encoding='utf-8-sig')
        nodes = []
        for match in NODE.finditer(source):
            nodes.append({
                'id': match.group('id'),
                'text': plain(match.group('body')),
                'is_desc': 'image-audio-description' in match.group('attrs'),
            })

        grouped: dict[str, list[str]] = defaultdict(list)
        for index, node in enumerate(nodes):
            if not node['is_desc']:
                continue
            caption_id = None
            for lookahead in range(index + 1, min(len(nodes), index + 24)):
                candidate = nodes[lookahead]
                if CAPTION.match(candidate['text']):
                    caption_id = candidate['id']
                    break
                if candidate['is_desc'] and lookahead > index + 8:
                    break
            if caption_id:
                grouped[caption_id].append(node['id'])

        multi_ids = {item for group in grouped.values() if len(group) > 1 for item in group}
        figures += sum(1 for group in grouped.values() if len(group) > 1)
        if not multi_ids:
            continue

        group_letters = {
            text_id: chr(ord('A') + position)
            for group in grouped.values() if len(group) > 1
            for position, text_id in enumerate(group)
        }

        def replace(match: re.Match[str]) -> str:
            text_id = match.group('id')
            if text_id not in multi_ids:
                return match.group(0)
            normalized = normalize_description(html.unescape(match.group('body')), group_letters[text_id])
            texts[text_id] = normalized
            if normalized != html.unescape(match.group('body')).strip():
                changed_ids.add(text_id)
                changed_pages.add(path.name)
            return match.group('open') + html.escape(normalized, quote=False) + match.group('close')

        updated = DESC_SPAN.sub(replace, source)
        if updated != source:
            path.write_text(updated, encoding='utf-8')

    TEXTS_PATH.write_text(json.dumps(texts, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    all_changed_ids = existing_ids | changed_ids
    IDS_PATH.write_text(json.dumps(sorted(all_changed_ids), ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({
        'multi_panel_figures': figures,
        'changed_pages': len(changed_pages),
        'changed_audio_ids_this_run': len(changed_ids),
        'audio_ids_to_render': len(all_changed_ids),
        'pages': sorted(changed_pages),
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
