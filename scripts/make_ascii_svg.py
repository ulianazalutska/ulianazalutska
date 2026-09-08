"""
Перетворює source-prepped.png на самодрукуючий монохромний
ASCII-портрет у форматі анімованого SVG.

Використання:
    python scripts/make_ascii_svg.py
Результат: avi-ascii.svg (тут: portrait.svg за замовчуванням)
"""
import sys

import numpy as np
from PIL import Image, ImageFilter

# рампа символів: пробіл (яскраво/фон) -> щільні символи (темно/об'єкт).
# Довша й щільніша рампа з плавним переходом дає більше рівнів сірого,
# тому риси обличчя (тіні під бровами, вилиці, губи) не губляться в шумі.
RAMP = " .:-=+*#%@"

GRID_W = 210   # символів по горизонталі (визначає роздільність портрета)

FONT_SIZE = 8
CHAR_W = FONT_SIZE * 0.6   # приблизна ширина моноширинного символу
CHAR_H = FONT_SIZE * 1.15  # висота рядка

FILL_COLOR = "#c9d1d9"  # світло-сірий, монохром - без райдужних кольорів

GAMMA = 0.85  # <1 підсвітлює середні тони, підкреслюючи риси обличчя


def image_to_ascii_grid(path: str, grid_w: int) -> list[str]:
    img = Image.open(path).convert("L")
    img_w, img_h = img.size

    # Розмір сітки рахуємо від реальних пропорцій фото, компенсуючи
    # прямокутну форму символу моноширинного шрифту (CHAR_W x CHAR_H).
    # Інакше resize() до довільних grid_w x grid_h спотворює обличчя
    # (розтягує/стискає його) ще до того, як воно потрапить у ASCII.
    char_aspect = CHAR_H / CHAR_W
    grid_h = max(1, round(grid_w * (img_h / img_w) / char_aspect))

    # М'яке розмиття перед downsample прибирає піксельний шум/муар
    # (волосся, зернистість після CLAHE), залишаючи плавні світлотіні -
    # без цього кроку дрібні деталі перетворюються на випадкові символи.
    blur_radius = max(img_w / grid_w, img_h / grid_h) / 5
    if blur_radius > 0.3:
        img = img.filter(ImageFilter.GaussianBlur(radius=blur_radius))

    img = img.resize((grid_w, grid_h), Image.LANCZOS)
    arr = np.array(img).astype(np.float64) / 255.0

    # Гамма-корекція: підсвітлює середні тони, щоб риси обличчя
    # (не лише найтемніші волосся/тіні) отримали окремі символи рампи.
    arr = np.power(arr, GAMMA)

    rows = []
    ramp_len = len(RAMP)
    for y in range(grid_h):
        row_chars = []
        for x in range(grid_w):
            brightness = arr[y, x]  # 0.0 (темно) .. 1.0 (світло)
            idx = int((1.0 - brightness) * (ramp_len - 1))
            row_chars.append(RAMP[idx])
        rows.append("".join(row_chars))
    return rows


def escape_xml(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def render_svg(rows: list[str], out_path: str = "avi-ascii.svg"):
    grid_h = len(rows)
    grid_w = len(rows[0]) if rows else 0

    width = grid_w * CHAR_W
    height = grid_h * CHAR_H

    svg = []
    svg.append(
        f'<svg viewBox="0 0 {width:.0f} {height:.0f}" xmlns="http://www.w3.org/2000/svg" '
        f'font-family="Consolas, Menlo, monospace" font-size="{FONT_SIZE}">'
    )
    svg.append(f'<rect width="{width:.0f}" height="{height:.0f}" fill="#0d1117"/>')

    # clipPath для кожного рядка: анімована ширина 0 -> 100%, "друк" зліва направо
    svg.append("<defs>")
    for row_idx in range(grid_h):
        clip_id = f"clip{row_idx}"
        row_y = row_idx * CHAR_H
        svg.append(f'<clipPath id="{clip_id}">')
        svg.append(
            f'<rect x="0" y="{row_y:.1f}" height="{CHAR_H:.1f}" width="0">'
            f'<animate attributeName="width" from="0" to="{width:.0f}" '
            f'dur="0.35s" begin="{row_idx * 0.05:.2f}s" fill="freeze"/>'
            f'</rect>'
        )
        svg.append('</clipPath>')
    svg.append("</defs>")

    # текстові рядки, кожен обгорнутий власним clip-path
    for row_idx, row in enumerate(rows):
        y = (row_idx + 1) * CHAR_H - CHAR_H * 0.25
        text_escaped = escape_xml(row)
        svg.append(
            f'<g clip-path="url(#clip{row_idx})">'
            f'<text x="0" y="{y:.1f}" fill="{FILL_COLOR}" xml:space="preserve">{text_escaped}</text>'
            f'</g>'
        )

    svg.append("</svg>")

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("".join(svg))
    print(f"OK: записано {out_path} ({width:.0f}x{height:.0f}, {grid_w}x{grid_h} символів)")


def main():
    input_path = sys.argv[1] if len(sys.argv) > 1 else "source-prepped.png"
    out_path = sys.argv[2] if len(sys.argv) > 2 else "avi-ascii.svg"
    rows = image_to_ascii_grid(input_path, GRID_W)
    render_svg(rows, out_path)


if __name__ == "__main__":
    main()