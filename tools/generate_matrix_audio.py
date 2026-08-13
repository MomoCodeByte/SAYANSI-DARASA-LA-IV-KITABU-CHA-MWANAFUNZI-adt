"""Regenerate matrix-targeted page audio with natural Rehema and Swahili numbers."""

from __future__ import annotations

import argparse
import asyncio
import json
import re
from pathlib import Path

import edge_tts


ROOT = Path(__file__).resolve().parents[1]
LANG = ROOT / "content" / "i18n" / "sw-TZ"
VOICE = "sw-TZ-RehemaNeural"
FOOTER_TAG = re.compile(r"<[^>]*book-production-footer-text[^>]*>", re.I)
DATA_ID = re.compile(r"data-id=[\"']([^\"']+)", re.I)

ONES = {0:"sifuri",1:"moja",2:"mbili",3:"tatu",4:"nne",5:"tano",6:"sita",7:"saba",8:"nane",9:"tisa"}
TENS = {10:"kumi",20:"ishirini",30:"thelathini",40:"arobaini",50:"hamsini",60:"sitini",70:"sabini",80:"themanini",90:"tisini"}


def number_sw(value: int) -> str:
    if value < 10: return ONES[value]
    if value < 100:
        tens, rest = divmod(value, 10); base = TENS[tens * 10]
        return base if not rest else f"{base} na {number_sw(rest)}"
    if value < 1000:
        count, rest = divmod(value, 100); base = f"mia {number_sw(count)}"
        return base if not rest else f"{base} na {number_sw(rest)}"
    if value < 1_000_000:
        count, rest = divmod(value, 1000); base = f"elfu {number_sw(count)}"
        return base if not rest else f"{base} {number_sw(rest)}"
    return " ".join(ONES[int(char)] for char in str(value))


def spoken(text: str) -> tuple[str, list[int]]:
    display = re.findall(r"\S+", text)
    words: list[str] = []
    display_map: list[int] = []
    for index, token in enumerate(display):
        value = token
        value = re.sub(r"(?<!\w)Dkt\.?(?!\w)", "Doctor", value, flags=re.I)
        value = re.sub(r"(?<!\w)Bi\.(?!\w)", "Bibi", value, flags=re.I)
        value = re.sub(r"(?<!\w)Bw\.(?!\w)", "Bwana", value, flags=re.I)
        value = re.sub(r"\d+", lambda m: number_sw(int(m.group())), value)
        expanded = re.findall(r"\S+", value)
        words.extend(expanded)
        display_map.extend([index] * len(expanded))
    return " ".join(words), display_map


async def render(job: tuple[str, str, list[int], Path]) -> tuple[str, dict]:
    text_id, text, display_map, destination = job
    last_error = None
    for attempt in range(5):
        try:
            audio = bytearray(); boundaries = []
            request = edge_tts.Communicate(text, VOICE, rate="+0%", boundary="WordBoundary")
            async with asyncio.timeout(45):
                async for part in request.stream():
                    if part["type"] == "audio": audio.extend(part["data"])
                    elif part["type"] == "WordBoundary": boundaries.append(part)
            if not audio: raise RuntimeError("empty audio")
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(audio)
            timestamps = []
            for index, item in enumerate(boundaries):
                start = item["offset"] / 10_000_000
                timestamps.append({
                    "text": item["text"], "start": round(start, 4),
                    "end": round(start + item["duration"] / 10_000_000, 4),
                    "display_index": display_map[min(index, len(display_map)-1)] if display_map else index,
                })
            return text_id, {"timecodes": [None, {"word_timestamps": timestamps}]}
        except Exception as error:
            last_error = error; await asyncio.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"{text_id}: {last_error}")


async def main() -> None:
    parser = argparse.ArgumentParser(); parser.add_argument("--limit", type=int); parser.add_argument("--workers", type=int, default=12); parser.add_argument("--ids", nargs="*"); parser.add_argument("--force", action="store_true"); parser.add_argument("--all", action="store_true")
    args = parser.parse_args()
    plan = json.loads((ROOT / "content/validation-matrix-plan.json").read_text(encoding="utf-8"))
    texts = json.loads((LANG / "texts.json").read_text(encoding="utf-8")); audios = json.loads((LANG / "audios.json").read_text(encoding="utf-8"))
    files = {f for item in plan["items"] if item["category"] == "audio_pronunciation" for f in item["files"] if f.startswith("pg")}
    prefixes = {filename[:5] + "_" for filename in files}
    footer_ids: set[str] = set()
    for page in ROOT.glob("pg*_sec*.html"):
        source = page.read_text(encoding="utf-8-sig")
        for tag in FOOTER_TAG.findall(source):
            match = DATA_ID.search(tag)
            if match:
                footer_ids.add(match.group(1))
    jobs = []
    requested = set(args.ids or [])
    for text_id, filename in audios.items():
        if text_id.endswith("_easy_read") or text_id in footer_ids or (requested and text_id not in requested): continue
        if not requested and not args.all and not any(text_id.startswith(prefix) for prefix in prefixes): continue
        shown = str(texts.get(text_id, "")).strip()
        if not shown: continue
        destination = LANG / "audio" / str(filename).split("?")[0]
        if destination.exists() and destination.stat().st_size > 100 and not requested and not args.force: continue
        normalized, display_map = spoken(shown); jobs.append((text_id, normalized, display_map, destination))
    if args.limit is not None: jobs = jobs[:args.limit]
    timecode_path = LANG / "timecode" / "timecode_output.json"; timecode_path.parent.mkdir(exist_ok=True)
    timecodes = json.loads(timecode_path.read_text(encoding="utf-8")) if timecode_path.exists() else {}
    semaphore = asyncio.Semaphore(args.workers)
    async def guarded(job):
        async with semaphore: return await render(job)
    done = 0
    for start in range(0, len(jobs), 40):
        for text_id, timing in await asyncio.gather(*(guarded(job) for job in jobs[start:start+40])):
            timecodes[text_id] = timing; done += 1
        timecode_path.write_text(json.dumps(timecodes, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"generated {done}/{len(jobs)}", flush=True)
    print(f"complete={done} voice={VOICE} rate=natural excluded_footers={len(footer_ids)}")


if __name__ == "__main__": asyncio.run(main())
