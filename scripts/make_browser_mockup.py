"""
Генерує анімований SVG-мокап браузера, що показує трансформацію
сайту від wireframe (сірі плейсхолдери) до готового кольорового дизайну.

Використання:
    python scripts/make_browser_mockup.py
Результат: browser-mockup.svg
"""

# --- Розміри канви й вікна браузера -----------------------------------
CANVAS_W, CANVAS_H = 370, 420
WIN_X, WIN_Y, WIN_W, WIN_H = 6, 6, 358, 408
CHROME_H = 34               # висота верхньої панелі браузера
PAD = 10                    # внутрішні відступи "сайту" від країв вікна

# --- Палітра ------------------------------------------------------------
PAGE_BG = "#0d1117"         # фон навколо вікна браузера (GitHub dark)
CANVAS_BG = "#ffffff"       # фон самого сайту (світлий, як реальний сайт)
CHROME_BG = "#21262d"
ADDR_BG = "#30363d"
ADDR_TEXT = "#8b949e"
WIN_BORDER = "#30363d"

GRAY_BLOCK = "#e1e4e8"      # wireframe: великі блоки-заглушки
GRAY_ACCENT = "#444c56"     # wireframe: текст/іконки-заглушки

HEADER_FINAL = "#161b22"
LOGO_FINAL = "#ffffff"
NAV_FINAL = "#c9d1d9"

HERO_GRAD_FROM = "#7c3aed"
HERO_GRAD_TO = "#2563eb"
HERO_TEXT_FINAL = "#ffffff"
BUTTON_FINAL = "#ffffff"

CARD_BG_FINAL = "#ffffff"
CARD_STROKE_FINAL = "#d0d7de"
CARD_TITLE_FINAL = "#1b1f24"
CARD_DESC_FINAL = "#57606a"
ICON_COLORS = ["#8957e5", "#1f6feb", "#2ea043"]

FOOTER_FINAL = "#161b22"
FOOTER_LOGO_FINAL = "#ffffff"
FOOTER_LINK_FINAL = "#8b949e"

REVEAL_DUR = 0.3   # тривалість появи (opacity) кожного блоку у фазі 1
COLOR_DUR = 0.55   # тривалість переходу кольору у фазі 2


def fade_in(begin: float, dur: float = REVEAL_DUR) -> str:
    """SMIL-анімація появи блоку: прозорий -> непрозорий, без повтору."""
    return (
        f'<animate attributeName="opacity" values="0;1" '
        f'begin="{begin:.2f}s" dur="{dur:.2f}s" fill="freeze"/>'
    )


def color_shift(attr: str, from_color: str, to_color: str, begin: float, dur: float = COLOR_DUR) -> str:
    """SMIL-анімація переходу кольору (fill/stroke) з сірого в фінальний."""
    return (
        f'<animate attributeName="{attr}" values="{from_color};{to_color}" '
        f'begin="{begin:.2f}s" dur="{dur:.2f}s" fill="freeze"/>'
    )


def rect(x, y, w, h, rx, fill, extra: str = "") -> str:
    return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{fill}">{extra}</rect>'


def circle(cx, cy, r, fill, extra: str = "") -> str:
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" fill="{fill}">{extra}</circle>'


def build_svg() -> str:
    parts: list[str] = []
    parts.append(
        f'<svg viewBox="0 0 {CANVAS_W} {CANVAS_H}" xmlns="http://www.w3.org/2000/svg" '
        f'font-family="Consolas, Menlo, monospace">'
    )

    # фон сторінки навколо вікна браузера
    parts.append(rect(0, 0, CANVAS_W, CANVAS_H, 0, PAGE_BG))

    # --- defs: градієнт для hero-банера, clip для заокругленого вікна ---
    parts.append("<defs>")
    parts.append(
        f'<linearGradient id="heroGrad" x1="0%" y1="0%" x2="100%" y2="100%">'
        f'<stop offset="0%" stop-color="{HERO_GRAD_FROM}"/>'
        f'<stop offset="100%" stop-color="{HERO_GRAD_TO}"/>'
        f'</linearGradient>'
    )
    parts.append(
        f'<clipPath id="winClip"><rect x="{WIN_X}" y="{WIN_Y}" width="{WIN_W}" '
        f'height="{WIN_H}" rx="10"/></clipPath>'
    )
    parts.append("</defs>")

    content_x0 = WIN_X + PAD
    content_x1 = WIN_X + WIN_W - PAD
    content_w = content_x1 - content_x0

    parts.append('<g clip-path="url(#winClip)">')

    # --- полотно сайту (біле тло) ---
    parts.append(rect(WIN_X, WIN_Y, WIN_W, WIN_H, 0, CANVAS_BG))

    # --- верхня панель браузера (chrome) ---
    parts.append(rect(WIN_X, WIN_Y, WIN_W, CHROME_H, 0, CHROME_BG))
    parts.append(circle(WIN_X + 18, WIN_Y + 17, 5, "#ff5f56"))
    parts.append(circle(WIN_X + 36, WIN_Y + 17, 5, "#ffbd2e"))
    parts.append(circle(WIN_X + 54, WIN_Y + 17, 5, "#27c93f"))
    addr_w = 160
    addr_x = WIN_X + (WIN_W - addr_w) / 2
    parts.append(rect(addr_x, WIN_Y + 8, addr_w, 18, 9, ADDR_BG))
    parts.append(
        f'<text x="{addr_x + addr_w / 2:.1f}" y="{WIN_Y + 20.5:.1f}" '
        f'font-size="10" fill="{ADDR_TEXT}" text-anchor="middle">yoursite.com</text>'
    )

    # ============================= HEADER =================================
    header_y = WIN_Y + CHROME_H + PAD
    header_h = 36
    header_end = header_y + header_h

    parts.append(
        rect(content_x0, header_y, content_w, header_h, 6, GRAY_BLOCK,
             fade_in(0.0) + color_shift("fill", GRAY_BLOCK, HEADER_FINAL, 1.50))
    )
    logo_size = 20
    parts.append(
        rect(content_x0 + 10, header_y + (header_h - logo_size) / 2, logo_size, logo_size, 4, GRAY_ACCENT,
             fade_in(0.05) + color_shift("fill", GRAY_ACCENT, LOGO_FINAL, 1.60))
    )
    nav_w, nav_h, nav_gap = 36, 10, 46
    nav_right_pad = 14  # відступ nav/футер-посилань від правого краю хедера/футера
    nav_y = header_y + (header_h - nav_h) / 2
    nav_xs = [content_x1 - nav_right_pad - nav_w - i * nav_gap for i in range(3)][::-1]
    for i, nx in enumerate(nav_xs):
        parts.append(
            rect(nx, nav_y, nav_w, nav_h, 2, GRAY_ACCENT,
                 fade_in(0.05 + i * 0.03) + color_shift("fill", GRAY_ACCENT, NAV_FINAL, 1.60 + i * 0.05))
        )

    # ============================== HERO ===================================
    hero_y = header_end + 14
    hero_h = 120
    hero_end = hero_y + hero_h

    parts.append(
        rect(content_x0, hero_y, content_w, hero_h, 8, GRAY_BLOCK, fade_in(0.20))
    )
    # кольоровий градієнт "проявляється" поверх сірого банера
    parts.append(
        f'<rect x="{content_x0:.1f}" y="{hero_y:.1f}" width="{content_w:.1f}" height="{hero_h:.1f}" '
        f'rx="8" fill="url(#heroGrad)" opacity="0">'
        f'<animate attributeName="opacity" values="0;1" begin="1.50s" dur="0.70s" fill="freeze"/>'
        f'</rect>'
    )

    hx = content_x0 + 20
    parts.append(
        rect(hx, hero_y + 18, 170, 16, 3, GRAY_ACCENT,
             fade_in(0.35) + color_shift("fill", GRAY_ACCENT, HERO_TEXT_FINAL, 1.85))
    )
    parts.append(
        rect(hx, hero_y + 40, 120, 16, 3, GRAY_ACCENT,
             fade_in(0.45) + color_shift("fill", GRAY_ACCENT, HERO_TEXT_FINAL, 1.90))
    )
    parts.append(
        rect(hx, hero_y + 64, 150, 10, 2, GRAY_ACCENT,
             fade_in(0.55) + color_shift("fill", GRAY_ACCENT, "#e6e9f5", 1.95))
    )
    parts.append(
        rect(hx, hero_y + 86, 100, 24, 5, GRAY_ACCENT,
             fade_in(0.65) + color_shift("fill", GRAY_ACCENT, BUTTON_FINAL, 2.00))
    )

    # ============================= FEATURES ================================
    feat_y = hero_end + 16
    feat_h = 90
    feat_end = feat_y + feat_h
    card_gap = 13
    card_w = (content_w - 2 * card_gap) / 3

    for i in range(3):
        cx0 = content_x0 + i * (card_w + card_gap)
        begin = 0.75 + i * 0.10
        color_begin = 1.80 + i * 0.10

        parts.append(
            rect(cx0, feat_y, card_w, feat_h, 8, GRAY_BLOCK,
                 fade_in(begin) + color_shift("fill", GRAY_BLOCK, CARD_BG_FINAL, color_begin)
                 + color_shift("stroke", GRAY_BLOCK, CARD_STROKE_FINAL, color_begin))
        )
        icon_cx = cx0 + card_w / 2
        parts.append(
            circle(icon_cx, feat_y + 26, 12, GRAY_ACCENT,
                   fade_in(begin + 0.05) + color_shift("fill", GRAY_ACCENT, ICON_COLORS[i], color_begin + 0.05))
        )
        title_w = card_w - 34
        parts.append(
            rect(cx0 + 17, feat_y + 50, title_w, 8, 2, GRAY_ACCENT,
                 fade_in(begin + 0.08) + color_shift("fill", GRAY_ACCENT, CARD_TITLE_FINAL, color_begin + 0.08))
        )
        parts.append(
            rect(cx0 + 17, feat_y + 64, title_w, 6, 2, GRAY_ACCENT,
                 fade_in(begin + 0.11) + color_shift("fill", GRAY_ACCENT, CARD_DESC_FINAL, color_begin + 0.11))
        )
        parts.append(
            rect(cx0 + 17, feat_y + 74, title_w * 0.65, 6, 2, GRAY_ACCENT,
                 fade_in(begin + 0.14) + color_shift("fill", GRAY_ACCENT, CARD_DESC_FINAL, color_begin + 0.14))
        )

    # ============================== FOOTER ==================================
    footer_y = feat_end + 16
    footer_h = (WIN_Y + WIN_H - PAD) - footer_y

    parts.append(
        rect(content_x0, footer_y, content_w, footer_h, 8, GRAY_BLOCK,
             fade_in(1.10) + color_shift("fill", GRAY_BLOCK, FOOTER_FINAL, 2.10))
    )
    parts.append(
        rect(content_x0 + 20, footer_y + footer_h / 2 - 5, 50, 10, 2, GRAY_ACCENT,
             fade_in(1.20) + color_shift("fill", GRAY_ACCENT, FOOTER_LOGO_FINAL, 2.20))
    )
    f_nav_y = footer_y + footer_h / 2 - 4
    for i, nx in enumerate(nav_xs):
        parts.append(
            rect(nx, f_nav_y, nav_w, 8, 2, GRAY_ACCENT,
                 fade_in(1.20 + i * 0.03) + color_shift("fill", GRAY_ACCENT, FOOTER_LINK_FINAL, 2.20 + i * 0.05))
        )

    parts.append("</g>")  # кінець clip-path групи

    # рамка вікна поверх усього - завжди чітка, незалежно від clip
    parts.append(
        f'<rect x="{WIN_X}" y="{WIN_Y}" width="{WIN_W}" height="{WIN_H}" rx="10" '
        f'fill="none" stroke="{WIN_BORDER}" stroke-width="1"/>'
    )

    parts.append("</svg>")
    return "".join(parts)


def main():
    svg = build_svg()
    with open("browser-mockup.svg", "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"OK: записано browser-mockup.svg ({CANVAS_W}x{CANVAS_H})")


if __name__ == "__main__":
    main()
