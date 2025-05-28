import os
from odds_API import get_all_current_odds
from weather import get_weather_score
from injuries import get_injury_score
from sentiment import get_sentiment_score
from matchup_model import get_matchup_score
from pace import get_pace_score
from fatigue import get_fatigue_score
from promos import get_promo_score
from sharp_sentiment import get_sharp_sentiment_score
from team_locations import TEAM_COORDS

SPORT_SCALING = {
    "americanfootball_nfl": {"weather": 1.0, "injuries": 1.0, "sentiment": 0.9, "matchup": 1.0, "pace": 0.5, "fatigue": 0.7, "promo": 0.6, "sharp": 1.0},
    "americanfootball_ncaaf": {"weather": 0.9, "injuries": 0.8, "sentiment": 0.8, "matchup": 0.9, "pace": 0.5, "fatigue": 0.5, "promo": 0.5, "sharp": 1.0},
    "basketball_nba": {"weather": 0.2, "injuries": 1.0, "sentiment": 1.0, "matchup": 1.0, "pace": 1.0, "fatigue": 1.0, "promo": 0.6, "sharp": 1.0},
    "basketball_ncaab": {"weather": 0.2, "injuries": 0.8, "sentiment": 0.8, "matchup": 0.9, "pace": 0.8, "fatigue": 0.6, "promo": 0.5, "sharp": 1.0},
    "baseball_mlb": {"weather": 1.0, "injuries": 0.7, "sentiment": 0.9, "matchup": 1.0, "pace": 0.9, "fatigue": 0.8, "promo": 0.5, "sharp": 1.0}
}

def get_all_composite_signals():
    games = get_all_current_odds()
    signals = []

    for game in games:
        try:
            sport = game.get("sport_key", "unknown")
            home = game.get("home_team", "")
            away = game.get("away_team", "")
            weights = SPORT_SCALING.get(sport, {})

            lat, lon = TEAM_COORDS.get(home, (None, None))
            if lat is None or lon is None:
                raise ValueError(f"Missing coordinates for {home}")

            weather = get_weather_score(lat, lon, sport) * weights.get("weather", 1.0)
            injuries = get_injury_score(game) * weights.get("injuries", 1.0)
            sentiment = get_sentiment_score(game) * weights.get("sentiment", 1.0)
            matchup = get_matchup_score(game) * weights.get("matchup", 1.0)
            pace = get_pace_score(game) * weights.get("pace", 1.0)
            fatigue = get_fatigue_score(game) * weights.get("fatigue", 1.0)
            promo = get_promo_score(game) * weights.get("promo", 1.0)
            sharp = get_sharp_sentiment_score(game) * weights.get("sharp", 1.0)

            composite = round((weather + injuries + sentiment + matchup + pace + fatigue + promo + sharp), 2)

            signals.append({
                "game": f"{home} vs {away}",
                "line": game.get("bookmakers", [{}])[0].get("markets", [{}])[0].get("outcomes", [{}])[0].get("point", "N/A"),
                "handle": game.get("bookmakers", [{}])[0].get("markets", [{}])[0].get("outcomes", [{}])[0].get("price", "N/A"),
                "weather": round(weather, 2),
                "injuries": round(injuries, 2),
                "sentiment": round(sentiment, 2),
                "matchup": round(matchup, 2),
                "pace": round(pace, 2),
                "fatigue": round(fatigue, 2),
                "promo": round(promo, 2),
                "sharp": round(sharp, 2),
                "composite_score": composite,
                "sport_key": sport
            })
        except Exception as e:
            print(f"[ERROR] Problem processing game: {e}")
            continue

    return signals
