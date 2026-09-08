"""
Генерує neofetch-стиль SVG-картку: заголовок + рядки key/value,
кожен рядок з'являється з невеликою затримкою (fade + slide-in).

Використання:
    python scripts/make_info_card.py
Результат: info-card.svg

Змінна оточення STATIC=1 вимикає анімацію (для статичного прев'ю).
"""
import os

# ------- Дані картки: онови під себе -------
NAME = "Uliana Zalutska"
USER_AT = "uliana@github"

ROWS = [
    ("Role", "Web Designer / Full-stack Sites"),
    ("Design", "Figma, Photoshop, Elementor"),
    ("Frontend", "HTML/CSS/JS, React, Next.js, TS, Tailwind"),
    ("Backend", "PHP, Node.js, WordPress, MySQL, REST API"),
    ("Extras", "Git/GitHub, SEO, AI tools (ChatGPT, Claude, MJ)"),
    ("Highlight", "5+ years working with AI"),
]

WIDTH = 490
PADDING = 22
LINE_HEIGHT = 30
TITLE_H = 46

FONT = "Consolas, Menlo, monospace"
BG = "#0d1117"
TITLE_BG = "#161b22"
BORDER = "#30363d"
KEY_COLOR = "#39d353"   # зелений, як GitHub-акцент
VALUE_COLOR = "#c9d1d9"
DOT_COLORS = ["#ff5f56", "#ffbd2e", "#27c93f"]  # macOS-стиль кружечків у шапці

STATIC = os.environ.get("STATIC") == "1"


def escape_xml(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_svg() -> str:
    height = TITLE_H + PADDING + len(ROWS) * LINE_HEIGHT + PADDING

    svg = []
    svg.append(
        f'<svg viewBox="0 0 {WIDTH} {height}" xmlns="http://www.w3.org/2000/svg" '
        f'font-family="{FONT}">'
    )

    # фон + рамка
    svg.append(
        f'<rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{height - 1}" '
        f'rx="8" fill="{BG}" stroke="{BORDER}"/>'
    )

    # титульна панель, як термінал (з кружечками)
    svg.append(
        f'<path d="M1,8 a7,7 0 0 1 7,-7 h{WIDTH - 16} a7,7 0 0 1 7,7 v{TITLE_H - 8} '
        f'h-{WIDTH - 2} z" fill="{TITLE_BG}"/>'
    )
    for i, color in enumerate(DOT_COLORS):
        cx = PADDING + i * 18
        svg.append(f'<circle cx="{cx}" cy="{TITLE_H / 2:.0f}" r="6" fill="{color}"/>')

    title_text = escape_xml(f"{USER_AT} ~ $ neofetch")
    svg.append(
        f'<text x="{WIDTH / 2:.0f}" y="{TITLE_H / 2 + 4:.0f}" fill="{VALUE_COLOR}" '
        f'font-size="12" text-anchor="middle">{title_text}</text>'
    )

    # стилі анімації рядків
    if not STATIC:
        svg.append("""
        <style>
        .row { opacity: 0; transform: translateX(-6px); animation: slideFade 0.35s ease-out forwards; }
        @keyframes slideFade { to { opacity: 1; transform: translateX(0); } }
        </style>
        """)

    # ім'я великим шрифтом одразу під шапкою
    name_y = TITLE_H + PADDING
    svg.append(
        f'<text x="{PADDING}" y="{name_y:.0f}" fill="{VALUE_COLOR}" '
        f'font-size="17" font-weight="bold" class="row" '
        f'style="animation-delay:0.05s">{escape_xml(NAME)}</text>'
    )
    svg.append(
        f'<line x1="{PADDING}" y1="{name_y + 10}" x2="{WIDTH - PADDING}" y2="{name_y + 10}" '
        f'stroke="{BORDER}"/>'
    )

    # key: value рядки
    start_y = name_y + 10 + LINE_HEIGHT
    for i, (key, value) in enumerate(ROWS):
        y = start_y + i * LINE_HEIGHT
        delay = 0.15 + i * 0.12
        svg.append(
            f'<text x="{PADDING}" y="{y:.0f}" fill="{KEY_COLOR}" font-size="13" '
            f'font-weight="bold" class="row" style="animation-delay:{delay:.2f}s">{escape_xml(key)}</text>'
        )
        svg.append(
            f'<text x="{PADDING + 90}" y="{y:.0f}" fill="{VALUE_COLOR}" font-size="13" '
            f'class="row" style="animation-delay:{delay:.2f}s">{escape_xml(value)}</text>'
        )

    svg.append("</svg>")
    return "".join(svg)


def main():
    svg = build_svg()
    with open("info-card.svg", "w", encoding="utf-8") as f:
        f.write(svg)
    print("OK: записано info-card.svg")


if __name__ == "__main__":
    main()