import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LANG = ROOT / "content/i18n/sw-TZ"
TEXTS = {
    "pg121_n0013": "Bofya au tumia mishale kwenye zana ya pembetatu mraba ‘Right angled triangle’ kama inavyooneshwa au inavyobainishwa katika Kielelezo namba 5.",
    "pg121_n0013_easy_read": "Bofya au tumia mishale kwenye zana ya pembetatu mraba ‘Right angled triangle’ kama inavyooneshwa au inavyobainishwa katika Kielelezo namba 5.",
}

texts_path = LANG / "texts.json"
texts = json.loads(texts_path.read_text(encoding="utf-8"))
texts.update(TEXTS)
texts_path.write_text(json.dumps(texts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

ids_path = ROOT / "content/page122-triangle-instruction-audio-ids.json"
ids_path.write_text(json.dumps(sorted(TEXTS), indent=2) + "\n", encoding="utf-8")
print({"updated_ids": sorted(TEXTS)})
