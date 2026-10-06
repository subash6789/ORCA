"""
ORCA REAL WIND + WAVE DATA PIPELINE
INCOIS RSMC / WW3

Purpose:
- Find latest official INCOIS RSMC WW3 NetCDF
- Download it with resumable download support
- Extract real wind + wave data
- Save data into PostgreSQL
- Reuse already downloaded files
"""

import math
import re
import time
from pathlib import Path
from datetime import datetime, timezone

import requests
import xarray as xr

from db_connection import get_connection


# ============================================================
# CONFIGURATION
# ============================================================

INCOIS_DOWNLOAD_PAGE = (
    "https://incois.gov.in/oceanservices/rsmc_download.jsp"
)

INCOIS_FILE_BASE = (
    "https://incois.gov.in/thredds/fileServer/osf/ww3/"
)

BACKEND_DIR = Path(__file__).resolve().parent

DOWNLOAD_DIR = (
    BACKEND_DIR / "rsmc_ww3_downloads"
)

DOWNLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# REGION CONFIGURATION
# ============================================================

REGIONS = {

    "Tamil Nadu": {
        "region": "Tamil Nadu / Bay of Bengal",
        "latitude": 13.0827,
        "longitude": 80.2707,
    },

    "Kerala": {
        "region": "Kerala / Arabian Sea",
        "latitude": 8.5241,
        "longitude": 76.9366,
    },

    "Karnataka": {
        "region": "Karnataka / Arabian Sea",
        "latitude": 12.9141,
        "longitude": 74.8560,
    },

    "Gujarat": {
        "region": "Gujarat / Arabian Sea",
        "latitude": 23.0225,
        "longitude": 72.5714,
    },
}


# ============================================================
# DATABASE TABLE
# ============================================================

def create_wind_forecast_table():

    connection = get_connection()

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

            UNIQUE (region, forecast_time)
        )
        """
    )

    connection.commit()

    cursor.close()
    connection.close()

    print("Wind + wave forecast table: READY")


# ============================================================
# FIND LATEST OFFICIAL INCOIS FILE
# ============================================================

def find_latest_incois_file():

    print()
    print("Checking official INCOIS RSMC WW3 source...")
    print(INCOIS_DOWNLOAD_PAGE)

    response = requests.get(
        INCOIS_DOWNLOAD_PAGE,
        timeout=(20, 60),
        headers={
            "User-Agent": (
                "Mozilla/5.0 ORCA Marine Intelligence"
            )
        }
    )

    response.raise_for_status()

    html = response.text

    pattern = (
        r"rsmc_combined_ww3_(\d{8})\.nc"
    )

    matches = re.findall(
        pattern,
        html,
        flags=re.IGNORECASE
    )

    if not matches:

        raise RuntimeError(
            "No INCOIS RSMC WW3 NetCDF file "
            "was found on the official page."
        )

    latest_date = max(matches)

    filename = (
        f"rsmc_combined_ww3_{latest_date}.nc"
    )

    print()
    print("Latest INCOIS WW3 file:")
    print(filename)

    return filename


# ============================================================
# RESUMABLE DOWNLOAD
# ============================================================

def download_file_resumable(
    url,
    destination
):

    temp_file = destination.with_suffix(
        destination.suffix + ".part"
    )

    existing_size = 0

    if temp_file.exists():

        existing_size = (
            temp_file.stat().st_size
        )

    headers = {
        "User-Agent": (
            "Mozilla/5.0 ORCA Marine Intelligence"
        )
    }

    if existing_size > 0:

        headers["Range"] = (
            f"bytes={existing_size}-"
        )

        print()
        print(
            "Resuming download from "
            f"{existing_size / 1048576:.2f} MB"
        )

    else:

        print()
        print("Starting new download...")

    response = requests.get(
        url,
        headers=headers,
        stream=True,
        timeout=(30, 120),
    )

    # --------------------------------------------------------
    # RANGE NOT SUPPORTED
    # --------------------------------------------------------

    if (
        existing_size > 0
        and response.status_code == 200
    ):

        print()
        print(
            "Server did not provide HTTP range support."
        )

        print(
            "Restarting download from beginning..."
        )

        existing_size = 0

        if temp_file.exists():
            temp_file.unlink()

        response.close()

        response = requests.get(
            url,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 ORCA Marine Intelligence"
                )
            },
            stream=True,
            timeout=(30, 120),
        )

    response.raise_for_status()

    total_size = response.headers.get(
        "Content-Length"
    )

    if total_size:

        total_size = int(total_size)

        if existing_size > 0:
            total_size += existing_size

    mode = (
        "ab"
        if existing_size > 0
        else "wb"
    )

    downloaded = existing_size

    start_time = time.time()

    last_print = 0

    try:

        with open(
            temp_file,
            mode
        ) as file:

            for chunk in response.iter_content(
                chunk_size=256 * 1024
            ):

                if not chunk:
                    continue

                file.write(chunk)

                downloaded += len(chunk)

                now = time.time()

                if now - last_print >= 2:

                    elapsed = max(
                        now - start_time,
                        0.1
                    )

                    speed = (
                        downloaded - existing_size
                    ) / elapsed

                    if total_size:

                        percent = (
                            downloaded /
                            total_size
                        ) * 100

                        print(
                            f"\rDownload: "
                            f"{percent:6.2f}% | "
                            f"{downloaded / 1048576:.1f} MB | "
                            f"{speed / 1048576:.2f} MB/s",
                            end="",
                            flush=True
                        )

                    else:

                        print(
                            f"\rDownloaded: "
                            f"{downloaded / 1048576:.1f} MB | "
                            f"{speed / 1048576:.2f} MB/s",
                            end="",
                            flush=True
                        )

                    last_print = now

    except (
        requests.exceptions.Timeout,
        requests.exceptions.ConnectionError,
    ) as error:

        print()
        print(
            "Download interrupted."
        )

        print(
            "Partial file preserved:"
        )

        print(temp_file)

        raise error

    finally:

        response.close()

    print()

    temp_file.replace(destination)

    print()
    print("Download completed:")
    print(destination)

    return destination


# ============================================================
# DOWNLOAD LATEST WW3 FILE
# ============================================================

def download_latest_nc_file():

    filename = find_latest_incois_file()

    destination = (
        DOWNLOAD_DIR / filename
    )

    # --------------------------------------------------------
    # IMPORTANT:
    # REUSE ALREADY DOWNLOADED FILE
    # --------------------------------------------------------

    if destination.exists():

        size_mb = (
            destination.stat().st_size
            / 1048576
        )

        print()
        print(
            "WW3 file already downloaded."
        )

        print(
            f"Existing file size: "
            f"{size_mb:.2f} MB"
        )

        print(
            "Reusing existing file."
        )

        print(destination)

        return destination

    url = (
        INCOIS_FILE_BASE + filename
    )

    print()
    print(
        "Downloading official INCOIS WW3 file..."
    )

    print(url)

    return download_file_resumable(
        url,
        destination
    )


# ============================================================
# FIND DATASET VARIABLE
# ============================================================

def find_variable(
    dataset,
    possible_names
):

    available = {
        name.lower(): name
        for name in dataset.variables
    }

    for candidate in possible_names:

        if candidate.lower() in available:

            return available[
                candidate.lower()
            ]

    return None


# ============================================================
# CONVERT NUMPY DATETIME64
# ============================================================

def convert_numpy_datetime(value):

    if value is None:
        return None

    try:

        # Convert numpy.datetime64
        converted = (
            value
            .astype("datetime64[us]")
            .astype(datetime)
        )

        return converted

    except Exception:

        # Fallback
        try:

            return datetime.fromisoformat(
                str(value).replace(
                    "Z",
                    ""
                )
            )

        except Exception:

            return None


# ============================================================
# CLEAN NUMERIC VALUES
# ============================================================

def clean_numeric(value):

    if value is None:
        return None

    try:

        value = float(value)

        if math.isnan(value):
            return None

        if math.isinf(value):
            return None

        return value

    except (
        TypeError,
        ValueError,
    ):

        return None


# ============================================================
# NEAREST GRID VALUE
# ============================================================

def nearest_value(
    data_array,
    latitude,
    longitude,
    lat_name,
    lon_name,
):

    try:

        selected = data_array.sel(
            {
                lat_name: latitude,
                lon_name: longitude,
            },
            method="nearest",
        )

        value = selected.values

        if hasattr(value, "item"):
            value = value.item()

        return clean_numeric(value)

    except Exception:

        return None


# ============================================================
# GET LATEST TIME
# ============================================================

def get_latest_time(
    dataset,
    time_name
):

    times = dataset[
        time_name
    ].values

    if len(times) == 0:

        return None

    return times[-1]


# ============================================================
# COLLECT WIND + WAVE DATA
# ============================================================

def collect_wind_data():

    print()
    print(
        "-----------------------------------------"
    )

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
    # DOWNLOAD / REUSE FILE
    # --------------------------------------------------------

    nc_file = (
        download_latest_nc_file()
    )

    print()
    print(
        "Opening WW3 NetCDF..."
    )

    print(nc_file)

    # --------------------------------------------------------
    # OPEN DATASET
    # --------------------------------------------------------

    dataset = xr.open_dataset(
        nc_file
    )

    print()
    print(
        "Dataset opened successfully."
    )

    # --------------------------------------------------------
    # FIND VARIABLES
    # --------------------------------------------------------

    time_name = find_variable(
        dataset,
        [
            "TIME",
            "time",
            "forecast_time",
        ]
    )

    lat_name = find_variable(
        dataset,
        [
            "IOYAXIS",
            "latitude",
            "lat",
            "LAT",
        ]
    )

    lon_name = find_variable(
        dataset,
        [
            "IOXAXIS",
            "longitude",
            "lon",
            "LON",
        ]
    )

    u_name = find_variable(
        dataset,
        [
            "UWND",
            "u10",
            "wind_u",
        ]
    )

    v_name = find_variable(
        dataset,
        [
            "VWND",
            "v10",
            "wind_v",
        ]
    )

    wave_name = find_variable(
        dataset,
        [
            "HS",
            "hs",
            "significant_wave_height",
            "wave_height",
        ]
    )

    print()
    print(
        "Detected variables:"
    )

    print(
        "TIME:",
        time_name
    )

    print(
        "LAT :",
        lat_name
    )

    print(
        "LON :",
        lon_name
    )

    print(
        "UWND:",
        u_name
    )

    print(
        "VWND:",
        v_name
    )

    print(
        "HS  :",
        wave_name
    )

    if not time_name:

        raise RuntimeError(
            "TIME variable not found."
        )

    if not lat_name:

        raise RuntimeError(
            "Latitude variable not found."
        )

    if not lon_name:

        raise RuntimeError(
            "Longitude variable not found."
        )

    # --------------------------------------------------------
    # GET LATEST FORECAST TIME
    # --------------------------------------------------------

    latest_time = get_latest_time(
        dataset,
        time_name
    )

    print()
    print(
        "Raw forecast time:"
    )

    print(latest_time)

    # --------------------------------------------------------
    # FIX:
    # numpy.datetime64 -> Python datetime
    # --------------------------------------------------------

    latest_time = (
        convert_numpy_datetime(
            latest_time
        )
    )

    print()
    print(
        "Converted forecast time:"
    )

    print(latest_time)

    if latest_time is None:

        raise RuntimeError(
            "Could not convert forecast time."
        )

    # --------------------------------------------------------
    # UTC RETRIEVAL TIME
    # --------------------------------------------------------

    retrieved_at = datetime.now(
        timezone.utc
    ).replace(
        tzinfo=None
    )

    results = []

    # --------------------------------------------------------
    # PROCESS STATES
    # --------------------------------------------------------

    for state, config in REGIONS.items():

        latitude = (
            config["latitude"]
        )

        longitude = (
            config["longitude"]
        )

        print()
        print(
            f"Processing {state}..."
        )

        wind_speed = None

        u_wind = None

        v_wind = None

        wave_height = None

        # ----------------------------------------------------
        # U WIND
        # ----------------------------------------------------

        if u_name:

            u_data = dataset[
                u_name
            ].isel(
                {
                    time_name: -1
                }
            )

            u_wind = nearest_value(
                u_data,
                latitude,
                longitude,
                lat_name,
                lon_name,
            )

        # ----------------------------------------------------
        # V WIND
        # ----------------------------------------------------

        if v_name:

            v_data = dataset[
                v_name
            ].isel(
                {
                    time_name: -1
                }
            )

            v_wind = nearest_value(
                v_data,
                latitude,
                longitude,
                lat_name,
                lon_name,
            )

        # ----------------------------------------------------
        # WIND SPEED
        # ----------------------------------------------------

        if (
            u_wind is not None
            and
            v_wind is not None
        ):

            wind_speed = math.sqrt(
                (
                    u_wind ** 2
                )
                +
                (
                    v_wind ** 2
                )
            )

            wind_speed = (
                clean_numeric(
                    wind_speed
                )
            )

        # ----------------------------------------------------
        # WAVE HEIGHT
        # ----------------------------------------------------

        if wave_name:

            wave_data = dataset[
                wave_name
            ].isel(
                {
                    time_name: -1
                }
            )

            wave_height = nearest_value(
                wave_data,
                latitude,
                longitude,
                lat_name,
                lon_name,
            )

        # ----------------------------------------------------
        # RESULT
        # ----------------------------------------------------

        result = {

            "state": state,

            "region": (
                config["region"]
            ),

            "forecast_time": (
                latest_time
            ),

            "latitude": latitude,

            "longitude": longitude,

            "wind_speed_ms": (
                wind_speed
            ),

            "u_wind_ms": (
                u_wind
            ),

            "v_wind_ms": (
                v_wind
            ),

            "wave_height_m": (
                wave_height
            ),

            "source": (
                "INCOIS RSMC / WW3"
            ),

            "data_status": (
                "FORECAST"
            ),

            "retrieved_at": (
                retrieved_at
            ),
        }

        results.append(
            result
        )

        print(
            f"  Wind speed : "
            f"{wind_speed}"
        )

        print(
            f"  Wave height: "
            f"{wave_height}"
        )

    # --------------------------------------------------------
    # CLOSE DATASET
    # --------------------------------------------------------

    dataset.close()

    print()
    print(
        f"Collected "
        f"{len(results)} regional records."
    )

    # --------------------------------------------------------
    # SAVE
    # --------------------------------------------------------

    save_wind_data(
        results
    )

    return results


# ============================================================
# SAVE TO DATABASE
# ============================================================

def save_wind_data(
    results
):

    if not results:

        print(
            "No wind/wave data to save."
        )

        return

    connection = (
        get_connection()
    )

    cursor = (
        connection.cursor()
    )

    inserted = 0

    updated = 0

    for row in results:

        cursor.execute(
            """
            INSERT INTO wind_forecast (

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

            VALUES (

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

            ON CONFLICT (
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

                row[
                    "forecast_time"
                ],

                row[
                    "region"
                ],

                row[
                    "latitude"
                ],

                row[
                    "longitude"
                ],

                row[
                    "wind_speed_ms"
                ],

                row[
                    "u_wind_ms"
                ],

                row[
                    "v_wind_ms"
                ],

                row[
                    "wave_height_m"
                ],

                row[
                    "source"
                ],

                row[
                    "data_status"
                ],

                row[
                    "retrieved_at"
                ],
            )
        )

        # rowcount is 1 for both INSERT
        # and UPDATE in PostgreSQL.
        #
        # We count successful database
        # operations as updated/processed.

        updated += 1

    connection.commit()

    cursor.close()

    connection.close()

    print()
    print(
        "Wind + wave database update completed."
    )

    print(
        f"Processed: {updated}"
    )


# ============================================================
# MAIN
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

    create_wind_forecast_table()

    collect_wind_data()

    print()
    print(
        "=========================================="
    )

    print(
        " WIND + WAVE UPDATE COMPLETED"
    )

    print(
        "=========================================="
    )