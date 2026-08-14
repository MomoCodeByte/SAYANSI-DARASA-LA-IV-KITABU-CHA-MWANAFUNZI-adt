import json
from pathlib import Path

from lxml import etree, html


ROOT = Path(__file__).resolve().parents[1]
LANG = ROOT / "content/i18n/sw-TZ"
CLASS_NAME = "matrix-audio-description"


def main():
    removed_ids = set()
    changed_pages = []
    for page in sorted(ROOT.glob("pg*_sec*.html")):
        tree = html.fromstring(page.read_text(encoding="utf-8-sig"))
        nodes = tree.xpath(
            f'//*[contains(concat(" ", normalize-space(@class), " "), " {CLASS_NAME} ")]'
        )
        if not nodes:
            continue
        for node in nodes:
            if node.get("data-id"):
                removed_ids.add(node.get("data-id"))
            node.getparent().remove(node)
        page.write_text(
            etree.tostring(tree, encoding="unicode", method="html", doctype="<!DOCTYPE html>"),
            encoding="utf-8",
        )
        changed_pages.append(page.name)

    audio_names = []
    for path in (
        LANG / "texts.json",
        LANG / "audios.json",
        LANG / "timecode/timecode_output.json",
    ):
        data = json.loads(path.read_text(encoding="utf-8"))
        if path.name == "audios.json":
            audio_names = [str(data[text_id]).split("?", 1)[0] for text_id in removed_ids if text_id in data]
        for text_id in removed_ids:
            data.pop(text_id, None)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    for name in audio_names:
        audio_file = LANG / "audio" / name
        if audio_file.exists():
            audio_file.unlink()

    print({
        "changed_pages": changed_pages,
        "removed_visible_description_ids": sorted(removed_ids),
        "image_audio_descriptions_retained": True,
    })


if __name__ == "__main__":
    main()
