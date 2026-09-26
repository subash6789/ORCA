from datetime import datetime

from ocean_agent import ocean_agent
from weather_agent import weather_agent


def safety_agent(state="Tamil Nadu"):

    # Get region-specific ocean and weather data
    ocean = ocean_agent(state)
    weather = weather_agent(state)

    alerts = []

    # Read available values
    wind = weather.get("wind_speed_kmh")
    rain = weather.get("precipitation_mm")
    current = ocean.get("current_speed_ms")

    region_map = {
        "Tamil Nadu": "Tamil Nadu / Bay of Bengal",
        "Kerala": "Kerala / Arabian Sea",
        "Karnataka": "Karnataka / Arabian Sea",
        "Gujarat": "Gujarat / Arabian Sea"
    }

    if state not in region_map:
        return {
            "agent": "Safety Agent",
            "status": "UNAVAILABLE",
            "data_status": "UNAVAILABLE",
            "state": state,
            "message": "Unsupported region"
        }

    region = region_map[state]

    # -------------------------------------------------
    # ORCA DEMO SAFETY RULES
    # -------------------------------------------------

    if wind is not None and wind >= 40:
        alerts.append(
            f"High wind speed detected: {wind} km/h."
        )

    if rain is not None and rain >= 10:
        alerts.append(
            f"Heavy precipitation detected: {rain} mm."
        )

    if current is not None and current >= 2:
        alerts.append(
            f"Strong ocean current detected: {current} m/s."
        )

    # -------------------------------------------------
    # SAFETY STATUS
    # -------------------------------------------------

    if alerts:
        safety_status = "WARNING"
    else:
        safety_status = "NO_RULE_TRIGGERED"

    return {
        "agent": "Safety Agent",
        "status": "SUCCESS",
        "data_status": "DEMO_RULE",

        "state": state,
        "region": region,
        "location": region,

        "safety_status": safety_status,
        "alerts": alerts,

        "rules": {
            "high_wind_kmh": 40,
            "heavy_precipitation_mm": 10,
            "strong_current_ms": 2
        },

        "source": [
            "ORCA Ocean Agent",
            "ORCA Weather Agent"
        ],

        "message": (
            "Safety status is generated from the current ORCA "
            "demo safety rules using available ocean and weather data. "
            "It is not an official marine warning or government alert."
        ),

        "evaluated_at": datetime.now().isoformat()
    }


if __name__ == "__main__":

    result = safety_agent("Tamil Nadu")

    print("===== ORCA SAFETY AGENT =====")

    for key, value in result.items():
        print(f"{key}: {value}")