import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LANG = ROOT / "content/i18n/sw-TZ"
TEXT_ID = "pg120_n0013"
TEXT = (
    "Hatua za kufungua programu ya Paint au Quorum kwa kutumia Windows 11 zinaonyeshwa "
    "au zina bainishwa kwenye Kielelezo namba 3."
)

texts_path = LANG / "texts.json"
texts = json.loads(texts_path.read_text(encoding="utf-8"))
texts[TEXT_ID] = TEXT
texts_path.write_text(json.dumps(texts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

ids_path = ROOT / "content/page121-paint-quorum-reference-audio-ids.json"
ids_path.write_text(json.dumps([TEXT_ID], indent=2) + "\n", encoding="utf-8")
print({"updated": TEXT_ID, "text": TEXT})
