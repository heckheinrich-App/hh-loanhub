"""
HH LOANHUB - PWA Icon Generator
Generates icon-192.png and icon-512.png
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ICONS_DIR = Path(__file__).resolve().parent.parent / "ui" / "icons"
ICONS_DIR.mkdir(parents=True, exist_ok=True)


def create_app_icon(size: int, output_path: Path):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Rounded background
    radius = int(size * 0.22)
    # Emerald gradient background approximation
    draw.rounded_rectangle([0, 0, size, size], radius=radius, fill=(11, 122, 40, 255))
    draw.rounded_rectangle([int(size * 0.05), int(size * 0.05), int(size * 0.95), int(size * 0.95)], radius=radius, fill=(25, 169, 62, 255))

    # White swoosh arc at top
    draw.arc([int(size * 0.15), int(size * 0.08), int(size * 0.85), int(size * 0.55)], start=180, end=360, fill=(255, 255, 255, 200), width=int(size * 0.04))

    # Bold HH Monogram
    h_top = int(size * 0.32)
    h_bottom = int(size * 0.68)
    h_thick = int(size * 0.08)

    # First H
    h1_left = int(size * 0.24)
    h1_right = int(size * 0.42)
    draw.rectangle([h1_left, h_top, h1_left + h_thick, h_bottom], fill=(255, 255, 255, 255))
    draw.rectangle([h1_right, h_top, h1_right + h_thick, h_bottom], fill=(255, 255, 255, 255))
    draw.rectangle([h1_left, int(size * 0.47), h1_right + h_thick, int(size * 0.47) + h_thick], fill=(255, 255, 255, 255))

    # Second H
    h2_left = int(size * 0.54)
    h2_right = int(size * 0.72)
    draw.rectangle([h2_left, h_top, h2_left + h_thick, h_bottom], fill=(255, 255, 255, 255))
    draw.rectangle([h2_right, h_top, h2_right + h_thick, h_bottom], fill=(255, 255, 255, 255))
    draw.rectangle([h2_left, int(size * 0.47), h2_right + h_thick, int(size * 0.47) + h_thick], fill=(255, 255, 255, 255))

    # Gold Rand Coin in lower right
    coin_cx = int(size * 0.76)
    coin_cy = int(size * 0.74)
    coin_r = int(size * 0.13)
    draw.ellipse([coin_cx - coin_r, coin_cy - coin_r, coin_cx + coin_r, coin_cy + coin_r], fill=(245, 158, 11, 255), outline=(255, 255, 255, 255), width=int(size * 0.015))

    # Letter 'R' on coin
    try:
        font = ImageFont.truetype("arial.ttf", int(coin_r * 1.2))
        draw.text((coin_cx - int(coin_r * 0.35), coin_cy - int(coin_r * 0.65)), "R", fill=(17, 24, 39, 255), font=font)
    except Exception:
        # Fallback if font missing
        draw.rectangle([coin_cx - int(coin_r * 0.3), coin_cy - int(coin_r * 0.5), coin_cx - int(coin_r * 0.1), coin_cy + int(coin_r * 0.5)], fill=(17, 24, 39, 255))

    img.save(output_path, "PNG")
    print(f"Generated {output_path} ({size}x{size})")


if __name__ == "__main__":
    create_app_icon(192, ICONS_DIR / "icon-192.png")
    create_app_icon(512, ICONS_DIR / "icon-512.png")
