import json
from pathlib import Path

from lxml import etree, html


ROOT = Path(__file__).resolve().parents[1]
LANG = ROOT / "content/i18n/sw-TZ"

DESCRIPTIONS = {
    "pg120_im001": ("pg120_image_audio_desc", "Maelezo ya picha: Skrini ya Windows 11 inaonesha hatua tatu za kufungua programu ya Paint au Quorum. Namba 1 inaonesha upau wa utafutaji chini ya skrini. Namba 2 inaonesha neno Paint lililoandikwa kwenye upau wa utafutaji. Namba 3 inaonesha programu ya Paint iliyochaguliwa kwenye matokeo ya utafutaji."),
    "pg108_im001": ("pg108_fix_desc", "Maelezo ya picha: Mwanafunzi yuko katika ukumbi mtupu, amesimama mbali na ukuta na anapiga kelele ili achunguze mwangwi unaorudi kutoka ukutani."),
    "pg113_im003": ("pg113_fix_desc", "Maelezo ya picha: Watu wanatazama televisheni sebuleni. Umeme unatoa mwanga kwenye balbu na picha pamoja na sauti kwenye televisheni."),
    "pg121_im001": ("pg121_fix_desc", "Maelezo ya picha: Dirisha la Paint au Quorum lina eneo la kuchorea, upau wa zana, maumbo na sehemu ya kuchagua rangi."),
    "pg122_im001": ("pg122_fix_desc6", "Maelezo ya picha: Kishale kinaonesha kuburuta kipanya ili kuchora pembetatu mraba."),
    "pg122_im002": ("pg122_fix_desc7", "Maelezo ya picha: Pembetatu mraba iliyochorwa inaonekana kama mteremko."),
    "pg147_im001": ("pg147_fix_desc", "Maelezo ya picha: Bloku ya ikiwa basi imeunganishwa katika eneo la kuandikia ili programu ifanye kitendo masharti yanapotimia."),
    "pg147_im002": ("pg147_fix_desc2", "Maelezo ya picha: Bloku ya kubwa kuliko imewekwa ndani ya bloku ya ikiwa basi ili kulinganisha thamani mbili."),
    "pg148_im001": ("pg148_fix_desc", "Maelezo ya picha: Bloku ya kucheza sauti hadi ikamilike imewekwa ndani ya bloku ya ikiwa basi."),
    "pg148_im002": ("pg148_fix_desc2", "Maelezo ya picha: Programu iliyokamilika hucheza sauti pale hali iliyowekwa inapokuwa ya kweli."),
}


def main():
    changed_pages = []
    for page in sorted(ROOT.glob("pg*_sec*.html")):
        tree = html.fromstring(page.read_text(encoding="utf-8-sig"))
        dirty = False
        for image_id, (description_id, description) in DESCRIPTIONS.items():
            images = tree.xpath(f'//img[@data-id="{image_id}"]')
            if not images or tree.xpath(f'//*[@data-id="{description_id}"]'):
                continue
            image = images[0]
            hidden = etree.Element("span", {
                "data-id": description_id,
                "class": "sr-only image-audio-description",
            })
            hidden.text = description
            image.addnext(hidden)
            dirty = True
        if dirty:
            page.write_text(
                etree.tostring(tree, encoding="unicode", method="html", doctype="<!DOCTYPE html>"),
                encoding="utf-8",
            )
            changed_pages.append(page.name)

    texts_path = LANG / "texts.json"
    audios_path = LANG / "audios.json"
    texts = json.loads(texts_path.read_text(encoding="utf-8"))
    audios = json.loads(audios_path.read_text(encoding="utf-8"))
    ids = []
    for _, (description_id, description) in DESCRIPTIONS.items():
        texts[description_id] = description
        audios[description_id] = f"{description_id}.mp3"
        ids.append(description_id)
    texts_path.write_text(json.dumps(texts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    audios_path.write_text(json.dumps(audios, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    ids_path = ROOT / "content/hidden-image-audio-description-ids.json"
    ids_path.write_text(json.dumps(sorted(ids), indent=2) + "\n", encoding="utf-8")
    print({"changed_pages": changed_pages, "hidden_audio_descriptions": len(ids)})


if __name__ == "__main__":
    main()
