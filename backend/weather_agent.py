import json
from urllib.request import urlopen


def weather_agent():
    # Chennai coordinates
    latitude = 13.0827
    longitude = 80.2707

    url = (
        "https://api.open-meteo.com/v1/forecast"
        "?latitude=13.0827"
        "&longitude=80.2707"
        "&current=temperature_2m,relative_humidity_2m,"
        "wind_speed_10m,wind_direction_10m,precipitation"
    )

    try:
        with urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())

        current = data["current"]

        return {
            "agent": "Weather Agent",
            "status": "SUCCESS",
            "location": "Chennai",
            "temperature_c": current["temperature_2m"],
            "humidity_percent": current["relative_humidity_2m"],
            "wind_speed_kmh": current["wind_speed_10m"],
            "wind_direction_degrees": current["wind_direction_10m"],
            "precipitation_mm": current["precipitation"],
            "source": "Open-Meteo"
        }

    except Exception as e:
        return {
            "agent": "Weather Agent",
            "status": "ERROR",
            "message": str(e)
        }


if __name__ == "__main__":
    result = weather_agent()

    print("===== ORCA WEATHER AGENT =====")

    for key, value in result.items():
        print(f"{key}: {value}")