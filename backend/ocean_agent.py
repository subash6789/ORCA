import math

from db_connection import get_connection


REGION_MAP = {
    "Tamil Nadu": "Tamil Nadu",
    "Kerala": "Kerala",
    "Karnataka": "Karnataka",
    "Gujarat": "Gujarat",
}

CHLOROPHYLL_REGION_MAP = {
    "Tamil Nadu": "Tamil Nadu / Bay of Bengal",
    "Kerala": "Kerala / Arabian Sea",
    "Karnataka": "Karnataka / Arabian Sea",
    "Gujarat": "Gujarat / Arabian Sea",
}

WIND_WAVE_REGION_MAP = {
    "Tamil Nadu": "Tamil Nadu / Bay of Bengal",
    "Kerala": "Kerala / Arabian Sea",
    "Karnataka": "Karnataka / Arabian Sea",
    "Gujarat": "Gujarat / Arabian Sea",
}


def clean_number(value):
    if value is None:
        return None

    try:
        value = float(value)
    except (TypeError, ValueError):
        return None

    if not math.isfinite(value):
        return None

    return value


def get_ocean_observation(region):
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            """
            SELECT
                data_time,
                retrieved_at,
                source,
                data_status,
                latitude,
                longitude,
                sst_c,
                ssh_m,
                salinity,
                current_speed_ms,
                mld_m,
                wind_speed_ms,
                wave_height_m
            FROM public.ocean_observation
            WHERE region = %s
              AND data_status = 'FORECAST'
              AND source IS NOT NULL
              AND sst_c IS NOT NULL
            ORDER BY data_time DESC
            LIMIT 1
            """,
            (region,),
        )

        row = cur.fetchone()

        if row is None:
            return None

        return {
            "observation_time": row[0],
            "retrieved_at": row[1],
            "source": row[2],
            "data_status": row[3],
            "latitude": clean_number(row[4]),
            "longitude": clean_number(row[5]),
            "sea_surface_temperature_c": clean_number(row[6]),
            "sea_surface_height_m": clean_number(row[7]),
            "salinity": clean_number(row[8]),
            "current_speed_ms": clean_number(row[9]),
            "mixed_layer_depth_m": clean_number(row[10]),
            "wind_speed_ms": clean_number(row[11]),
            "wave_height_m": clean_number(row[12]),
        }

    finally:
        cur.close()
        conn.close()


def get_wind_wave_forecast(region):
    lookup_region = WIND_WAVE_REGION_MAP.get(region, region)

    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            """
            SELECT
                forecast_time,
                wind_speed_ms,
                wave_height_m,
                source,
                retrieved_at
            FROM public.wind_forecast
            WHERE region = %s
              AND (wind_speed_ms IS NOT NULL OR wave_height_m IS NOT NULL)
            ORDER BY forecast_time DESC
            LIMIT 1
            """,
            (lookup_region,),
        )

        row = cur.fetchone()

        if row is None:
            return None

        return {
            "forecast_time": row[0],
            "wind_speed_ms": clean_number(row[1]),
            "wave_height_m": clean_number(row[2]),
            "source": row[3],
            "retrieved_at": row[4],
        }

    finally:
        cur.close()
        conn.close()


def get_chlorophyll(region):
    lookup_region = CHLOROPHYLL_REGION_MAP.get(region, region)

    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            """
            SELECT
                source,
                data_status,
                observation_time,
                retrieved_at,
                chlorophyll_mg_m3,
                valid_pixels,
                minimum_mg_m3,
                maximum_mg_m3,
                median_mg_m3
            FROM public.chlorophyll_observation
            WHERE region = %s
            ORDER BY observation_time DESC
            LIMIT 1
            """,
            (lookup_region,),
        )

        row = cur.fetchone()

        if row is None:
            return None

        return {
            "source": row[0],
            "data_status": row[1],
            "observation_time": row[2],
            "retrieved_at": row[3],
            "chlorophyll_mg_m3": clean_number(row[4]),
            "valid_pixels": row[5],
            "minimum_mg_m3": clean_number(row[6]),
            "maximum_mg_m3": clean_number(row[7]),
            "median_mg_m3": clean_number(row[8]),
        }

    finally:
        cur.close()
        conn.close()


def ocean_agent(state="Tamil Nadu", district=""):
    try:
        state = str(state or "").strip()
        district = str(district or "").strip()

        if state not in REGION_MAP:
            return {
                "agent": "Ocean Agent",
                "status": "NO_DATA",
                "data_status": "NO_DATA",
                "state": state,
                "district": district,
                "message": "Unsupported state.",
            }

        region = REGION_MAP[state]

        observation = get_ocean_observation(region)

        if observation is None:
            return {
                "agent": "Ocean Agent",
                "status": "NO_DATA",
                "data_status": "NO_DATA",
                "state": state,
                "district": district,
                "region": region,
                "message": "No valid ocean forecast observation is currently available.",
            }

        chlorophyll = get_chlorophyll(state)
        wind_wave = get_wind_wave_forecast(state)

        # Safe fallback to validated satellite composite if database has no regional row
        if chlorophyll is None:
            try:
                from satellite_agent import satellite_agent
                sat_res = satellite_agent(state=state, district=district)
                if sat_res and sat_res.get("status") == "SUCCESS" and sat_res.get("chlorophyll_a_mg_m3") is not None:
                    chlorophyll = {
                        "source": sat_res.get("source") or "NASA Ocean Biology / MODIS Aqua",
                        "data_status": sat_res.get("data_status") or "REAL_SATELLITE_DATA",
                        "observation_time": sat_res.get("observation_time"),
                        "retrieved_at": sat_res.get("retrieved_at"),
                        "chlorophyll_mg_m3": sat_res.get("chlorophyll_a_mg_m3"),
                        "valid_pixels": sat_res.get("valid_pixels"),
                        "minimum_mg_m3": None,
                        "maximum_mg_m3": None,
                        "median_mg_m3": None,
                    }
            except Exception:
                pass

        # Use observation's wind/wave if already present, otherwise fall back to WW3 forecast
        eff_wind_speed = observation["wind_speed_ms"]
        eff_wave_height = observation["wave_height_m"]

        if eff_wind_speed is None and wind_wave and wind_wave["wind_speed_ms"] is not None:
            eff_wind_speed = wind_wave["wind_speed_ms"]

        if eff_wave_height is None and wind_wave and wind_wave["wave_height_m"] is not None:
            eff_wave_height = wind_wave["wave_height_m"]

        result = {
            "agent": "Ocean Agent",
            "status": "SUCCESS",
            "data_status": observation["data_status"],
            "state": state,
            "district": district,
            "region": region,
            "selected_area": {
                "state": state,
                "district": district,
                "marine_region": region,
                "data_scope": "MARINE_REGION",
            },
            "observation_time": observation["observation_time"],
            "retrieved_at": observation["retrieved_at"],
            "source": observation["source"],
            "latitude": observation["latitude"],
            "longitude": observation["longitude"],
            "sea_surface_temperature_c": observation["sea_surface_temperature_c"],
            "sea_surface_height_m": observation["sea_surface_height_m"],
            "salinity": observation["salinity"],
            "current_speed_ms": observation["current_speed_ms"],
            "mixed_layer_depth_m": observation["mixed_layer_depth_m"],
            "wind_speed_ms": eff_wind_speed,
            "wave_height_m": eff_wave_height,
            "wind_wave_source": wind_wave["source"] if wind_wave else None,
            "wind_wave_forecast_time": wind_wave["forecast_time"] if wind_wave else None,
            "wind_wave_retrieved_at": wind_wave["retrieved_at"] if wind_wave else None,
            "chlorophyll": (
                chlorophyll["chlorophyll_mg_m3"]
                if chlorophyll
                else None
            ),
        }

        if chlorophyll:
            result["chlorophyll_source"] = chlorophyll["source"]
            result["chlorophyll_status"] = chlorophyll["data_status"]
            result["chlorophyll_observation_time"] = chlorophyll["observation_time"]
            result["chlorophyll_retrieved_at"] = chlorophyll["retrieved_at"]
            result["chlorophyll_valid_pixels"] = chlorophyll["valid_pixels"]
            result["chlorophyll_minimum_mg_m3"] = chlorophyll["minimum_mg_m3"]
            result["chlorophyll_maximum_mg_m3"] = chlorophyll["maximum_mg_m3"]
            result["chlorophyll_median_mg_m3"] = chlorophyll["median_mg_m3"]
        else:
            result["chlorophyll_source"] = None
            result["chlorophyll_status"] = "NO_DATA"
            result["chlorophyll_observation_time"] = None
            result["chlorophyll_retrieved_at"] = None
            result["chlorophyll_valid_pixels"] = None
            result["chlorophyll_minimum_mg_m3"] = None
            result["chlorophyll_maximum_mg_m3"] = None
            result["chlorophyll_median_mg_m3"] = None

        return result

    except Exception as exc:
        return {
            "agent": "Ocean Agent",
            "status": "ERROR",
            "data_status": "ERROR",
            "state": state,
            "district": district,
            "error": str(exc),
        }


if __name__ == "__main__":
    import json

    print(
        json.dumps(
            ocean_agent("Tamil Nadu", "Chennai"),
            indent=2,
            default=str,
        )
    )
