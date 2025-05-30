import os
import requests
import openai
import json
import time
import csv
from datetime import datetime
from signals import get_all_composite_signals
from team_locations import get_team_coordinates

# CONFIG (now fully environment-driven)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "").strip()
BANKROLL = 20000
FEEDBACK_FILE = "feedback_tracker.csv"
CONFIDENCE_THRESHOLD = 0.0

# Fail fast if missing env vars
assert OPENAI_API_KEY, "❌ Missing or invalid OPENAI_API_KEY environment variable."
assert DISCORD_WEBHOOK_URL, "❌ Missing or invalid DISCORD_WEBHOOK_URL environment variable."

openai.api_key = OPENAI_API_KEY

def build_gpt_prompt(signal):
    expected_keys = ['line', 'handle', 'sentiment', 'injuries', 'weather', 'matchup', 'composite_score']
    missing = [k for k in expected_keys if k not in signal]
    if missing:
        print(f"[WARN] Missing keys in signal: {missing}")

    return f"""Game: {signal.get('matchup', 'N/A')}
Line Move: {signal.get('line', 'N/A')}
Public Handle: {signal.get('handle', 'N/A')}
Sharp Sentiment: {signal.get('sentiment', 'N/A')}
Injuries: {signal.get('injuries', 'N/A')}
Weather: {signal.get('weather', 'N/A')}
Matchup Mismatch: {signal.get('matchup', 'N/A')}
Composite Score: {signal.get('composite_score', 'N/A')}
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
    test_games = [
        {"home_team": "Florida State", "away_team": "Miami FL", "sport": "ncaaf"},
        {"home_team": "Detroit Tigers", "away_team": "Kansas City Royals", "sport": "mlb"}
    ]
    signals = get_all_composite_signals(test_games)
    for signal in signals:
        prompt = build_gpt_prompt(signal)
        recommendation = get_openai_recommendation(prompt)
        confidence = extract_confidence_score(recommendation)

        if confidence is None or confidence < CONFIDENCE_THRESHOLD:
            continue

        send_to_discord(recommendation)
        log_feedback(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), signal.get('matchup', 'Unknown'), recommendation, confidence)

if __name__ == "__main__":
    main()

    main()

