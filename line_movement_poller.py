import os
import requests
import json
import datetime
import pytz

WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL_LINE")
API_KEY = os.getenv("ODDS_API_KEY")
SPORTS = ["americanfootball_nfl", "basketball_nba", "baseball_mlb", "americanfootball_ncaaf", "basketball_ncaab"]
REGIONS = "us"
MARKETS = "spreads"

def fetch_odds(sport):
    url = f"https://api.the-odds-api.com/v4/sports/{sport}/odds"
    params = {
        "apiKey": API_KEY,
        "regions": REGIONS,
        "markets": MARKETS,
        "oddsFormat": "american"
    }
    response = requests.get(url, params=params)
    return response.json() if response.status_code == 200 else []

def post_to_discord(message):
    payload = {
        "content": f"**Line Movement Detected**\n{message}"
    }
    headers = {"Content-Type": "application/json"}
    requests.post(WEBHOOK_URL, data=json.dumps(payload), headers=headers)

def detect_line_movements():
    eastern = pytz.timezone("US/Eastern")
    now = datetime.datetime.now(eastern).strftime("%I:%M %p EST")

    for sport in SPORTS:
        games = fetch_odds(sport)
        for game in games:
            teams = game.get("teams", [])
            if len(teams) != 2:
                continue  # Skip malformed or future markets without opponent

            home_team = game.get("home_team")
            away_team = [team for team in teams if team != home_team][0]

            bookmakers = game.get("bookmakers", [])
            for book in bookmakers:
                book_name = book.get("title")
                for market in book.get("markets", []):
                    if market.get("key") != "spreads":
                        continue
                    outcomes = market.get("outcomes", [])
                    if len(outcomes) != 2:
                        continue
                    line1 = outcomes[0]["point"]
                    line2 = outcomes[1]["point"]
                    delta = abs(line1 - line2)
                    if delta >= 1.0:
                        message = (
                            f"- Game: {away_team} vs {home_team}\n"
                            f"- Line Moved: {outcomes[0]['name']} {line1} → {line2}\n"
                            f"- Book: {book_name}\n"
                            f"- Time: {now}"
                        )
                        post_to_discord(message)

if __name__ == "__main__":
    detect_line_movements()

if __name__ == "__main__":
    detect_line_moves()
