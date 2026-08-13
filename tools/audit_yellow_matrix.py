from pathlib import Path
from zipfile import ZipFile
from lxml import etree
import json

DOCX = Path(r"C:\Users\Admin\Downloads\RIPOTI YA ADT VALIDATION SAYANSI 11.08.2026 (3).docx")
OUT = Path(__file__).resolve().parents[1] / "reports" / "yellow-matrix-rows.json"
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W}


def text(node):
    return " ".join("".join(node.itertext()).split())


def yellow(node):
    for mark in node.xpath(".//w:highlight|.//w:shd", namespaces=NS):
        value = mark.get(f"{{{W}}}val") or mark.get(f"{{{W}}}fill") or ""
        if value.lower() in {"yellow", "ffff00", "fff2cc", "ffff99", "ffffcc"}:
            return True
    return False


with ZipFile(DOCX) as archive:
    root = etree.fromstring(archive.read("word/document.xml"))

tables = []
for ti, table in enumerate(root.xpath("//w:tbl", namespaces=NS), 1):
    rows = []
    for ri, row in enumerate(table.xpath("./w:tr", namespaces=NS), 1):
        cells = row.xpath("./w:tc", namespaces=NS)
        item = {
            "row": ri,
            "cells": [text(cell) for cell in cells],
            "yellow_cells": [i + 1 for i, cell in enumerate(cells) if yellow(cell)],
        }
        if item["yellow_cells"]:
            rows.append(item)
    if rows:
        tables.append({"table": ti, "yellow_rows": rows})

OUT.parent.mkdir(exist_ok=True)
OUT.write_text(json.dumps(tables, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({
    "tables_with_yellow": len(tables),
    "yellow_rows": sum(len(t["yellow_rows"]) for t in tables),
    "output": str(OUT),
}, ensure_ascii=False))
