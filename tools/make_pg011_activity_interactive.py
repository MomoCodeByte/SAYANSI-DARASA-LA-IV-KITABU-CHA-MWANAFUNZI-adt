"""Add answer controls to Kazi ya kufanya namba 3 on converted page 12."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / "pg011_sec001.html"
source = path.read_text(encoding="utf-8-sig")

def matching_div_end(text: str, start: int) -> int:
    depth, cursor = 0, start
    while True:
        opening, closing = text.find("<div", cursor), text.find("</div>", cursor)
        if closing < 0:
            raise RuntimeError("Unclosed div")
        if opening >= 0 and opening < closing:
            depth += 1
            cursor = opening + 4
        else:
            depth -= 1
            cursor = closing + 6
            if depth == 0:
                return cursor

questions = [
    ("pg011_n0023", '<div class="flex items-start gap-4 text-[28px] leading-[1.28] text-neutral-800 max-lg:text-[22px] max-sm:gap-3 max-sm:text-[18px]">', "aria-pg011-1", "Jibu la swali la kwanza kuhusu kupanga mlo kamili wa mchana"),
    ("pg011_n0025", '<div class="mt-5 flex items-start gap-4 text-[28px] leading-[1.28] text-neutral-800 max-lg:text-[22px] max-sm:gap-3 max-sm:text-[18px]">', "aria-pg011-2", "Jibu la swali la pili kuhusu umuhimu wa vyakula katika mlo"),
]
for marker, opening, aria_id, label in reversed(questions):
    marker_at = source.index(f'data-id="{marker}"')
    start = source.rfind(opening, 0, marker_at)
    end = matching_div_end(source, start)
    block = source[start:end].replace('class="mt-5 flex ', 'class="flex ', 1)
    control = f'<textarea class="mt-3 w-full rounded-md border border-sky-400 bg-white px-3 py-2 min-h-16 resize-y focus:outline-none focus:ring-2 focus:ring-sky-300" data-aria-id="{aria_id}" aria-label="{label}" tabindex="0"></textarea>'
    source = source[:start] + f'<div class="mt-5">{block}{control}</div>' + source[end:]
source = source.replace('data-section-type="text_and_single_image"', 'data-section-type="activity_open_ended_answer"', 1)
source = source.replace('offline-preloader.js?v=full-order-1', 'offline-preloader.js?v=kazi-inputs-11', 1)
path.write_text(source, encoding="utf-8")
print("pg011_kazi_3_interactive=2")
