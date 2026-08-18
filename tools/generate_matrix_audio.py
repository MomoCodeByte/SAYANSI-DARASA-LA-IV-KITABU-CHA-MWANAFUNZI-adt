"""Regenerate matrix-targeted page audio with natural Rehema and Swahili numbers."""

from __future__ import annotations

import argparse
import asyncio
import difflib
import json
import re
from pathlib import Path

import edge_tts


ROOT = Path(__file__).resolve().parents[1]
LANG = ROOT / "content" / "i18n" / "sw-TZ"
VOICE = "sw-TZ-RehemaNeural"
FOOTER_TAG = re.compile(r"<[^>]*book-production-footer-text[^>]*>", re.I)
DATA_ID = re.compile(r"data-id=[\"']([^\"']+)", re.I)
FOOTER_TEXT = re.compile(
    r"(?:FOR ONLINE READING ONLY|SAYANSI DARASA LA IV KITABU CHA MWANAFUNZI\.indd|"
    r"^\d{1,2}/\d{1,2}/\d{4}\s+\d{1,2}:\d{2}$)",
    re.I,
)

ONES = {0:"sifuri",1:"moja",2:"mbili",3:"tatu",4:"nne",5:"tano",6:"sita",7:"saba",8:"nane",9:"tisa"}
TENS = {10:"kumi",20:"ishirini",30:"thelathini",40:"arobaini",50:"hamsini",60:"sitini",70:"sabini",80:"themanini",90:"tisini"}
ROMAN_VALUES = {"I":1,"V":5,"X":10,"L":50,"C":100,"D":500,"M":1000}
PRONUNCIATION_OVERRIDES = {
    "VVU": "vivi u", "UKIMWI": "ukimwi", "ISBN": "ai es bi en",
    "TET": "teti", "DUCE": "duse", "UDOM": "yudomu",
    "SUA": "suaa", "MOTCO": "motiko", "MU": "Muu",
    "maziwa": "ma-ziwa", "njegere": "nje-ge-re", "matumizi": "ma-tu-mi-zi",
    "bidhaa": "bi-dhaa", "msamiati": "m-sa-mi-a-ti",
    "Quorum": "Kuramu", "quorum": "Kuramu", "au": "auu",
    "TIE": "tai", "tie": "tai",
}

LETTER_PRONUNCIATIONS = {
    "a": "ai", "b": "bii", "c": "sii", "d": "dii", "e": "ii",
    "f": "efu", "g": "jii", "h": "eichi", "i": "ai", "j": "jei",
    "k": "kei", "l": "eli", "m": "emu", "n": "eni", "o": "ou",
    "p": "pii", "q": "kyuu", "r": "aa", "s": "esi", "t": "tii",
    "u": "yuu", "v": "vii", "w": "dabiliu", "x": "eksi",
    "y": "wai", "z": "zed",
}


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


def roman_to_int(token: str) -> int | None:
    clean = token.upper()
    if not re.fullmatch(r"[IVXLCDM]+", clean): return None
    total = previous = 0
    for char in reversed(clean):
        value = ROMAN_VALUES[char]
        total += -value if value < previous else value
        previous = max(previous, value)
    return total if 0 < total <= 3999 else None


def spoken(text: str) -> tuple[str, list[int]]:
    original_display = re.findall(r"\S+", text)
    text = re.sub(r"(?i)(?<!\w)S\.L\.P\.?(?!\w)", "esielopi", text)
    text = re.sub(r"(?i)(?<!\w)www(?!\w)", "dabiliyu dabiliyu dabiliyu", text)
    text = re.sub(r"(?i)(?<!\w)tz(?!\w)", "Tanzania", text)
    # Standalone lower-case Roman numerals are used in the front-matter TOC.
    # Expand them for Rehema while preserving the printed form on the page.
    standalone_roman = text.strip().upper()
    if text.strip().islower() and re.fullmatch(r"[IVXLCDM]+", standalone_roman):
        text = number_sw(roman_to_int(standalone_roman) or 0)
    text = text.replace("©", "atimiliki ")
    text = text.replace("+", " jumlisha ")
    text = re.sub(r"(?i)\bdirector\b", "dairecta", text)
    text = re.sub(r"(?i)\bgeneral\b", "jenerali", text)
    text = text.replace("√", " alama ya tiki ")
    text = re.sub(r"(?i)\bmbalimbali\b", "mbali mbali", text)
    text = re.sub(r"(?i)\bCity\s+Bus\b", "siti basi", text)
    text = re.sub(r"(?i)\bcar\b", "kaa", text)
    text = re.sub(
        r"(?i)\bPicha\s+([a-z])\b",
        lambda match: f"picha {LETTER_PRONUNCIATIONS[match.group(1).lower()]}",
        text,
    )
    # Standalone section letters are labels, not Roman numerals. Without
    # these overrides Edge TTS receives C/D as 100/500 (mia moja/mia tano).
    text = re.sub(r"(?i)\bSehemu\s+C\b", "Sehemu sii", text)
    text = re.sub(r"(?i)\bSehemu\s+D\b", "Sehemu dii", text)
    # Panel labels are read as picture labels: (a) = "picha ai", etc.
    text = re.sub(
        r"(?i)(?<!\w)\(([a-z])\)",
        lambda match: f" picha {LETTER_PRONUNCIATIONS[match.group(1).lower()]} ",
        text,
    )
    text = re.sub(r"(?i)^\(c\)\s+(?=Jiko\s+la\s+mkaa)", "picha sii ", text)
    text = re.sub(r"(?i)^\(d\)\s+(?=Jiko\s+la\s+umeme)", "picha dii ", text)
    text = re.sub(r"(?i)^\(e\)\s+(?=Jiko\s+la\s+gesi)", "picha iii ", text)
    text = re.sub(r"(?i)\bhttps\b", "echititipi", text)
    text = re.sub(r"(?i)\bJPEG\s+picture\b", "jipieniji picha", text)
    text = re.sub(r"(?i)\bPNG\s+picture\b", "pieniji picha", text)
    text = re.sub(r"(?i)\bBMP\s+picture\b", "biempi picha", text)
    text = re.sub(r"(?i)\bJPEG\b", "jipieniji", text)
    text = re.sub(r"(?i)\bPNG\b", "pieniji", text)
    text = re.sub(r"(?i)\bBMP\b", "biempi", text)
    text = re.sub(r"(?i)\bShape\b", "shepu", text)
    text = re.sub(r"(?i)\bchemli\b", "chem-li", text)
    text = re.sub(r"(?i)\bardhi\b", "ar-dhi", text)
    text = re.sub(r"(?i)\bPurple\b", "papo", text)
    text = re.sub(r"(?i)\bRose\b", "rozi", text)
    text = re.sub(r"(?i)\bRectangle\b", "rectango", text)
    text = re.sub(
        r"(?i)\bSave\s+as\b",
        "sevuu azi",
        text,
    )
    text = re.sub(r"(?i)\bSave\b", "sevuu", text)
    text = re.sub(r"(?i)\bDesktop\b", "desikitop", text)
    text = re.sub(
        r"(?i)\bRight\s+angled\s+triangle\b",
        "raiti engo traiengo",
        text,
    )
    display = re.findall(r"\S+", text)
    original_normalized = [re.sub(r"\W+", "", token, flags=re.UNICODE).casefold() for token in original_display]
    transformed_normalized = [re.sub(r"\W+", "", token, flags=re.UNICODE).casefold() for token in display]
    transformed_to_original: list[int | None] = [None] * len(display)
    matcher = difflib.SequenceMatcher(None, original_normalized, transformed_normalized, autojunk=False)
    for operation, original_start, original_end, transformed_start, transformed_end in matcher.get_opcodes():
        if operation == "equal":
            for offset in range(transformed_end - transformed_start):
                transformed_to_original[transformed_start + offset] = original_start + offset
            continue
        original_length = original_end - original_start
        transformed_length = transformed_end - transformed_start
        for offset in range(transformed_length):
            if original_length:
                mapped_offset = min((offset * original_length) // max(transformed_length, 1), original_length - 1)
                transformed_to_original[transformed_start + offset] = original_start + mapped_offset
            elif original_display:
                transformed_to_original[transformed_start + offset] = min(original_start, len(original_display) - 1)
    fallback = 0
    for index, mapped in enumerate(transformed_to_original):
        if mapped is None:
            transformed_to_original[index] = fallback
        else:
            fallback = mapped
    words: list[str] = []
    display_map: list[int] = []
    for index, token in enumerate(display):
        value = token.replace("/", " au ")
        if re.fullmatch(r"\d+(?:-\d+){2,}", value.strip(".,;:()")):
            value = re.sub(r"\d", lambda m: ONES[int(m.group())] + " ", value).replace("-", " ")
        value = re.sub(r"(?<!\w)Dkt\.?(?!\w)", "Doctor", value, flags=re.I)
        value = re.sub(r"(?<!\w)Bi\.(?!\w)", "Bibi", value, flags=re.I)
        value = re.sub(r"(?<!\w)Bw\.(?!\w)", "Bwana", value, flags=re.I)
        bare = re.sub(r"^[^A-Za-z]+|[^A-Za-z]+$", "", value)
        roman = roman_to_int(bare) if bare and bare.upper() == bare else None
        if roman is not None:
            value = value.replace(bare, number_sw(roman))
        elif re.search(r"\d+-\d+", value):
            value = re.sub(r"\d", lambda m: ONES[int(m.group())] + " ", value).replace("-", " ")
        else:
            value = re.sub(r"\d+", lambda m: number_sw(int(m.group())), value)
        for written, pronounced in PRONUNCIATION_OVERRIDES.items():
            flags = re.I if written.islower() else 0
            value = re.sub(rf"(?<!\w){re.escape(written)}(?!\w)", pronounced, value, flags=flags)
        expanded = [token for token in re.findall(r"\S+", value) if re.search(r"\w", token, flags=re.UNICODE)]
        words.extend(expanded)
        display_map.extend([int(transformed_to_original[index])] * len(expanded))
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
    parser = argparse.ArgumentParser(); parser.add_argument("--limit", type=int); parser.add_argument("--workers", type=int, default=12); parser.add_argument("--ids", nargs="*"); parser.add_argument("--ids-file"); parser.add_argument("--force", action="store_true"); parser.add_argument("--all", action="store_true"); parser.add_argument("--page-start", type=int); parser.add_argument("--page-end", type=int)
    args = parser.parse_args()
    plan = json.loads((ROOT / "content/validation-matrix-plan.json").read_text(encoding="utf-8"))
    texts = json.loads((LANG / "texts.json").read_text(encoding="utf-8")); audios = json.loads((LANG / "audios.json").read_text(encoding="utf-8"))
    override_path = ROOT / "content" / "audio-spoken-overrides.json"
    spoken_overrides = json.loads(override_path.read_text(encoding="utf-8")) if override_path.exists() else {}
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
    if args.ids_file:
        requested.update(json.loads((ROOT / args.ids_file).read_text(encoding="utf-8")))
    for text_id, filename in audios.items():
        if (text_id.endswith("_easy_read") and text_id not in requested) or text_id in footer_ids or (requested and text_id not in requested): continue
        page_match = re.match(r"pg(\d{3})_", text_id)
        page_number = int(page_match.group(1)) if page_match else None
        if args.page_start is not None and (page_number is None or page_number < args.page_start): continue
        if args.page_end is not None and (page_number is None or page_number > args.page_end): continue
        if not requested and not args.all and not any(text_id.startswith(prefix) for prefix in prefixes): continue
        shown = str(texts.get(text_id, "")).strip()
        if not shown or FOOTER_TEXT.search(shown): continue
        destination = LANG / "audio" / str(filename).split("?")[0]
        if destination.exists() and destination.stat().st_size > 100 and not requested and not args.force: continue
        speech_source = str(spoken_overrides.get(text_id, shown)).strip()
        normalized, display_map = spoken(speech_source)
        if text_id in spoken_overrides:
            # The extra spoken context is intentionally not visible on the page.
            # Associate every spoken word with the displayed number token.
            display_map = [0] * len(display_map)
        jobs.append((text_id, normalized, display_map, destination))
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
