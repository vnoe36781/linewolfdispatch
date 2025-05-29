import os
import requests
from team_locations import get_team_coordinates

# CONFIG
OWM_API_KEY = os.getenv("WEATHER_API_KEY")
WEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5/forecast"

def get_weather_score(team_name: str, sport_type: str):
    coords = get_team_coordinates(team_name)
    
    if not coords:
        return {"score": 5.0, "summary": f"No coordinates found for {team_name}."}

    lat, lon = coords

    try:
        params = {
            "lat": lat,
            "lon": lon,
            "appid": OWM_API_KEY,
            "units": "imperial"
        }
        response = requests.get(WEATHER_BASE_URL, params=params, timeout=10)
        data = response.json()

        if "list" not in data:
            return {"score": 5.0, "summary": "Weather data unavailable."}

        forecast = data["list"][0]
        wind = forecast["wind"]["speed"]
        rain = forecast.get("rain", {}).get("3h", 0)
        snow = forecast.get("snow", {}).get("3h", 0)
        conditions = forecast["weather"][0]["main"]

        impact_score = 5.0
        context = []

        # WIND FACTOR
        if wind >= 15:
            impact_score += 1.5
            context.append(f"High wind: {wind} mph")
        elif wind >= 10:
            impact_score += 0.5
            context.append(f"Moderate wind: {wind} mph")

        # RAIN/SNOW
        if rain > 0:
            impact_score += 1.0
            context.append(f"Rain: {rain:.2f} in")
        if snow > 0:
            impact_score += 1.5
            context.append(f"Snow: {snow:.2f} in")

        # SPORT-SPECIFIC ADJUSTMENTS
        if sport_type.lower() == "nfl" and wind >= 15:
            impact_score += 1.0
            context.append("⚠️ Wind is especially impactful for passing in football.")

        if sport_type.lower() == "mlb" and wind >= 10:
            impact_score += 0.7
            context.append("⚠️ Wind may affect fly balls in baseball.")

        if not context:
            context.append("No significant weather impact.")

        return {
            "score": round(min(max(impact_score, 1.0), 10.0), 2),
            "summary": "; ".join(context)
        }

    except Exception as e:
        return {"score": 5.0, "summary": f"Weather error: {str(e)}"}

if __name__ == "__main__":
    test = get_weather_score("Florida State", "nfl")
    print(test)
