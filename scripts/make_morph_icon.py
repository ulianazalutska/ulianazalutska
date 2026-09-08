"""
Генерує анімовану SVG-іконку "Design -> Code -> Launch": олівець,
дужки коду </> й ракета по черзі проявляються та зникають по колу
(нескінченний цикл, SMIL-анімація, без JS).

Використання:
    python scripts/make_morph_icon.py
Результат: morph-icon.svg
"""

SIZE = 120
CARD_BG = "#161b22"
CARD_BORDER = "#30363d"
GRAD_FROM = "#7c3aed"   # той самий фіолетовий, що й у browser-mockup.svg
GRAD_TO = "#2563eb"
FLAME = "#f59e0b"

CYCLE = 6.0  # тривалість повного циклу (секунди), кожна фаза ~2s


def anim_opacity(values: str, key_times: str) -> str:
    return (
        f'<animate attributeName="opacity" values="{values}" keyTimes="{key_times}" '
        f'dur="{CYCLE}s" repeatCount="indefinite"/>'
    )


def anim_scale(values: str, key_times: str) -> str:
    return (
        f'<animateTransform attributeName="transform" type="scale" '
        f'values="{values}" keyTimes="{key_times}" additive="sum" '
        f'dur="{CYCLE}s" repeatCount="indefinite"/>'
    )


def phase_group(inner: str, opacity_values: str, opacity_times: str,
                 scale_values: str, scale_times: str) -> str:
    # зовнішня <g> масштабує відносно центру (0,0), тому іконку малюємо
    # теж навколо (0,0) і переносимо всю групу в центр картки окремим transform
    return (
        f'<g opacity="0">'
        f'{anim_opacity(opacity_values, opacity_times)}'
        f'<g transform="scale(1)">'
        f'{anim_scale(scale_values, scale_times)}'
        f'{inner}'
        f'</g>'
        f'</g>'
    )


def build_svg() -> str:
    cx, cy = SIZE / 2, SIZE / 2

    svg = []
    svg.append(
        f'<svg viewBox="0 0 {SIZE} {SIZE}" xmlns="http://www.w3.org/2000/svg">'
    )

    svg.append("<defs>")
    svg.append(
        f'<linearGradient id="iconGrad" x1="0%" y1="0%" x2="100%" y2="100%">'
        f'<stop offset="0%" stop-color="{GRAD_FROM}"/>'
        f'<stop offset="100%" stop-color="{GRAD_TO}"/>'
        f'</linearGradient>'
    )
    svg.append("</defs>")

    # картка-тло в стилі решти елементів профілю
    svg.append(
        f'<rect x="1" y="1" width="{SIZE - 2}" height="{SIZE - 2}" rx="16" '
        f'fill="{CARD_BG}" stroke="{CARD_BORDER}"/>'
        f'<title>Design → Code → Launch</title>'
    )

    stroke = 'fill="none" stroke="url(#iconGrad)" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round"'

    # ---- Фаза 1: Design (пензлик) ----
    pencil = (
        # держак
        f'<path d="M16,-16 L5,-5" stroke="url(#iconGrad)" stroke-width="4.2" '
        f'stroke-linecap="round" fill="none"/>'
        # металевий обідок (феруль) - світліший і товщий за держак
        f'<path d="M5,-5 L0,0" stroke="#c9d1d9" stroke-width="6.4" '
        f'stroke-linecap="round" fill="none"/>'
        # ворс пензля - клин від феруля до кінчика
        f'<path d="M0,0 L-12,-3 L-8,10 Z" fill="url(#iconGrad)" stroke-linejoin="round"/>'
        # тонкі волосинки ворсу для текстури
        f'<path d="M-3,-1 L-4,7 M-6,-2 L-7,8" stroke="{CARD_BG}" stroke-width="0.8" '
        f'stroke-linecap="round" opacity="0.5"/>'
        # мазок фарби під кінчиком
        f'<ellipse cx="-8" cy="13" rx="3.4" ry="1.8" fill="url(#iconGrad)" opacity="0.85"/>'
    )
    design_times = "0;0.02;0.30;0.333;1"
    svg.append(
        f'<g transform="translate({cx},{cy})">'
        + phase_group(pencil, "0;1;1;0;0", design_times, "0.85;1;1;0.85;0.85", design_times)
        + "</g>"
    )

    # ---- Фаза 2: Code (</>) ----
    code = (
        f'<path d="M-6,-11 L-16,0 L-6,11" {stroke}/>'
        f'<path d="M6,-11 L16,0 L6,11" {stroke}/>'
        f'<path d="M2,-15 L-2,15" stroke="url(#iconGrad)" stroke-width="2.6" '
        f'stroke-linecap="round" fill="none"/>'
    )
    code_times = "0;0.333;0.353;0.633;0.667;1"
    svg.append(
        f'<g transform="translate({cx},{cy})">'
        + phase_group(code, "0;0;1;1;0;0", code_times, "0.85;0.85;1;1;0.85;0.85", code_times)
        + "</g>"
    )

    # ---- Фаза 3: Launch (ракета) ----
    rocket = (
        f'<path d="M0,-19 C9,-9 9,6 0,15 C-9,6 -9,-9 0,-19 Z" fill="url(#iconGrad)"/>'
        f'<circle cx="0" cy="-4" r="3.2" fill="{CARD_BG}"/>'
        f'<path d="M-3,9 L-11,17 L-3,15 Z" fill="url(#iconGrad)"/>'
        f'<path d="M3,9 L11,17 L3,15 Z" fill="url(#iconGrad)"/>'
        f'<path d="M-3,15 L0,23 L3,15 Z" fill="{FLAME}"/>'
    )
    launch_times = "0;0.667;0.687;0.967;1"
    svg.append(
        f'<g transform="translate({cx},{cy})">'
        + phase_group(rocket, "0;0;1;1;0", launch_times, "0.85;0.85;1;1;0.85", launch_times)
        + "</g>"
    )

    svg.append("</svg>")
    return "".join(svg)


def main():
    svg = build_svg()
    with open("morph-icon.svg", "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"OK: записано morph-icon.svg ({SIZE}x{SIZE})")


if __name__ == "__main__":
    main()
