from pathlib import Path
from PIL import Image, ImageEnhance, ImageFilter

src = Path(r"C:\Users\Admin\Downloads")
out = Path(r"C:\Users\Admin\Documents\New project\sayansi-std4-source\tmp\matrix-photos")
out.mkdir(parents=True, exist_ok=True)
specs = [
    ("WhatsApp Image 2026-08-14 at 16.35.19.jpeg", (35, 555, 505, 1015), "matrix-1.png"),
    ("WhatsApp Image 2026-08-14 at 16.35.20 (2).jpeg", (0, 300, 510, 700), "matrix-2.png"),
    ("WhatsApp Image 2026-08-14 at 16.35.20 (1).jpeg", (0, 300, 510, 700), "matrix-3.png"),
    ("WhatsApp Image 2026-08-14 at 16.35.20.jpeg", (0, 335, 510, 720), "matrix-4.png"),
    ("WhatsApp Image 2026-08-14 at 16.35.21.jpeg", (25, 330, 500, 760), "matrix-5.png"),
]
for name, box, target in specs:
    im = Image.open(src / name).convert("RGB").crop(box)
    im = im.resize((im.width * 3, im.height * 3), Image.Resampling.LANCZOS)
    im = ImageEnhance.Contrast(im).enhance(1.25)
    im = ImageEnhance.Sharpness(im).enhance(1.6)
    im = im.filter(ImageFilter.UnsharpMask(radius=1.2, percent=130, threshold=2))
    if target == "matrix-1.png":
        im = im.rotate(14, expand=True, fillcolor="white")
    im.save(out / target)
    print(out / target)
