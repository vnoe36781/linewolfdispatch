import requests
import os
from datetime import datetime

ODDS_API_KEY = os.getenv("ODDS_API_KEY")
SPORTS_URL = "https://api.the-odds-api.com/v4/sports"
ODDS_URL_TEMPLATE = "https://api.the-odds-api.com/v4/sports/{sport}/odds/?apiKey={key}&regions=us&markets=spreads,totals&oddsFormat=american"

def get_sports():
    response = requests.get(f"{SPORTS_URL}?apiKey={ODDS_API_KEY}")
    return response.json()

def get_odds_for_sport(sport_key):
    url = ODDS_URL_TEMPLATE.format(sport=sport_key, key=ODDS_API_KEY)
    response = requests.get(url)
    if response.status_code != 200:
        print(f"[{datetime.now()}] Error fetching odds for {sport_key}: {response.status_code}")
        return []
    return response.json()

def get_all_us_odds():
    sports = get_sports()
    valid_sports = [s for s in sports if s.get("active") and s.get("key", "").startswith(("americanfootball", "basketball", "baseball"))]

    all_odds = []
    for sport in valid_sports:
        sport_key = sport["key"]
        sport_odds = get_odds_for_sport(sport_key)
        for game in sport_odds:
            game['sport_key'] = sport_key
            all_odds.append(game)

    return all_odds
