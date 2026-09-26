import os
import numpy as np
import xarray as xr
from datetime import datetime

from db_connection import get_connection


# =========================================================
# REAL OCEAN DATA FILE
# =========================================================

FILE_PATH = r"C:\Users\Acer\ORCA\data\ocean_data\latest_ocean.nc"


# =========================================================
# FOUR SUPPORTED ORCA REGIONS
# Representative valid coastal/ocean grid locations
# =========================================================

REGIONS = {
    "Tamil Nadu": {
        "region": "Tamil Nadu / Bay of Bengal",
        "lat": 11.0312,
        "lon": 80.0000
    },

    "Kerala": {
        "region": "Kerala / Arabian Sea",
        "lat": 10.0000,
        "lon": 76.0000
    },

    "Karnataka": {
        "region": "Karnataka / Arabian Sea",
        "lat": 14.5000,
        "lon": 74.0000
    },

    "Gujarat": {
        "region": "Gujarat / Arabian Sea",
        "lat": 21.5000,
        "lon": 69.5000
    }
}


# =========================================================
# CHECK WHETHER A VALUE IS VALID
# =========================================================

def is_valid(value):

    try:
        return np.isfinite(float(value))

    except (TypeError, ValueError):

        return False


# =========================================================
# GET LATEST VALID OBSERVATION
# =========================================================

def get_latest_valid_observation(
    ds,
    latitude,
    longitude
):

    # Select nearest NetCDF grid point.
    # This does NOT calculate a fake state average.

    point = ds.sel(
        LAT=latitude,
        LON=longitude,
        method="nearest"
    )

    # Surface layer

    temp_surface = point["TEMP"].sel(
        DEPTH=0,
        method="nearest"
    )

    salinity_surface = point["SALN"].sel(
        DEPTH=0,
        method="nearest"
    )

    u_surface = point["UVEL"].sel(
        DEPTH=0,
        method="nearest"
    )

    v_surface = point["VVEL"].sel(
        DEPTH=0,
        method="nearest"
    )

    ssh = point["SSH"]

    mld = point["MLD"]

    # Search from newest observation backwards.

    for time_index in range(
        len(ds["TIME"]) - 1,
        -1,
        -1
    ):

        data_time = ds["TIME"].isel(
            TIME=time_index
        ).values

        sst_value = temp_surface.isel(
            TIME=time_index
        ).values

        salinity_value = salinity_surface.isel(
            TIME=time_index
        ).values

        u_value = u_surface.isel(
            TIME=time_index
        ).values

        v_value = v_surface.isel(
            TIME=time_index
        ).values

        ssh_value = ssh.isel(
            TIME=time_index
        ).values

        mld_value = mld.isel(
            TIME=time_index
        ).values

        # Make sure all required values are real.

        if not all([
            is_valid(sst_value),
            is_valid(salinity_value),
            is_valid(u_value),
            is_valid(v_value),
            is_valid(ssh_value),
            is_valid(mld_value)
        ]):

            continue

        # Calculate current speed from U and V.

        current_speed = (
            float(u_value) ** 2 +
            float(v_value) ** 2
        ) ** 0.5

        # Find actual nearest coordinates used by NetCDF.

        actual_lat = float(
            point["LAT"].values
        )

        actual_lon = float(
            point["LON"].values
        )

        return {
            "data_time": str(data_time)[:19],

            "latitude": actual_lat,

            "longitude": actual_lon,

            "sst": float(sst_value),

            "ssh": float(ssh_value),

            "salinity": float(salinity_value),

            "current_speed": float(current_speed),

            "mld": float(mld_value)
        }

    return None


# =========================================================
# INSERT OR UPDATE DATA IN POSTGRESQL
# =========================================================

def insert_ocean_observation(
    region_name,
    observation
):

    conn = get_connection()

    cursor = conn.cursor()

    data_time = observation["data_time"]

    # -----------------------------------------------------
    # Retrieval time
    #
    # This is different from data_time.
    #
    # data_time    = time of the ocean observation
    # retrieved_at = time ORCA processed/retrieved it
    # -----------------------------------------------------

    retrieved_at = datetime.now()

    # -----------------------------------------------------
    # Check whether this exact region + observation time
    # already exists.
    # -----------------------------------------------------

    cursor.execute(
        """
        SELECT id
        FROM ocean_observation
        WHERE region = %s
        AND data_time = %s
        ORDER BY id
        LIMIT 1;
        """,
        (
            region_name,
            data_time
        )
    )

    existing = cursor.fetchone()

    # -----------------------------------------------------
    # If it exists, update the existing record.
    #
    # This prevents duplicate records.
    # -----------------------------------------------------

    if existing:

        cursor.execute(
            """
            UPDATE ocean_observation
            SET
                sst_c = %s,
                ssh_m = %s,
                salinity = %s,
                current_speed_ms = %s,
                mld_m = %s,
                retrieved_at = %s
            WHERE id = %s;
            """,
            (
                observation["sst"],
                observation["ssh"],
                observation["salinity"],
                observation["current_speed"],
                observation["mld"],
                retrieved_at,
                existing[0]
            )
        )

        print(
            "EXISTING OBSERVATION UPDATED:",
            region_name,
            "|",
            data_time
        )

        print(
            "Retrieved at:",
            retrieved_at
        )

    # -----------------------------------------------------
    # Otherwise insert a new observation.
    # -----------------------------------------------------

    else:

        cursor.execute(
            """
            INSERT INTO ocean_observation
            (
                data_time,
                region,
                sst_c,
                ssh_m,
                salinity,
                current_speed_ms,
                mld_m,
                retrieved_at
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            );
            """,
            (
                observation["data_time"],
                region_name,
                observation["sst"],
                observation["ssh"],
                observation["salinity"],
                observation["current_speed"],
                observation["mld"],
                retrieved_at
            )
        )

        print(
            "NEW OBSERVATION INSERTED:",
            region_name,
            "|",
            data_time
        )

        print(
            "Retrieved at:",
            retrieved_at
        )

    conn.commit()

    cursor.close()

    conn.close()


# =========================================================
# MAIN LOADER
# =========================================================

def load_ocean_data():

    print()

    print("=" * 60)

    print(
        "ORCA REAL OCEAN DATA LOADER"
    )

    print("=" * 60)

    # -----------------------------------------------------
    # Check file
    # -----------------------------------------------------

    if not os.path.exists(FILE_PATH):

        print()

        print(
            "ERROR: NetCDF file was not found."
        )

        print()

        print(
            "Expected file:"
        )

        print(FILE_PATH)

        print()

        return

    print()

    print(
        "Opening real ocean data..."
    )

    print(FILE_PATH)

    print()

    # -----------------------------------------------------
    # Open NetCDF
    # -----------------------------------------------------

    ds = xr.open_dataset(
        FILE_PATH
    )

    try:

        print(
            "NetCDF opened successfully."
        )

        print()

        print(
            "Available variables:"
        )

        for variable in ds.data_vars:

            print(
                " -",
                variable
            )

        print()

        # -------------------------------------------------
        # Process each region
        # -------------------------------------------------

        successful = 0

        for state, config in REGIONS.items():

            print("-" * 60)

            print(
                "Processing:",
                state
            )

            print(
                "Region:",
                config["region"]
            )

            print(
                "Requested location:",
                config["lat"],
                config["lon"]
            )

            observation = get_latest_valid_observation(
                ds,
                config["lat"],
                config["lon"]
            )

            # ---------------------------------------------
            # No valid observation
            # ---------------------------------------------

            if observation is None:

                print()

                print(
                    "NO VALID DATA FOUND FOR:",
                    state
                )

                continue

            # ---------------------------------------------
            # Insert or update real observation
            # ---------------------------------------------

            insert_ocean_observation(
                config["region"],
                observation
            )

            successful += 1

            print()

            print(
                "REAL DATA PROCESSED"
            )

            print(
                "Observation time:",
                observation["data_time"]
            )

            print(
                "Grid latitude:",
                round(
                    observation["latitude"],
                    4
                )
            )

            print(
                "Grid longitude:",
                round(
                    observation["longitude"],
                    4
                )
            )

            print(
                "SST:",
                round(
                    observation["sst"],
                    2
                ),
                "°C"
            )

            print(
                "SSH:",
                round(
                    observation["ssh"],
                    3
                ),
                "m"
            )

            print(
                "Salinity:",
                round(
                    observation["salinity"],
                    2
                )
            )

            print(
                "Current speed:",
                round(
                    observation["current_speed"],
                    3
                ),
                "m/s"
            )

            print(
                "Mixed layer depth:",
                round(
                    observation["mld"],
                    2
                ),
                "m"
            )

        # -------------------------------------------------
        # Final summary
        # -------------------------------------------------

        print()

        print("=" * 60)

        print(
            "OCEAN DATA LOADING COMPLETED"
        )

        print("=" * 60)

        print(
            f"Successful regions: "
            f"{successful}/{len(REGIONS)}"
        )

        print()

        if successful == len(REGIONS):

            print(
                "SUCCESS: Real ocean data was "
                "processed for all 4 regions."
            )

        else:

            print(
                "WARNING: Some regions did not "
                "have valid observations."
            )

        print("=" * 60)

        print()

    finally:

        # Always close the NetCDF file.

        ds.close()


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    load_ocean_data()