from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ocean_agent import ocean_agent
from weather_agent import weather_agent
from gis_agent import gis_agent
from pfz_agent import pfz_agent
from safety_agent import safety_agent
from satellite_agent import satellite_agent
from language_agent import language_agent

app = FastAPI(title="ORCA Real Marine Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {
        "message": "ORCA Real Backend is running!",
        "project": "ORCA - Marine EcoSystem Reasoning with Collaborative Agents"
    }


@app.get("/health")
def health():
    return {
        "status": "OK",
        "message": "ORCA backend is healthy"
    }


@app.get("/ocean")
def ocean():
    return ocean_agent()


@app.get("/weather")
def weather():
    return weather_agent()


@app.get("/gis")
def gis():
    return gis_agent()


@app.get("/pfz")
def pfz():
    return pfz_agent()


@app.get("/safety")
def safety():
    return safety_agent()


@app.get("/satellite")
def satellite():
    return satellite_agent()


@app.get("/language")
def language(question: str = ""):
    return language_agent(question)


@app.get("/reasoning")
def reasoning(
    question: str = "What is the marine condition, PFZ status, satellite status and safety near Chennai?"
):

    language = language_agent(question)
    ocean = ocean_agent()
    weather = weather_agent()
    gis = gis_agent()
    pfz = pfz_agent()
    satellite = satellite_agent()
    safety = safety_agent()

    reasoning_points = []

    # Language
    reasoning_points.append(
        f"Detected language: {language['detected_language']}."
    )

    # Ocean
    if ocean.get("sea_surface_temperature_c") is not None:
        reasoning_points.append(
            f"Ocean temperature is {ocean['sea_surface_temperature_c']} °C."
        )

    if ocean.get("current_speed_ms") is not None:
        reasoning_points.append(
            f"Average ocean current speed is {ocean['current_speed_ms']} m/s."
        )

    if ocean.get("salinity") is not None:
        reasoning_points.append(
            f"Sea-water salinity is {ocean['salinity']}."
        )

    # Weather
    if weather.get("temperature_c") is not None:
        reasoning_points.append(
            f"Current air temperature is {weather['temperature_c']} °C."
        )

    if weather.get("wind_speed_kmh") is not None:
        reasoning_points.append(
            f"Wind speed is {weather['wind_speed_kmh']} km/h."
        )

    precipitation = weather.get("precipitation_mm")

    if precipitation is not None:
        if precipitation > 0:
            reasoning_points.append(
                f"Current precipitation is {precipitation} mm."
            )
        else:
            reasoning_points.append(
                "No precipitation is currently reported."
            )

    # GIS
    location = gis.get("location", "Unknown")
    marine_region = gis.get("marine_region", "Unknown")

    reasoning_points.append(
        f"Location identified as {location} in the {marine_region}."
    )

    # PFZ
    pfz_status = pfz.get(
        "pfz_available",
        "PFZ information unavailable"
    )

    pfz_message = pfz.get(
        "message",
        "PFZ information is not currently available."
    )

    pfz_assessment = (
        f"PFZ status: {pfz_status}. {pfz_message}"
    )

    reasoning_points.append(pfz_assessment)

    # Satellite
    satellite_name = satellite.get(
        "satellite",
        "Satellite"
    )

    satellite_status = satellite.get(
        "integration_status",
        "Unknown"
    )

    satellite_message = satellite.get(
        "message",
        "Satellite information unavailable."
    )

    satellite_assessment = (
        f"Satellite status: {satellite_name} - "
        f"{satellite_status}. {satellite_message}"
    )

    reasoning_points.append(satellite_assessment)

    # Safety
    alerts = safety.get("alerts", [])

    if alerts:
        safety_assessment = (
            "Safety alerts detected: " + " ".join(alerts)
        )
    else:
        safety_assessment = (
            "Safety assessment: No immediate warning condition detected."
        )

    reasoning_points.append(safety_assessment)

    # Final assessment
    final_assessment = (
        "ORCA combines Language, Ocean, Weather, GIS, PFZ, "
        "Satellite and Safety agents to provide a marine "
        "decision-support assessment."
    )

    if alerts:
        final_assessment += (
            " Safety conditions require attention based on "
            "the current demo rules."
        )
    else:
        final_assessment += (
            " No immediate warning condition was detected "
            "by the current demo safety rules."
        )

    return {
        "agent": "ORCA Reasoning Layer",
        "status": "SUCCESS",
        "question": question,

        "selected_agents": [
            "Language Agent",
            "Ocean Agent",
            "Weather Agent",
            "GIS Agent",
            "PFZ Agent",
            "Satellite Agent",
            "Safety Agent"
        ],

        "language_analysis": language,
        "ocean_analysis": ocean,
        "weather_analysis": weather,
        "gis_analysis": gis,
        "pfz_analysis": pfz,
        "satellite_analysis": satellite,
        "safety_analysis": safety,

        "reasoning_points": reasoning_points,

        "pfz_assessment": pfz_assessment,
        "satellite_assessment": satellite_assessment,
        "safety_assessment": safety_assessment,

        "final_assessment": final_assessment,

        "source_note": (
            "ORCA provides decision support. PFZ and satellite "
            "information are currently integration-ready. "
            "Safety results are not official government warnings."
        )
    }


@app.get("/ask")
def ask(question: str):
    return reasoning(question)