from pathlib import Path
import json
from lxml import html, etree

root=Path(__file__).resolve().parents[1]
tp=root/'content/i18n/sw-TZ/texts.json'; texts=json.loads(tp.read_text(encoding='utf-8'))
changed=[]
for n in range(35,57):
    p=root/f'pg{n:03d}_sec001.html'; doc=html.fromstring(p.read_text(encoding='utf-8')); dirty=False
    for el in doc.xpath('//*[@data-id]'):
        did=el.get('data-id'); old=' '.join(el.text_content().split()); new=old
        if 'Kielelezo namba' in old and ':' not in old and 'kinaonesha' in old and 'kinabainisha' not in old:
            new=old.replace('kinaonesha','kinaonesha/kinabainisha',1)
        if new != old and len(el)==0:
            el.text=new; texts[did]=new; dirty=True
    # These became duplicate fragments after the matrix-required completion was added.
    for did in ('pg037_n0002','pg046_n0028'):
        found=doc.xpath(f'//*[@data-id="{did}"]')
        for el in found:
            el.getparent().remove(el); texts.pop(did,None); dirty=True
    if dirty:
        p.write_text(etree.tostring(doc,encoding='unicode',method='html',doctype='<!DOCTYPE html>'),encoding='utf-8');changed.append(p.name)
tp.write_text(json.dumps(texts,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('updated',len(changed),'pages',changed)
