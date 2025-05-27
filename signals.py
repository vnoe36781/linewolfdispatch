
import requests
import random
from collections import defaultdict
from sentiment import get_sentiment_for_game

ODDS_API_KEY = "96c5b309c0dd26637015b8772f450abf"
OPENWEATHER_KEY = "4fa20ed06da34783779674e788464386"
SPORTS = ["basketball_nba", "basketball_ncaab", "baseball_mlb", "americanfootball_nfl", "americanfootball_ncaaf"]
REGIONS = "us"
MARKETS = "spreads"
ODDS_API_URL = "https://api.the-odds-api.com/v4/sports/{sport}/odds"
SLEEPER_INJURY_URL = "https://api.sleeper.app/v1/players/injuries"
OPENWEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"

NFL_TEAM_CITIES = {
    "BUF": "Buffalo", "KC": "Kansas City", "NYJ": "East Rutherford", "NYG": "East Rutherford",
    "PHI": "Philadelphia", "GB": "Green Bay", "NE": "Foxborough", "CHI": "Chicago",
    "DAL": "Arlington", "MIA": "Miami", "TB": "Tampa", "LA": "Los Angeles",
    "LV": "Las Vegas", "NO": "New Orleans", "IND": "Indianapolis", "ATL": "Atlanta"
}
DOME_TEAMS = {"ATL", "NO", "IND", "MIN", "DAL", "DET", "ARI", "LAR", "LV", "HOU"}

def fetch_odds(sport):
    url = ODDS_API_URL.format(sport=sport)
    params = {
        "apiKey": ODDS_API_KEY,
        "regions": REGIONS,
        "markets": MARKETS,
        "oddsFormat": "american"
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        print(f"Failed to fetch odds for {sport}: {response.status_code}")
        return []
    return response.json()

def fetch_nfl_injuries():
    response = requests.get(SLEEPER_INJURY_URL)
    if response.status_code != 200:
        return {}
    injuries = response.json()
    team_injuries = defaultdict(list)
    for p in injuries:
        team = p.get("team")
        if not team or p.get("status") not in ["out", "questionable", "doubtful"]:
            continue
        name = p.get("full_name", "Unknown")
        pos = p.get("position", "??")
        status = p.get("status")
        team_injuries[team].append(f"{pos} {name} ({status})")
    return team_injuries

def fetch_weather(city):
    params = {"q": city, "appid": OPENWEATHER_KEY, "units": "imperial"}
    response = requests.get("https://api.openweathermap.org/data/2.5/weather", params=params)
    if response.status_code != 200:
        return "Weather data unavailable"
    data = response.json()
    wind = data.get("wind", {}).get("speed", 0)
    temp = data.get("main", {}).get("temp", "?")
    desc = data.get("weather", [{}])[0].get("description", "?")
    return f"{int(wind)}mph wind, {desc}, {int(temp)}°F"

def parse_game(game, team_injuries):
    teams = game.get("teams", [])
    if len(teams) != 2:
        return None
    home_team = game.get("home_team")
    away_team = [t for t in teams if t != home_team][0]
    game_name = f"{away_team} vs {home_team}"

    bookmakers = game.get("bookmakers", [])
    if not bookmakers:
        return None

    lines = {}
    for book in bookmakers:
        for market in book.get("markets", []):
            for outcome in market.get("outcomes", []):
                if outcome["name"] in teams:
                    lines[outcome["name"]] = outcome["point"]

    is_nfl = game.get("sport_key", "") == "americanfootball_nfl"
    injury_summary = ""
    if is_nfl:
        away_injuries = "; ".join(team_injuries.get(away_team, [])) or "No notable injuries"
        home_injuries = "; ".join(team_injuries.get(home_team, [])) or "No notable injuries"
        injury_summary = f"{away_team}: {away_injuries} | {home_team}: {home_injuries}"
    else:
        injury_summary = "No verified data (non-NFL game)"

    if home_team in DOME_TEAMS:
        weather_summary = "Dome – weather irrelevant"
    else:
        city = NFL_TEAM_CITIES.get(home_team, "Philadelphia")
        weather_summary = fetch_weather(city)

    sentiment_summary = get_sentiment_for_game(game_name)

    return {
        "game": game_name,
        "composite_score": round(random.uniform(6.0, 9.5), 2),
        "line": f"{away_team}: {lines.get(away_team, '?')} | {home_team}: {lines.get(home_team, '?')}",
        "handle": "Mock handle data",
        "sentiment": sentiment_summary,
        "injuries": injury_summary,
        "weather": weather_summary,
        "matchup": f"{away_team} tempo advantage, {home_team} weak red zone D"
    }

def get_all_composite_signals():
    all_signals = []
    nfl_injuries = fetch_nfl_injuries()
    for sport in SPORTS:
        games = fetch_odds(sport)
        for game in games:
            parsed = parse_game(game, nfl_injuries)
            if parsed:
                all_signals.append(parsed)
    return all_signals
