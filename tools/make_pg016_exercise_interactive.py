"""Make questions 1-3 on converted page 19 interactive like continuation page 20."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / "pg016_sec001.html"
source = path.read_text(encoding="utf-8-sig")

def matching_div_end(text: str, start: int) -> int:
    depth = 0
    cursor = start
    while True:
        opening = text.find("<div", cursor)
        closing = text.find("</div>", cursor)
        if closing < 0:
            raise RuntimeError("Unclosed div")
        if opening >= 0 and opening < closing:
            depth += 1
            cursor = opening + 4
        else:
            depth -= 1
            cursor = closing + len("</div>")
            if depth == 0:
                return cursor

questions = [
    ("pg016_n0014", '<div class="mb-5 flex items-start gap-5 max-sm:gap-3">', "aria-pg016-1", "Jibu la swali la 1 kuhusu mlo wa Maria"),
    ("pg016_n0018", '<div class="mb-5 flex items-start gap-5 max-sm:gap-3">', "aria-pg016-2", "Jibu la swali la 2 kuhusu kupanga mlo kamili wa mgonjwa"),
    ("pg016_n0021", '<div class="flex items-start gap-5 max-sm:gap-3">', "aria-pg016-3", "Jibu la swali la 3 kuhusu tofauti ya mahitaji ya mlo"),
]
for marker, opening, aria_id, label in reversed(questions):
    marker_at = source.index(f'data-id="{marker}"')
    start = source.rfind(opening, 0, marker_at)
    if start < 0:
        raise RuntimeError(f"Question container not found: {marker}")
    end = matching_div_end(source, start)
    question = source[start:end].replace('class="mb-5 flex ', 'class="flex ', 1)
    textarea = (
        f'<textarea class="mt-3 w-full bg-transparent border-0 border-b border-dotted border-slate-400 '
        f'rounded-none min-h-16 resize-y focus:outline-none focus:ring-0" data-aria-id="{aria_id}" '
        f'aria-label="{label}" tabindex="0"></textarea>'
    )
    source = source[:start] + f'<div class="mb-5">{question}{textarea}</div>' + source[end:]

source = source.replace('data-section-type="text_and_single_image"', 'data-section-type="activity_open_ended_answer"', 1)
source = source.replace('offline-preloader.js?v=full-order-1', 'offline-preloader.js?v=exercise-inputs-9', 1)
path.write_text(source, encoding="utf-8")
print("pg016_questions_interactive=3")
