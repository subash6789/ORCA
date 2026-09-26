import json
from datetime import datetime
from urllib.request import urlopen


# ORCA supported regions
REGIONS = {
    "Tamil Nadu": {
        "latitude": 13.0827,
        "longitude": 80.2707,
        "location": "Chennai, Tamil Nadu"
    },
    "Kerala": {
        "latitude": 10.8505,
        "longitude": 76.2711,
        "location": "Kerala"
    },
    "Karnataka": {
        "latitude": 12.9716,
        "longitude": 77.5946,
        "location": "Bengaluru, Karnataka"
    },
    "Gujarat": {
        "latitude": 23.0225,
        "longitude": 72.5714,
        "location": "Ahmedabad, Gujarat"
    }
}


def weather_agent(region="Tamil Nadu"):

    # Check region
    if region not in REGIONS:
        return {
            "agent": "Weather Agent",
            "status": "ERROR",
            "message": f"Unsupported region: {region}"
        }

    location_data = REGIONS[region]

    latitude = location_data["latitude"]
    longitude = location_data["longitude"]
    location_name = location_data["location"]

    # Open-Meteo current weather API
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={latitude}"
        f"&longitude={longitude}"
        "&current=temperature_2m,relative_humidity_2m,"
        "wind_speed_10m,wind_direction_10m,precipitation"
        "&timezone=auto"
    )

    try:

        # Time when ORCA retrieves the weather
        retrieved_at = datetime.now()

        with urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())

        current = data["current"]

        # Time provided by the weather source
        observation_time = current["time"]

        return {
            "agent": "Weather Agent",
            "status": "SUCCESS",
            "region": region,
            "location": location_name,

            "temperature_c": current["temperature_2m"],
            "humidity_percent": current["relative_humidity_2m"],
            "wind_speed_kmh": current["wind_speed_10m"],
            "wind_direction_degrees": current["wind_direction_10m"],
            "precipitation_mm": current["precipitation"],

            "observation_time": observation_time,
            "retrieved_at": retrieved_at.isoformat(),

            "source": "Open-Meteo",
            "data_status": "CURRENT_WEATHER"
        }

    except Exception as e:

        return {
            "agent": "Weather Agent",
            "status": "ERROR",
            "region": region,
            "location": location_name,
            "source": "Open-Meteo",
            "message": str(e)
        }


if __name__ == "__main__":

    print("==============================================")
    print("ORCA WEATHER AGENT")
    print("==============================================")

    for region in REGIONS:

        print()
        print("----------------------------------------------")
        print(f"Processing: {region}")
        print("----------------------------------------------")

        result = weather_agent(region)

        for key, value in result.items():
            print(f"{key}: {value}")

    print()
    print("==============================================")
    print("WEATHER AGENT TEST COMPLETED")
    print("==============================================")