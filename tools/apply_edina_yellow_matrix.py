import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEXTS = ROOT / "content/i18n/sw-TZ/texts.json"
REPLACEMENTS = {
    "pg073_n0016": "Kiberiti, mishumaa miwili, chombo angavu chenye uwazi upande mmoja au jagi lenye kuzuia hewa kupita, saa, meza, kipimajoto sauti na programu saidizi",
    "pg073_n0016_easy_read": "Mahitaji ni:\n- Kiberiti\n- Mishumaa 2\n- Chombo angavu chenye uwazi upande 1 au jagi linalozuia hewa kupita\n- Saa\n- Meza\n- Kipimajoto sauti\n- Programu saidizi",
    "pg110_n0020_easy_read": "Je, unasikia, unahisi au unatambua nini? Andika matokeo.",
    "pg110_n0030_easy_read": "Mahitaji:\n- Kipande kirefu cha chuma\n- Meza\n- Rula\n- Saa ya mtetemo\n- Programu saidizi",
    "pg111_n0013_easy_read": "Muulize rafiki yako anachosikia, anachohisi au anachotambua. Kisha andika jibu.",
    "pg111_n0019_easy_read": "Andika unachosikia, unachohisi au unachotambua.",
}

def patch_html_text(path: Path, data_id: str, value: str) -> None:
    text = path.read_text(encoding="utf-8")
    pattern = re.compile(rf'(<[^>]+data-id="{re.escape(data_id)}"[^>]*>)(.*?)(</[^>]+>)', re.S)
    text2, count = pattern.subn(lambda m: m.group(1) + value.replace("\n", "<br>") + m.group(3), text, count=1)
    if count:
        path.write_text(text2, encoding="utf-8")

data = json.loads(TEXTS.read_text(encoding="utf-8"))
for key, value in REPLACEMENTS.items():
    data[key] = value
    html = ROOT / f"{key[:5]}_sec001.html"
    if html.exists() and not key.endswith("_easy_read"):
        patch_html_text(html, key, value)
TEXTS.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

audio_ids = [
    "pg073_n0016", "pg095_n0014", "pg097_n0011", "pg110_n0020",
    "pg110_n0030", "pg111_n0013", "pg111_n0019", "pg120_n0008",
]
audios_path = ROOT / "content/i18n/sw-TZ/audios.json"
audios = json.loads(audios_path.read_text(encoding="utf-8"))
for key in audio_ids:
    if key in audios:
        audios[key] = audios[key].split("?")[0] + "?v=edina-yellow-1"
audios_path.write_text(json.dumps(audios, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
(ROOT / "content/edina-yellow-audio-ids.json").write_text(json.dumps(audio_ids, indent=2) + "\n", encoding="utf-8")

for name in ("pg087_sec001.html", "pg103_sec001.html"):
    path = ROOT / name
    text = path.read_text(encoding="utf-8")
    if "edina-yellow-layout" not in text:
        text = text.replace("</head>", '<style id="edina-yellow-layout">figure,.text-center:has(> img){margin-block:1.25rem} img{object-fit:contain}</style></head>', 1)
        path.write_text(text, encoding="utf-8")
print("Applied Edina yellow-highlight matrix corrections.")
