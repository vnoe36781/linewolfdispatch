import requests
import json
from weather import get_weather_data
from injuries import get_injury_data
from sentiment import get_combined_sentiment
from matchup_model import get_matchup_score
from utils import get_sport_type

# CONFIG
SPORT_WEIGHTS = {
    'NFL': {'weather': 0.25, 'injuries': 0.25, 'sentiment': 0.15, 'matchup': 0.35},
    'NCAAF': {'weather': 0.2, 'injuries': 0.25, 'sentiment': 0.15, 'matchup': 0.4},
    'NBA': {'weather': 0.05, 'injuries': 0.2, 'sentiment': 0.2, 'matchup': 0.55},
    'NCAAM': {'weather': 0.05, 'injuries': 0.2, 'sentiment': 0.15, 'matchup': 0.6},
    'MLB': {'weather': 0.15, 'injuries': 0.15, 'sentiment': 0.2, 'matchup': 0.5},
}

def get_all_composite_signals():
    response = requests.get("https://api.the-odds-api.com/v4/sports/?apiKey=your-key")
    games = response.json()

    signal_data = []
    for game in games:
        sport = get_sport_type(game)
        teams = game.get('teams', [])
        team1, team2 = teams if len(teams) == 2 else ("Unknown", "Unknown")

        weather = get_weather_data(game)
        injuries = get_injury_data(game)
        sentiment = get_combined_sentiment(team1, team2)
        matchup = get_matchup_score(game)

        weights = SPORT_WEIGHTS.get(sport, SPORT_WEIGHTS['NFL'])
        composite = (
            weights['weather'] * weather.get('score', 0) +
            weights['injuries'] * injuries.get('score', 0) +
            weights['sentiment'] * sentiment.get('score', 0) +
            weights['matchup'] * matchup.get('score', 0)
        )

        signal_data.append({
            'game': f"{team1} vs {team2}",
            'line': game.get('bookmakers', [{}])[0].get('markets', [{}])[0].get('outcomes', [{}])[0].get('point', 'N/A'),
            'handle': game.get('handle', 'N/A'),
            'sentiment': sentiment.get('summary', 'N/A'),
            'injuries': injuries.get('summary', 'N/A'),
            'weather': weather.get('summary', 'N/A'),
            'matchup': matchup.get('summary', 'N/A'),
            'composite_score': round(composite, 2)
        })

    return signal_data

