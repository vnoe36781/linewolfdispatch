
import requests
import openai
import json
import time
import csv
from datetime import datetime
from signals import get_all_composite_signals
test_games = [
    {
        "home_team": "Florida State",
        "away_team": "Miami FL",
        "sport": "ncaaf"
    },
    {
        "home_team": "Detroit Tigers",
        "away_team": "Kansas City Royals",
        "sport": "mlb"
    }
]

signals = get_all_composite_signals(test_games)
from team_locations import get_team_coordinates

# CONFIG
OPENAI_API_KEY = "your-openai-api-key"
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1375652751324876800/LDKEh-tCIcPvQKsbnBEi-4pfK5SllCiCjqk54IvyfwULlNdeFG73d_5iwiDfuUfb7Ti3"
BANKROLL = 20000
FEEDBACK_FILE = "feedback_tracker.csv"
CONFIDENCE_THRESHOLD = 7.0

openai.api_key = OPENAI_API_KEY

def build_gpt_prompt(signal):
    return f"""Game: {signal['matchup']}
Line Move: {signal['line']}
Public Handle: {signal['handle']}
Sharp Sentiment: {signal['sentiment']}
Injuries: {signal['injuries']}
Weather: {signal['weather']}
Matchup Mismatch: {signal['matchup']}
Composite Score: {signal['composite_score']}
[bankroll=${BANKROLL}]
"""

def get_openai_recommendation(context):
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "You are a tactical sports betting analyst. Use market signals, sentiment overlays, and environmental context to identify high-confidence plays. Avoid public traps. Prioritize sharp alignment, matchup mismatch, and actionable line opportunities. Output: bet recommendation, confidence score (1–10), % of bankroll to risk, and explanation."},
            {"role": "user", "content": context}
        ],
        temperature=0.3
    )
    return response['choices'][0]['message']['content']

def send_to_discord(message):
    payload = {
        "content": f"**LineWolf AI Recommendation**\n{message}"
    }
    headers = {"Content-Type": "application/json"}
    requests.post(DISCORD_WEBHOOK_URL, data=json.dumps(payload), headers=headers)

def log_feedback(date, game, recommendation, confidence, action_taken="pending", outcome="pending"):
    with open(FEEDBACK_FILE, mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([date, game, recommendation, confidence, action_taken, outcome])

def extract_confidence_score(text):
    try:
        for line in text.splitlines():
            if "confidence" in line.lower():
                return float([word for word in line.split() if word.replace('.', '', 1).isdigit()][0])
    except:
        return None

def main():
    signals = get_all_composite_signals(test_games)
    for signal in signals:
        prompt = build_gpt_prompt(signal)
        recommendation = get_openai_recommendation(prompt)
        confidence = extract_confidence_score(recommendation)

        if confidence is None or confidence < CONFIDENCE_THRESHOLD:
            continue

        send_to_discord(recommendation)
        log_feedback(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), signal['game'], recommendation, confidence)

if __name__ == "__main__":
    main()
if __name__ == "__main__":
    test_games = [
        {"home_team": "Florida State", "away_team": "Miami FL", "sport": "ncaaf"},
        {"home_team": "Georgia", "away_team": "Tennessee", "sport": "ncaaf"},
        {"home_team": "Alabama", "away_team": "Auburn", "sport": "ncaaf"}
    ]

    results = get_all_composite_signals(test_games)
    for r in results:
        print(r)
