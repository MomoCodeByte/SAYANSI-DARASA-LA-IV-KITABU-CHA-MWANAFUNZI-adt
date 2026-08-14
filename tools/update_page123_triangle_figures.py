import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LANG = ROOT / "content/i18n/sw-TZ"
TEXTS = {
    "pg122_n0007": "Bonyeza kitufe cha kushoto cha kipanya na ushikilie kisha, ukiburute kwa uelekeo kama inavyooneshwa au inavyobainishwa katika Kielelezo namba 6.",
    "pg122_n0012": "Kielelezo namba 6: kuchora umbo la pembetatu mraba.",
    "pg122_n0014": "Kielelezo namba 7: pembetatu mraba inayounda mteremko.",
    "pg122_fix_desc6": "Maelezo ya picha: Dirisha la Paint au Quorum linaonesha eneo jeupe la kuchorea. Namba 2 inaonesha mahali pa kuweka mshale wa kipanya na kushikilia kitufe cha kushoto. Mstari mwekundu unaelekea chini kulia hadi namba 3, inayoonesha upande wa kuburuta kipanya na kisha kuachia.",
    "pg122_fix_desc7": "Maelezo ya picha: Dirisha la Paint au Quorum linaonesha pembetatu mraba yenye upande wima kushoto, msingi mlalo na upande mrefu unaoteremka kutoka juu kushoto kwenda chini kulia. Mshale mwekundu wenye neno mteremko unaonesha upande huo wa mteremko.",
}

texts_path = LANG / "texts.json"
texts = json.loads(texts_path.read_text(encoding="utf-8"))
texts.update(TEXTS)
texts_path.write_text(json.dumps(texts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
ids_path = ROOT / "content/page123-triangle-figure-audio-ids.json"
ids_path.write_text(json.dumps(sorted(TEXTS), indent=2) + "\n", encoding="utf-8")
print({"updated_ids": sorted(TEXTS)})
