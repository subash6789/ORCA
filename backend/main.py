from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import threading

from ocean_agent import ocean_agent
from weather_agent import weather_agent
from gis_agent import gis_agent
from pfz_agent import pfz_agent
from safety_agent import safety_agent
from satellite_agent import satellite_agent
from language_agent import language_agent
from auto_update import automatic_update_loop


# ============================================================
# ORCA AUTOMATIC UPDATE SERVICE
# ============================================================

def run_automatic_updates():
    try:
        asyncio.run(automatic_update_loop())
    except Exception as error:
        print(f"[ORCA] Automatic update service error: {error}")


@asynccontextmanager
async def lifespan(app: FastAPI):

    update_thread = threading.Thread(
        target=run_automatic_updates,
        daemon=True,
        name="ORCA-Automatic-Update"
    )

    update_thread.start()

    print(
        "[ORCA] Automatic update service started in background thread."
    )

    try:
        yield

    finally:
        print("[ORCA] FastAPI shutdown requested.")
        print(
            "[ORCA] Background update thread will stop "
            "with the service."
        )


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="ORCA Real Marine Assistant",
    lifespan=lifespan
)


# ============================================================
# CORS
# ============================================================

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


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def home():
    return {
        "message": "ORCA Real Backend is running!",
        "project": "ORCA - Marine EcoSystem Reasoning with Collaborative Agents"
    }


# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
def health():
    return {
        "status": "OK",
        "message": "ORCA backend is healthy"
    }


# ============================================================
# OCEAN
# ============================================================

@app.get("/ocean")
def ocean(state: str = "Tamil Nadu"):
    return ocean_agent(state)


# ============================================================
# WEATHER
# ============================================================

@app.get("/weather")
def weather(state: str = "Tamil Nadu"):
    return weather_agent(state)


# ============================================================
# GIS
# ============================================================

@app.get("/gis")
def gis(
    state: str = "Tamil Nadu",
    district: str = None
):
    return gis_agent(state)


# ============================================================
# PFZ
# ============================================================

@app.get("/pfz")
def pfz(state: str = "Tamil Nadu"):
    return pfz_agent(state)


# ============================================================
# MARINE SAFETY
# ============================================================

@app.get("/safety")
def safety(state: str = "Tamil Nadu"):
    return safety_agent(state)


# ============================================================
# SATELLITE
# ============================================================

@app.get("/satellite")
def satellite(state: str = "Tamil Nadu"):
    return satellite_agent(state)


# ============================================================
# LANGUAGE
# ============================================================

@app.get("/language")
def language(question: str = ""):
    return language_agent(question)


# ============================================================
# COLLABORATIVE AGENTS
# ============================================================

@app.get("/agents")
def get_agents():

    return {
        "status": "SUCCESS",
        "system": "ORCA Collaborative Agent System",
        "agent_count": 6,

        "agents": [
            {
                "name": "Ocean Agent",
                "role": "Ocean and marine condition analysis"
            },
            {
                "name": "Weather Agent",
                "role": "Weather and forecast analysis"
            },
            {
                "name": "GIS Agent",
                "role": "Geospatial and location reasoning"
            },
            {
                "name": "PFZ Agent",
                "role": "Potential Fishing Zone intelligence"
            },
            {
                "name": "Marine Safety Agent",
                "role": "Marine safety and risk analysis"
            },
            {
                "name": "Satellite Agent",
                "role": "Satellite-derived marine intelligence"
            }
        ],

        "source": "ORCA Backend",

        "note": (
            "Agent outputs are based on available authoritative "
            "data sources and ORCA reasoning. They do not represent "
            "fabricated live marine observations."
        )
    }


# ============================================================
# ORCA REASONING
# ============================================================

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

    except Exception as error:

        return {
            "agent": "ORCA Reasoning Layer",
            "status": "ERROR",
            "question": question,
            "state": state,
            "district": district,
            "message": "Unable to generate ORCA reasoning.",
            "error": str(error)
        }


# ============================================================
# ORCA ASSISTANT
# ============================================================

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


# ============================================================
# FORECAST HISTORY
# ============================================================

@app.get("/forecast-history")
def forecast_history(
    state: str = "Tamil Nadu"
):

    try:

        from db_connection import get_connection

        # ----------------------------------------------------
        # FRONTEND STATE -> DATABASE REGION
        # ----------------------------------------------------

        region_map = {

            "Tamil Nadu":
                "Tamil Nadu / Bay of Bengal",

            "Kerala":
                "Kerala / Arabian Sea",

            "Karnataka":
                "Karnataka / Arabian Sea",

            "Gujarat":
                "Gujarat / Arabian Sea"
        }

        database_region = region_map.get(
            state,
            state
        )

        # ----------------------------------------------------
        # DATABASE CONNECTION
        # ----------------------------------------------------

        connection = get_connection()

        cursor = connection.cursor()

        # ----------------------------------------------------
        # GET FORECAST DATA
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT
                forecast_time,
                wind_speed_ms,
                wave_height_m,
                source
            FROM wind_forecast
            WHERE LOWER(region) = LOWER(%s)
            ORDER BY forecast_time DESC
            LIMIT 50
            """,
            (database_region,)
        )

        rows = cursor.fetchall()

        # ----------------------------------------------------
        # FORMAT RESPONSE
        # ----------------------------------------------------

        data = []

        for row in rows:

            data.append(
                {
                    "forecast_time":
                        row[0].isoformat()
                        if row[0]
                        else None,

                    "wind_speed_ms":
                        row[1],

                    "wave_height_m":
                        row[2],

                    "source":
                        row[3]
                }
            )

        # ----------------------------------------------------
        # CLOSE DATABASE
        # ----------------------------------------------------

        cursor.close()
        connection.close()

        # ----------------------------------------------------
        # RESPONSE
        # ----------------------------------------------------

        return {

            "status": "SUCCESS",

            "state": state,

            "region": database_region,

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

            "message":
                "Forecast history could not be loaded."
        }