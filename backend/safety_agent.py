from ocean_agent import ocean_agent
from weather_agent import weather_agent


def safety_agent():

    ocean = ocean_agent()
    weather = weather_agent()

    alerts = []

    wind = weather.get("wind_speed_kmh")
    rain = weather.get("precipitation_mm")
    current = ocean.get("current_speed_ms")

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

    return {
        "agent": "Safety Agent",
        "status": "SUCCESS",
        "location": "Chennai / Bay of Bengal",
        "alerts": alerts
    }