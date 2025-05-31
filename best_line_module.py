
import os
import requests
import json

def fetch_best_lines(sport):
    ODDS_API_KEY = os.getenv("ODDS_API_KEY")
    url = f"https://api.the-odds-api.com/v4/sports/{sport}/odds"
    params = {
        "apiKey": ODDS_API_KEY,
        "regions": "us",
        "markets": "spreads,totals",
        "oddsFormat": "american"
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        games = response.json()
        best_lines = []
        for game in games:
            home_team = game.get("home_team")
            away_team = game.get("away_team")
            bookmakers = game.get("bookmakers", [])
            if not bookmakers:
                continue
            best_book = max(bookmakers, key=lambda b: b["markets"][0]["outcomes"][0]["point"] if b["markets"] else 0)
            best_market = best_book["markets"][0] if best_book.get("markets") else {}
            if not best_market:
                continue
            best_outcome = max(best_market.get("outcomes", []), key=lambda o: o.get("point", 0))
            best_lines.append({
                "matchup": f"{away_team} at {home_team}",
                "book": best_book["title"],
                "line": best_outcome.get("point")
            })
        return best_lines

    print(f"Error fetching odds for {sport}: {response.status_code}")
    return []
```
