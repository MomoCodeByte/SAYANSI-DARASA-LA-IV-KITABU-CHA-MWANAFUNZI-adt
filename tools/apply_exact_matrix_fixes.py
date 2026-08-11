from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]

replacements = {
    "pg007_sec001.html": [
        ("Kielelezo namba 1 kinaonesha mifano ya kanuni za afya.",
         "Kielelezo namba 1 kinaonesha na kinaeleza mifano ya kanuni za afya."),
    ],
    "pg016_sec001.html": [
        ("Kielelezo namba 10 kinaonesha mlo kamili wa mgonjwa.",
         "Kielelezo namba 10 kinaonesha na kinaeleza mlo kamili wa mgonjwa."),
    ],
    "pg036_sec001.html": [
        ("Magonjwa hayo ni kama vile kipindupindu, tetekuwanga, kifua kikuu, homa ya ini na Ugonjwa wa Virusi vya</span>",
         "Magonjwa hayo ni kama vile kipindupindu, tetekuwanga, kifua kikuu, homa ya ini na Ugonjwa wa Virusi vya Korona (UVIKO-19).</span>"),
    ],
    "pg092_sec001.html": [
        (">(e) Mnururisho ni usafirishaji", ">(c) Mnururisho ni usafirishaji"),
    ],
    "pg055_sec001.html": [
        ('data-section-id="pg055_sec001" class="mx-auto max-w-4xl text-neutral-800"',
         'data-section-id="pg055_sec001" class="mx-auto max-w-4xl text-neutral-800 flex flex-col"'),
        ("space-y-6 text-[1.05rem] leading-relaxed max-sm:text-base",
         "space-y-6 text-[1.05rem] leading-relaxed max-sm:text-base hidden"),
        ('class="mb-4 text-4xl font-bold text-green-600 max-sm:text-3xl" data-id="pg055_n0010"',
         'class="mb-4 text-4xl font-bold text-green-600 max-sm:text-3xl order-2" data-id="pg055_n0010"'),
        ('class="space-y-7 text-[1.05rem] leading-snug max-sm:space-y-6 max-sm:text-base"',
         'class="space-y-7 text-[1.05rem] leading-snug max-sm:space-y-6 max-sm:text-base order-3"'),
        ('<div class="mt-10 space-y-6 hidden" aria-hidden="true">',
         '<div class="mb-8 space-y-6 order-1">'),
    ],
    "pg040_sec001.html": [
        ("grid grid-cols-[1.1fr_0.9fr] items-start gap-8 max-sm:grid-cols-1",
         "grid grid-cols-[1.1fr_0.9fr] items-start gap-5 max-sm:grid-cols-1"),
        ("max-w-full h-auto w-48 max-lg:w-44 max-sm:w-40",
         "max-w-full h-auto w-40 max-lg:w-36 max-sm:w-32"),
        ("<div class=\"mb-10\"><div class=\"mb-3 text-[27px] italic",
         "<div class=\"mb-5\"><div class=\"mb-2 text-[27px] italic"),
    ],
}

for relative, edits in replacements.items():
    path = ROOT / relative
    text = path.read_text(encoding="utf-8")
    for old, new in edits:
        if old not in text and new in text:
            continue
        if old not in text:
            raise SystemExit(f"Expected text missing in {relative}: {old}")
        text = text.replace(old, new, 1)
    path.write_text(text, encoding="utf-8")

texts_path = ROOT / "content/i18n/sw-TZ/texts.json"
texts = json.loads(texts_path.read_text(encoding="utf-8"))
texts["pg036_n0033"] = "Magonjwa hayo ni kama vile kipindupindu, tetekuwanga, kifua kikuu, homa ya ini na Ugonjwa wa Virusi vya Korona (UVIKO-19)."
texts["pg092_n0002"] = "(c) Mnururisho ni usafirishaji wa nishati ya joto kwenye nafasi tupu kama vile hewa."
texts["pg007_n0024"] = "Kielelezo namba 1 kinaonesha na kinaeleza mifano ya kanuni za afya."
texts["pg016_n0006"] = "Kielelezo namba 10 kinaonesha na kinaeleza mlo kamili wa mgonjwa."
texts_path.write_text(json.dumps(texts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print("Applied exact matrix fixes: pg036_n0033, pg092_n0002")

# Matrix items 75, 77, 78, 80 and 81: retain the canonical interactive
# exercise as its own section. The surrounding textbook content is split so
# the reading order matches the PDF without nesting one activity in another.
page40 = ROOT / "pg040_sec001.html"
html = page40.read_text(encoding="utf-8")
html = html.replace("min-h-[120px]", "min-h-[72px]")
tb_marker = '<div class="mb-8"><div class="mb-3 text-[28px] font-semibold leading-tight max-lg:text-[24px] max-sm:text-[20px]" data-id="pg041_n0008">Kifua kikuu</div>'
import re
embedded = re.search(r'<div data-section-id="pg040_exercise004" data-matrix-fix="exercise-4-interactive".*?</div>', html, re.S)
if embedded:
    following_tb = html.index(tb_marker, embedded.start())
    html = html[:embedded.start()] + html[following_tb:]
if tb_marker in html:
    tb_start = html.index(tb_marker)
    section_end = html.index('</section></div>', tb_start)
    tuberculosis = html[tb_start:section_end]
    html = html[:tb_start] + html[section_end:]
    page40.write_text(html, encoding="utf-8")

    page40b = ROOT / "pg040_sec002.html"
    continuation = page40b.read_text(encoding="utf-8")
    continuation = re.sub(
        r'<div id="content" class="opacity-0">.*?</div>\s*</main>',
        '<div id="content" class="mx-auto max-w-5xl bg-white px-16 pt-10 pb-12 max-lg:px-10 max-sm:px-4 opacity-0"><section class="mx-auto max-w-4xl font-serif text-neutral-900">' + tuberculosis + '</section></div></main>',
        continuation,
        count=1,
        flags=re.S,
    )
    page40b.write_text(continuation, encoding="utf-8")

pages_path = ROOT / "content/pages.json"
pages = json.loads(pages_path.read_text(encoding="utf-8"))
excluded = {"pg040_sec002", "pg041_sec001", "pg041_sec002"}
pages = [page for page in pages if page.get("section_id") not in excluded]
insert_at = next(i for i, page in enumerate(pages) if page.get("section_id") == "pg040_sec001") + 1
pages[insert_at:insert_at] = [
    {"section_id": "pg041_sec001", "href": "pg041_sec001.html", "page_number": 35},
    {"section_id": "pg040_sec002", "href": "pg040_sec002.html", "page_number": 35},
]
pages_path.write_text(json.dumps(pages, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print("Applied PDF-faithful interactive exercise order without nested activities")
