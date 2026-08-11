"""Add answer controls in place to the remaining static exercise pages."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

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

def add_after_container(source: str, marker: str, opening: str, control: str) -> str:
    marker_at = source.index(f'data-id="{marker}"')
    start = source.rfind(opening, 0, marker_at)
    if start < 0:
        raise RuntimeError(f"Container missing for {marker}")
    end = matching_div_end(source, start)
    return source[:end] + control + source[end:]

textarea = lambda aria, label: (
    f'<textarea class="mt-3 w-full rounded-md border border-sky-400 bg-white px-3 py-2 min-h-16 resize-y '
    f'focus:outline-none focus:ring-2 focus:ring-sky-300" data-aria-id="{aria}" '
    f'aria-label="{label}" tabindex="0"></textarea>'
)

# Converted page 36: answer control remains with the original review question.
path = ROOT / "pg030_sec001.html"
source = path.read_text(encoding="utf-8-sig")
source = add_after_container(
    source, "pg030_n0024", '<div class="flex items-start gap-4 max-sm:gap-3">',
    textarea("aria-pg030-review-1", "Jibu la swali la kwanza la Zoezi la marudio"),
)
source = source.replace('data-section-type="text_and_single_image"', 'data-section-type="activity_open_ended_answer"', 1)
source = source.replace('offline-preloader.js?v=full-order-1', 'offline-preloader.js?v=static-exercises-10', 1)
path.write_text(source, encoding="utf-8")

# Converted page 46: four malaria questions receive compact answer controls in place.
path = ROOT / "pg038_sec001.html"
source = path.read_text(encoding="utf-8-sig")
opening = '<div class="grid grid-cols-[2.5rem_1fr] items-start gap-x-3 max-sm:grid-cols-[1.75rem_1fr] max-sm:gap-x-2">'
for number, marker, label in reversed([
    (1, "pg038_n0023", "Jibu kuhusu dalili nne za malaria"),
    (2, "pg038_n0025", "Jibu kuhusu umuhimu wa kulala kwenye chandarua"),
    (3, "pg038_n0027", "Jibu kuhusu namna malaria inavyoambukizwa"),
    (4, "pg038_n0029", "Jibu kuhusu kujikinga dhidi ya malaria"),
]):
    source = add_after_container(source, marker, opening, textarea(f"aria-pg038-{number}", label))
source = source.replace('data-section-type="text_only"', 'data-section-type="activity_open_ended_answer"', 1)
source = source.replace('offline-preloader.js?v=full-order-1', 'offline-preloader.js?v=static-exercises-10', 1)
path.write_text(source, encoding="utf-8")

# Converted page 64: matching response stays directly with its original instruction/table.
path = ROOT / "pg053_sec001.html"
source = path.read_text(encoding="utf-8-sig")
source = add_after_container(
    source, "pg053_n0023", '<div class="flex items-start gap-4 max-sm:gap-3">',
    textarea("aria-pg053-match", "Andika uoanifu wa magonjwa na dalili zake"),
)
source = source.replace('data-section-type="text_and_single_image"', 'data-section-type="activity_open_ended_answer"', 1)
source = source.replace('offline-preloader.js?v=full-order-1', 'offline-preloader.js?v=static-exercises-10', 1)
path.write_text(source, encoding="utf-8")
print("static_exercises_made_interactive=3 answer_controls_added=6")
