from datetime import datetime, timezone

from ocean_agent import ocean_agent
from weather_agent import weather_agent


REGION_MAP = {
    "Tamil Nadu": "Tamil Nadu / Bay of Bengal",
    "Kerala": "Kerala / Arabian Sea",
    "Karnataka": "Karnataka / Arabian Sea",
    "Gujarat": "Gujarat / Arabian Sea",
}


def safety_agent(state="Tamil Nadu", district=""):

    state = str(state or "").strip()
    district = str(district or "").strip()

    # -------------------------------------------------
    # VALIDATE REGION
    # -------------------------------------------------

    if state not in REGION_MAP:
        return {
            "agent": "Safety Agent",
            "status": "UNAVAILABLE",
            "data_status": "UNAVAILABLE",
            "state": state,
            "district": district,
            "message": "Unsupported region."
        }

    region = REGION_MAP[state]

    # -------------------------------------------------
    # GET REAL OCEAN + WEATHER DATA
    # -------------------------------------------------

    ocean = ocean_agent(state, district)
    weather = weather_agent(state, district)

    # -------------------------------------------------
    # CHECK AGENT DATA AVAILABILITY
    # -------------------------------------------------

    ocean_available = ocean.get("status") == "SUCCESS"
    weather_available = weather.get("status") == "SUCCESS"

    if not ocean_available and not weather_available:
        return {
            "agent": "Safety Agent",
            "status": "NO_DATA",
            "data_status": "NO_DATA",
            "state": state,
            "district": district,
            "region": region,
            "safety_status": "NO_DATA",
            "alerts": [],
            "risk_factors": [],
            "message": (
                "Safety decision support could not be evaluated "
                "because both ocean and weather data are unavailable."
            ),
            "evaluated_at": datetime.now(timezone.utc).isoformat()
        }

    # -------------------------------------------------
    # REAL OBSERVED WEATHER VALUES
    # -------------------------------------------------

    cw = weather.get("current_weather")
    if isinstance(cw, dict):
        wind_kmh = cw.get("wind_speed_kmh", weather.get("wind_speed_kmh"))
        precipitation_mm = cw.get("precipitation_mm", weather.get("precipitation_mm"))
        weather_observation_time = cw.get("observation_time", weather.get("observation_time"))
    else:
        wind_kmh = weather.get("wind_speed_kmh")
        precipitation_mm = weather.get("precipitation_mm")
        weather_observation_time = weather.get("observation_time")

    # -------------------------------------------------
    # REAL OCEAN FORECAST VALUES
    #
    # These come directly from the current Ocean Agent,
    # which uses INCOIS RSMC / HYCOM + WW3 THREDDS.
    # -------------------------------------------------

    current_speed_ms = ocean.get("current_speed_ms")
    forecast_wind_ms = ocean.get("wind_speed_ms")
    forecast_wave_m = ocean.get("wave_height_m")

    ocean_source = ocean.get("source")
    ocean_data_status = ocean.get("data_status")

    weather_source = weather.get("source")
    weather_data_status = weather.get("data_status")

    ocean_observation_time = ocean.get("observation_time")
    ocean_retrieved_at = ocean.get("retrieved_at")

    weather_retrieved_at = weather.get("retrieved_at")

    # -------------------------------------------------
    # ORCA DECISION-SUPPORT RULES
    #
    # These thresholds are project heuristics.
    # They are NOT official government warnings.
    # -------------------------------------------------

    alerts = []
    risk_factors = []

    # -------------------------------------------------
    # OBSERVED WEATHER RULE
    # -------------------------------------------------

    if wind_kmh is not None and wind_kmh >= 40:

        alerts.append(
            f"High observed wind speed detected: {wind_kmh} km/h."
        )

        risk_factors.append("Observed wind speed")

    # -------------------------------------------------
    # PRECIPITATION RULE
    # -------------------------------------------------

    if precipitation_mm is not None and precipitation_mm >= 10:

        alerts.append(
            f"High precipitation detected: {precipitation_mm} mm."
        )

        risk_factors.append("Precipitation")

    # -------------------------------------------------
    # OCEAN CURRENT RULE
    # -------------------------------------------------

    if current_speed_ms is not None and current_speed_ms >= 2:

        alerts.append(
            f"Strong ocean current detected: {current_speed_ms} m/s."
        )

        risk_factors.append("Ocean current")

    # -------------------------------------------------
    # FORECAST WIND DECISION SUPPORT
    # -------------------------------------------------

    forecast_risk = "NO_RULE_TRIGGERED"

    if forecast_wind_ms is not None:

        if forecast_wind_ms >= 10:

            forecast_risk = "HIGH"
            risk_factors.append("Forecast wind")

        elif forecast_wind_ms >= 5:

            forecast_risk = "MODERATE"
            risk_factors.append("Forecast wind")

    # -------------------------------------------------
    # FORECAST WAVE DECISION SUPPORT
    # -------------------------------------------------

    if forecast_wave_m is not None:

        if forecast_wave_m >= 3:

            forecast_risk = "HIGH"
            risk_factors.append("Forecast wave height")

        elif forecast_wave_m >= 1.5:

            if forecast_risk != "HIGH":
                forecast_risk = "MODERATE"

            risk_factors.append("Forecast wave height")

    # -------------------------------------------------
    # FINAL SAFETY STATUS
    # -------------------------------------------------

    if forecast_risk == "HIGH" or alerts:

        safety_status = "WARNING"

    elif forecast_risk == "MODERATE":

        safety_status = "CAUTION"

    else:

        safety_status = "NO_RULE_TRIGGERED"

    # -------------------------------------------------
    # DATA STATUS
    # -------------------------------------------------

    available_sources = []

    if ocean_available:
        available_sources.append(ocean_source or "ORCA Ocean Agent")

    if weather_available:
        available_sources.append(weather_source or "ORCA Weather Agent")

    # -------------------------------------------------
    # FINAL RESULT
    # -------------------------------------------------

    return {

        "agent": "Safety Agent",

        "status": "SUCCESS",

        "data_status": "ORCA_HEURISTIC",

        "state": state,

        "district": district,

        "region": region,

        # ---------------------------------------------
        # FINAL DECISION
        # ---------------------------------------------

        "safety_status": safety_status,

        "alerts": alerts,

        "risk_factors": list(
            dict.fromkeys(risk_factors)
        ),

        # ---------------------------------------------
        # REAL INPUT VALUES
        # ---------------------------------------------

        "input_data": {

            "observed_wind_speed_kmh": wind_kmh,

            "precipitation_mm": precipitation_mm,

            "ocean_current_speed_ms": current_speed_ms,

            "forecast_wind_speed_ms": forecast_wind_ms,

            "forecast_wave_height_m": forecast_wave_m
        },

        # ---------------------------------------------
        # FORECAST DECISION SUPPORT
        # ---------------------------------------------

        "forecast_decision_support": {

            "risk_level": forecast_risk,

            "wind_speed_ms": forecast_wind_ms,

            "wave_height_m": forecast_wave_m,

            "source": ocean_source,

            "data_status": ocean_data_status,

            "forecast_time": ocean_observation_time,

            "retrieved_at": ocean_retrieved_at
        },

        # ---------------------------------------------
        # WEATHER DATA PROVENANCE
        # ---------------------------------------------

        "weather_data": {

            "wind_speed_kmh": wind_kmh,

            "precipitation_mm": precipitation_mm,

            "source": weather_source,

            "data_status": weather_data_status,

            "observation_time": weather_observation_time,

            "retrieved_at": weather_retrieved_at
        },

        # ---------------------------------------------
        # PROJECT HEURISTIC RULES
        # ---------------------------------------------

        "rules": {

            "high_wind_kmh": 40,

            "heavy_precipitation_mm": 10,

            "strong_current_ms": 2,

            "forecast_wind_moderate_ms": 5,

            "forecast_wind_high_ms": 10,

            "forecast_wave_moderate_m": 1.5,

            "forecast_wave_high_m": 3
        },

        # ---------------------------------------------
        # DATA SOURCES
        # ---------------------------------------------

        "source": available_sources,

        # ---------------------------------------------
        # IMPORTANT TRANSPARENCY
        # ---------------------------------------------

        "message": (
            "Marine safety status is generated by ORCA "
            "decision-support heuristics using available "
            "real ocean and weather data. Ocean forecast "
            "values are obtained through the ORCA Ocean Agent "
            "from its configured authoritative data sources. "
            "This result is decision support and is not an "
            "official government marine warning or safety alert."
        ),

        "evaluated_at": datetime.now(
            timezone.utc
        ).isoformat()
    }


# -------------------------------------------------
# DIRECT TEST
# -------------------------------------------------

if __name__ == "__main__":

    import json

    result = safety_agent(
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