"""Move questions 7-8 before Msamiati in actual DOM order, not CSS order only."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / "pg055_sec001.html"
source = path.read_text(encoding="utf-8-sig")
start = source.index('<div class="mb-8 space-y-6 order-1">')
section_end = source.index('</section>', start)
question_end = source.rfind('</div>', start, section_end) + len('</div>')
questions = source[start:question_end].replace(' order-1', '')
source = source[:start] + source[question_end:]
heading = source.index('<h1', source.index('<section'))
source = source[:heading] + questions + source[heading:]
source = source.replace(' max-sm:text-3xl order-2"', ' max-sm:text-3xl"', 1)
source = source.replace(' max-sm:text-base order-3"', ' max-sm:text-base"', 1)
path.write_text(source, encoding="utf-8")
print("pg055_semantic_order=fixed")
