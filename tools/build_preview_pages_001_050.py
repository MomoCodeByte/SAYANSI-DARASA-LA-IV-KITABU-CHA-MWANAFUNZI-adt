"""Build a focused preview navigator for converted pages 1–50."""

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
audit = json.loads((ROOT / "content/review-pages-001-050.json").read_text(encoding="utf-8"))
pages = audit["pages"]
buttons = "".join(
    f'<button data-href="{html.escape(row["file"])}" data-page="{row["converted_page"]}">{row["converted_page"]}</button>'
    for row in pages
)
document = f'''<!doctype html>
<html lang="sw"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Preview Pages 1–50</title><style>
*{{box-sizing:border-box}}body{{margin:0;background:#17212b;font:15px Arial}}header{{height:52px;display:flex;align-items:center;padding:0 16px;background:#0d768a;color:#fff;font-weight:700}}
main{{display:grid;grid-template-columns:230px 1fr;height:calc(100vh - 52px)}}nav{{overflow:auto;padding:12px;background:#eef5f7;display:grid;grid-template-columns:repeat(5,1fr);gap:7px;align-content:start}}
button{{padding:9px 2px;border:0;border-radius:7px;background:#d1e8ed;cursor:pointer}}button.active{{background:#087f94;color:#fff;font-weight:700}}iframe{{border:0;width:100%;height:100%;background:#fff}}
@media(max-width:700px){{main{{grid-template-columns:1fr}}nav{{height:125px;grid-template-columns:repeat(10,1fr)}}iframe{{height:calc(100vh - 177px)}}}}
</style></head><body><header>Sayansi ADT — Preview ya converted pages 1–50</header><main><nav>{buttons}</nav><iframe title="Preview ya ukurasa"></iframe></main>
<script>const frame=document.querySelector('iframe'),buttons=[...document.querySelectorAll('button')];function openPage(b){{buttons.forEach(x=>x.classList.remove('active'));b.classList.add('active');frame.src=b.dataset.href+'?preview50=1';history.replaceState(null,'','#page-'+b.dataset.page)}}buttons.forEach(b=>b.onclick=()=>openPage(b));const requested=location.hash.replace('#page-','');openPage(buttons.find(b=>b.dataset.page===requested)||buttons[0]);</script>
</body></html>'''
(ROOT / "preview-pages-001-050.html").write_text(document, encoding="utf-8")
print(f"preview_pages={len(pages)}")
