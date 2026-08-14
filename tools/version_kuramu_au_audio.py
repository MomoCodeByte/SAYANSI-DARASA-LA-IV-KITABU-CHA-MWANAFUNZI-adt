import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LANG = ROOT / "content/i18n/sw-TZ"
VERSION = "kuramu-auu-2"


def main():
    texts = json.loads((LANG / "texts.json").read_text(encoding="utf-8"))
    audio_path = LANG / "audios.json"
    audios = json.loads(audio_path.read_text(encoding="utf-8"))
    changed = 0
    for text_id, text in texts.items():
        if text_id.endswith("_easy_read") or text_id not in audios:
            continue
        if not re.search(r"(?i)\b(?:Quorum|au)\b", str(text)):
            continue
        base = str(audios[text_id]).split("?", 1)[0]
        versioned = f"{base}?v={VERSION}"
        if audios[text_id] != versioned:
            audios[text_id] = versioned
            changed += 1
    audio_path.write_text(
        json.dumps(audios, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print({"versioned_audio_ids": changed, "version": VERSION})


if __name__ == "__main__":
    main()
