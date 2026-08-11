"""Build a preview navigator from the canonical pages.json reading order."""

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
pages = json.loads((ROOT / "content/pages.json").read_text(encoding="utf-8-sig"))
buttons = "".join(
    f'<button data-href="{html.escape(entry["href"])}" data-page="{position}">{position}</button>'
    for position, entry in enumerate(pages, start=1)
)
document = f'''<!doctype html><html lang="sw"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Full Book Preview</title><style>*{{box-sizing:border-box}}body{{margin:0;background:#17212b;font:15px Arial}}header{{height:52px;display:flex;align-items:center;padding:0 16px;background:#0d768a;color:#fff;font-weight:700}}main{{display:grid;grid-template-columns:250px 1fr;height:calc(100vh - 52px)}}nav{{overflow:auto;padding:12px;background:#eef5f7;display:grid;grid-template-columns:repeat(5,1fr);gap:7px;align-content:start}}button{{padding:9px 2px;border:0;border-radius:7px;background:#d1e8ed;cursor:pointer}}button.active{{background:#087f94;color:#fff;font-weight:700}}iframe{{border:0;width:100%;height:100%;background:#fff}}@media(max-width:700px){{main{{grid-template-columns:1fr}}nav{{height:145px;grid-template-columns:repeat(10,1fr)}}iframe{{height:calc(100vh - 197px)}}}}</style></head>
<body><header>Sayansi ADT - Full Book Preview (reading order halisi)</header><main><nav>{buttons}</nav><iframe title="Preview ya ukurasa"></iframe></main>
<script>const f=document.querySelector('iframe'),bs=[...document.querySelectorAll('button')];function openPage(b){{bs.forEach(x=>x.classList.remove('active'));b.classList.add('active');f.src=b.dataset.href+'?full-preview=1';history.replaceState(null,'','#page-'+b.dataset.page)}}bs.forEach(b=>b.onclick=()=>openPage(b));const p=location.hash.replace('#page-','');openPage(bs.find(b=>b.dataset.page===p)||bs[0]);</script></body></html>'''
(ROOT / "preview-full-book.html").write_text(document, encoding="utf-8")
print(f"preview_pages={len(pages)}")
