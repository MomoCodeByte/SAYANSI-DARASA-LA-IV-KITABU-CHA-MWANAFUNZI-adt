import re
from pathlib import Path

root = Path(__file__).resolve().parents[1]
manifest = root / "imsmanifest.xml"
source = manifest.read_text(encoding="utf-8")
source, removed = re.subn(r'^\s*<file href="qz\d+\.html"/>\s*\r?\n', '', source, flags=re.MULTILINE)
manifest.write_text(source, encoding="utf-8")
print(f"Removed {removed} standalone quiz references from imsmanifest.xml")
