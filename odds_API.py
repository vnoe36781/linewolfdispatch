import os
import requests
import time

ODDS_API_KEY = os.getenv("ODDS_API_KEY")

SPORTS = [
    "americanfootball_nfl",
    "americanfootball_ncaaf",
    "baseball_mlb",
    "basketball_nba",
    "basketball_ncaab"
]

def fetch_odds_for_sport(sport_key):
    url = f"https://api.the-odds-api.com/v4/sports/{sport_key}/odds"
    params = {
        "apiKey": ODDS_API_KEY,
        "regions": "us",
        "markets": "spreads,totals",
        "oddsFormat": "american"
    }
    response = requests.get(url, params=params)

    if response.status_code != 200:
        print(f"[{time.time()}] Error fetching odds for {sport_key}: {response.status_code}")
        return []

    try:
        games = response.json()
        # Filter out any games that are futures markets
        return [g for g in games if not g.get("key", "").endswith("_winner")]
    except Exception as e:
        print(f"[ERROR] Problem processing odds response: {e}")
        return []

def get_all_current_odds():
    all_games = []
    for sport in SPORTS:
        games = fetch_odds_for_sport(sport)
        all_games.extend(games)
    return all_games
