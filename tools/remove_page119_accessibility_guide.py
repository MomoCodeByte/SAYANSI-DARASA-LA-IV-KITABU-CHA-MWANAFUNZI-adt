import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEXT_ID = "pg118_n0023"
JSON_PATHS = (
    ROOT / "content/i18n/sw-TZ/texts.json",
    ROOT / "content/i18n/sw-TZ/audios.json",
    ROOT / "content/i18n/sw-TZ/timecode/timecode_output.json",
)


def main():
    audio_name = None
    for path in JSON_PATHS:
        data = json.loads(path.read_text(encoding="utf-8"))
        if path.name == "audios.json":
            audio_name = data.get(TEXT_ID)
        if data.pop(TEXT_ID, None) is not None:
            path.write_text(
                json.dumps(data, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            print(f"Removed {TEXT_ID} from {path.relative_to(ROOT)}")

    if audio_name:
        audio_path = ROOT / "content/i18n/sw-TZ/audio" / audio_name
        if audio_path.exists():
            audio_path.unlink()
            print(f"Deleted {audio_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
