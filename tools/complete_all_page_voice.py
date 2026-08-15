import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
lang = root / "content/i18n/sw-TZ"
audios_path = lang / "audios.json"
texts_path = lang / "texts.json"
audios = json.loads(audios_path.read_text(encoding="utf-8"))
texts = json.loads(texts_path.read_text(encoding="utf-8"))

# Images that still lacked an audio entry after the full 167-page audit.
# Page-one certificate remains intentionally silent by validator instruction.
image_ids = [
    "pg108_im001", "pg113_im003", "pg121_im001", "pg122_im001",
    "pg122_im002", "pg147_im001", "pg147_im002", "pg148_im001",
    "pg148_im002",
]

ready = []
for text_id in image_ids:
    if str(texts.get(text_id, "")).strip():
        audios[text_id] = f"{text_id}.mp3?v=all-pages-voice-1"
        ready.append(text_id)

audios_path.write_text(json.dumps(audios, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
(root / "content/all-pages-final-voice-ids.json").write_text(json.dumps(ready, indent=2) + "\n", encoding="utf-8")
print(f"Prepared {len(ready)} final image voice entries")
