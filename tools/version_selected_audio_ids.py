import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUDIO_PATH = ROOT / "content/i18n/sw-TZ/audios.json"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("ids_file")
    parser.add_argument("version")
    args = parser.parse_args()
    ids = set(json.loads((ROOT / args.ids_file).read_text(encoding="utf-8-sig")))
    audios = json.loads(AUDIO_PATH.read_text(encoding="utf-8"))
    changed = 0
    for text_id in ids:
        if text_id not in audios:
            continue
        base = str(audios[text_id]).split("?", 1)[0]
        updated = f"{base}?v={args.version}"
        if audios[text_id] != updated:
            audios[text_id] = updated
            changed += 1
    AUDIO_PATH.write_text(
        json.dumps(audios, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print({"versioned_audio_ids": changed, "version": args.version})


if __name__ == "__main__":
    main()
