"""Generate resumable Rehema read-aloud MP3s and exact word timestamps."""

from __future__ import annotations

import argparse
import asyncio
import json
import re
from pathlib import Path

import edge_tts


ROOT = Path(__file__).resolve().parents[1]
I18N = ROOT / "content" / "i18n" / "sw-TZ"
VOICE = "sw-TZ-RehemaNeural"
RATE = "-12%"


def spoken_text(text: str) -> str:
    """Expand Tanzanian honorifics without changing the printed text."""
    text = re.sub(r"(?<!\w)Dkt\.(?!\w)", "Doctor", text, flags=re.IGNORECASE)
    text = re.sub(r"(?<!\w)Dkt(?=\s+[A-Z])", "Doctor", text)
    text = re.sub(r"(?<!\w)Bi\.(?!\w)", "Bibi", text, flags=re.IGNORECASE)
    text = re.sub(r"(?<!\w)Bw\.(?!\w)", "Bwana", text, flags=re.IGNORECASE)
    return text


async def render(text_id: str, text: str, destination: Path) -> tuple[str, dict]:
    error: Exception | None = None
    for attempt in range(5):
        try:
            audio = bytearray()
            words: list[dict] = []
            request = edge_tts.Communicate(spoken_text(text), VOICE, rate=RATE, boundary="WordBoundary")
            async for part in request.stream():
                if part["type"] == "audio":
                    audio.extend(part["data"])
                elif part["type"] == "WordBoundary":
                    words.append({
                        "text": part["text"],
                        "start": round(part["offset"] / 10_000_000, 4),
                        "end": round((part["offset"] + part["duration"]) / 10_000_000, 4),
                    })
            if not audio:
                raise RuntimeError("TTS returned no audio")
            destination.write_bytes(audio)
            return text_id, {"timecodes": [None, {"word_timestamps": words}]}
        except Exception as exc:
            error = exc
            await asyncio.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"{text_id}: {error}")


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pages", nargs="*", type=int)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--ids", nargs="*")
    parser.add_argument("--ids-file")
    args = parser.parse_args()

    texts = json.loads((I18N / "texts.json").read_text(encoding="utf-8"))
    audios = json.loads((I18N / "audios.json").read_text(encoding="utf-8"))
    timecode_path = I18N / "timecode" / "timecode_output.json"
    timecodes = json.loads(timecode_path.read_text(encoding="utf-8"))
    output = I18N / "audio"
    output.mkdir(exist_ok=True)
    prefixes = {f"pg{page:03d}_" for page in args.pages or []}
    requested = set(args.ids or [])
    if args.ids_file:
        requested.update(json.loads(Path(args.ids_file).read_text(encoding="utf-8")))
    jobs = []
    for text_id, filename in audios.items():
        text = str(texts.get(text_id, "")).strip()
        destination = output / str(filename).split("?")[0]
        if not text or (prefixes and not any(text_id.startswith(p) for p in prefixes)):
            continue
        if requested and text_id not in requested:
            continue
        if destination.exists() and destination.stat().st_size > 100 and not args.force:
            continue
        jobs.append((text_id, text, destination))
    if args.limit is not None:
        jobs = jobs[: args.limit]

    semaphore = asyncio.Semaphore(args.workers)

    async def guarded(job: tuple[str, str, Path]) -> tuple[str, dict]:
        async with semaphore:
            return await render(*job)

    done = 0
    for start in range(0, len(jobs), 40):
        results = await asyncio.gather(*(guarded(job) for job in jobs[start:start + 40]))
        for text_id, timing in results:
            timecodes[text_id] = timing
            done += 1
        timecode_path.write_text(json.dumps(timecodes, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"generated {done}/{len(jobs)}", flush=True)
    print(f"complete: {done} files using {VOICE} at {RATE}")


if __name__ == "__main__":
    asyncio.run(main())
