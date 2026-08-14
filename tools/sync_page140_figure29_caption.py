import json
from pathlib import Path


root = Path(__file__).resolve().parents[1]
texts_path = root / "content/i18n/sw-TZ/texts.json"
ids_path = root / "content/page140-figure29-audio-ids.json"
texts = json.loads(texts_path.read_text(encoding="utf-8"))
caption = "Kielelezo namba 29: kuunganisha bloku mbalimbali za mwendo."
ids = ["pg139_n0009", "pg139_n0009_easy_read"]
for text_id in ids:
    texts[text_id] = caption
texts_path.write_text(json.dumps(texts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
ids_path.write_text(json.dumps(ids, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print({"caption": caption, "ids": ids})
