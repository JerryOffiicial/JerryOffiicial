"""Step 5b: public GitHub stats -> data/github.json (feeds Uptime / GitHub / Langs in neofetch.svg)

Uses GH_TOKEN or GITHUB_TOKEN when set (the workflow passes one) to avoid the
60-requests-an-hour anonymous limit. Only public, non-fork repos are counted, and
this profile repo is skipped so its own scripts don't show up as a language.
On any error the previous data/github.json is kept.
"""
import json
import os
import sys
from datetime import datetime, timezone

import requests

USERNAME = os.environ.get("GH_USER", "JerryOffiicial")
API = "https://api.github.com"
OUT = "data/github.json"

s = requests.Session()
s.headers["Accept"] = "application/vnd.github+json"
token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
if token:
    s.headers["Authorization"] = f"Bearer {token}"


def get(path):
    r = s.get(f"{API}{path}", timeout=30)
    r.raise_for_status()
    return r.json()


try:
    user = get(f"/users/{USERNAME}")
    repos, page = [], 1
    while True:
        batch = get(f"/users/{USERNAME}/repos?type=owner&per_page=100&page={page}")
        repos += batch
        if len(batch) < 100:
            break
        page += 1

    languages = {}
    for r in repos:
        if r["fork"] or r["name"].lower() == USERNAME.lower() or not r["size"]:
            continue
        for lang, n in get(f"/repos/{USERNAME}/{r['name']}/languages").items():
            languages[lang] = languages.get(lang, 0) + n
except requests.RequestException as e:
    print(f"GitHub API failed ({e}); keeping the previous {OUT}", file=sys.stderr)
    sys.exit(0)

data = {
    "username": USERNAME,
    "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    "created_at": user["created_at"],
    "public_repos": user["public_repos"],
    "languages": dict(sorted(languages.items(), key=lambda kv: -kv[1])),
}
os.makedirs("data", exist_ok=True)
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=1)
print(f"{USERNAME}: {data['public_repos']} public repos, {len(languages)} languages")
