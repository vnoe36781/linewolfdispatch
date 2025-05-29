import requests

# CONFIG
MATCHUP_DATA_URL = "https://your-matchup-dvoa-api.com/team_rankings"

def fetch_team_metrics():
    try:
        response = requests.get(MATCHUP_DATA_URL, timeout=10)
        response.raise_for_status()
        return response.json()
    except:
        return {}

def evaluate_mismatch(team1, team2, injury_context=None):
    data = fetch_team_metrics()

    if not data or team1 not in data or team2 not in data:
        return {
            "score": 5.0,
            "summary": "Matchup data unavailable — default score applied."
        }

    t1_off = data[team1].get("offense_rank", 15)
    t1_def = data[team1].get("defense_rank", 15)
    t2_off = data[team2].get("offense_rank", 15)
    t2_def = data[team2].get("defense_rank", 15)

    delta_offense = t1_off - t2_def
    delta_defense = t2_off - t1_def
    abs_gap = abs(delta_offense - delta_defense)

    score = 7.0 + (abs_gap / 10.0)
    summary = f"{team1} Off vs {team2} Def: Δ={delta_offense} | {team2} Off vs {team1} Def: Δ={delta_defense}"

    if injury_context:
        summary += f"\n⚠️ Injury Context: {injury_context}"

    return {
        "score": round(min(max(score, 1), 10), 2),
        "summary": summary
    }
def get_matchup_score(home_team: str, away_team: str, sport: str) -> float:
    # Placeholder logic until implemented
    return 0.0
    team1 = game.get("home_team")
    team2 = game.get("away_team")

    result = evaluate_mismatch(team1, team2)
    return result["score"]
