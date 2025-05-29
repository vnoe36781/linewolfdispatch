import os
from weather import get_weather_score
from team_locations import get_team_coordinates
from matchup_model import get_matchup_score
from sentiment import get_sentiment_home
from pace import get_pace_score
from ref_trends import get_ref_score
from promo_scraper import get_promo_score

# Indoor game exclusions
INDOOR_SPORTS = {"nba", "ncaab"}
DOME_TEAMS = {
    "New Orleans Saints",
    "Atlanta Falcons",
    "Detroit Lions",
    "Minnesota Vikings",
    "Indianapolis Colts",
    "Las Vegas Raiders",
    "Los Angeles Rams",
    "Arizona Cardinals",
    "Dallas Cowboys",
    "Houston Texans"
}

# Main Composite Signal Function
def get_all_composite_signals(games):
    signals = []
    for game in games:
        home = game.get("home_team")
        away = game.get("away_team")
        sport = game.get("sport")

        home_coords = get_team_coordinates(home)
        away_coords = get_team_coordinates(away)

        # Skip games with missing coordinates
        if not home_coords or not away_coords:
            continue

        # Weather Scores (suppressed for indoor games)
        if sport.lower() in INDOOR_SPORTS or home in DOME_TEAMS or away in DOME_TEAMS:
            weather_home = {"score": 5.0, "summary": "Indoor game – weather not applicable."}
            weather_away = {"score": 5.0, "summary": "Indoor game – weather not applicable."}
        else:
            weather_home = get_weather_score(*home_coords, sport)
            weather_away = get_weather_score(*away_coords, sport)

        # Sentiment
        sentiment_home = sentiment_home(home)
        if not isinstance(sentiment_home, (int, float)):
            sentiment_home = 0.0

        sentiment_away = sentiment_home(away)
        if not isinstance(sentiment_away, (int, float)):
            sentiment_away = 0.0

        # Matchup
        matchup_score = get_matchup_score(home, away, sport)

        # Pace (placeholder penalty suppression)
        pace_score = get_pace_score(home, away, sport)
        pace_penalty = 0.0
        if pace_score == 0.0:
            pace_penalty = 0.0  # suppress until implemented

        # Ref Trends (placeholder penalty suppression)
        ref_score = get_ref_score(home, away, sport)
        ref_penalty = 0.0
        if ref_score == 0.0:
            ref_penalty = 0.0  # suppress until implemented

        # Promos (placeholder penalty suppression)
        promo_score = get_promo_score(home, away, sport)
        promo_penalty = 0.0
        if promo_score == 0.0:
            promo_penalty = 0.0  # suppress until implemented

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

        # Apply temporary suppression penalties (currently zero)
        composite_score -= pace_penalty
        composite_score -= ref_penalty
        composite_score -= promo_penalty

        signals.append({
            "matchup": f"{away} at {home}",
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


