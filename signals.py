import os
from datetime import datetime
from team_locations import get_team_coordinates
from weather import get_weather_score
from pace import get_pace_score
from sentiment import get_sentiment_score
from fatigue import get_fatigue_score
from ref_trends import get_ref_score
from promo_scraper import get_promo_score

# Enable/disable modules with environment flags
ENABLE_WEATHER = os.getenv("ENABLE_WEATHER", "true").lower() == "true"
ENABLE_PACE = os.getenv("ENABLE_PACE", "true").lower() == "true"
ENABLE_SENTIMENT = os.getenv("ENABLE_SENTIMENT", "true").lower() == "true"
ENABLE_FATIGUE = os.getenv("ENABLE_FATIGUE", "true").lower() == "true"
ENABLE_REFS = os.getenv("ENABLE_REFS", "true").lower() == "true"
ENABLE_PROMOS = os.getenv("ENABLE_PROMOS", "true").lower() == "true"

def get_composite_score(game: dict) -> dict:
    home = game["home_team"]
    away = game["away_team"]
    sport = game.get("sport", "nfl")

    signals = []
    summary = []

    # WEATHER
    if ENABLE_WEATHER:
        weather_result = get_weather_score(home, sport)
        signals.append(weather_result["score"])
        summary.append(f"🌤️ {weather_result['summary']}")

    # PACE
    if ENABLE_PACE:
        pace_score = get_pace_score(home, away, sport)
        signals.append(pace_score)
        summary.append(f"⏱️ Pace Score: {pace_score:.2f}")

    # SENTIMENT
    if ENABLE_SENTIMENT:
        sentiment_score = get_sentiment_score(home, away)
        signals.append(sentiment_score)
        summary.append(f"📈 Sentiment Score: {sentiment_score:.2f}")

    # FATIGUE
    if ENABLE_FATIGUE:
        fatigue_score = get_fatigue_score(home, away)
        signals.append(fatigue_score)
        summary.append(f"😴 Fatigue Score: {fatigue_score:.2f}")

    # REFEREE TRENDS
    if ENABLE_REFS:
        ref_score = get_ref_score(game)
        signals.append(ref_score)
        summary.append(f"🧑‍⚖️ Ref Score: {ref_score:.2f}")

    # PROMOTIONS / PUBLIC INCENTIVES
    if ENABLE_PROMOS:
        promo_score = get_promo_score(game)
        signals.append(promo_score)
        summary.append(f"💰 Promo Influence: {promo_score:.2f}")

    # FALLBACK if no signals loaded
    if not signals:
        signals = [5.0]
        summary.append("⚠️ No signal modules enabled.")

    avg_score = round(sum(signals) / len(signals), 2)
    return {
        "home_team": home,
        "away_team": away,
        "avg_score": avg_score,
        "signal_breakdown": "; ".join(summary),
        "timestamp": datetime.utcnow().isoformat()
    }

def get_all_composite_signals(games: list[dict]) -> list[dict]:
    return [get_composite_score(game) for game in games]

