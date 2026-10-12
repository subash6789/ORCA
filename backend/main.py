from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pathlib import Path
import asyncio
import json
import logging


# ============================================================
# ORCA AGENTS
# ============================================================

from auto_update import automatic_update_loop

from ocean_agent import ocean_agent
from weather_agent import weather_agent
from gis_agent import gis_agent
from pfz_agent import pfz_agent
from safety_agent import safety_agent
from satellite_agent import satellite_agent
from language_agent import language_agent


# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

logger = logging.getLogger("ORCA")


# ============================================================
# LOCATION VALIDATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

DISTRICT_GEOJSON = (
    BASE_DIR
    / "data"
    / "district_boundary_extracted"
    / "district_nwic.GeoJSON"
)


SUPPORTED_STATES = {
    "Tamil Nadu",
    "Kerala",
    "Karnataka",
    "Gujarat"
}


# Common user/frontend names -> official GeoJSON names
DISTRICT_ALIASES = {

    # Karnataka
    "bagalkot": "Bagalkote",
    "bagalkote": "Bagalkote",
    "ballari": "Ballari",
    "bellary": "Ballari",
    "belagavi": "Belagavi",
    "belgaum": "Belagavi",
    "bengaluru rural": "Bengaluru Rural",
    "bangalore rural": "Bengaluru Rural",
    "bengaluru urban": "Bengaluru Urban",
    "bangalore urban": "Bengaluru Urban",
    "bangalore": "Bengaluru Urban",
    "bengaluru": "Bengaluru Urban",
    "bidar": "Bidar",
    "chamarajanagar": "Chamarajanagara",
    "chamarajanagara": "Chamarajanagara",
    "chikkaballapur": "Chikkaballapura",
    "chikkaballapura": "Chikkaballapura",
    "chikkamagaluru": "Chikkamagaluru",
    "chikmagalur": "Chikkamagaluru",
    "chikkamagalur": "Chikkamagaluru",
    "chitradurga": "Chitradurga",
    "dakshina kannada": "Dakshina Kannada",
    "south canara": "Dakshina Kannada",
    "mangaluru": "Dakshina Kannada",
    "mangalore": "Dakshina Kannada",
    "davangere": "Davangere",
    "davanagere": "Davangere",
    "dharwad": "Dharwad",
    "gadag": "Gadag",
    "hassan": "Hassan",
    "haveri": "Haveri",
    "kalaburagi": "Kalaburagi",
    "gulbarga": "Kalaburagi",
    "kodagu": "Kodagu",
    "coorg": "Kodagu",
    "kolar": "Kolar",
    "koppal": "Koppal",
    "mandya": "Mandya",
    "mysuru": "Mysuru",
    "mysore": "Mysuru",
    "raichur": "Raichur",
    "ramanagara": "Ramanagara",
    "shivamogga": "Shivamogga",
    "shimoga": "Shivamogga",
    "tumakuru": "Tumakuru",
    "tumkur": "Tumakuru",
    "udupi": "Udupi",
    "uttara kannada": "Uttara Kannada",
    "north canara": "Uttara Kannada",
    "karwar": "Uttara Kannada",
    "vijayapura": "Vijayapura",
    "bijapur": "Vijayapura",
    "yadgir": "Yadgir",

    # Gujarat
    "ahmedabad": "Ahmadabad",
    "ahmadabad": "Ahmadabad",
    "aravalli": "Arvalli",
    "arvalli": "Arvalli",
    "banaskantha": "Banas Kantha",
    "banas kantha": "Banas Kantha",
    "banaaskantha": "Banas Kantha",
    "baroda": "Vadodara",
    "vadodara": "Vadodara",
    "chhota udepur": "Chhotaudepur",
    "chhotaudepur": "Chhotaudepur",
    "chhota udaipur": "Chhotaudepur",
    "chhota-udepur": "Chhotaudepur",
    "dang": "Dang",
    "dangs": "Dang",
    "the dang": "Dang",
    "the dangs": "Dang",
    "dahod": "Dohad",
    "dohad": "Dohad",
    "devbhoomi dwarka": "Devbhumi Dwarka",
    "devbhumi dwarka": "Devbhumi Dwarka",
    "dwarka": "Devbhumi Dwarka",
    "kutch": "Kachchh",
    "kutchh": "Kachchh",
    "kachchh": "Kachchh",
    "mehsana": "Mahesana",
    "mahesana": "Mahesana",
    "panchmahal": "Panch Mahals",
    "panch mahals": "Panch Mahals",
    "sabarkantha": "Sabar Kantha",
    "sabar kantha": "Sabar Kantha",

    # Kerala aliases
    "calicut": "Kozhikode",
    "kozhikode": "Kozhikode",
    "cochin": "Ernakulam",
    "kochi": "Ernakulam",
    "ernakulam": "Ernakulam",
    "trivandrum": "Thiruvananthapuram",
    "thiruvananthapuram": "Thiruvananthapuram",
    "alleppey": "Alappuzha",
    "alappuzha": "Alappuzha",
    "palghat": "Palakkad",
    "palakkad": "Palakkad",
    "quilon": "Kollam",
    "kollam": "Kollam",
    "trichur": "Thrissur",
    "thrissur": "Thrissur",
    "cannanore": "Kannur",
    "kannur": "Kannur",
    "kasargod": "Kasaragod",
    "kasaragod": "Kasaragod",
    "wynad": "Wayanad",
    "wayanad": "Wayanad",

    # Tamil Nadu common spellings
    "chennai": "Chennai",
    "madras": "Chennai",
    "kancheepuram": "Kanchipuram",
    "kanchipuram": "Kanchipuram",
    "kanniyakumari": "Kanniyakumari",
    "kanyakumari": "Kanniyakumari",
    "madura": "Madurai",
    "madurai": "Madurai",
    "nilgiris": "The Nilgiris",
    "the nilgiris": "The Nilgiris",
    "tanjore": "Thanjavur",
    "thanjavur": "Thanjavur",
    "tiruvallur": "Thiruvallur",
    "thiruvallur": "Thiruvallur",
    "tiruvarur": "Thiruvarur",
    "thiruvarur": "Thiruvarur",
    "thoothukudi": "Tuticorin",
    "tuticorin": "Tuticorin",
    "trichy": "Tiruchirappalli",
    "tiruchy": "Tiruchirappalli",
    "tiruchirapalli": "Tiruchirappalli",
    "tiruchirappalli": "Tiruchirappalli",
    "tinnevelly": "Tirunelveli",
    "tirunelveli": "Tirunelveli",
    "tirunelveli kattabo": "Tirunelveli",
    "tirunelveli kattabomman": "Tirunelveli",
    "viluppuram": "Villupuram",
    "villupuram": "Villupuram",

}


def load_orca_districts():
    """
    Load supported state/district combinations from
    the official district GeoJSON used by ORCA, or fall back to
    district_canonical_coords.json if the 100MB GeoJSON is not bundled in git.
    """

    if DISTRICT_GEOJSON.exists():
        try:
            with open(
                DISTRICT_GEOJSON,
                "r",
                encoding="utf-8"
            ) as file:
                geojson = json.load(file)

            districts = {}
            for feature in geojson.get("features", []):
                properties = feature.get(
                    "properties",
                    {}
                )
                state_name = properties.get(
                    "state_name"
                )
                district_name = properties.get(
                    "district"
                )
                if (
                    state_name in SUPPORTED_STATES
                    and district_name
                ):
                    districts.setdefault(
                        state_name,
                        set()
                    ).add(
                        district_name
                    )

            logger.info(
                "Loaded district validation data from GeoJSON for %d states.",
                len(districts)
            )
            return districts
        except Exception as error:
            logger.exception(
                "Failed to load district GeoJSON: %s",
                error
            )

    # Fallback to district_canonical_coords.json
    coords_json = BASE_DIR / "district_canonical_coords.json"
    if coords_json.exists():
        try:
            with open(coords_json, "r", encoding="utf-8") as f:
                coords_data = json.load(f)
            districts = {
                state: set(d_dict.keys())
                for state, d_dict in coords_data.items()
                if state in SUPPORTED_STATES
            }
            logger.info(
                "Loaded district validation data from coords JSON fallback for %d states.",
                len(districts)
            )
            return districts
        except Exception as error:
            logger.exception(
                "Failed to load district_canonical_coords.json: %s",
                error
            )

    logger.warning("District validation datasets not found.")
    return {}


ORCA_DISTRICTS = load_orca_districts()


def normalize_district_name(district):
    """
    Normalize spaces and common district aliases.
    """

    if district is None:
        return None

    cleaned = " ".join(
        str(district)
        .strip()
        .split()
    )

    alias = DISTRICT_ALIASES.get(
        cleaned.lower()
    )

    if alias:
        return alias

    return cleaned


def validate_state(state):
    """
    Validate state and return canonical state name.
    """

    if state is None:
        raise HTTPException(
            status_code=400,
            detail="State is required."
        )

    state_clean = " ".join(
        str(state)
        .strip()
        .split()
    )

    matched_state = next(
        (
            supported
            for supported in SUPPORTED_STATES
            if supported.lower() == state_clean.lower()
        ),
        None
    )

    if matched_state is None:

        raise HTTPException(
            status_code=400,
            detail={
                "error": "INVALID_STATE",
                "message": (
                    f"Invalid state: {state}."
                ),
                "supported_states": sorted(
                    SUPPORTED_STATES
                )
            }
        )

    return matched_state


def validate_location(
    state,
    district=None
):
    """
    Validate state and optional district.

    Returns:
        canonical_state,
        canonical_district
    """

    matched_state = validate_state(state)

    # District is optional for state-level endpoints
    if (
        district is None
        or str(district).strip() == ""
    ):
        return matched_state, None

    district_clean = normalize_district_name(
        district
    )

    valid_districts = ORCA_DISTRICTS.get(
        matched_state,
        set()
    )

    # If GeoJSON is unavailable, do not silently
    # accept an unknown district.
    if not valid_districts:

        raise HTTPException(
            status_code=503,
            detail={
                "error": "DISTRICT_DATA_UNAVAILABLE",
                "message": (
                    "District validation data is unavailable."
                ),
                "state": matched_state
            }
        )

    matched_district = next(
        (
            valid
            for valid in valid_districts
            if valid.lower() == district_clean.lower()
        ),
        None
    )

    # Secondary fuzzy / alphanumeric stem match (e.g. Bagalkot <-> Bagalkote)
    if matched_district is None:
        import re
        clean_tok = lambda s: re.sub(r"[^a-z0-9]", "", str(s).lower())
        d_norm = clean_tok(district_clean)
        d_nothe = clean_tok(re.sub(r"^(the\s+)", "", district_clean.lower()))

        for valid in valid_districts:
            v_norm = clean_tok(valid)
            v_nothe = clean_tok(re.sub(r"^(the\s+)", "", valid.lower()))
            if v_norm == d_norm or v_nothe == d_nothe:
                matched_district = valid
                break

        if matched_district is None and len(d_norm) >= 4:
            for valid in valid_districts:
                v_norm = clean_tok(valid)
                if len(v_norm) >= 4 and (v_norm.startswith(d_norm) or d_norm.startswith(v_norm)):
                    matched_district = valid
                    break

    if matched_district is None:

        raise HTTPException(
            status_code=400,
            detail={
                "error": "INVALID_DISTRICT",
                "message": (
                    f"Invalid district '{district}' "
                    f"for state '{matched_state}'."
                ),
                "state": matched_state,
                "district": district,
                "supported_district_count": len(
                    valid_districts
                )
            }
        )

    return matched_state, matched_district


# ============================================================
# DATABASE SCHEMA MIGRATION
# ============================================================

def ensure_database_schema():
    """
    Ensure all required tables and columns exist in PostgreSQL.
    Safely and idempotently adds missing columns (e.g. source, data_status)
    without modifying existing schemas or dropping data.
    """
    try:
        from db_connection import get_connection
        conn = get_connection()
        cur = conn.cursor()

        # 1. Ensure columns exist on ocean_observation
        cur.execute("""
            CREATE TABLE IF NOT EXISTS public.ocean_observation (
                id SERIAL PRIMARY KEY,
                data_time TIMESTAMP,
                region VARCHAR(100),
                sst_c DOUBLE PRECISION,
                ssh_m DOUBLE PRECISION,
                salinity DOUBLE PRECISION,
                current_speed_ms DOUBLE PRECISION,
                mld_m DOUBLE PRECISION,
                retrieved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                wind_speed_ms DOUBLE PRECISION,
                wave_height_m DOUBLE PRECISION,
                source TEXT,
                data_status TEXT,
                latitude DOUBLE PRECISION,
                longitude DOUBLE PRECISION
            );
        """)

        # Add any missing columns to ocean_observation idempotently
        ocean_cols = [
            ("source", "TEXT"),
            ("data_status", "TEXT"),
            ("latitude", "DOUBLE PRECISION"),
            ("longitude", "DOUBLE PRECISION"),
            ("wind_speed_ms", "DOUBLE PRECISION"),
            ("wave_height_m", "DOUBLE PRECISION"),
            ("retrieved_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
        ]
        for col_name, col_type in ocean_cols:
            cur.execute(f"""
                ALTER TABLE public.ocean_observation
                ADD COLUMN IF NOT EXISTS {col_name} {col_type};
            """)

        conn.commit()
        cur.close()
        conn.close()
        logger.info("[ORCA] Database schema verified and updated successfully.")
    except Exception as e:
        logger.warning(f"[ORCA] Database schema check encountered notice/warning: {e}")


# ============================================================
# AUTOMATIC UPDATE LIFESPAN
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):

    ensure_database_schema()

    update_task = asyncio.create_task(
        automatic_update_loop()
    )

    logger.info(
        "[ORCA] Automatic update service started."
    )

    try:

        yield

    finally:

        update_task.cancel()

        try:

            await update_task

        except asyncio.CancelledError:

            pass

        logger.info(
            "[ORCA] Automatic update service stopped."
        )


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="ORCA Real Marine Assistant",
    description=(
        "ORCA - Marine Ecosystem Reasoning "
        "with Collaborative Agents"
    ),
    version="1.0.0",
    lifespan=lifespan
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,

    allow_origins=["*"],

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
        "project": (
            "ORCA - Marine EcoSystem Reasoning "
            "with Collaborative Agents"
        )
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
# LOCATION INFORMATION
# ============================================================

@app.get("/locations")
def locations():

    return {
        "status": "SUCCESS",
        "states": sorted(
            SUPPORTED_STATES
        ),
        "districts": {
            state: sorted(
                districts
            )
            for state, districts
            in ORCA_DISTRICTS.items()
        }
    }


# ============================================================
# OCEAN
# ============================================================

@app.get("/ocean")
def ocean(
    state: str = "Tamil Nadu",
    district: str = None
):

    state, district = validate_location(
        state,
        district
    )

    return ocean_agent(
        state,
        district
    )


# ============================================================
# WEATHER
# ============================================================

@app.get("/weather")
def weather(
    state: str = "Tamil Nadu",
    district: str = None
):

    state, district = validate_location(
        state,
        district
    )

    return weather_agent(
        state,
        district
    )


# ============================================================
# GIS
# ============================================================

@app.get("/gis")
def gis(
    state: str = "Tamil Nadu",
    district: str = None
):

    state, district = validate_location(
        state,
        district
    )

    return gis_agent(
        state,
        district
    )


# ============================================================
# PFZ
# ============================================================

@app.get("/pfz")
def pfz(
    state: str = "Tamil Nadu",
    district: str = None
):

    state, district = validate_location(
        state,
        district
    )

    return pfz_agent(
        state,
        district
    )


# ============================================================
# MARINE SAFETY
# ============================================================

@app.get("/safety")
def safety(
    state: str = "Tamil Nadu",
    district: str = None
):

    state, district = validate_location(
        state,
        district
    )

    return safety_agent(
        state,
        district
    )


# ============================================================
# SATELLITE
# ============================================================

@app.get("/satellite")
def satellite(
    state: str = "Tamil Nadu",
    district: str = None
):

    state, district = validate_location(
        state,
        district
    )

    return satellite_agent(
        state,
        district
    )


# ============================================================
# LANGUAGE
# ============================================================

@app.get("/language")
def language(
    question: str = ""
):

    return language_agent(
        question
    )


# ============================================================
# REASONING
# ============================================================

@app.get("/reasoning")
def reasoning(
    question: str = "What are the marine conditions?",
    state: str = "Tamil Nadu",
    district: str = None
):

    # --------------------------------------------------------
    # Validate location BEFORE running any agents
    # --------------------------------------------------------

    state, district = validate_location(
        state,
        district
    )

    logger.info(
        "[ORCA] Reasoning request | state=%s | district=%s",
        state,
        district
    )

    try:

        from orca_reasoning import orca_reasoning

        result = orca_reasoning(
            question,
            state,
            district
        )

        # Make sure canonical validated location
        # is returned to the frontend.

        result["state"] = state
        result["district"] = district

        return result

    except HTTPException:

        raise

    except Exception as error:

        logger.exception(
            "[ORCA] Reasoning error"
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "ORCA reasoning service encountered "
                "an internal error."
            )
        )


# ============================================================
# ASK
# ============================================================

@app.get("/ask")
def ask(
    question: str,
    state: str = "Tamil Nadu",
    district: str = None
):

    # Validate here too so /ask behaves consistently.

    state, district = validate_location(
        state,
        district
    )

    return reasoning(
        question=question,
        state=state,
        district=district
    )


# ============================================================
# FORECAST HISTORY
# ============================================================

@app.get("/forecast-history")
def forecast_history(
    state: str = "Tamil Nadu"
):

    state = validate_state(
        state
    )

    try:

        from db_connection import get_connection

        connection = get_connection()

        cursor = connection.cursor()

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
            (state,)
        )

        rows = cursor.fetchall()

        cursor.close()
        connection.close()

        data = []

        for row in rows:

            data.append(
                {
                    "forecast_time": (
                        row[0].isoformat()
                        if hasattr(
                            row[0],
                            "isoformat"
                        )
                        else row[0]
                    ),

                    "wind_speed_ms": row[1],

                    "wave_height_m": row[2],

                    "source": row[3]
                }
            )

        return {
            "status": "SUCCESS",
            "state": state,
            "count": len(data),
            "data": data
        }

    except Exception as error:

        logger.exception(
            "[ORCA] Forecast history error"
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Forecast history could not be loaded."
            )
        )


# ============================================================
# GLOBAL EXCEPTION HANDLER
# ============================================================

@app.exception_handler(Exception)
async def global_exception_handler(
    request,
    exc
):

    logger.exception(
        "[ORCA] Unhandled exception: %s",
        exc
    )

    return {
        "status": "ERROR",
        "message": (
            "ORCA backend encountered an internal error."
        )
    }