import os
from datetime import datetime

import numpy as np
import xarray as xr

from db_connection import get_connection


SATELLITE_FILE = r"C:\ORCA_ALL_FILES\backend\mosdac_downloads\E06OCML3CQ_20260925_01km_LAC_v1.0.0.nc"


REGIONS = {
    "Tamil Nadu": {
        "lat_min": 8.0,
        "lat_max": 14.0,
        "lon_min": 76.0,
        "lon_max": 81.0,
    },
    "Kerala": {
        "lat_min": 8.0,
        "lat_max": 13.0,
        "lon_min": 74.5,
        "lon_max": 77.5,
    },
    "Karnataka": {
        "lat_min": 11.5,
        "lat_max": 18.5,
        "lon_min": 74.0,
        "lon_max": 78.5,
    },
    "Gujarat": {
        "lat_min": 20.0,
        "lat_max": 24.5,
        "lon_min": 68.0,
        "lon_max": 74.5,
    },
}


def create_satellite_table():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS satellite_observation (
            id SERIAL PRIMARY KEY,
            observation_time TIMESTAMP,
            state VARCHAR(100) NOT NULL,
            product_id VARCHAR(100) NOT NULL,
            variable VARCHAR(100),
            value DOUBLE PRECISION,
            valid_pixels INTEGER,
            source VARCHAR(200),
            data_status VARCHAR(50),
            retrieved_at TIMESTAMP NOT NULL,
            UNIQUE (
                observation_time,
                state,
                product_id,
                variable
            )
        )
    """)

    conn.commit()
    cur.close()
    conn.close()


def find_lat_lon_names(ds):
    lat_name = None
    lon_name = None

    for name in ds.coords:
        low = name.lower()

        if lat_name is None and ("lat" in low or "latitude" in low):
            lat_name = name

        if lon_name is None and ("lon" in low or "longitude" in low):
            lon_name = name

    return lat_name, lon_name


def find_chlorophyll_variable(ds):
    candidates = []

    for name in ds.data_vars:
        low = name.lower()

        if (
            "chl" in low
            or "chlorophyll" in low
            or "chlor_a" in low
        ):
            candidates.append(name)

    return candidates[0] if candidates else None


def extract_region_data(ds, variable_name, state):
    region = REGIONS[state]

    lat_name, lon_name = find_lat_lon_names(ds)

    if not lat_name or not lon_name:
        raise Exception(
            "Latitude/longitude coordinates were not found in the EOS-06 file."
        )

    da = ds[variable_name]

    lat = ds[lat_name]
    lon = ds[lon_name]

    mask = (
        (lat >= region["lat_min"])
        & (lat <= region["lat_max"])
        & (lon >= region["lon_min"])
        & (lon <= region["lon_max"])
    )

    values = da.where(mask)

    values_np = np.asarray(values.values, dtype=float)

    valid = values_np[np.isfinite(values_np)]

    if valid.size == 0:
        return None

    return {
        "state": state,
        "value": float(np.nanmedian(valid)),
        "valid_pixels": int(valid.size),
    }


def collect_satellite_data():
    if not os.path.exists(SATELLITE_FILE):
        print("EOS-06 file is not available yet.")
        print(f"Expected file: {SATELLITE_FILE}")
        return []

    print("Opening real EOS-06 satellite product...")
    print(SATELLITE_FILE)

    ds = xr.open_dataset(SATELLITE_FILE)

    print("\n===== EOS-06 DATASET =====")
    print(ds)

    variable_name = find_chlorophyll_variable(ds)

    if variable_name is None:
        print("\nNo chlorophyll variable was found.")
        print("No satellite values will be invented.")
        ds.close()
        return []

    print(f"\nSatellite variable selected: {variable_name}")

    results = []

    for state in REGIONS:

        try:
            result = extract_region_data(
                ds,
                variable_name,
                state
            )

            if result is None:
                print(f"{state}: No valid satellite pixels.")
                continue

            result["product_id"] = "E06OCM_L3_LAC_CQ"
            result["variable"] = variable_name
            result["source"] = "MOSDAC / ISRO EOS-06"
            result["data_status"] = "OBSERVED"
            result["retrieved_at"] = datetime.now()

            results.append(result)

            print(
                f"{state}: "
                f"value={result['value']}, "
                f"valid_pixels={result['valid_pixels']}"
            )

        except Exception as error:
            print(f"{state}: ERROR - {error}")

    ds.close()

    return results


def save_satellite_data(results):
    if not results:
        print("No satellite observations to save.")
        return

    conn = get_connection()
    cur = conn.cursor()

    for item in results:

        cur.execute(
            """
            INSERT INTO satellite_observation (
                observation_time,
                state,
                product_id,
                variable,
                value,
                valid_pixels,
                source,
                data_status,
                retrieved_at
            )
            VALUES (
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s
            )
            ON CONFLICT (
                observation_time,
                state,
                product_id,
                variable
            )
            DO UPDATE SET
                value = EXCLUDED.value,
                valid_pixels = EXCLUDED.valid_pixels,
                retrieved_at = EXCLUDED.retrieved_at
            """,
            (
                None,
                item["state"],
                item["product_id"],
                item["variable"],
                item["value"],
                item["valid_pixels"],
                item["source"],
                item["data_status"],
                item["retrieved_at"],
            )
        )

    conn.commit()

    cur.close()
    conn.close()

    print(
        f"\nSaved {len(results)} real satellite observations to PostgreSQL."
    )


if __name__ == "__main__":

    print("===== ORCA EOS-06 SATELLITE COLLECTOR =====")

    create_satellite_table()

    results = collect_satellite_data()

    save_satellite_data(results)