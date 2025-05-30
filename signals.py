import os
from weather import get_weather_score
from team_locations import get_team_coordinates
from matchup_model import get_matchup_score
from sentiment import get_sentiment_score
from pace import get_pace_score
from ref_trends import get_ref_score
from promo_scraper import get_promo_score
from odds_API import get_all_current_odds

# Indoor game exclusions
INDOOR_SPORTS = {"nba", "ncaab"}
DOME_TEAMS = {
    "New Orleans Saints", "Atlanta Falcons", "Detroit Lions", "Minnesota Vikings",
    "Indianapolis Colts", "Las Vegas Raiders", "Los Angeles Rams", "Arizona Cardinals",
    "Dallas Cowboys", "Houston Texans"
}

# Fetch once per run for performance
ODDS_CACHE = get_all_current_odds()

def find_line_for_game(home, away, sport):
    for game in ODDS_CACHE:
        teams = game.get("teams", [])
        if home in teams and away in teams:
            for book in game.get("bookmakers", []):
                for market in book.get("markets", []):
                    if market.get("key") == "spreads":
                        for outcome in market.get("outcomes", []):
                            if outcome.get("name") == home:
                                return outcome.get("point")
    return None

def get_all_composite_signals(games):
    signals = []
    for game in games:
        home = game.get("home_team")
        away = game.get("away_team")
        sport = game.get("sport")

        home_coords = get_team_coordinates(home)
        away_coords = get_team_coordinates(away)

        if not home_coords or not away_coords:
            continue

        if sport.lower() in INDOOR_SPORTS or home in DOME_TEAMS or away in DOME_TEAMS:
            weather_home = {"score": 5.0, "summary": "Indoor game – weather not applicable."}
            weather_away = {"score": 5.0, "summary": "Indoor game – weather not applicable."}
        else:
            weather_home = get_weather_score(*home_coords, sport)
            weather_away = get_weather_score(*away_coords, sport)

        sentiment_home = get_sentiment_score(home)
        if not isinstance(sentiment_home, (int, float)):
            sentiment_home = 0.0

        sentiment_away = get_sentiment_score(away)
        if not isinstance(sentiment_away, (int, float)):
            sentiment_away = 0.0

        matchup_score = get_matchup_score(home, away, sport)

        pace_score = get_pace_score(home, away, sport)
        pace_penalty = 0.0 if pace_score == 0.0 else 0.0

        ref_score = get_ref_score(home, away, sport)
        ref_penalty = 0.0 if ref_score == 0.0 else 0.0

        promo_score = get_promo_score(home, away, sport)
        promo_penalty = 0.0 if promo_score == 0.0 else 0.0

        composite_score = (
            matchup_score * 0.30 +
            sentiment_home * 0.15 +
            sentiment_away * 0.15 +
            weather_home["score"] * 0.10 +
            weather_away["score"] * 0.10 +
            pace_score * 0.05 +
            ref_score * 0.05 +
            promo_score * 0.10
        )

        composite_score -= (pace_penalty + ref_penalty + promo_penalty)

        signals.append({
            "matchup": f"{away} at {home}",
            "composite_score": round(composite_score, 2),
            "line": find_line_for_game(home, away, sport) or "N/A",
            "handle": "N/A",  # placeholder
            "sentiment": f"H: {sentiment_home}, A: {sentiment_away}",
            "injuries": "TBD",  # integrate if needed
            "weather": weather_home["summary"],
            "score": round(composite_score, 2),
            "components": {
                "matchup": matchup_score,
                "sentiment_home": sentiment_home,
                "sentiment_away": sentiment_away,
                "weather_home": weather_home,
                "weather_away": weather_away,
                "pace": pace_score,
                "ref": ref_score,
                "promo": promo_score
            }
        })
    return signals

# Note: Once pace.py, ref_trends.py, and promo_scraper.py are fully implemented,
# remove suppression logic for zero-value scores.


