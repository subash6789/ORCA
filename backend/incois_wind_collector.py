import math
from datetime import datetime, timezone
from pathlib import Path

import xarray as xr

from db_connection import get_connection


# ============================================================
# ORCA - INCOIS REAL WIND + WAVE FORECAST COLLECTOR
# ============================================================

BACKEND_DIR = Path(
    "C:/ORCA_ALL_FILES/backend"
)


# ============================================================
# FIND NEWEST LOCAL INCOIS WW3 FILE
# ============================================================

def find_latest_nc_file():

    files = list(
        BACKEND_DIR.glob(
            "rsmc_combined_ww3_*.nc"
        )
    )

    if not files:

        print(
            "ERROR: No INCOIS WW3 NetCDF file found."
        )

        print(
            "Expected file pattern:"
        )

        print(
            "rsmc_combined_ww3_YYYYMMDD.nc"
        )

        return None

    # --------------------------------------------------------
    # Sort using filename date
    # --------------------------------------------------------

    files.sort(
        key=lambda file: file.name,
        reverse=True
    )

    latest_file = files[0]

    print(
        "Latest local INCOIS WW3 file:"
    )

    print(
        latest_file.name
    )

    return latest_file


# ============================================================
# ORCA SUPPORTED REGIONS
# ============================================================

REGIONS = {

    "Tamil Nadu": {

        "region":
            "Tamil Nadu / Bay of Bengal",

        "lat":
            13.0827,

        "lon":
            80.2707
    },


    "Kerala": {

        "region":
            "Kerala / Arabian Sea",

        "lat":
            8.5241,

        "lon":
            76.9366
    },


    "Karnataka": {

        "region":
            "Karnataka / Arabian Sea",

        "lat":
            12.9141,

        "lon":
            74.8560
    },


    "Gujarat": {

        "region":
            "Gujarat / Arabian Sea",

        "lat":
            23.0225,

        "lon":
            72.5714
    }

}


# ============================================================
# WIND SPEED CALCULATION
# ============================================================

def calculate_wind_speed(
    u,
    v
):

    if u is None or v is None:

        return None

    try:

        u = float(u)
        v = float(v)

    except (
        TypeError,
        ValueError
    ):

        return None

    if (
        math.isnan(u)
        or math.isnan(v)
    ):

        return None

    return math.sqrt(
        u ** 2 +
        v ** 2
    )


# ============================================================
# CREATE / UPDATE DATABASE TABLE
# ============================================================

def create_wind_forecast_table():

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS wind_forecast (

                id SERIAL PRIMARY KEY,

                forecast_time TIMESTAMP NOT NULL,

                region VARCHAR(100) NOT NULL,

                latitude DOUBLE PRECISION,

                longitude DOUBLE PRECISION,

                wind_speed_ms DOUBLE PRECISION,

                u_wind_ms DOUBLE PRECISION,

                v_wind_ms DOUBLE PRECISION,

                wave_height_m DOUBLE PRECISION,

                source VARCHAR(200),

                data_status VARCHAR(50),

                retrieved_at TIMESTAMP NOT NULL,

                UNIQUE (
                    region,
                    forecast_time
                )
            )
            """
        )


        cursor.execute(
            """
            ALTER TABLE wind_forecast

            ADD COLUMN IF NOT EXISTS
            wave_height_m
            DOUBLE PRECISION
            """
        )


        connection.commit()

        cursor.close()

        print(
            "Wind + wave forecast table: READY"
        )

    finally:

        connection.close()


# ============================================================
# FIND LATEST VALID FORECAST TIME
# ============================================================

def find_latest_forecast_index(
    dataset
):

    try:

        time_values = (
            dataset["TIME"].values
        )

        if len(time_values) == 0:

            return None

        # ----------------------------------------------------
        # The NetCDF forecast normally contains multiple
        # forecast times.
        #
        # We use the latest available forecast time.
        # ----------------------------------------------------

        latest_index = (
            len(time_values) - 1
        )

        latest_time = (
            time_values[latest_index]
        )

        print(
            "Forecast time selected:"
        )

        print(
            latest_time
        )

        return latest_index

    except Exception as error:

        print(
            "ERROR reading forecast times:"
        )

        print(
            error
        )

        return None


# ============================================================
# FIND VALID WIND + WAVE CELL
# ============================================================

def find_valid_forecast_cell(
    dataset,
    target_lat,
    target_lon,
    time_index,
    max_radius=20
):

    lat_values = (
        dataset["IOYAXIS"].values
    )

    lon_values = (
        dataset["IOXAXIS"].values
    )


    # --------------------------------------------------------
    # Find nearest grid index
    # --------------------------------------------------------

    lat_index = int(
        abs(
            lat_values -
            target_lat
        ).argmin()
    )


    lon_index = int(
        abs(
            lon_values -
            target_lon
        ).argmin()
    )


    # --------------------------------------------------------
    # Read nearest cell
    # --------------------------------------------------------

    try:

        nearest_u = float(
            dataset["UWND"]
            .isel(
                TIME=time_index,
                IOYAXIS=lat_index,
                IOXAXIS=lon_index
            )
            .item()
        )


        nearest_v = float(
            dataset["VWND"]
            .isel(
                TIME=time_index,
                IOYAXIS=lat_index,
                IOXAXIS=lon_index
            )
            .item()
        )


        nearest_wave = float(
            dataset["HS"]
            .isel(
                TIME=time_index,
                IOYAXIS=lat_index,
                IOXAXIS=lon_index
            )
            .item()
        )


        if (

            not math.isnan(
                nearest_u
            )

            and

            not math.isnan(
                nearest_v
            )

            and

            not math.isnan(
                nearest_wave
            )

        ):

            return {

                "u":
                    nearest_u,

                "v":
                    nearest_v,

                "wave_height":
                    nearest_wave,

                "lat":
                    float(
                        lat_values[
                            lat_index
                        ]
                    ),

                "lon":
                    float(
                        lon_values[
                            lon_index
                        ]
                    )
            }


    except Exception:

        pass


    # --------------------------------------------------------
    # Search surrounding cells
    # --------------------------------------------------------

    best_cell = None

    best_distance = None


    for radius in range(
        1,
        max_radius + 1
    ):


        lat_start = max(
            0,
            lat_index - radius
        )


        lat_end = min(
            len(lat_values),
            lat_index +
            radius +
            1
        )


        lon_start = max(
            0,
            lon_index - radius
        )


        lon_end = min(
            len(lon_values),
            lon_index +
            radius +
            1
        )


        area_u = (
            dataset["UWND"]
            .isel(
                TIME=time_index,
                IOYAXIS=slice(
                    lat_start,
                    lat_end
                ),
                IOXAXIS=slice(
                    lon_start,
                    lon_end
                )
            )
        )


        area_v = (
            dataset["VWND"]
            .isel(
                TIME=time_index,
                IOYAXIS=slice(
                    lat_start,
                    lat_end
                ),
                IOXAXIS=slice(
                    lon_start,
                    lon_end
                )
            )
        )


        area_wave = (
            dataset["HS"]
            .isel(
                TIME=time_index,
                IOYAXIS=slice(
                    lat_start,
                    lat_end
                ),
                IOXAXIS=slice(
                    lon_start,
                    lon_end
                )
            )
        )


        u_values = area_u.values

        v_values = area_v.values

        wave_values = area_wave.values


        for i in range(
            u_values.shape[0]
        ):

            for j in range(
                u_values.shape[1]
            ):


                try:

                    test_u = float(
                        u_values[i, j]
                    )

                    test_v = float(
                        v_values[i, j]
                    )

                    test_wave = float(
                        wave_values[i, j]
                    )

                except (
                    TypeError,
                    ValueError
                ):

                    continue


                if (

                    math.isnan(test_u)

                    or

                    math.isnan(test_v)

                    or

                    math.isnan(test_wave)

                ):

                    continue


                actual_lat = float(
                    lat_values[
                        lat_start + i
                    ]
                )


                actual_lon = float(
                    lon_values[
                        lon_start + j
                    ]
                )


                distance = (

                    (
                        actual_lat -
                        target_lat
                    ) ** 2

                    +

                    (
                        actual_lon -
                        target_lon
                    ) ** 2
                )


                if (

                    best_distance is None

                    or

                    distance <
                    best_distance

                ):

                    best_distance = (
                        distance
                    )


                    best_cell = {

                        "u":
                            test_u,

                        "v":
                            test_v,

                        "wave_height":
                            test_wave,

                        "lat":
                            actual_lat,

                        "lon":
                            actual_lon
                    }


        if best_cell is not None:

            return best_cell


    return None


# ============================================================
# COLLECT REAL INCOIS WIND + WAVE DATA
# ============================================================

def collect_wind_data():

    print()

    print(
        "ORCA - REAL INCOIS WIND + WAVE COLLECTOR"
    )

    print(
        "-----------------------------------------"
    )

    print(
        "Source: INCOIS RSMC / WW3"
    )

    print(
        "Data type: FORECAST"
    )

    print()


    # --------------------------------------------------------
    # Find newest local file
    # --------------------------------------------------------

    nc_file = (
        find_latest_nc_file()
    )


    if nc_file is None:

        return []


    # --------------------------------------------------------
    # Open NetCDF
    # --------------------------------------------------------

    try:

      dataset = xr.open_dataset(
    nc_file,
    decode_times=True,
    use_cftime=True
)

    except Exception as error:

        print(
            "ERROR: Unable to open INCOIS "
            "forecast file."
        )

        print(
            "Reason:",
            error
        )

        return []


    results = []


    try:

        # ----------------------------------------------------
        # Required variables
        # ----------------------------------------------------

        required_variables = [

            "UWND",

            "VWND",

            "HS",

            "TIME"

        ]


        for variable in (
            required_variables
        ):

            if variable not in dataset:

                print(
                    f"ERROR: Required variable "
                    f"{variable} not found."
                )

                return []


        # ----------------------------------------------------
        # Select latest forecast time
        # ----------------------------------------------------

        time_index = (
            find_latest_forecast_index(
                dataset
            )
        )


        if time_index is None:

            print(
                "ERROR: No forecast time available."
            )

            return []


        time_value = (
            dataset["TIME"]
            .isel(
                TIME=time_index
            )
            .item()
        )


        print()

        print(
            "Using forecast timestamp:"
        )

        print(
            time_value
        )

        print()


        # ----------------------------------------------------
        # Process every ORCA region
        # ----------------------------------------------------

        for state, info in (
            REGIONS.items()
        ):


            print(
                f"Processing {state}..."
            )


            forecast_cell = (
                find_valid_forecast_cell(

                    dataset,

                    info["lat"],

                    info["lon"],

                    time_index

                )
            )


            if forecast_cell is None:

                print(
                    f"{state}: "
                    "Wind/wave data unavailable"
                )

                print()

                continue


            u_value = (
                forecast_cell["u"]
            )


            v_value = (
                forecast_cell["v"]
            )


            wave_height = (
                forecast_cell[
                    "wave_height"
                ]
            )


            actual_lat = (
                forecast_cell["lat"]
            )


            actual_lon = (
                forecast_cell["lon"]
            )


            # ------------------------------------------------
            # Calculate wind speed
            # ------------------------------------------------

            wind_speed = (
                calculate_wind_speed(
                    u_value,
                    v_value
                )
            )


            if wind_speed is None:

                print(
                    f"{state}: "
                    "Wind data unavailable"
                )

                print()

                continue


            # ------------------------------------------------
            # Validate wave
            # ------------------------------------------------

            if (

                wave_height is None

                or

                math.isnan(
                    wave_height
                )

            ):

                print(
                    f"{state}: "
                    "Wave height unavailable"
                )

                wave_height = None


            # ------------------------------------------------
            # Retrieved timestamp
            # ------------------------------------------------

            retrieved_at = (
                datetime.now(
                    timezone.utc
                )
            )


            # ------------------------------------------------
            # Build result
            # ------------------------------------------------

            result = {

                "state":
                    state,

                "region":
                    info["region"],

                "latitude":
                    actual_lat,

                "longitude":
                    actual_lon,

                "wind_speed_ms":
                    round(
                        wind_speed,
                        3
                    ),

                "u_wind_ms":
                    round(
                        u_value,
                        3
                    ),

                "v_wind_ms":
                    round(
                        v_value,
                        3
                    ),

                "wave_height_m":

                    (
                        round(
                            wave_height,
                            3
                        )

                        if
                        wave_height is not None

                        else
                        None
                    ),

                "forecast_time":
                    str(
                        time_value
                    ),

                "retrieved_at":
                    retrieved_at

            }


            results.append(
                result
            )


            # ------------------------------------------------
            # Display result
            # ------------------------------------------------

            print(
                f"{state}: "
                f"Wind "
                f"{result['wind_speed_ms']} m/s"
            )


            print(
                f"  U Wind: "
                f"{result['u_wind_ms']} m/s"
            )


            print(
                f"  V Wind: "
                f"{result['v_wind_ms']} m/s"
            )


            print(
                f"  Wave Height: "
                f"{result['wave_height_m']} m"
            )


            print(
                f"  Grid Latitude: "
                f"{result['latitude']}"
            )


            print(
                f"  Grid Longitude: "
                f"{result['longitude']}"
            )


            print(
                f"  Forecast: "
                f"{result['forecast_time']}"
            )


            print()


    finally:

        dataset.close()


    return results


# ============================================================
# SAVE WIND + WAVE DATA TO POSTGRESQL
# ============================================================

def save_wind_data(
    results
):

    if not results:

        print(
            "No wind/wave results available "
            "for database update."
        )

        return


    connection = (
        get_connection()
    )


    try:

        cursor = (
            connection.cursor()
        )


        for result in results:

            cursor.execute(

                """
                INSERT INTO wind_forecast
                (
                    forecast_time,
                    region,
                    latitude,
                    longitude,
                    wind_speed_ms,
                    u_wind_ms,
                    v_wind_ms,
                    wave_height_m,
                    source,
                    data_status,
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
                    %s,
                    %s,
                    %s,
                    %s
                )

                ON CONFLICT
                (
                    region,
                    forecast_time
                )

                DO UPDATE SET

                    latitude =
                        EXCLUDED.latitude,

                    longitude =
                        EXCLUDED.longitude,

                    wind_speed_ms =
                        EXCLUDED.wind_speed_ms,

                    u_wind_ms =
                        EXCLUDED.u_wind_ms,

                    v_wind_ms =
                        EXCLUDED.v_wind_ms,

                    wave_height_m =
                        EXCLUDED.wave_height_m,

                    source =
                        EXCLUDED.source,

                    data_status =
                        EXCLUDED.data_status,

                    retrieved_at =
                        EXCLUDED.retrieved_at
                """,

                (

                    result[
                        "forecast_time"
                    ],

                    result[
                        "region"
                    ],

                    result[
                        "latitude"
                    ],

                    result[
                        "longitude"
                    ],

                    result[
                        "wind_speed_ms"
                    ],

                    result[
                        "u_wind_ms"
                    ],

                    result[
                        "v_wind_ms"
                    ],

                    result[
                        "wave_height_m"
                    ],

                    "INCOIS RSMC / WW3",

                    "FORECAST",

                    result[
                        "retrieved_at"
                    ].replace(
                        tzinfo=None
                    )

                )
            )


        connection.commit()


        cursor.close()


        print(
            "Wind + wave forecast database "
            "update completed."
        )


    finally:

        connection.close()


# ============================================================
# MAIN PROGRAM
# ============================================================

if __name__ == "__main__":

    print()

    print(
        "=========================================="
    )

    print(
        " ORCA REAL WIND + WAVE DATA PIPELINE"
    )

    print(
        " INCOIS RSMC / WW3"
    )

    print(
        "=========================================="
    )

    print()


    # --------------------------------------------------------
    # Create / update table
    # --------------------------------------------------------

    create_wind_forecast_table()


    # --------------------------------------------------------
    # Collect latest available local forecast
    # --------------------------------------------------------

    forecast_results = (
        collect_wind_data()
    )


    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    if forecast_results:

        save_wind_data(
            forecast_results
        )


        print()

        print(
            "ORCA INCOIS wind + wave processing "
            "completed successfully."
        )


        print(
            f"Regions with valid forecast data: "
            f"{len(forecast_results)}/4"
        )


    else:

        print()

        print(
            "No wind/wave data was collected."
        )