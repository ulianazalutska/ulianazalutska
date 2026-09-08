"""
Отримує публічний календар контрибуцій GitHub без токена
і зберігає його у data/contributions.json
"""
import json
import os
import sys
from datetime import datetime

import requests
from bs4 import BeautifulSoup

USERNAME = os.environ.get("GITHUB_USERNAME", "ulianazalutska")


def fetch_contributions(username: str) -> list[dict]:
    url = f"https://github.com/users/{username}/contributions"
    resp = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    days = []

    # GitHub рендерить кожен день як <td> з data-date і data-level
    cells = soup.select("td.ContributionCalendar-day")
    for cell in cells:
        date = cell.get("data-date")
        level = cell.get("data-level")
        if date is None or level is None:
            continue
        days.append({"date": date, "level": int(level)})

    days.sort(key=lambda d: d["date"])
    return days


def compute_stats(days: list[dict]) -> dict:
    counts = [d["level"] for d in days]
    total = sum(1 for c in counts if c > 0)  # рахуємо дні з активністю
    # рахуємо поточний і найдовший стрік
    longest = current = 0
    for c in counts:
        if c > 0:
            current += 1
            longest = max(longest, current)
        else:
            current = 0
    # поточний активний стрік (з кінця)
    tail_streak = 0
    for c in reversed(counts):
        if c > 0:
            tail_streak += 1
        else:
            break

    return {
        "active_days": total,
        "longest_streak": longest,
        "current_streak": tail_streak,
        "generated_at": datetime.utcnow().isoformat() + "Z",
    }


def main():
    username = sys.argv[1] if len(sys.argv) > 1 else USERNAME
    days = fetch_contributions(username)
    if not days:
        print("Не вдалося знайти жодного дня контрибуцій — перевір username", file=sys.stderr)
        sys.exit(1)

    stats = compute_stats(days)
    out = {"username": username, "days": days, "stats": stats}

    os.makedirs("data", exist_ok=True)
    with open("data/contributions.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(f"OK: збережено {len(days)} днів для {username}")
    print(stats)


if __name__ == "__main__":
    main()