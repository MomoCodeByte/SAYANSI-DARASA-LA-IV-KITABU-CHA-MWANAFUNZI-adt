import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LANG = ROOT / "content/i18n/sw-TZ"
TEXT_ID = "pg119_fix_n0012"
TEXT = (
    "Unaweza pia kuunda muundo kwa kuchanganya maumbo tofauti kwa njia ya kimantiki kama "
    "inavyooneshwa au inavyo bainishwa kwenye Kielelezo namba 2. Unapaswa kufikiria kimantiki "
    "kuhusu mpangilio wa maumbo ili kutambua ni umbo gani linaanza na ni umbo gani linafuata. "
    "Pia, unapaswa kuwa na wazo la muundo wa mwisho unaotaka kuunda."
)


texts_path = LANG / "texts.json"
texts = json.loads(texts_path.read_text(encoding="utf-8"))
texts[TEXT_ID] = TEXT
texts_path.write_text(json.dumps(texts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

ids_path = ROOT / "content/page120-figure-reference-audio-ids.json"
ids_path.write_text(json.dumps([TEXT_ID], indent=2) + "\n", encoding="utf-8")
print({"updated": TEXT_ID})
