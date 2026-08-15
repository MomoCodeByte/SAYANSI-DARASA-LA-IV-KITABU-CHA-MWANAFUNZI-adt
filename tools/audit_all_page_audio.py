import json
import re
from pathlib import Path

root = Path(__file__).resolve().parents[1]
lang = root / "content/i18n/sw-TZ"
audios = json.loads((lang / "audios.json").read_text(encoding="utf-8"))
texts = json.loads((lang / "texts.json").read_text(encoding="utf-8"))
timecodes = json.loads((lang / "timecode/timecode_output.json").read_text(encoding="utf-8"))
pages = json.loads((root / "content/pages.json").read_text(encoding="utf-8"))

ids = []
for entry in pages:
    href = entry if isinstance(entry, str) else entry.get("href", "")
    page = root / href
    if page.exists():
        ids.extend(re.findall(r'data-id=["\']([^"\']+)', page.read_text(encoding="utf-8-sig")))

ids = list(dict.fromkeys(ids))
footer_text = re.compile(r"FOR ONLINE READING ONLY|\.indd\s+\d+|^\d{1,2}\s+au\s+\d{1,2}\s+au\s+\d{4}", re.I)
certificate = {"pg001_im001_audio_desc"}
certificate.update(f"pg001_n{i:04d}" for i in range(7, 22))

content = [
    text_id for text_id in ids
    if text_id in texts
    and not text_id.endswith("_easy_read")
    and text_id not in certificate
    and not footer_text.search(str(texts[text_id]).strip())
]
missing_map = [text_id for text_id in content if text_id not in audios]
missing_file = [
    text_id for text_id in content if text_id in audios
    and not (lang / "audio" / audios[text_id].split("?")[0]).exists()
]
missing_timecode = [text_id for text_id in content if text_id in audios and text_id not in timecodes]

report = {
    "pages": len(pages), "content_ids": len(content),
    "missing_map": missing_map, "missing_file": missing_file,
    "missing_timecode": missing_timecode,
}
(root / "content/all-page-audio-audit.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({key: (len(value) if isinstance(value, list) else value) for key, value in report.items()}, indent=2))
