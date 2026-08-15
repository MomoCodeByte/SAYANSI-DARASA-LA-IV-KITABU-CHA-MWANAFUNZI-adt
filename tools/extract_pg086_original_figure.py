from pathlib import Path

from PIL import Image
from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path(r"C:\Users\Admin\Desktop\additionBooks\SAYANSI STD 4 PB\SAYANSI DARASA LA IV KITABU CHA MWANAFUNZI.pdf")
DESTINATION = ROOT / "images" / "pg086_figure2_original.png"


reader = PdfReader(SOURCE)
embedded = reader.pages[85].images[0].image.convert("RGBA")
pixels = []
for red, green, blue, _alpha in embedded.getdata():
    brightness = min(red, green, blue)
    if brightness >= 248:
        alpha = 0
    elif brightness >= 238:
        alpha = round((248 - brightness) * 25.5)
    else:
        alpha = 255
    pixels.append((red, green, blue, alpha))
embedded.putdata(pixels)
embedded.save(DESTINATION, optimize=True)
print(DESTINATION)
