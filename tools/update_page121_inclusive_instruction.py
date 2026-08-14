import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LANG = ROOT / "content/i18n/sw-TZ"
TEXT_ID = "pg120_n0004"
TEXT = "Tazama au Chunguza Kielelezo namba 2 na utaje maumbo matatu yanayofuata katika mfuatano."

texts_path = LANG / "texts.json"
texts = json.loads(texts_path.read_text(encoding="utf-8"))
texts[TEXT_ID] = TEXT
texts_path.write_text(json.dumps(texts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

ids_path = ROOT / "content/page121-inclusive-instruction-audio-ids.json"
ids_path.write_text(json.dumps([TEXT_ID], indent=2) + "\n", encoding="utf-8")
print({"updated": TEXT_ID, "text": TEXT})
