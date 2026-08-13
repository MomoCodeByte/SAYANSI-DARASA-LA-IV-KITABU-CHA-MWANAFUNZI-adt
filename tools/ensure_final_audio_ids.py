from pathlib import Path
import json

root = Path(__file__).resolve().parents[1]
path = root / "content/i18n/sw-TZ/audios.json"
audios = json.loads(path.read_text(encoding="utf-8"))
ids = ["pg004_signature", "pg031_fix_n0050", "pg031_fix_n0051", "pg083_im001", "pg156_n0006", "pg156_n0008"]
for text_id in ids:
    audios.setdefault(text_id, f"{text_id}.mp3")
path.write_text(json.dumps(audios, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("ensured", len(ids), "audio mappings")
