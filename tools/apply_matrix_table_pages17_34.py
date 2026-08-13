from pathlib import Path
import json
from lxml import html, etree

root = Path(__file__).resolve().parents[1]
tp = root / "content/i18n/sw-TZ/texts.json"
texts = json.loads(tp.read_text(encoding="utf-8"))
exact = {
    "pg024_n0019": "Kielelezo namba 14: Mifano ya alama za kuzuia au kukataza",
}
changed=[]
for n in range(17,35):
    p=root/f"pg{n:03d}_sec001.html"
    doc=html.fromstring(p.read_text(encoding="utf-8")); dirty=False
    for el in doc.xpath('//*[@data-id]'):
        did=el.get('data-id'); old=' '.join(el.text_content().split()); new=exact.get(did,old)
        if did not in exact and 'Kielelezo namba' in old and ':' not in old and 'kinaonesha' in old and 'kinabainisha' not in old:
            new=old.replace('kinaonesha','kinaonesha/kinabainisha',1)
        if new != old and len(el)==0:
            el.text=new; texts[did]=new; dirty=True
    if dirty:
        p.write_text(etree.tostring(doc,encoding='unicode',method='html',doctype='<!DOCTYPE html>'),encoding='utf-8'); changed.append(p.name)
tp.write_text(json.dumps(texts,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('updated',len(changed),'pages',changed)
