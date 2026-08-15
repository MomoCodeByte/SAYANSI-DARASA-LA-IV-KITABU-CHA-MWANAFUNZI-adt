from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
IMAGES = ROOT / "images"
OUTPUT = IMAGES / "pg043_sharp_tools_complete.png"
CANVAS_SIZE = (900, 470)


def transparent_white(image: Image.Image) -> Image.Image:
    rgba = image.convert("RGBA")
    pixels = []
    for red, green, blue, alpha in rgba.getdata():
        whiteness = min(red, green, blue)
        if whiteness >= 250:
            alpha = 0
        elif whiteness >= 238:
            alpha = int(alpha * (250 - whiteness) / 12)
        pixels.append((red, green, blue, alpha))
    rgba.putdata(pixels)
    return rgba


def place(
    canvas: Image.Image,
    filename: str,
    x: int,
    y: int,
    width: int,
    crop_left: float = 0,
    crop_right: float = 0,
    crop_bottom: float = 0,
) -> None:
    layer = Image.open(IMAGES / filename)
    height = round(layer.height * width / layer.width)
    layer = layer.resize((width, height), Image.Resampling.LANCZOS)
    layer = transparent_white(layer)
    if filename == "pg043_im001_seg003_v1.png":
        # This source tile overlaps the razor tile and contains a small piece
        # of the toothbrush at its lower edge. Retain only the needle/thread.
        alpha = layer.getchannel("A")
        alpha.paste(0, (0, 0, round(layer.width * 0.20), round(layer.height * 0.48)))
        alpha.paste(0, (0, round(layer.height * 0.91), layer.width, layer.height))
        layer.putalpha(alpha)
    left = round(layer.width * crop_left)
    right = layer.width - round(layer.width * crop_right)
    bottom = layer.height - round(layer.height * crop_bottom)
    if crop_left or crop_right or crop_bottom:
        layer = layer.crop((left, 0, right, bottom))
        x += left
    canvas.alpha_composite(layer, (x, y))


canvas = Image.new("RGBA", CANVAS_SIZE, "white")
place(canvas, "pg043_im001_seg001_v1.png", 9, 9, 306)
place(canvas, "pg043_im003.jpg", 333, 23, 81)
place(canvas, "pg043_im001_seg002_v1.png", 423, 0, 288, crop_right=0.16)
place(canvas, "pg043_im001_seg003_v1.png", 620, 5, 306)
place(canvas, "pg043_im001_seg004_v1.png", 0, 230, 333)
place(canvas, "pg043_im002_seg001_v1.png", 351, 240, 63)
place(canvas, "pg043_im002_seg002_v1.png", 459, 240, 63)
place(canvas, "pg043_im001_seg005_v1.png", 558, 259, 333)
canvas.convert("RGB").save(OUTPUT, quality=96)
print(OUTPUT)
