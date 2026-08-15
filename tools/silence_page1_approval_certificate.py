import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
audio_path = root / "content/i18n/sw-TZ/audios.json"
audios = json.loads(audio_path.read_text(encoding="utf-8"))

# Keep the visible cover/title intact. Silence only the approval-certificate
# image description and its hidden transcription.
certificate_ids = {"pg001_im001_audio_desc"}
certificate_ids.update(f"pg001_n{number:04d}" for number in range(7, 22))
certificate_ids.update(f"pg001_n{number:04d}_easy_read" for number in range(7, 22))

removed = []
for text_id in sorted(certificate_ids):
    if audios.pop(text_id, None) is not None:
        removed.append(text_id)

audio_path.write_text(json.dumps(audios, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"Silenced {len(removed)} approval-certificate audio entries")
