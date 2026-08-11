"""Register the restored PDF page 119 activity text in the Swahili catalogue."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / "content/i18n/sw-TZ/texts.json"
texts = json.loads(path.read_text(encoding="utf-8-sig"))
texts["pg119_fix_n0010"] = "Angalia Kielelezo namba 1 na ueleze mpangilio wa kimantiki wa kila picha."
texts["pg119_fix_n0012"] = "Unaweza pia kuunda muundo kwa kuchanganya maumbo tofauti kwa njia ya kimantiki kama inavyooneshwa kwenye Kielelezo namba 2. Unapaswa kufikiria kimantiki kuhusu mpangilio wa maumbo ili kutambua ni umbo gani linaanza na ni umbo gani linafuata. Pia, unapaswa kuwa na wazo la muundo wa mwisho unaotaka kuunda."
path.write_text(json.dumps(texts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("restored_text_ids=2")
