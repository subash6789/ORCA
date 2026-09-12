from db_connection import get_connection


def ocean_agent():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            data_time,
            region,
            sst_c,
            ssh_m,
            salinity,
            current_speed_ms,
            mld_m
        FROM ocean_observation
        ORDER BY id DESC
        LIMIT 1
    """)

    row = cursor.fetchone()

    cursor.close()
    conn.close()

    if row is None:
        return {
            "status": "NO_DATA",
            "message": "No ocean data is available."
        }

    data_time, region, sst, ssh, salinity, current_speed, mld = row

    return {
        "agent": "Ocean Agent",
        "status": "SUCCESS",
        "time": str(data_time),
        "region": region,
        "sea_surface_temperature_c": round(sst, 2),
        "sea_surface_height_m": round(ssh, 3),
        "salinity": round(salinity, 2),
        "current_speed_ms": round(current_speed, 3),
        "mixed_layer_depth_m": round(mld, 2)
    }


if __name__ == "__main__":
    result = ocean_agent()

    print("===== ORCA OCEAN AGENT =====")

    for key, value in result.items():
        print(f"{key}: {value}")