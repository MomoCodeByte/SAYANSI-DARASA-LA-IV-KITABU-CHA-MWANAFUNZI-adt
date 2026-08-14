import json
from pathlib import Path

from lxml import etree, html


ROOT = Path(__file__).resolve().parents[1]
LANG = ROOT / "content/i18n/sw-TZ"
IDS_PATH = ROOT / "content/all-hidden-image-audio-description-ids.json"

CUSTOM_IDS = {
    "pg108_im001": "pg108_fix_desc",
    "pg113_im003": "pg113_fix_desc",
    "pg120_im001": "pg120_image_audio_desc",
    "pg121_im001": "pg121_fix_desc",
    "pg122_im001": "pg122_fix_desc6",
    "pg122_im002": "pg122_fix_desc7",
    "pg147_im001": "pg147_fix_desc",
    "pg147_im002": "pg147_fix_desc2",
    "pg148_im001": "pg148_fix_desc",
    "pg148_im002": "pg148_fix_desc2",
}


def description_for(alt):
    clean = " ".join(alt.split())
    if clean.lower().startswith(("maelezo ya picha", "maelezo ya programu")):
        return clean
    return f"Maelezo ya picha: {clean}"


def main():
    texts_path = LANG / "texts.json"
    audios_path = LANG / "audios.json"
    timecodes_path = LANG / "timecode/timecode_output.json"
    texts = json.loads(texts_path.read_text(encoding="utf-8"))
    audios = json.loads(audios_path.read_text(encoding="utf-8"))
    timecodes = json.loads(timecodes_path.read_text(encoding="utf-8"))

    hidden_ids = set()
    original_image_audio_names = set()
    changed_pages = []
    unique_images = set()

    pages = sorted(ROOT.glob("pg*_sec*.html")) + [ROOT / "index.html"]
    for page in pages:
        tree = html.fromstring(page.read_text(encoding="utf-8-sig"))
        dirty = False
        page_hidden_ids = {node.get("data-id") for node in tree.xpath('//*[contains(concat(" ", normalize-space(@class), " "), " image-audio-description ")]')}
        for image in tree.xpath('//img[@data-id and not(@aria-hidden="true")]'):
            image_id = image.get("data-id")
            alt = " ".join((image.get("alt") or "").split())
            if not alt:
                continue
            description_id = CUSTOM_IDS.get(image_id, f"{image_id}_audio_desc")
            unique_images.add(image_id)
            hidden_ids.add(description_id)

            if description_id not in page_hidden_ids:
                hidden = etree.Element("span", {
                    "data-id": description_id,
                    "class": "sr-only image-audio-description",
                })
                hidden.text = description_for(alt)
                image.addnext(hidden)
                page_hidden_ids.add(description_id)
                dirty = True

            node = tree.xpath(f'//*[@data-id="{description_id}"]')[0]
            description = " ".join(" ".join(node.itertext()).split())
            texts[description_id] = description
            audios[description_id] = f"{description_id}.mp3"

            if image_id in audios:
                original_image_audio_names.add(str(audios.pop(image_id)).split("?", 1)[0])
            timecodes.pop(image_id, None)

        if dirty:
            page.write_text(
                etree.tostring(tree, encoding="unicode", method="html", doctype="<!DOCTYPE html>"),
                encoding="utf-8",
            )
            changed_pages.append(page.name)

    referenced = {str(value).split("?", 1)[0] for value in audios.values()}
    for name in original_image_audio_names - referenced:
        audio_file = LANG / "audio" / name
        if audio_file.exists():
            audio_file.unlink()

    texts_path.write_text(json.dumps(texts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    audios_path.write_text(json.dumps(audios, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    timecodes_path.write_text(json.dumps(timecodes, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    IDS_PATH.write_text(json.dumps(sorted(hidden_ids), indent=2) + "\n", encoding="utf-8")
    print({
        "unique_images": len(unique_images),
        "hidden_audio_descriptions": len(hidden_ids),
        "changed_pages": len(changed_pages),
        "removed_original_image_audio_mappings": len(original_image_audio_names),
    })


if __name__ == "__main__":
    main()
