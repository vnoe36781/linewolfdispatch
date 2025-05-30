import os
from weather import get_weather_score
from team_locations import get_team_coordinates
from matchup_model import get_matchup_score
from sentiment import get_sentiment_score
from pace import get_pace_score
from ref_trends import get_ref_score
from promo_scraper import get_promo_score
from odds_API import get_all_current_odds
from datetime import datetime

INDOOR_SPORTS = {"nba", "ncaab"}
DOME_TEAMS = {
    "New Orleans Saints", "Atlanta Falcons", "Detroit Lions", "Minnesota Vikings",
    "Indianapolis Colts", "Las Vegas Raiders", "Los Angeles Rams", "Arizona Cardinals",
    "Dallas Cowboys", "Houston Texans"
}

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

def safe_component(value, weight):
    return value * weight if isinstance(value, (int, float)) and value > 0 else 0, weight if isinstance(value, (int, float)) and value > 0 else 0

def infer_sport_from_teams(home, away):
    nfl_teams = {
        "Arizona Cardinals", "Atlanta Falcons", "Baltimore Ravens", "Buffalo Bills",
        "Carolina Panthers", "Chicago Bears", "Cincinnati Bengals", "Cleveland Browns",
        "Dallas Cowboys", "Denver Broncos", "Detroit Lions", "Green Bay Packers",
        "Houston Texans", "Indianapolis Colts", "Jacksonville Jaguars", "Kansas City Chiefs",
        "Las Vegas Raiders", "Los Angeles Chargers", "Los Angeles Rams", "Miami Dolphins",
        "Minnesota Vikings", "New England Patriots", "New Orleans Saints", "New York Giants",
        "New York Jets", "Philadelphia Eagles", "Pittsburgh Steelers", "San Francisco 49ers",
        "Seattle Seahawks", "Tampa Bay Buccaneers", "Tennessee Titans", "Washington Commanders"
    }
    if home in nfl_teams and away in nfl_teams:
        return "nfl"
    return None

def get_all_composite_signals(games):
    signals = []
    nfl_earliest_game = None
    nfl_earliest_time = None

    for game in games:
        home = game.get("home_team")
        away = game.get("away_team")
        sport = game.get("sport")
        commence_time = game.get("commence_time")

        if not sport:
            sport = infer_sport_from_teams(home, away)
            if sport:
                print(f"[INFO] Inferred sport for {away} at {home} → {sport}")
            else:
                print(f"[WARN] Missing sport value for matchup: {home} vs {away}")

        if sport == "nfl":
            game_time = datetime.fromisoformat(commence_time.replace("Z", "+00:00"))
            if not nfl_earliest_time or game_time < nfl_earliest_time:
                nfl_earliest_time = game_time
                nfl_earliest_game = game

    for game in games:
        home = game.get("home_team")
        away = game.get("away_team")
        sport = game.get("sport")

        if not sport:
            sport = infer_sport_from_teams(home, away)

        if sport == "nfl" and game != nfl_earliest_game:
            continue

        print(f"[START] Processing: {away} at {home} ({sport})")

        home_coords = get_team_coordinates(home)
        away_coords = get_team_coordinates(away)
        if not home_coords or not away_coords:
            print(f"[SKIP] Coordinates missing: {home} → {home_coords}, {away} → {away_coords}")
            continue

        if (sport or "").lower() in INDOOR_SPORTS or home in DOME_TEAMS or away in DOME_TEAMS:
            weather_home = {"score": 5.0, "summary": "Indoor game – weather not applicable."}
            weather_away = {"score": 5.0, "summary": "Indoor game – weather not applicable."}
        else:
            weather_home = get_weather_score(*home_coords, sport)
            weather_away = get_weather_score(*away_coords, sport)

        # Pull scores
        matchup_score = get_matchup_score(home, away, sport)
        sentiment_home = get_sentiment_score(home)
        sentiment_away = get_sentiment_score(away)
        pace_score = get_pace_score(home, away, sport)
        ref_score = get_ref_score(home, away, sport)
        promo_score = get_promo_score(home, away, sport)

        # Weighted scoring w/ null suppression
        score_total = 0
        weight_total = 0

        for val, weight in [
            safe_component(matchup_score, 0.30),
            safe_component(sentiment_home, 0.15),
            safe_component(sentiment_away, 0.15),
            safe_component(weather_home["score"], 0.10),
            safe_component(weather_away["score"], 0.10),
            safe_component(pace_score, 0.05),
            safe_component(ref_score, 0.05),
            safe_component(promo_score, 0.10)
        ]:
            score_total += val
            weight_total += weight

        composite_score = round(score_total / weight_total, 2) if weight_total > 0 else 0.0

        signal = {
            "matchup": f"{away} at {home}",
            "composite_score": composite_score,
            "line": find_line_for_game(home, away, sport) or "N/A",
            "handle": "N/A",
            "sentiment": f"H: {sentiment_home}, A: {sentiment_away}",
            "injuries": "TBD",
            "weather": weather_home["summary"],
            "score": composite_score,
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
        }

        print(f"[DONE] Created signal for {away} at {home} → Score: {composite_score}")
        signals.append(signal)

    return signals



# Note: Once pace.py, ref_trends.py, and promo_scraper.py are fully implemented,
# remove suppression logic for zero-value scores.


