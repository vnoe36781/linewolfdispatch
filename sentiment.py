import requests
import json
import time

# CONFIGURATION
TWITTER_HANDLES = [
    "RightAngleSports", "Hitman428", "JoeyKnish22", "Clevta", "TheSharpPlays",
    "whale_capper", "SportsCheetah", "BetsStats", "VSiNLive", "Covers"
]
REDDIT_SENTIMENT_API = "https://your-reddit-sentiment-endpoint.com"
TWITTER_SCRAPE_ENDPOINT = "https://your-twitter-scrape-endpoint.com"

def fetch_reddit_sentiment(team):
    try:
        response = requests.get(REDDIT_SENTIMENT_API, params={"team": team})
        data = response.json()
        return data.get("score", 0), data.get("summary", "No Reddit sentiment found.")
    except:
        return 0, "Reddit data unavailable"

def fetch_twitter_sentiment(team):
    try:
        response = requests.post(TWITTER_SCRAPE_ENDPOINT, json={
            "team": team,
            "handles": TWITTER_HANDLES
        }, timeout=10)
        data = response.json()
        return data.get("score", 0), data.get("summary", "No Twitter sentiment found.")
    except:
        return 0, "Twitter data unavailable"

def get_combined_sentiment(team1, team2):
    t1_reddit_score, t1_reddit_text = fetch_reddit_sentiment(team1)
    t2_reddit_score, t2_reddit_text = fetch_reddit_sentiment(team2)

    t1_twitter_score, t1_twitter_text = fetch_twitter_sentiment(team1)
    t2_twitter_score, t2_twitter_text = fetch_twitter_sentiment(team2)

    avg_score = round((t1_reddit_score + t2_reddit_score + t1_twitter_score + t2_twitter_score) / 4, 2)
    combined_summary = f"""
**{team1}**:
- Reddit: {t1_reddit_text}
- Twitter: {t1_twitter_text}

**{team2}**:
- Reddit: {t2_reddit_text}
- Twitter: {t2_twitter_text}
    """.strip()

    return {
        "score": avg_score,
        "summary": combined_summary
    }

