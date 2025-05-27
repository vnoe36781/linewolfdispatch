
import requests
import json
import time
from datetime import datetime

ODDS_API_KEY = "96c5b309c0dd26637015b8772f450abf"
SPORT = "americanfootball_nfl"
REGIONS = "us"
MARKETS = "spreads"
BOOK_NAME = "FanDuel"
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1376076095627071618/gpOqarzq4rNt1zI5OgTu1Jf-27-aAra5d8AD7QXY6O4jOLQtWxt-R5y_aqiiVoUkcozH"

ODDS_API_URL = f"https://api.the-odds-api.com/v4/sports/{SPORT}/odds"

last_seen_lines = {}

def fetch_current_odds():
    params = {
        "apiKey": ODDS_API_KEY,
        "regions": REGIONS,
        "markets": MARKETS,
        "oddsFormat": "american"
    }
    response = requests.get(ODDS_API_URL, params=params)
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        return []
    return response.json()

def detect_line_moves():
    global last_seen_lines
    games = fetch_current_odds()
    if not games:
        return

    for game in games:
        game_name = f"{game.get('teams', ['?','?'])[0]} vs {game.get('teams', ['?','?'])[1]}"
        bookmakers = game.get("bookmakers", [])
        book = next((b for b in bookmakers if b["title"] == BOOK_NAME), None)
        if not book:
            continue

        market = next((m for m in book["markets"] if m["key"] == "spreads"), None)
        if not market:
            continue

        for outcome in market["outcomes"]:
            team = outcome["name"]
            current_point = outcome["point"]
            game_key = f"{game_name}_{team}"
            previous_point = last_seen_lines.get(game_key)

            if previous_point is not None and abs(current_point - previous_point) >= 1.0:
                send_alert(game_name, team, previous_point, current_point)

            last_seen_lines[game_key] = current_point

def send_alert(game, team, old_line, new_line):
    now = datetime.now().strftime("%I:%M %p EST")
    content = (
        "**Line Movement Detected**\n"
        f"- Game: {game}\n"
        f"- Team: {team}\n"
        f"- Line Moved: {old_line} -> {new_line}\n"
        f"- Book: {BOOK_NAME}\n"
        f"- Time: {now}"
    )
    requests.post(DISCORD_WEBHOOK_URL, json={"content": content})

if __name__ == "__main__":
    detect_line_moves()
