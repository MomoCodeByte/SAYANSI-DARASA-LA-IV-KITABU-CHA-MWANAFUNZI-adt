from pathlib import Path
import json
from lxml import html, etree

root=Path(__file__).resolve().parents[1]
tp=root/'content/i18n/sw-TZ/texts.json'; texts=json.loads(tp.read_text(encoding='utf-8'))
exact={
 'pg058_n0016':'Majaribio namba 1–4 yatatumika kuchunguza na kubainisha hali tatu za maada kwa kutumia maji.',
 'pg058_n0026':'Vipande sita vya barafu vyenye ukubwa sawa, sufuria, deli la kutunzia barafu, kitu chenye uso ulionyooka kama vile sinia, jagi, jiko au chanzo chochote cha moto, programu saidizi na kipimajoto sauti.',
 'pg060_n0009':'Jagi, sufuria, maji safi na salama, mfuko wa plastiki, kikombe safi na programu saidizi.',
 'pg060_n0020':'Je, umeona, umehisi au umetambua rangi gani?',
 'pg061_n0014':'Maji, sufuria, kioo, kipimajoto, kipimajoto sauti, chanzo cha moto (jiko) na programu saidizi.',
 'pg061_n0035':'Andika ulichoona, ulichohisi au ulichotambua.',
 'pg062_n0021':'Kioo, glasi, maji, birika, chanzo cha moto (jiko) na programu saidizi.',
}
changed=[]
for n in range(57,73):
 p=root/f'pg{n:03d}_sec001.html'; doc=html.fromstring(p.read_text(encoding='utf-8'));dirty=False
 for el in doc.xpath('//*[@data-id]'):
  did=el.get('data-id');old=' '.join(el.text_content().split());new=exact.get(did,old)
  if did not in exact and 'Kielelezo namba' in old and ':' not in old and 'kinaonesha' in old and 'kinabainisha' not in old:
   new=old.replace('kinaonesha','kinaonesha/kinabainisha',1)
  if new!=old and len(el)==0:
   el.text=new;texts[did]=new;dirty=True
 if dirty:
  p.write_text(etree.tostring(doc,encoding='unicode',method='html',doctype='<!DOCTYPE html>'),encoding='utf-8');changed.append(p.name)

# Matrix global rule: production watermarks, INDD timestamps and online-reading footers must not appear or be read.
removed=0
for p in [root/'index.html',*root.glob('pg*_sec*.html')]:
 doc=html.fromstring(p.read_text(encoding='utf-8')); dirty=False
 for el in doc.xpath('//*[contains(concat(" ",normalize-space(@class)," ")," book-production-footer-text ")]'):
  parent=el.getparent()
  if parent is not None: parent.remove(el); removed+=1;dirty=True
 if dirty: p.write_text(etree.tostring(doc,encoding='unicode',method='html',doctype='<!DOCTYPE html>'),encoding='utf-8')
tp.write_text(json.dumps(texts,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('updated',len(changed),'pages; removed production footer elements',removed)
