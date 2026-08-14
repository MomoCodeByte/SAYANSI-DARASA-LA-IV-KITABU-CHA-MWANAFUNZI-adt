import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LANG = ROOT / "content/i18n/sw-TZ"
TEXT_ID = "pg120_fix_desc"


def main():
    audio_name = None
    paths = (
        LANG / "texts.json",
        LANG / "audios.json",
        LANG / "timecode/timecode_output.json",
    )
    for path in paths:
        data = json.loads(path.read_text(encoding="utf-8"))
        if path.name == "audios.json":
            audio_name = data.get(TEXT_ID)
        if data.pop(TEXT_ID, None) is not None:
            path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            print(f"Removed {TEXT_ID} from {path.relative_to(ROOT)}")

    if audio_name:
        audio_file = LANG / "audio" / str(audio_name).split("?", 1)[0]
        if audio_file.exists():
            audio_file.unlink()
            print(f"Deleted {audio_file.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
