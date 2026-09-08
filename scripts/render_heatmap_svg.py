"""
Читає data/contributions.json і малює анімовану SVG-теплокарту
контрибуцій (53 тижні x 7 днів), схожу на GitHub, з ефектом
діагонального "з'їзду" квадратиків при завантаженні.
"""
import json
import os
from datetime import datetime, timedelta

# Кольорова палітра: 0 = немає активності, 1..5 = зростання інтенсивності
PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]

CELL = 12          # розмір квадратика
GAP = 3            # відступ між квадратиками
RADIUS = 2         # заокруглення кутів
LEFT_PAD = 30       # місце під підписи днів тижня
TOP_PAD = 30        # місце під підписи місяців
WEEKDAY_LABELS = ["", "Mon", "", "Wed", "", "Fri", ""]


def load_data(path="data/contributions.json") -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_weeks(days: list[dict]) -> list[list[dict | None]]:
    """Розкладає плаский список днів у список тижнів (7 днів кожен),
    вирівняний так, щоб перший день кожного тижня був неділею,
    як на GitHub."""
    parsed = []
    for d in days:
        date = datetime.strptime(d["date"], "%Y-%m-%d")
        parsed.append({"date": date, "level": d["level"]})

    if not parsed:
        return []

    first = parsed[0]["date"]
    # зсуваємось назад до найближчої неділі
    offset = (first.weekday() + 1) % 7  # weekday(): Mon=0 -> зсув до Sun=0
    pad_start = [None] * offset

    all_cells = pad_start + parsed
    weeks = [all_cells[i:i + 7] for i in range(0, len(all_cells), 7)]
    return weeks


def month_labels(weeks: list[list[dict | None]]) -> list[tuple[int, str]]:
    """Повертає список (індекс_тижня, назва_місяця) для підписів зверху."""
    labels = []
    last_month = None
    months_ua = ["Січ", "Лют", "Бер", "Кві", "Тра", "Чер",
                 "Лип", "Сер", "Вер", "Жов", "Лис", "Гру"]
    for i, week in enumerate(weeks):
        first_real = next((d for d in week if d is not None), None)
        if first_real is None:
            continue
        m = first_real["date"].month
        if m != last_month:
            labels.append((i, months_ua[m - 1]))
            last_month = m
    return labels


def render_svg(data: dict, out_path="contrib-heatmap.svg"):
    weeks = build_weeks(data["days"])
    stats = data["stats"]
    username = data["username"]

    n_weeks = len(weeks)
    width = LEFT_PAD + n_weeks * (CELL + GAP) + 20
    height = TOP_PAD + 7 * (CELL + GAP) + 40

    svg_parts = []
    svg_parts.append(
        f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" '
        f'font-family="Segoe UI, Helvetica, Arial, sans-serif">'
    )

    # фон
    svg_parts.append(f'<rect width="{width}" height="{height}" fill="#0d1117" rx="8"/>')

    # стилі анімації: кожен стовпець (тиждень) з'їжджає зверху з невеликою затримкою
    style_lines = ["<style>"]
    style_lines.append("""
    .cell { opacity: 0; transform: translateY(-8px); animation: dropIn 0.4s ease-out forwards; }
    @keyframes dropIn {
        to { opacity: 1; transform: translateY(0); }
    }
    .label { fill: #8b949e; font-size: 10px; }
    """)
    style_lines.append("</style>")
    svg_parts.append("".join(style_lines))

    # підписи місяців
    labels = month_labels(weeks)
    for week_idx, name in labels:
        x = LEFT_PAD + week_idx * (CELL + GAP)
        svg_parts.append(f'<text x="{x}" y="{TOP_PAD - 10}" class="label">{name}</text>')

    # підписи днів тижня
    for row, label in enumerate(WEEKDAY_LABELS):
        if label:
            y = TOP_PAD + row * (CELL + GAP) + CELL - 2
            svg_parts.append(f'<text x="0" y="{y}" class="label">{label}</text>')

    # квадратики, з діагональним стагером (тиждень + день дає затримку)
    for week_idx, week in enumerate(weeks):
        for day_idx, cell in enumerate(week):
            if cell is None:
                continue
            x = LEFT_PAD + week_idx * (CELL + GAP)
            y = TOP_PAD + day_idx * (CELL + GAP)
            level = min(cell["level"], 5)
            color = PALETTE[level]
            delay = (week_idx * 0.012) + (day_idx * 0.02)
            date_str = cell["date"].strftime("%Y-%m-%d")
            svg_parts.append(
                f'<rect class="cell" x="{x}" y="{y}" width="{CELL}" height="{CELL}" '
                f'rx="{RADIUS}" fill="{color}" style="animation-delay:{delay:.3f}s">'
                f'<title>{date_str}</title></rect>'
            )

    # легенда Less -> More
    legend_y = height - 24
    svg_parts.append(f'<text x="{LEFT_PAD}" y="{legend_y + 9}" class="label">Less</text>')
    lx = LEFT_PAD + 35
    for level, color in enumerate(PALETTE):
        svg_parts.append(
            f'<rect x="{lx}" y="{legend_y}" width="{CELL}" height="{CELL}" rx="{RADIUS}" fill="{color}"/>'
        )
        lx += CELL + GAP
    svg_parts.append(f'<text x="{lx + 4}" y="{legend_y + 9}" class="label">More</text>')

    # статистика знизу
    stats_text = (
        f"{stats['active_days']} активних днів · "
        f"найдовший стрік {stats['longest_streak']} · "
        f"поточний стрік {stats['current_streak']}"
    )
    svg_parts.append(
        f'<text x="{LEFT_PAD}" y="{height - 4}" class="label">{stats_text}</text>'
    )

    svg_parts.append("</svg>")

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("".join(svg_parts))

    print(f"OK: записано {out_path} ({width}x{height}, {n_weeks} тижнів)")


def main():
    data = load_data()
    render_svg(data)


if __name__ == "__main__":
    main()