from pathlib import Path


path = Path(__file__).resolve().parents[1] / "pg123_sec001.html"
text = path.read_text(encoding="utf-8")
for proper in ("‘", "’"):
    broken = proper
    for _ in range(3):
        broken = broken.encode("utf-8").decode("cp1252")
        text = text.replace(broken, proper)
path.write_text(text, encoding="utf-8")
print({"remaining_mojibake": text.count("Ã")})
