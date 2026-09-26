from db_connection import get_connection


def ocean_agent(state="Tamil Nadu"):

    region_map = {
        "Tamil Nadu": "Tamil Nadu / Bay of Bengal",
        "Kerala": "Kerala / Arabian Sea",
        "Karnataka": "Karnataka / Arabian Sea",
        "Gujarat": "Gujarat / Arabian Sea"
    }

    if state not in region_map:
        return {
            "agent": "Ocean Agent",
            "status": "ERROR",
            "data_status": "UNAVAILABLE",
            "state": state,
            "message": "Unsupported region"
        }

    region = region_map[state]

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            data_time,
            retrieved_at,
            region,
            sst_c,
            ssh_m,
            salinity,
            current_speed_ms,
            mld_m
        FROM ocean_observation
        WHERE region = %s
        ORDER BY data_time DESC, id DESC
        LIMIT 1
    """, (region,))

    row = cursor.fetchone()

    cursor.close()
    conn.close()

    if not row:
        return {
            "agent": "Ocean Agent",
            "status": "UNAVAILABLE",
            "data_status": "UNAVAILABLE",
            "state": state,
            "region": region,
            "message": "No ocean observation available"
        }

    (
        data_time,
        retrieved_at,
        db_region,
        sst,
        ssh,
        salinity,
        current_speed,
        mld
    ) = row

    return {
        "agent": "Ocean Agent",
        "status": "SUCCESS",
        "data_status": "OBSERVED",

        "state": state,
        "region": db_region,

        "observation_time": str(data_time),
        "retrieved_at": str(retrieved_at),

        "sea_surface_temperature_c": round(sst, 2),
        "sea_surface_height_m": round(ssh, 3),
        "salinity": round(salinity, 2),
        "current_speed_ms": round(current_speed, 3),
        "mixed_layer_depth_m": round(mld, 2)
    }