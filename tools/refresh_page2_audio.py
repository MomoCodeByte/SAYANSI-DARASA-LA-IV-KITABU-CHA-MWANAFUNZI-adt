import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
lang = root / "content/i18n/sw-TZ"
texts_path = lang / "texts.json"
audio_path = lang / "audios.json"

texts = json.loads(texts_path.read_text(encoding="utf-8"))
audios = json.loads(audio_path.read_text(encoding="utf-8"))

# Correct the legacy copyright glyph without changing the visible layout.
texts["pg002_n0002"] = "© Taasisi ya Elimu Tanzania 2024"

ids = [
    key for key in audios
    if key.startswith("pg002_") and not key.endswith("_easy_read")
]
for key in ids:
    audios[key] = audios[key].split("?")[0] + "?v=page2-tai-highlight-2"

texts_path.write_text(json.dumps(texts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
audio_path.write_text(json.dumps(audios, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
(root / "content/page2-audio-ids.json").write_text(json.dumps(ids, indent=2) + "\n", encoding="utf-8")
print(f"Prepared {len(ids)} page-two audio entries")
