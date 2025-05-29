import os
import requests
import re
import time
from datetime import datetime
from collections import defaultdict

# Reddit credentials (for Pushshift)
REDDIT_BASE_URL = "https://api.pushshift.io/reddit/search/comment"
REDDIT_QUERY = "game thread|odds|spread|moneyline|total|underdog|favorite|bet"
REDDIT_LOOKBACK_HOURS = 6

# Twitter credentials
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
TWITTER_SEARCH_URL = "https://api.twitter.com/2/tweets/search/recent"
TWITTER_ACCOUNTS = [
    "TheSharpPlays", "Covers", "ActionNetworkHQ", "BettingProsNFL",
    "VSiNLive", "SportsInsights", "Pregame", "RJinVegas", "CapperTek", "WagerTalk"
]

HEADERS_TWITTER = {"Authorization": f"Bearer {TWITTER_BEARER_TOKEN}"}

def fetch_reddit_sentiment(team_name: str) -> float:
    try:
        response = requests.get(f"https://api.pushshift.io/reddit/search/comment/?q={team_name}&size=100", timeout=10)
        try:
            data = response.json()
        except Exception:
            return 0.0  # Gracefully handle invalid JSON

        comments = data.get("data", [])
        if not comments:
            return 0.0

        # Placeholder for sentiment logic
        return 0.5  # Neutral default until implemented

    except requests.exceptions.RequestException:
        return 0.0


def fetch_twitter_sentiment(team_name):
    combined_score = 0
    for account in TWITTER_ACCOUNTS:
        params = {
            "query": f"from:{account} {team_name} (bet OR line OR spread OR total OR underdog OR moneyline)",
            "tweet.fields": "created_at",
            "max_results": 10
        }
        try:
            resp = requests.get(TWITTER_SEARCH_URL, headers=HEADERS_TWITTER, params=params)
            tweets = resp.json().get("data", [])
            tweet_texts = [t["text"] for t in tweets if "text" in t]
            combined_score += analyze_sentiment_from_texts(tweet_texts)
        except:
            continue
    return combined_score / len(TWITTER_ACCOUNTS) if TWITTER_ACCOUNTS else 0

def analyze_sentiment_from_texts(texts):
    score = 0
    for text in texts:
        lower = text.lower()
        if any(word in lower for word in ["lock", "hammer", "sharp", "guarantee", "love this pick"]):
            score += 1
        elif any(word in lower for word in ["fade", "trap", "square", "public", "no value"]):
            score -= 1
    return score

def get_sentiment_score(team_name):
    reddit_score = fetch_reddit_sentiment(team_name)
    twitter_score = fetch_twitter_sentiment(team_name)
    combined = reddit_score + twitter_score
    if combined > 3:
        return "Strong Support"
    elif combined > 1:
        return "Lean Support"
    elif combined < -3:
        return "Sharp Fade"
    elif combined < -1:
        return "Lean Fade"
    return "Neutral"

