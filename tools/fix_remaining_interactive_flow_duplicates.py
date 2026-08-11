"""Remove known duplicate question/header copies while preserving inline answer controls."""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

path = ROOT / "pg055_sec001.html"
source = path.read_text(encoding="utf-8-sig")
source, count_55 = re.subn(
    r'<div class="mb-8 rounded-\[1\.75rem\] bg-sky-100 px-8 py-6 max-sm:px-5 max-sm:py-5"><div class="space-y-6[^>]*hidden[^>]*>.*?</div></div><h1',
    '<h1', source, count=1, flags=re.S,
)
path.write_text(source, encoding="utf-8")

path = ROOT / "pg094_sec001.html"
source = path.read_text(encoding="utf-8-sig")
source, count_94 = re.subn(
    r'<p class="text-xl mb-8"><i[^>]*></i><span data-id="pg094_n0002">.*?</span></p>',
    '', source, count=1, flags=re.S,
)
path.write_text(source, encoding="utf-8")
print(f"pg055_removed={count_55} pg094_removed={count_94}")
