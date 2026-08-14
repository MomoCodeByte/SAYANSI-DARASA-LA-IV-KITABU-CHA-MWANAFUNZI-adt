import json
from pathlib import Path

from lxml import html


ROOT = Path(__file__).resolve().parents[1]
LANG = ROOT / "content/i18n/sw-TZ"


def main():
    audios = json.loads((LANG / "audios.json").read_text(encoding="utf-8"))
    pages = sorted(ROOT.glob("pg*_sec*.html")) + [ROOT / "index.html"]
    total = 0
    missing_alt = []
    missing_id = []
    missing_audio = []
    short_alt = []

    for page in pages:
        tree = html.fromstring(page.read_text(encoding="utf-8-sig"))
        for image in tree.xpath('//img[not(@aria-hidden="true")]'):
            total += 1
            text_id = image.get("data-id")
            alt = " ".join((image.get("alt") or "").split())
            if not alt:
                missing_alt.append((page.name, text_id))
            if not text_id:
                missing_id.append((page.name, alt[:80]))
            elif text_id not in audios and f"{text_id}_audio_desc" not in audios and text_id not in {
                "pg108_im001", "pg113_im003", "pg120_im001", "pg121_im001", "pg122_im001",
                "pg122_im002", "pg147_im001", "pg147_im002", "pg148_im001", "pg148_im002",
            }:
                missing_audio.append((page.name, text_id, alt[:80]))
            if alt and len(alt.split()) < 5:
                short_alt.append((page.name, text_id, alt))

    report = {
        "images": total,
        "missing_alt": missing_alt,
        "missing_data_id": missing_id,
        "missing_audio": missing_audio,
        "short_alt": short_alt,
    }
    output = ROOT / "content/image-audio-description-audit.json"
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print({key: len(value) if isinstance(value, list) else value for key, value in report.items()})
    print("Report:", output.relative_to(ROOT))


if __name__ == "__main__":
    main()
