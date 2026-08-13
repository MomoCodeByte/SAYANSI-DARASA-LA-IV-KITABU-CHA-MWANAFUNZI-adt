from pathlib import Path
import json,re
from lxml import html,etree

root=Path(__file__).resolve().parents[1];tp=root/'content/i18n/sw-TZ/texts.json';texts=json.loads(tp.read_text(encoding='utf-8'))

# The final setup in step 4 still refers to figure 2(c), but uses distinct
# wording so the instruction flow is clear and is not reported as duplicate.
texts['pg086_n0022'] = 'Mpangilio kamili unaonekana katika Kielelezo namba 2(c).'
exact={
 'pg084_n0026':'Mahitaji: Kijiti kimoja kikavu, kipande cha mti kilichokauka na programu saidizi.',
 'pg085_n0035':'Kipande cha metali au spoku, kipande cha ubao, chanzo cha joto kama vile jiko, kibiriti, nta au mshumaa, na programu saidizi.',
 'pg087_n0008':'Kijiko cha chuma, kijiko cha plastiki, kijiti cha mbao, kikombe chenye maji ya moto, vipande vidogo vya siagi na programu saidizi.',
 'pg090_n0016':'Kitambaa, maji, kamba ya kuanikia nguo, vibanio, beseni na programu saidizi.',
 'pg092_n0002':'(c) Mnunurisho ni usafirishaji wa nishati ya joto kwenye nafasi tupu kama vile hewa.',
 'pg094_n0035':'(d) Tochi',
 'pg100_n0026':'Chunguza Kielelezo namba 8 kinachoonesha/kinachobainisha namna mwanga unavyosaidia kutambua vitu mbalimbali.',
}
changed=[]
for n in range(74,101):
 p=root/f'pg{n:03d}_sec001.html'
 if not p.exists():continue
 doc=html.fromstring(p.read_text(encoding='utf-8'));dirty=False
 for el in doc.xpath('//*[@data-id]'):
  did=el.get('data-id');old=' '.join(el.text_content().split());new=exact.get(did,old)
  if did not in exact:
   new=re.sub(r'\bAngalia Kielelezo\b','Chunguza Kielelezo',new)
   new=re.sub(r'\bangalia kielelezo\b','chunguza kielelezo',new)
   if 'Kielelezo namba' in new and ':' not in new and 'kinaonesha' in new and 'kinabainisha' not in new:
    new=new.replace('kinaonesha','kinaonesha/kinabainisha',1)
  if new!=old and len(el)==0:
   el.text=new;texts[did]=new;dirty=True
 if dirty:p.write_text(etree.tostring(doc,encoding='unicode',method='html',doctype='<!DOCTYPE html>'),encoding='utf-8');changed.append(p.name)
tp.write_text(json.dumps(texts,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print('updated',len(changed),'pages',changed)
