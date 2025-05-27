
import requests
import re
import random

# Reddit config
REDDIT_SUBS = [
    "sportsbook", "gambling",
    "nfl", "nba", "cfb", "ncaab",
    "bills", "chiefs", "cowboys", "49ers", "lakers"
]
REDDIT_ENDPOINT = "https://www.reddit.com/r/{sub}/top/.json?limit=10&t=day"
USER_AGENT = {"User-Agent": "LineWolfSentimentBot"}

# Twitter config (structure only — credentials injected securely)
TWITTER_SHARP_USERS = [
    "Covers", "TheSharpPlays", "RightAngleSports", "WagerTalk", "BettingPros"
]

SHARP_KEYWORDS = ["lock", "value", "trap", "steam", "tail", "fade", "sharp", "max bet", "free play"]

def score_sentiment(text_block):
    hits = [kw for kw in SHARP_KEYWORDS if kw in text_block.lower()]
    return len(hits)

def pull_reddit_sentiment():
    all_comments = []
    for sub in REDDIT_SUBS:
        try:
            url = REDDIT_ENDPOINT.format(sub=sub)
            r = requests.get(url, headers=USER_AGENT)
            if r.status_code != 200:
                continue
            posts = r.json().get("data", {}).get("children", [])
            for post in posts:
                title = post["data"].get("title", "")
                comments = post["data"].get("selftext", "")
                combined = title + " " + comments
                if any(kw in combined.lower() for kw in SHARP_KEYWORDS):
                    all_comments.append(combined)
        except:
            continue
    return all_comments

def summarize_sentiment(text_list, team_keywords):
    team_scores = {}
    for team in team_keywords:
        score = 0
        for comment in text_list:
            if team.lower() in comment.lower():
                score += score_sentiment(comment)
        if score > 0:
            team_scores[team] = score
    return team_scores

def get_sentiment_for_game(game_name):
    teams = [t.strip() for t in re.split("vs|VS|Vs", game_name)]
    if len(teams) != 2:
        return "Unknown teams, skipping sentiment"

    reddit_comments = pull_reddit_sentiment()
    team_scores = summarize_sentiment(reddit_comments, teams)

    if not team_scores:
        return "No clear sentiment trend"

    best = sorted(team_scores.items(), key=lambda x: x[1], reverse=True)
    desc = []
    for team, score in best:
        label = "steam" if score >= 3 else "light steam"
        desc.append(f"{team}: {label} (score {score})")

    return " | ".join(desc)

def get_sentiment_batch(game_list):
    sentiment_dict = {}
    for game in game_list:
        sentiment_dict[game] = get_sentiment_for_game(game)
    return sentiment_dict
