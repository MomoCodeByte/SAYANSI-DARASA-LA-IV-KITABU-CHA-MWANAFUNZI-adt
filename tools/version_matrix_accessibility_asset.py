#!/usr/bin/env python3
"""Cache-bust the shared matrix accessibility runtime on every book page."""

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
VERSION = "heading-consistency-v9"
pattern = re.compile(r"(assets/matrix-accessibility\.js\?v=)[^\"']+")
changed = 0
for page in ROOT.glob("pg*_sec*.html"):
    source = page.read_text(encoding="utf-8-sig")
    updated = pattern.sub(rf"\g<1>{VERSION}", source)
    if updated != source:
        page.write_text(updated, encoding="utf-8")
        changed += 1
print({"version": VERSION, "pages_changed": changed})
