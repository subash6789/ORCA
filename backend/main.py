from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio

from ocean_agent import ocean_agent
from weather_agent import weather_agent
from gis_agent import gis_agent
from pfz_agent import pfz_agent
from safety_agent import safety_agent
from satellite_agent import satellite_agent
from language_agent import language_agent
from auto_update import automatic_update_loop


# =========================================================
# APPLICATION LIFESPAN
# =========================================================

@asynccontextmanager
async def lifespan(app: FastAPI):

    update_task = asyncio.create_task(
        automatic_update_loop()
    )

    print("[ORCA] Automatic update service started.")

    try:
        yield

    finally:

        update_task.cancel()

        try:
            await update_task

        except asyncio.CancelledError:
            pass

        print("[ORCA] Automatic update service stopped.")


# =========================================================
# FASTAPI APPLICATION
# =========================================================

app = FastAPI(
    title="ORCA Real Marine Assistant",
    lifespan=lifespan
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5501",
        "http://localhost:5501"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# ROOT
# =========================================================

@app.get("/")
def home():

    return {
        "message": "ORCA Real Backend is running!",
        "project": (
            "ORCA - Marine EcoSystem Reasoning "
            "with Collaborative Agents"
        )
    }


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/health")
def health():

    return {
        "status": "OK",
        "message": "ORCA backend is healthy"
    }


# =========================================================
# OCEAN AGENT
# =========================================================

@app.get("/ocean")
def ocean(
    state: str = "Tamil Nadu"
):

    return ocean_agent(state)


# =========================================================
# WEATHER AGENT
# =========================================================

@app.get("/weather")
def weather(
    state: str = "Tamil Nadu"
):

    return weather_agent(state)


# =========================================================
# GIS AGENT
# =========================================================

@app.get("/gis")
def gis(
    state: str = "Tamil Nadu",
    district: str = None
):

    return gis_agent(state)


# =========================================================
# PFZ / FISHING AGENT
# =========================================================

@app.get("/pfz")
def pfz(
    state: str = "Tamil Nadu"
):

    return pfz_agent(state)


# =========================================================
# SAFETY AGENT
# =========================================================

@app.get("/safety")
def safety(
    state: str = "Tamil Nadu"
):

    return safety_agent(state)


# =========================================================
# SATELLITE AGENT
# =========================================================

@app.get("/satellite")
def satellite(
    state: str = "Tamil Nadu"
):

    return satellite_agent(state)


# =========================================================
# LANGUAGE AGENT
# =========================================================

@app.get("/language")
def language(
    question: str = ""
):

    return language_agent(question)


# =========================================================
# COLLABORATIVE AGENTS
# =========================================================

@app.get("/agents")
def get_agents():

    return {

        "status": "SUCCESS",

        "system": (
            "ORCA Collaborative Agent System"
        ),

        "agent_count": 6,

        "agents": [

            {
                "name": "Ocean Agent",
                "status": "Integration Ready",
                "responsibilities": [
                    "SST",
                    "Waves",
                    "Currents"
                ]
            },

            {
                "name": "Weather Agent",
                "status": "Integration Ready",
                "responsibilities": [
                    "Wind",
                    "Weather",
                    "Storms"
                ]
            },

            {
                "name": "GIS Agent",
                "status": "Integration Ready",
                "responsibilities": [
                    "Coordinates",
                    "Distance",
                    "Spatial"
                ]
            },

            {
                "name": "Fishing Agent",
                "status": "Integration Ready",
                "responsibilities": [
                    "PFZ",
                    "Chlorophyll",
                    "Fishing"
                ]
            },

            {
                "name": "Safety Agent",
                "status": "Integration Ready",
                "responsibilities": [
                    "Hazards",
                    "Alerts",
                    "Risk"
                ]
            },

            {
                "name": "Coordinator / Planner",
                "status": "Integration Ready",
                "responsibilities": [
                    "Planning",
                    "Coordination",
                    "Evidence"
                ]
            }
        ],

        "source": "ORCA Backend",

        "note": (
            "These agent records describe the ORCA "
            "collaborative-agent architecture and "
            "integration status. They do not represent "
            "fabricated live marine observations."
        )
    }


# =========================================================
# ORCA REASONING / COORDINATOR
# =========================================================

@app.get("/reasoning")
def reasoning(
    question: str = "What are the marine conditions?",
    state: str = "Tamil Nadu",
    district: str = None
):

    try:

        from orca_reasoning import orca_reasoning

        result = orca_reasoning(
            question,
            state
        )

        result["state"] = state
        result["district"] = district

        return result

    except Exception as e:

        return {

            "agent": "ORCA Reasoning Layer",

            "status": "ERROR",

            "question": question,

            "state": state,

            "district": district,

            "message": (
                "Unable to generate ORCA reasoning."
            ),

            "error": str(e)
        }


# =========================================================
# ORCA AI ASSISTANT
# =========================================================

@app.get("/ask")
def ask(
    question: str,
    state: str = "Tamil Nadu",
    district: str = None
):

    return reasoning(
        question,
        state,
        district
    )


# =========================================================
# FORECAST HISTORY
# =========================================================

@app.get("/forecast-history")
def forecast_history(
    state: str = "Tamil Nadu"
):

    try:

        from db_connection import get_connection

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                forecast_time,
                wind_speed_ms,
                wave_height_m,
                source
            FROM wind_forecast
            WHERE LOWER(region) = LOWER(%s)
            ORDER BY forecast_time DESC
            LIMIT 50
        """, (state,))

        rows = cursor.fetchall()

        data = []

        for row in rows:

            data.append({
                "forecast_time": (
                    row[0].isoformat()
                    if row[0]
                    else None
                ),

                "wind_speed_ms": row[1],

                "wave_height_m": row[2],

                "source": row[3]
            })

        cursor.close()
        connection.close()

        return {
            "status": "SUCCESS",
            "state": state,
            "count": len(data),
            "data": data
        }

    except Exception as error:

        print(
            f"[ORCA] Forecast history error: {error}"
        )

        return {
            "status": "ERROR",
            "state": state,
            "count": 0,
            "data": [],
            "message": (
                "Forecast history could not be loaded."
            )
        }