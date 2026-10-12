import requests
from datetime import datetime, timezone


# ============================================================
# DISTRICT COORDINATES
# ============================================================

DISTRICT_COORDINATES = {
    "Tamil Nadu": {
        "Ariyalur": (11.1401, 79.0786),
        "Chengalpattu": (12.6819, 79.9888),
        "Chennai": (13.0827, 80.2707),
        "Coimbatore": (11.0168, 76.9558),
        "Cuddalore": (11.7480, 79.7714),
        "Dharmapuri": (12.1211, 78.1582),
        "Dindigul": (10.3673, 77.9803),
        "Erode": (11.3410, 77.7172),
        "Kallakurichi": (11.7401, 78.9597),
        "Kancheepuram": (12.8342, 79.7036),
        "Karur": (10.9601, 78.0766),
        "Krishnagiri": (12.5186, 78.2137),
        "Madurai": (9.9252, 78.1198),
        "Mayiladuthurai": (11.1018, 79.6524),
        "Nagapattinam": (10.7672, 79.8449),
        "Namakkal": (11.2194, 78.1677),
        "Nilgiris": (11.4102, 76.6950),
        "Perambalur": (11.2320, 78.8801),
        "Pudukkottai": (10.3797, 78.8208),
        "Ramanathapuram": (9.3639, 78.8395),
        "Ranipet": (12.9249, 79.3333),
        "Salem": (11.6643, 78.1460),
        "Sivaganga": (9.8433, 78.4809),
        "Tenkasi": (8.9590, 77.3152),
        "Thanjavur": (10.7870, 79.1378),
        "Theni": (10.0104, 77.4768),
        "Thoothukudi": (8.7642, 78.1348),
        "Tiruchirappalli": (10.7905, 78.7047),
        "Tirunelveli": (8.7139, 77.7567),
        "Tirupathur": (12.4970, 78.5670),
        "Tiruppur": (11.1085, 77.3411),
        "Tiruvallur": (13.1439, 79.9080),
        "Tiruvannamalai": (12.2253, 79.0747),
        "Tiruvarur": (10.7661, 79.6346),
        "Vellore": (12.9165, 79.1325),
        "Viluppuram": (11.9401, 79.4861),
        "Virudhunagar": (9.5851, 77.9624),
    },

    "Kerala": {
        "Alappuzha": (9.4981, 76.3388),
        "Ernakulam": (9.9816, 76.2999),
        "Idukki": (9.8500, 76.9700),
        "Kannur": (11.8745, 75.3704),
        "Kasaragod": (12.4996, 74.9869),
        "Kollam": (8.8932, 76.6141),
        "Kottayam": (9.5916, 76.5222),
        "Kozhikode": (11.2588, 75.7804),
        "Malappuram": (11.0510, 76.0711),
        "Palakkad": (10.7867, 76.6548),
        "Pathanamthitta": (9.2648, 76.7870),
        "Thiruvananthapuram": (8.5241, 76.9366),
        "Thrissur": (10.5276, 76.2144),
        "Wayanad": (11.6854, 76.1320),
    },

    "Karnataka": {
        "Bagalkot": (16.1691, 75.6615),
        "Ballari": (15.1394, 76.9214),
        "Belagavi": (15.8497, 74.4977),
        "Bengaluru Rural": (13.2257, 77.5750),
        "Bengaluru Urban": (12.9716, 77.5946),
        "Bidar": (17.9104, 77.5199),
        "Chamarajanagar": (11.9261, 76.9437),
        "Chikkaballapur": (13.4355, 77.7315),
        "Chikkamagaluru": (13.3161, 75.7720),
        "Chitradurga": (14.2306, 76.3980),
        "Dakshina Kannada": (12.9141, 74.8560),
        "Davanagere": (14.4644, 75.9218),
        "Dharwad": (15.4589, 75.0078),
        "Gadag": (15.4167, 75.6297),
        "Hassan": (13.0033, 76.1004),
        "Haveri": (14.7951, 75.3991),
        "Kalaburagi": (17.3297, 76.8343),
        "Kodagu": (12.3375, 75.8069),
        "Kolar": (13.1367, 78.1292),
        "Koppal": (15.3500, 76.1500),
        "Mandya": (12.5218, 76.8951),
        "Mysuru": (12.2958, 76.6394),
        "Raichur": (16.2120, 77.3439),
        "Ramanagara": (12.7150, 77.2810),
        "Shivamogga": (13.9299, 75.5681),
        "Tumakuru": (13.3392, 77.1017),
        "Udupi": (13.3409, 74.7421),
        "Uttara Kannada": (14.7951, 74.6869),
        "Vijayapura": (16.8302, 75.7100),
        "Yadgir": (16.7700, 77.1300),
    },

    "Gujarat": {
        "Ahmedabad": (23.0225, 72.5714),
        "Amreli": (21.6032, 71.2221),
        "Anand": (22.5645, 72.9289),
        "Aravalli": (23.3500, 73.3500),
        "Banaskantha": (24.1720, 72.4300),
        "Bharuch": (21.7051, 72.9959),
        "Bhavnagar": (21.7645, 72.1519),
        "Botad": (22.1700, 71.6680),
        "Chhota Udaipur": (22.3040, 74.0140),
        "Dahod": (22.8390, 74.2550),
        "Dang": (20.7500, 73.6900),
        "Devbhoomi Dwarka": (22.2442, 68.9685),
        "Gandhinagar": (23.2156, 72.6369),
        "Gir Somnath": (20.9000, 70.5000),
        "Jamnagar": (22.4707, 70.0577),
        "Junagadh": (21.5222, 70.4579),
        "Kheda": (22.7500, 72.6800),
        "Kutch": (23.7337, 69.8597),
        "Mahisagar": (23.1300, 73.6000),
        "Mehsana": (23.5880, 72.3693),
        "Morbi": (22.8173, 70.8377),
        "Narmada": (21.8700, 73.5000),
        "Navsari": (20.9467, 72.9520),
        "Panchmahal": (22.7500, 73.6000),
        "Patan": (23.8500, 72.1300),
        "Porbandar": (21.6417, 69.6293),
        "Rajkot": (22.3039, 70.8022),
        "Sabarkantha": (23.6000, 73.0000),
        "Surat": (21.1702, 72.8311),
        "Surendranagar": (22.7270, 71.6480),
        "Tapi": (21.1200, 73.4000),
        "Vadodara": (22.3072, 73.1812),
        "Valsad": (20.5992, 72.9342),
    },
}

# Augment with canonical official district coordinates if available
try:
    import json
    from pathlib import Path
    _canon_file = Path(__file__).resolve().parent / "district_canonical_coords.json"
    if _canon_file.exists():
        with open(_canon_file, "r", encoding="utf-8") as _f:
            _canon_data = json.load(_f)
        for _st, _dist_map in _canon_data.items():
            for _dname, _coords in _dist_map.items():
                DISTRICT_COORDINATES.setdefault(_st, {})[_dname] = tuple(_coords)
except Exception:
    pass


# ============================================================
# STATE CENTERS
# ============================================================

STATE_CENTERS = {
    "Tamil Nadu": (13.0827, 80.2707),
    "Kerala": (10.8505, 76.2711),
    "Karnataka": (12.9716, 77.5946),
    "Gujarat": (23.0225, 72.5714),
}


# ============================================================
# WEATHER CODE DESCRIPTION
# ============================================================

def weather_code_description(code):
    descriptions = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Fog",
        48: "Depositing rime fog",
        51: "Light drizzle",
        53: "Moderate drizzle",
        55: "Dense drizzle",
        56: "Light freezing drizzle",
        57: "Dense freezing drizzle",
        61: "Slight rain",
        63: "Moderate rain",
        65: "Heavy rain",
        66: "Light freezing rain",
        67: "Heavy freezing rain",
        71: "Slight snow",
        73: "Moderate snow",
        75: "Heavy snow",
        77: "Snow grains",
        80: "Slight rain showers",
        81: "Moderate rain showers",
        82: "Violent rain showers",
        85: "Slight snow showers",
        86: "Heavy snow showers",
        95: "Thunderstorm",
        96: "Thunderstorm with slight hail",
        99: "Thunderstorm with heavy hail",
    }

    return descriptions.get(
        code,
        "Weather condition unavailable"
    )


# ============================================================
# RAIN CONDITION
# ============================================================

def rain_condition(probability, precipitation):
    probability = float(probability or 0)
    precipitation = float(precipitation or 0)

    if precipitation > 10 or probability >= 80:
        return "High chance of rain"

    if precipitation > 2 or probability >= 50:
        return "Rain possible"

    if precipitation > 0 or probability >= 20:
        return "Low chance of rain"

    return "No significant rain expected"


# ============================================================
# WEATHER AGENT
# ============================================================

def weather_agent(state="Tamil Nadu", district=""):

    state = str(state or "").strip()
    district = str(district or "").strip()

    if state not in STATE_CENTERS:
        return {
            "status": "ERROR",
            "data_status": "ERROR",
            "region": state,
            "district": district,
            "message": "Unsupported state.",
        }

    latitude, longitude = STATE_CENTERS[state]
    location = state

    if district:

        district_coordinates = (
            DISTRICT_COORDINATES
            .get(state, {})
            .get(district)
        )

        if district_coordinates is None:
            # Case-insensitive or normalized lookup
            state_dists = DISTRICT_COORDINATES.get(state, {})
            for d_name, d_coords in state_dists.items():
                if d_name.lower() == district.lower():
                    district_coordinates = d_coords
                    break

        if district_coordinates is None:
            return {
                "status": "ERROR",
                "data_status": "ERROR",
                "region": state,
                "district": district,
                "message": "District not found for selected state.",
            }

        latitude, longitude = district_coordinates
        location = f"{district}, {state}"

    # ========================================================
    # OPEN-METEO REQUEST
    # ========================================================

    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": latitude,
        "longitude": longitude,

        "current": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "precipitation,"
            "rain,"
            "weather_code,"
            "wind_speed_10m,"
            "wind_direction_10m"
        ),

        "hourly": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "precipitation_probability,"
            "precipitation,"
            "rain,"
            "weather_code,"
            "wind_speed_10m,"
            "wind_direction_10m"
        ),

        "daily": (
            "temperature_2m_max,"
            "temperature_2m_min,"
            "precipitation_probability_max,"
            "precipitation_sum,"
            "rain_sum,"
            "wind_speed_10m_max,"
            "weather_code"
        ),

        "forecast_days": 3,
        "timezone": "auto",
    }

    try:
        response = requests.get(
            url,
            params=params,
            timeout=20
        )

        response.raise_for_status()
        data = response.json()

    except requests.RequestException as exc:
        return {
            "status": "ERROR",
            "data_status": "ERROR",
            "region": state,
            "district": district,
            "location": location,
            "source": "Open-Meteo",
            "error": str(exc),
            "retrieved_at": datetime.now(
                timezone.utc
            ).isoformat(),
        }

    # ========================================================
    # CURRENT WEATHER
    # ========================================================

    current = data.get("current", {})

    current_weather = {
        "temperature_c": current.get("temperature_2m"),
        "humidity_percent": current.get("relative_humidity_2m"),
        "precipitation_mm": current.get("precipitation"),
        "rain_mm": current.get("rain"),
        "weather_code": current.get("weather_code"),
        "weather_condition": weather_code_description(
            current.get("weather_code")
        ),
        "wind_speed_kmh": current.get("wind_speed_10m"),
        "wind_direction_degrees": current.get(
            "wind_direction_10m"
        ),
        "observation_time": current.get("time"),
    }

    # ========================================================
    # HOURLY FORECAST
    # ========================================================

    hourly = data.get("hourly", {})

    hourly_times = hourly.get("time", [])
    hourly_temperatures = hourly.get(
        "temperature_2m",
        []
    )
    hourly_humidity = hourly.get(
        "relative_humidity_2m",
        []
    )
    hourly_probability = hourly.get(
        "precipitation_probability",
        []
    )
    hourly_precipitation = hourly.get(
        "precipitation",
        []
    )
    hourly_rain = hourly.get(
        "rain",
        []
    )
    hourly_weather_codes = hourly.get(
        "weather_code",
        []
    )
    hourly_wind_speed = hourly.get(
        "wind_speed_10m",
        []
    )
    hourly_wind_direction = hourly.get(
        "wind_direction_10m",
        []
    )

    hourly_forecast = []

    for index, forecast_time in enumerate(
        hourly_times[:24]
    ):

        probability = (
            hourly_probability[index]
            if index < len(hourly_probability)
            else None
        )

        precipitation = (
            hourly_precipitation[index]
            if index < len(hourly_precipitation)
            else None
        )

        rain = (
            hourly_rain[index]
            if index < len(hourly_rain)
            else None
        )

        weather_code = (
            hourly_weather_codes[index]
            if index < len(hourly_weather_codes)
            else None
        )

        temperature = (
            hourly_temperatures[index]
            if index < len(hourly_temperatures)
            else None
        )

        humidity = (
            hourly_humidity[index]
            if index < len(hourly_humidity)
            else None
        )

        wind_speed = (
            hourly_wind_speed[index]
            if index < len(hourly_wind_speed)
            else None
        )

        wind_direction = (
            hourly_wind_direction[index]
            if index < len(hourly_wind_direction)
            else None
        )

        hourly_forecast.append({
            "time": forecast_time,
            "temperature_c": temperature,
            "humidity_percent": humidity,
            "precipitation_probability_percent": probability,
            "precipitation_mm": precipitation,
            "rain_mm": rain,
            "weather_code": weather_code,
            "weather_condition": weather_code_description(
                weather_code
            ),
            "wind_speed_kmh": wind_speed,
            "wind_direction_degrees": wind_direction,
            "rain_condition": rain_condition(
                probability,
                precipitation
            ),
        })

    # ========================================================
    # DAILY FORECAST
    # ========================================================

    daily = data.get("daily", {})

    daily_times = daily.get("time", [])

    daily_max_temperature = daily.get(
        "temperature_2m_max",
        []
    )

    daily_min_temperature = daily.get(
        "temperature_2m_min",
        []
    )

    daily_probability = daily.get(
        "precipitation_probability_max",
        []
    )

    daily_precipitation = daily.get(
        "precipitation_sum",
        []
    )

    daily_rain = daily.get(
        "rain_sum",
        []
    )

    daily_wind_speed_max = daily.get(
        "wind_speed_10m_max",
        []
    )

    daily_weather_codes = daily.get(
        "weather_code",
        []
    )

    daily_forecast = []

    for index, forecast_date in enumerate(
        daily_times
    ):

        maximum_temperature = (
            daily_max_temperature[index]
            if index < len(daily_max_temperature)
            else None
        )

        minimum_temperature = (
            daily_min_temperature[index]
            if index < len(daily_min_temperature)
            else None
        )

        probability = (
            daily_probability[index]
            if index < len(daily_probability)
            else None
        )

        precipitation = (
            daily_precipitation[index]
            if index < len(daily_precipitation)
            else None
        )

        rain = (
            daily_rain[index]
            if index < len(daily_rain)
            else None
        )

        wind_speed_max = (
            daily_wind_speed_max[index]
            if index < len(daily_wind_speed_max)
            else None
        )

        weather_code = (
            daily_weather_codes[index]
            if index < len(daily_weather_codes)
            else None
        )

        daily_forecast.append({
            "date": forecast_date,

            "temperature_max_c":
                maximum_temperature,

            "temperature_min_c":
                minimum_temperature,

            # Existing field
            "rain_probability_percent":
                probability,

            # Existing field
            "precipitation_mm":
                precipitation,

            "rain_mm":
                rain,

            # NEW: used by ORCA reasoning
            "wind_speed_max_kmh":
                wind_speed_max,

            # Compatibility fields used by reasoning
            "precipitation_probability_max_percent":
                probability,

            "precipitation_sum_mm":
                precipitation,

            "weather_code":
                weather_code,

            "weather_condition":
                weather_code_description(
                    weather_code
                ),

            "rain_condition":
                rain_condition(
                    probability,
                    precipitation
                ),
        })

    # ========================================================
    # NEXT RAIN FORECAST
    # ========================================================

    next_rain_forecast = None

    for forecast in hourly_forecast:

        probability = (
            forecast.get(
                "precipitation_probability_percent"
            ) or 0
        )

        precipitation = (
            forecast.get(
                "precipitation_mm"
            ) or 0
        )

        if probability >= 30 or precipitation > 0:
            next_rain_forecast = forecast
            break

    # ========================================================
    # CURRENT RAIN STATUS
    # ========================================================

    current_probability = 0

    if hourly_forecast:
        current_probability = (
            hourly_forecast[0].get(
                "precipitation_probability_percent"
            ) or 0
        )

    current_rain_status = rain_condition(
        current_probability,
        current.get("precipitation")
    )

    # ========================================================
    # FINAL RESULT
    # ========================================================

    return {
        "status": "SUCCESS",
        "data_status": "OBSERVED_AND_FORECAST",

        "region": state,
        "district": district,
        "location": location,

        "coordinates": {
            "latitude": latitude,
            "longitude": longitude,
        },

        "current_weather": {
            **current_weather,

            "rain_probability_percent":
                current_probability,

            "rain_status":
                current_rain_status,
        },

        "rain_forecast": {
            "current_probability_percent":
                current_probability,

            "current_precipitation_mm":
                current.get("precipitation"),

            "current_rain_mm":
                current.get("rain"),

            "current_status":
                current_rain_status,

            "next_rain":
                next_rain_forecast,
        },

        "hourly_forecast":
            hourly_forecast,

        "daily_forecast":
            daily_forecast,

        "source":
            "Open-Meteo",

        "retrieved_at":
            datetime.now(
                timezone.utc
            ).isoformat(),
    }


# ============================================================
# DIRECT TEST
# ============================================================

if __name__ == "__main__":

    import json

    result = weather_agent(
        "Tamil Nadu",
        "Chennai"
    )

    print(
        json.dumps(
            result,
            indent=2,
            default=str
        )
    )