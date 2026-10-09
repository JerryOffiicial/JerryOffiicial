"""Step 5a: scrape the public contribution calendar (no token) -> data/contributions.json"""
import json, os, re, sys
from collections import defaultdict
from datetime import date, datetime, timezone
import requests
from bs4 import BeautifulSoup

USERNAME = os.environ.get("GH_USER", "JerryOffiicial")
URL = f"https://github.com/users/{USERNAME}/contributions"

html = requests.get(URL, headers={"User-Agent": "profile-readme-bot"}, timeout=30).text
soup = BeautifulSoup(html, "html.parser")

# counts live in <tool-tip for="cell-id">N contributions on ...</tool-tip>
tips = {}
for t in soup.find_all("tool-tip"):
    txt = t.get_text(" ", strip=True)
    m = re.match(r"([\d,]+) contribution", txt)
    tips[t.get("for")] = int(m.group(1).replace(",", "")) if m else 0

days = []
for td in soup.select("td.ContributionCalendar-day[data-date]"):
    days.append({
        "date": td["data-date"],
        "level": int(td.get("data-level", 0)),
        "count": tips.get(td.get("id"), 0),
    })
days.sort(key=lambda d: d["date"])
if not days:
    sys.exit("No contribution cells found — GitHub markup may have changed.")

# streaks (today with 0 doesn't break the current streak yet)
today = date.today().isoformat()
cur = 0
for d in reversed(days):
    if d["date"] == today and d["count"] == 0:
        continue
    if d["count"] > 0:
        cur += 1
    else:
        break
longest = run = 0
for d in days:
    run = run + 1 if d["count"] > 0 else 0
    longest = max(longest, run)

monthly = defaultdict(int)
for d in days:
    monthly[d["date"][:7]] += d["count"]
best = max(days, key=lambda d: d["count"])

data = {
    "username": USERNAME,
    "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    "total": sum(d["count"] for d in days),
    "current_streak": cur,
    "longest_streak": longest,
    "best_day": {"date": best["date"], "count": best["count"]},
    "monthly": dict(monthly),
    "days": days,
}
os.makedirs("data", exist_ok=True)
json.dump(data, open("data/contributions.json", "w"), indent=1)
print(f"{USERNAME}: {data['total']} contributions, {len(days)} days, streak {cur}, longest {longest}")
