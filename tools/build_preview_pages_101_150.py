from pathlib import Path

root = Path(__file__).resolve().parents[1]
pages = [(p, f"pg{p-1:03d}_sec001.html") for p in range(101, 144)] + [(p, f"pg{p:03d}_sec001.html") for p in range(144, 151)]
buttons = "".join(f'<button data-href="{f}" data-page="{p}">{p}</button>' for p, f in pages if (root / f).exists())
out = f'''<!doctype html><html lang="sw"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Preview Pages 101-150</title><style>*{{box-sizing:border-box}}body{{margin:0;background:#17212b;font:15px Arial}}header{{height:52px;display:flex;align-items:center;padding:0 16px;background:#0d768a;color:#fff;font-weight:700}}main{{display:grid;grid-template-columns:230px 1fr;height:calc(100vh - 52px)}}nav{{overflow:auto;padding:12px;background:#eef5f7;display:grid;grid-template-columns:repeat(5,1fr);gap:7px;align-content:start}}button{{padding:9px 2px;border:0;border-radius:7px;background:#d1e8ed;cursor:pointer}}button.active{{background:#087f94;color:#fff;font-weight:700}}iframe{{border:0;width:100%;height:100%;background:#fff}}@media(max-width:700px){{main{{grid-template-columns:1fr}}nav{{height:125px;grid-template-columns:repeat(10,1fr)}}iframe{{height:calc(100vh - 177px)}}}}</style></head>
<body><header>Sayansi ADT - Preview ya kurasa 101–150</header><main><nav>{buttons}</nav><iframe title="Preview ya ukurasa"></iframe></main>
<script>const frame=document.querySelector('iframe'),buttons=[...document.querySelectorAll('button')];function openPage(b){{buttons.forEach(x=>x.classList.remove('active'));b.classList.add('active');frame.src=b.dataset.href+'?preview150=matrix3-78';history.replaceState(null,'','#page-'+b.dataset.page)}}buttons.forEach(b=>b.onclick=()=>openPage(b));const requested=location.hash.replace('#page-','');openPage(buttons.find(b=>b.dataset.page===requested)||buttons[0]);</script></body></html>'''
for name in ("preview-pages-101-150.html", "preview-matrix3-pages101-150.html"):
    (root / name).write_text(out, encoding="utf-8")
print(f"preview-pages-101-150.html: {len(pages)} pages")
