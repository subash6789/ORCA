import os
from datetime import datetime, timezone

import numpy as np
import xarray as xr

from db_connection import get_connection


# ============================================================
# ORCA REAL CHLOROPHYLL-A COLLECTOR
# Source: INCOIS Ocean Colour / MODIS Aqua CHL product
# Unit: mg m^-3
#
# This collector:
# 1. Downloads the official INCOIS MODIS-Aqua CHL product
# 2. Detects latitude/longitude orientation automatically
# 3. Handles common longitude conventions
# 4. Extracts valid ocean CHL pixels for ORCA regions
# 5. Saves only real observed values
# ============================================================

SOURCE = "INCOIS Ocean Colour / MODIS Aqua"
DATA_STATUS = "OBSERVED"

CHL_URL = (
    "https://incois.gov.in/"
    "WEBSITE_FILES/MODISA/CHL/sep2026/"
    "A-Sep2026-d27-1KM-Entire-CHL.nc"
)

NC_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "A-Sep2026-d27-1KM-Entire-CHL.nc"
)


# ============================================================
# ORCA MARINE REGIONS
#
# Slightly expanded offshore boxes are used so that the
# collector is not restricted too tightly to the coastline.
# ============================================================

REGIONS = {

    "Tamil Nadu / Bay of Bengal": {
        "lat_min": 7.5,
        "lat_max": 15.5,
        "lon_min": 76.0,
        "lon_max": 83.0,
    },

    "Kerala / Arabian Sea": {
        "lat_min": 6.5,
        "lat_max": 13.5,
        "lon_min": 72.5,
        "lon_max": 79.0,
    },

    "Karnataka / Arabian Sea": {
        "lat_min": 10.0,
        "lat_max": 15.5,
        "lon_min": 71.5,
        "lon_max": 78.0,
    },

    "Gujarat / Arabian Sea": {
        "lat_min": 19.0,
        "lat_max": 25.5,
        "lon_min": 66.5,
        "lon_max": 74.5,
    },
}


# ============================================================
# CREATE DATABASE TABLE
# ============================================================

def create_chlorophyll_table():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS chlorophyll_observation (

            id SERIAL PRIMARY KEY,

            observation_time TIMESTAMP NOT NULL,

            region VARCHAR(100) NOT NULL,

            chlorophyll_mg_m3 DOUBLE PRECISION NOT NULL,

            valid_pixels INTEGER NOT NULL,

            minimum_mg_m3 DOUBLE PRECISION,

            maximum_mg_m3 DOUBLE PRECISION,

            median_mg_m3 DOUBLE PRECISION,

            source VARCHAR(200) NOT NULL,

            data_status VARCHAR(50) NOT NULL,

            retrieved_at TIMESTAMP NOT NULL,

            UNIQUE (
                observation_time,
                region
            )
        )
    """)

    conn.commit()

    cur.close()
    conn.close()

    print("Chlorophyll database table: READY")


# ============================================================
# DOWNLOAD OFFICIAL INCOIS PRODUCT
# ============================================================

def download_chlorophyll_product():

    print("\nDownloading official INCOIS CHL product...")
    print(f"Source URL: {CHL_URL}")
    print(f"Local file: {NC_FILE}")

    try:

        import urllib.request

        request = urllib.request.Request(
            CHL_URL,
            headers={
                "User-Agent": (
                    "ORCA-Marine-Intelligence-System/1.0"
                )
            }
        )

        with urllib.request.urlopen(
            request,
            timeout=180
        ) as response:

            print(
                f"HTTP status: {response.status}"
            )

            content_type = response.headers.get(
                "Content-Type",
                ""
            )

            print(
                f"Content-Type: {content_type}"
            )

            content_length = response.headers.get(
                "Content-Length"
            )

            if content_length:

                print(
                    f"Content-Length: "
                    f"{content_length} bytes"
                )

            if response.status != 200:

                raise RuntimeError(
                    f"INCOIS download failed: "
                    f"HTTP {response.status}"
                )

            with open(
                NC_FILE,
                "wb"
            ) as output_file:

                while True:

                    chunk = response.read(
                        1024 * 1024
                    )

                    if not chunk:
                        break

                    output_file.write(chunk)

        if not os.path.exists(NC_FILE):

            raise FileNotFoundError(
                "Downloaded CHL file was not created."
            )

        file_size = os.path.getsize(
            NC_FILE
        )

        if file_size <= 0:

            raise RuntimeError(
                "Downloaded CHL file is empty."
            )

        print(
            "Download completed: "
            f"{file_size / (1024 * 1024):.2f} MB"
        )

    except Exception as error:

        raise RuntimeError(
            "Unable to download official INCOIS "
            f"CHL product: {error}"
        )


# ============================================================
# FIND COORDINATE NAMES
# ============================================================

def find_coordinate_name(ds, candidates):

    for name in candidates:

        if name in ds.coords:

            return name

        if name in ds.variables:

            return name

    return None


# ============================================================
# OPEN CHL DATASET
# ============================================================

def open_chlorophyll_dataset():

    if not os.path.exists(NC_FILE):

        raise FileNotFoundError(
            f"CHL NetCDF file not found:\n{NC_FILE}"
        )

    print("\nOpening downloaded CHL dataset...")

    ds = xr.open_dataset(
        NC_FILE,
        engine="netcdf4"
    )

    if "chlor_a" not in ds.variables:

        ds.close()

        raise ValueError(
            "chlor_a variable was not found "
            "in the NetCDF file."
        )

    lat_name = find_coordinate_name(
        ds,
        [
            "lat",
            "latitude",
            "Latitude"
        ]
    )

    lon_name = find_coordinate_name(
        ds,
        [
            "lon",
            "longitude",
            "Longitude"
        ]
    )

    if not lat_name:

        ds.close()

        raise ValueError(
            "Latitude coordinate was not found."
        )

    if not lon_name:

        ds.close()

        raise ValueError(
            "Longitude coordinate was not found."
        )

    print(
        f"CHL variable: chlor_a"
    )

    print(
        f"Latitude coordinate: {lat_name}"
    )

    print(
        f"Longitude coordinate: {lon_name}"
    )

    print(
        "Unit: mg m^-3"
    )

    lat_values = np.asarray(
        ds[lat_name].values
    )

    lon_values = np.asarray(
        ds[lon_name].values
    )

    print(
        f"Latitude range: "
        f"{np.nanmin(lat_values):.4f} "
        f"to "
        f"{np.nanmax(lat_values):.4f}"
    )

    print(
        f"Longitude range: "
        f"{np.nanmin(lon_values):.4f} "
        f"to "
        f"{np.nanmax(lon_values):.4f}"
    )

    return ds, lat_name, lon_name


# ============================================================
# GET OBSERVATION TIME
# ============================================================

def get_observation_time(ds):

    start_time = ds.attrs.get(
        "time_coverage_start"
    )

    if start_time:

        try:

            dt = datetime.fromisoformat(
                start_time.replace(
                    "Z",
                    "+00:00"
                )
            )

            return dt.astimezone(
                timezone.utc
            ).replace(
                tzinfo=None
            )

        except Exception:
            pass

    # Fallback to time coordinate if metadata is absent
    if "time" in ds.coords:

        try:

            value = ds["time"].values

            if np.size(value) > 0:

                first_value = np.ravel(
                    value
                )[0]

                timestamp = (
                    np.datetime64(
                        first_value
                    ).astype(
                        "datetime64[us]"
                    ).astype(
                        datetime
                    )
                )

                return timestamp

        except Exception:
            pass

    raise ValueError(
        "Unable to determine CHL observation time."
    )


# ============================================================
# NORMALIZE LONGITUDE
# ============================================================

def normalize_region_longitudes(
    ds,
    lon_name,
    lon_min,
    lon_max
):

    lon_values = np.asarray(
        ds[lon_name].values
    )

    valid_lon_values = lon_values[
        np.isfinite(lon_values)
    ]

    if valid_lon_values.size == 0:

        raise ValueError(
            "Dataset longitude coordinate contains "
            "no valid values."
        )

    dataset_min = float(
        np.min(valid_lon_values)
    )

    dataset_max = float(
        np.max(valid_lon_values)
    )

    # Dataset uses 0..360 longitude.
    if dataset_max > 180:

        lon_min_normalized = (
            lon_min % 360
        )

        lon_max_normalized = (
            lon_max % 360
        )

        return (
            lon_min_normalized,
            lon_max_normalized
        )

    # Dataset uses -180..180 longitude.
    return lon_min, lon_max


# ============================================================
# EXTRACT CHL FOR ONE REGION
# ============================================================

def extract_region_chl(
    ds,
    lat_name,
    lon_name,
    region_name,
    bounds
):

    lat_min = bounds["lat_min"]
    lat_max = bounds["lat_max"]

    lon_min = bounds["lon_min"]
    lon_max = bounds["lon_max"]

    lat_values = np.asarray(
        ds[lat_name].values
    )

    lon_values = np.asarray(
        ds[lon_name].values
    )

    # --------------------------------------------------------
    # Check dataset latitude orientation
    # --------------------------------------------------------

    lat_valid = lat_values[
        np.isfinite(lat_values)
    ]

    if lat_valid.size == 0:

        print(
            f"{region_name}: "
            "NO VALID LATITUDE COORDINATES"
        )

        return None

    lat_ascending = (
        lat_valid[-1] >
        lat_valid[0]
    )

    if lat_ascending:

        lat_slice = slice(
            lat_min,
            lat_max
        )

    else:

        lat_slice = slice(
            lat_max,
            lat_min
        )

    # --------------------------------------------------------
    # Normalize longitude if required
    # --------------------------------------------------------

    lon_min_selected, lon_max_selected = (
        normalize_region_longitudes(
            ds,
            lon_name,
            lon_min,
            lon_max
        )
    )

    # --------------------------------------------------------
    # Check longitude orientation
    # --------------------------------------------------------

    lon_valid = lon_values[
        np.isfinite(lon_values)
    ]

    if lon_valid.size == 0:

        print(
            f"{region_name}: "
            "NO VALID LONGITUDE COORDINATES"
        )

        return None

    lon_ascending = (
        lon_valid[-1] >
        lon_valid[0]
    )

    if lon_ascending:

        lon_slice = slice(
            lon_min_selected,
            lon_max_selected
        )

    else:

        lon_slice = slice(
            lon_max_selected,
            lon_min_selected
        )

    # --------------------------------------------------------
    # Select region
    # --------------------------------------------------------

    try:

        region = ds["chlor_a"].sel(
            {
                lat_name: lat_slice,
                lon_name: lon_slice
            }
        )

    except Exception as error:

        print(
            f"{region_name}: "
            f"coordinate selection failed: {error}"
        )

        return None

    # --------------------------------------------------------
    # Convert to NumPy
    # --------------------------------------------------------

    values = np.asarray(
        region.values,
        dtype=float
    )

    if values.size == 0:

        print(
            f"{region_name}: "
            "NO PIXELS IN REGION"
        )

        return None

    # --------------------------------------------------------
    # Remove NaN and infinity
    # --------------------------------------------------------

    values = values[
        np.isfinite(values)
    ]

    if values.size == 0:

        print(
            f"{region_name}: "
            "ALL PIXELS ARE NaN/INVALID"
        )

        return None

    # --------------------------------------------------------
    # Remove common fill values
    # --------------------------------------------------------

    values = values[
        values > 0
    ]

    # Official practical CHL range used by ORCA
    values = values[
        (values >= 0.001)
        &
        (values <= 100.0)
    ]

    if values.size == 0:

        print(
            f"{region_name}: "
            "NO VALID CHL PIXELS AFTER QUALITY FILTER"
        )

        return None

    # --------------------------------------------------------
    # Calculate regional statistics
    # --------------------------------------------------------

    return {

        "region": region_name,

        "chlorophyll_mg_m3":
            float(
                np.mean(values)
            ),

        "valid_pixels":
            int(
                values.size
            ),

        "minimum_mg_m3":
            float(
                np.min(values)
            ),

        "maximum_mg_m3":
            float(
                np.max(values)
            ),

        "median_mg_m3":
            float(
                np.median(values)
            ),
    }


# ============================================================
# COLLECT CHL FOR ALL ORCA REGIONS
# ============================================================

def collect_chlorophyll_data():

    # --------------------------------------------------------
    # Download official product
    # --------------------------------------------------------

    download_chlorophyll_product()

    # --------------------------------------------------------
    # Open dataset
    # --------------------------------------------------------

    ds, lat_name, lon_name = (
        open_chlorophyll_dataset()
    )

    try:

        # ----------------------------------------------------
        # Observation time
        # ----------------------------------------------------

        observation_time = (
            get_observation_time(ds)
        )

        print(
            f"\nObservation time: "
            f"{observation_time}"
        )

        print(
            f"Product: "
            f"{ds.attrs.get('product_name', 'N/A')}"
        )

        print(
            f"Instrument: "
            f"{ds.attrs.get('instrument', 'N/A')}"
        )

        print(
            f"Platform: "
            f"{ds.attrs.get('platform', 'N/A')}"
        )

        # ----------------------------------------------------
        # Dataset coordinate information
        # ----------------------------------------------------

        print(
            "\nDataset coordinates:"
        )

        print(
            f"Latitude: {lat_name}"
        )

        print(
            f"Longitude: {lon_name}"
        )

        results = []

        # ----------------------------------------------------
        # Process every ORCA region
        # ----------------------------------------------------

        for region_name, bounds in REGIONS.items():

            print(
                "\n"
                + "-" * 60
            )

            print(
                f"Processing {region_name}..."
            )

            print(
                f"Latitude box: "
                f"{bounds['lat_min']} "
                f"to "
                f"{bounds['lat_max']}"
            )

            print(
                f"Longitude box: "
                f"{bounds['lon_min']} "
                f"to "
                f"{bounds['lon_max']}"
            )

            result = extract_region_chl(
                ds,
                lat_name,
                lon_name,
                region_name,
                bounds
            )

            if result is None:

                print(
                    f"{region_name}: "
                    "NO VALID CHL DATA"
                )

                continue

            result[
                "observation_time"
            ] = observation_time

            print(
                f"{region_name}: "
                f"{result['chlorophyll_mg_m3']:.4f} "
                "mg/m³"
            )

            print(
                f"  Valid pixels: "
                f"{result['valid_pixels']}"
            )

            print(
                f"  Minimum: "
                f"{result['minimum_mg_m3']:.4f}"
            )

            print(
                f"  Maximum: "
                f"{result['maximum_mg_m3']:.4f}"
            )

            print(
                f"  Median: "
                f"{result['median_mg_m3']:.4f}"
            )

            results.append(
                result
            )

        return results

    finally:

        ds.close()


# ============================================================
# SAVE CHL RESULTS TO POSTGRESQL
# ============================================================

def save_chlorophyll_data(results):

    if not results:

        print(
            "\nNo CHL observations to save."
        )

        return

    conn = get_connection()
    cur = conn.cursor()

    retrieved_at = (
        datetime.now(
            timezone.utc
        ).replace(
            tzinfo=None
        )
    )

    for result in results:

        cur.execute("""

            INSERT INTO chlorophyll_observation (

                observation_time,
                region,
                chlorophyll_mg_m3,
                valid_pixels,
                minimum_mg_m3,
                maximum_mg_m3,
                median_mg_m3,
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
                %s

            )

            ON CONFLICT (
                observation_time,
                region
            )

            DO UPDATE SET

                chlorophyll_mg_m3 =
                    EXCLUDED.chlorophyll_mg_m3,

                valid_pixels =
                    EXCLUDED.valid_pixels,

                minimum_mg_m3 =
                    EXCLUDED.minimum_mg_m3,

                maximum_mg_m3 =
                    EXCLUDED.maximum_mg_m3,

                median_mg_m3 =
                    EXCLUDED.median_mg_m3,

                source =
                    EXCLUDED.source,

                data_status =
                    EXCLUDED.data_status,

                retrieved_at =
                    EXCLUDED.retrieved_at

        """, (

            result["observation_time"],

            result["region"],

            result["chlorophyll_mg_m3"],

            result["valid_pixels"],

            result["minimum_mg_m3"],

            result["maximum_mg_m3"],

            result["median_mg_m3"],

            SOURCE,

            DATA_STATUS,

            retrieved_at

        ))

    conn.commit()

    cur.close()
    conn.close()

    print(
        "\nChlorophyll database update completed."
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print("=" * 60)

    print(
        "ORCA REAL CHLOROPHYLL-A DATA PIPELINE"
    )

    print(
        "INCOIS / MODIS Aqua / Ocean Colour"
    )

    print("=" * 60)

    try:

        create_chlorophyll_table()

        results = (
            collect_chlorophyll_data()
        )

        save_chlorophyll_data(
            results
        )

        print(
            "\nORCA CHL processing "
            "completed successfully."
        )

        print(
            f"Regions with valid CHL data: "
            f"{len(results)}/{len(REGIONS)}"
        )

    except Exception as error:

        print(
            "\nCHL PROCESSING ERROR"
        )

        print(
            type(error).__name__
        )

        print(
            str(error)
        )