import os
from odds_API import get_all_us_odds
from weather import get_weather_score
from injuries import get_injury_report
from sentiment import get_sentiment_for_team

# Optional: Future imports (pace, fatigue, refs, promos) for enrichment scaffolding

def get_all_composite_signals():
    games = get_all_us_odds()
    signals = []

    for game in games:
        try:
            home = game.get("home_team", "")
            away = game.get("away_team", "")
            kickoff = game.get("commence_time", "")
            line_data = game.get("bookmakers", [{}])[0].get("markets", [{}])[0].get("outcomes", [{}])

            sentiment_home = get_sentiment_for_team(home)
            sentiment_away = get_sentiment_for_team(away)

            injuries_home = get_injury_report(home)
            injuries_away = get_injury_report(away)

            weather_context = get_weather_score(kickoff, home)

            signal = {
                "game": f"{home} vs {away}",
                "line": line_data.get("point", "N/A"),
                "handle": line_data.get("price", "N/A"),
                "sentiment": f"{home}: {sentiment_home} / {away}: {sentiment_away}",
                "injuries": f"{home}: {injuries_home} / {away}: {injuries_away}",
                "weather": weather_context,
                "matchup": "Pending DVOA model deployment",
                "composite_score": 0  # Will be replaced by GPT evaluation
            }

            signals.append(signal)

        except Exception as e:
            print(f"[ERROR] Problem processing game: {e}")

    return signals


    return signal_data

