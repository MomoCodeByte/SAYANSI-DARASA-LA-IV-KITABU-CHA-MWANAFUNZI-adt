import json
from pathlib import Path

from lxml import etree, html


root = Path(__file__).resolve().parents[1]
page_path = root / "pg157_sec001.html"
texts_path = root / "content/i18n/sw-TZ/texts.json"
ids_path = root / "content/page157-pdf-match-audio-ids.json"
caption_id = "pg157_n0004"
caption_text = "Kielelezo namba 52: Programu iliyotolewa nakala"

texts = json.loads(texts_path.read_text(encoding="utf-8"))
audio_ids = {caption_id}
texts[caption_id] = caption_text
easy_id = f"{caption_id}_easy_read"
if easy_id in texts:
    texts[easy_id] = caption_text
    audio_ids.add(easy_id)
texts_path.write_text(json.dumps(texts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

tree = html.fromstring(page_path.read_text(encoding="utf-8-sig"))
head = tree.xpath("//head")[0]
style = etree.Element("style")
style.set("data-page-style", "pg157-pdf-match")
style.text = """
  .pdf-page-157 {
    width: min(780px, calc(100vw - 24px));
    max-width: 780px;
    margin: 18px auto;
    padding: 30px 38px 34px;
    border-radius: 24px;
    background: #d5e6ea;
  }
  .pdf-page-157 .page157-intro,
  .pdf-page-157 .page157-body {
    font-size: 1.08rem;
    line-height: 1.48;
  }
  .pdf-page-157 .page157-figure {
    width: 100%;
    max-width: 680px;
    margin: 16px auto 18px;
    padding: 0;
    background: transparent;
  }
  .pdf-page-157 .page157-figure img {
    display: block;
    width: 100%;
    height: auto;
    margin: 0 auto;
    border-radius: 0;
    background: #fff;
  }
  .pdf-page-157 .page157-caption {
    margin-top: 14px;
    text-align: center;
    font-size: 1rem;
    line-height: 1.35;
  }
  @media (max-width: 640px) {
    .pdf-page-157 {
      width: calc(100vw - 12px);
      margin: 6px auto;
      padding: 18px 14px 22px;
      border-radius: 18px;
    }
    .pdf-page-157 .page157-intro,
    .pdf-page-157 .page157-body {
      font-size: .92rem;
      line-height: 1.45;
    }
    .pdf-page-157 .page157-caption { font-size: .88rem; }
  }
"""
head.append(style)

section = tree.xpath('//*[@data-section-id="pg157_sec001"]')[0]
section.set("class", "pdf-page-157 text-slate-800 shadow-sm")

intro = tree.xpath('//*[@data-id="pg157_n0002"]')[0].getparent()
intro.set("class", "page157-intro mb-4 text-left text-slate-800")

figure = tree.xpath('//*[@data-id="pg157_im002"]')[0].getparent()
figure.set("class", "page157-figure")

caption = tree.xpath(f'//*[@data-id="{caption_id}"]')[0]
caption_parent = caption.getparent()
caption_parent.set("class", "page157-caption text-slate-800")
caption.text = None
for child in list(caption):
    caption.remove(child)
strong = etree.SubElement(caption, "strong")
strong.text = "Kielelezo namba 52:"
strong.tail = " "
em = etree.SubElement(caption, "em")
em.text = "Programu iliyotolewa nakala"

body = tree.xpath('//*[@data-id="pg157_n0006"]')[0].getparent().getparent()
body.set("class", "page157-body space-y-4 text-left text-slate-800")

page_path.write_text(
    etree.tostring(tree, encoding="unicode", method="html", doctype="<!DOCTYPE html>"),
    encoding="utf-8",
)
ids_path.write_text(json.dumps(sorted(audio_ids), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print({"updated": sorted(audio_ids)})
