import json
from pathlib import Path

from lxml import etree, html


root = Path(__file__).resolve().parents[1]
page = root / "pg137_sec001.html"
texts_path = root / "content/i18n/sw-TZ/texts.json"
audios_path = root / "content/i18n/sw-TZ/audios.json"
ids_path = root / "content/page138-activity8-audio-ids.json"
texts = json.loads(texts_path.read_text(encoding="utf-8"))

updates = {
    "pg137_n0005": "Bofya au tumia mishale kibendera cha ‘Anza’ ili kucheza mchezo wako.",
    "pg137_n0008": "Endelea kucheza ili kuona namna ‘Sprite’ anavyozunguka.",
    "pg137_im003_audio_desc": "Maelezo ya picha: Skrini ya Scratch au Quorum inaonesha bloku ya ‘enda kwa mahali popote’ ikiunganishwa chini ya bloku ya ‘wakati inapobonyezwa’.",
    "pg137_fix_act8_title": "Kazi ya kufanya namba 8: Kuunda mchezo wa nenda mahali popote",
    "pg137_fix_act8_intro": "Kuunda mchezo wa nenda mahali popote, fuata hatua zifuatazo:",
    "pg137_fix_act8_steps": "Hatua",
    "pg137_fix_act8_1": "Bofya au tumia mishale menyu ya bloku za ‘Matukio’.",
    "pg137_fix_act8_2": "Buruta au tumia mishale na dondosha bloku ya ‘wakati inapobonyezwa’ kwenye eneo la kuandikia.",
    "pg137_fix_act8_3": "Bofya au tumia mishale menyu ya bloku za ‘Mwendo’.",
    "pg137_fix_act8_4": "Buruta au tumia mishale na dondosha bloku ya ‘enda kwa (mahali popote)’ kwenye eneo la kuandikia.",
    "pg137_fix_act8_5": "Unganisha bloku ya ‘enda kwa (mahali popote)’ na bloku ya ‘wakati inapobonyezwa’ kama inavyoonekana au inavyobainishwa katika Kielelezo namba 28.",
}

ids = set()
for text_id, value in updates.items():
    texts[text_id] = value
    ids.add(text_id)
    if text_id.startswith("pg137_fix_act8_"):
        easy_id = f"{text_id}_easy_read"
        texts[easy_id] = value
        ids.add(easy_id)
texts_path.write_text(json.dumps(texts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

audios = json.loads(audios_path.read_text(encoding="utf-8"))
for text_id in ids:
    audios.setdefault(text_id, f"{text_id}.mp3")
audios_path.write_text(json.dumps(audios, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

tree = html.fromstring(page.read_text(encoding="utf-8-sig"))
for text_id in ("pg137_n0005", "pg137_n0008", "pg137_im003_audio_desc"):
    nodes = tree.xpath(f'//*[@data-id="{text_id}"]')
    if nodes and len(nodes[0]) == 0:
        nodes[0].text = updates[text_id]
tree.xpath('//*[@data-id="pg137_im003"]')[0].set("alt", updates["pg137_im003_audio_desc"])

# Remove an older injected copy, if this repair script is run again.
for node in tree.xpath('//*[@id="activity-eight-restored"]'):
    node.getparent().remove(node)

fragment = html.fragment_fromstring(
    '''
<div id="activity-eight-restored" class="mt-8 overflow-hidden rounded-[2rem] bg-sky-100 shadow-md">
  <div class="bg-teal-600 px-6 py-4 text-white max-sm:px-4">
    <h2 data-id="pg137_fix_act8_title" class="text-left text-[1.7rem] font-bold leading-snug max-lg:text-[1.4rem] max-sm:text-[1rem]">Kazi ya kufanya namba 8: Kuunda mchezo wa nenda mahali popote</h2>
  </div>
  <div class="px-6 py-5 text-gray-800 max-sm:px-4">
    <p data-id="pg137_fix_act8_intro" class="mb-4 text-[1.15rem] leading-relaxed max-sm:text-base">Kuunda mchezo wa nenda mahali popote, fuata hatua zifuatazo:</p>
    <h3 data-id="pg137_fix_act8_steps" class="mb-3 text-[1.35rem] font-bold">Hatua</h3>
    <ol class="space-y-3 text-[1.05rem] leading-relaxed max-sm:text-base">
      <li class="flex gap-3"><span aria-hidden="true">1.</span><span data-id="pg137_fix_act8_1">Bofya au tumia mishale menyu ya bloku za ‘Matukio’.</span></li>
      <li class="flex gap-3"><span aria-hidden="true">2.</span><span data-id="pg137_fix_act8_2">Buruta au tumia mishale na dondosha bloku ya ‘wakati inapobonyezwa’ kwenye eneo la kuandikia.</span></li>
      <li class="flex gap-3"><span aria-hidden="true">3.</span><span data-id="pg137_fix_act8_3">Bofya au tumia mishale menyu ya bloku za ‘Mwendo’.</span></li>
      <li class="flex gap-3"><span aria-hidden="true">4.</span><span data-id="pg137_fix_act8_4">Buruta au tumia mishale na dondosha bloku ya ‘enda kwa (mahali popote)’ kwenye eneo la kuandikia.</span></li>
      <li class="flex gap-3"><span aria-hidden="true">5.</span><span data-id="pg137_fix_act8_5">Unganisha bloku ya ‘enda kwa (mahali popote)’ na bloku ya ‘wakati inapobonyezwa’ kama inavyoonekana au inavyobainishwa katika Kielelezo namba 28.</span></li>
    </ol>
  </div>
</div>
''',
    create_parent=False,
)
image_block = tree.xpath('//*[@data-id="pg137_im003"]/ancestor::div[contains(@class,"overflow-hidden")][1]')[0]
image_block.addprevious(fragment)

page.write_text(
    etree.tostring(tree, encoding="unicode", method="html", doctype="<!DOCTYPE html>"),
    encoding="utf-8",
)
ids_path.write_text(json.dumps(sorted(ids), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print({"restored_activity_ids": len(ids), "duplicate_blocks": len(tree.xpath('//*[@id="activity-eight-restored"]'))})
