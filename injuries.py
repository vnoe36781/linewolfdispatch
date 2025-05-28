import requests

# CONFIG
SLEEPER_INJURY_URL = "https://api.sleeper.app/v1/players/injuries"

# Sample positional weights (can be adjusted per sport)
POSITION_WEIGHTS = {
    "QB": 2.0,
    "RB": 1.5,
    "WR": 1.4,
    "TE": 1.2,
    "OL": 1.0,
    "DL": 0.9,
    "LB": 1.1,
    "CB": 1.3,
    "S": 1.2,
    "K": 0.5
}

def get_injury_score(team):
    try:
        resp = requests.get(SLEEPER_INJURY_URL, timeout=10)
        all_data = resp.json()

        team_injuries = [player for player in all_data if player.get("team") == team]
        score = 5.0
        context = []

        for player in team_injuries:
            status = player.get("status", "").lower()
            pos = player.get("position", "UNK").upper()
            name = player.get("last_name", "Unknown")
            pos_weight = POSITION_WEIGHTS.get(pos, 1.0)

            if status in ["out", "doubtful"]:
                score += 1.5 * pos_weight
                context.append(f"{name} ({pos}) is {status.upper()}")

            elif status in ["questionable", "limited"]:
                score += 0.7 * pos_weight
                context.append(f"{name} ({pos}) is {status}")

        if not context:
            context.append("No key injuries detected.")

        return {
            "score": round(min(max(score, 1.0), 10.0), 2),
            "summary": "; ".join(context)
        }

    except Exception as e:
        return {"score": 5.0, "summary": f"Injury fetch error: {str(e)}"}
