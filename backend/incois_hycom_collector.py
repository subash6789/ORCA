import re
import math
import requests
from datetime import datetime, timedelta, timezone

from db_connection import get_connection


# ============================================================
# ORCA - INCOIS HYCOM REAL DATA COLLECTOR
# ============================================================

INCOIS_DOWNLOAD_PAGE = (
    "https://www.incois.gov.in/oceanservices/rsmc_download.jsp"
)

INCOIS_DODS_BASE = (
    "https://www.incois.gov.in/thredds/dodsC/osf/currents2/"
)

REQUEST_TIMEOUT = 30

MISSING_VALUE_LIMIT = 1.0e29

SEARCH_RADIUS = 6


# ============================================================
# MARINE REPRESENTATIVE LOCATIONS
# ============================================================

STATE_COORDINATES = {

    "Tamil Nadu": {
        "latitude": 13.0827,
        "longitude": 80.2707,
    },

    "Kerala": {
        "latitude": 8.5241,
        "longitude": 76.9366,
    },

    "Karnataka": {
        "latitude": 12.9093685,
        "longitude": 74.84,
    },

    # Coastal Gujarat - Veraval/Saurashtra region
    # Used instead of inland Ahmedabad.
    "Gujarat": {
        "latitude": 20.9006,
        "longitude": 70.3678,
    },
}


# ============================================================
# HTTP SESSION
# ============================================================

session = requests.Session()

session.headers.update(
    {
        "User-Agent": "ORCA-Marine-Intelligence/1.0"
    }
)


# ============================================================
# FIND LATEST HYCOM FILE
# ============================================================

def find_latest_dataset():

    print()
    print("Checking official INCOIS HYCOM dataset...")

    response = session.get(
        INCOIS_DOWNLOAD_PAGE,
        timeout=REQUEST_TIMEOUT
    )

    response.raise_for_status()

    matches = re.findall(
        r"RSMC_hycom_(\d{8})\.nc",
        response.text,
        flags=re.IGNORECASE
    )

    if not matches:
        raise RuntimeError(
            "Could not find HYCOM dataset on INCOIS page."
        )

    latest_date = sorted(set(matches))[-1]

    filename = (
        f"RSMC_hycom_{latest_date}.nc"
    )

    print(
        f"Latest HYCOM dataset: {filename}"
    )

    return filename


# ============================================================
# DATASET URL
# ============================================================

def dataset_url(filename):

    return (
        INCOIS_DODS_BASE
        + filename
    )


# ============================================================
# REQUEST ASCII DODS DATA
# ============================================================

def request_ascii(
    filename,
    expression
):

    url = (
        dataset_url(filename)
        + ".ascii?"
        + expression
    )

    response = session.get(
        url,
        timeout=REQUEST_TIMEOUT
    )

    response.raise_for_status()

    return response.text


# ============================================================
# NUMBER PARSER
# ============================================================

def parse_numbers(text):

    pattern = r"""
        [-+]?
        (?:
            \d+(?:\.\d*)?
            |
            \.\d+
        )
        (?:
            [Ee][-+]?\d+
        )?
    """

    return [
        float(value)
        for value in re.findall(
            pattern,
            text,
            flags=re.VERBOSE
        )
    ]


# ============================================================
# PARSE ARRAY COORDINATES
# ============================================================

def get_coordinate_array(
    filename,
    variable,
    expected_count
):

    print(
        f"Reading {variable} coordinates..."
    )

    text = request_ascii(
        filename,
        variable
    )

    lines = text.splitlines()

    marker_regex = re.compile(
        rf"^\s*{re.escape(variable)}\[{expected_count}\]\s*$"
    )

    marker_index = None

    for index, line in enumerate(lines):

        if marker_regex.match(line):

            marker_index = index
            break

    if marker_index is None:

        raise RuntimeError(
            f"Could not locate "
            f"{variable}[{expected_count}] "
            f"data marker."
        )

    values = []

    for line in lines[
        marker_index + 1:
    ]:

        stripped = line.strip()

        if not stripped:
            continue

        values.extend(
            parse_numbers(stripped)
        )

    if len(values) < expected_count:

        raise RuntimeError(
            f"{variable}: expected "
            f"{expected_count} values, "
            f"received {len(values)}."
        )

    return values[:expected_count]


# ============================================================
# GET HYCOM TIME VALUES
# ============================================================

def get_time_values(
    filename,
    expected_count
):

    print(
        "Reading HYCOM time values..."
    )

    text = request_ascii(
        filename,
        "TIME"
    )

    lines = text.splitlines()

    marker_regex = re.compile(
        rf"^\s*TIME\[{expected_count}\]\s*$"
    )

    marker_index = None

    for index, line in enumerate(lines):

        if marker_regex.match(line):

            marker_index = index
            break

    if marker_index is None:

        raise RuntimeError(
            "Could not locate TIME data marker."
        )

    values = []

    for line in lines[
        marker_index + 1:
    ]:

        stripped = line.strip()

        if not stripped:
            continue

        values.extend(
            parse_numbers(stripped)
        )

    if len(values) < expected_count:

        raise RuntimeError(
            f"TIME: expected "
            f"{expected_count} values, "
            f"received {len(values)}."
        )

    return values[:expected_count]


# ============================================================
# CONVERT HYCOM TIME
# ============================================================

def convert_hycom_time(
    value
):

    base_time = datetime(
        1900,
        12,
        31,
        tzinfo=timezone.utc
    )

    return (
        base_time
        + timedelta(days=value)
    )


# ============================================================
# NEAREST GRID INDEX
# ============================================================

def nearest_index(
    values,
    target
):

    return min(
        range(len(values)),
        key=lambda index:
        abs(values[index] - target)
    )


# ============================================================
# PARSE EXACT SINGLE VARIABLE VALUE
# ============================================================
#
# IMPORTANT:
#
# INCOIS DODS ASCII response looks like:
#
# SSH.SSH[1][1][1]
# [0][0][0], 0.52623534
# SSH.TIME[1]
# 45940.0
# SSH.LAT[1]
# 13.084758
# SSH.LON[1]
# 80.299995
#
# We MUST take the value immediately after
# the exact VAR.VAR[...] data marker.
#
# This prevents longitude/latitude from being
# accidentally returned as the variable value.
# ============================================================

def parse_exact_variable_value(
    text,
    variable
):

    lines = text.splitlines()

    marker_regex = re.compile(
        rf"^\s*"
        rf"{re.escape(variable)}\."
        rf"{re.escape(variable)}"
        rf"\[.*\]"
        rf"\s*$"
    )

    marker_index = None

    for index, line in enumerate(lines):

        if marker_regex.match(line):

            marker_index = index
            break

    if marker_index is None:

        raise RuntimeError(
            f"Could not find exact "
            f"{variable}.{variable} data marker."
        )

    # Find the first non-empty line after
    # the exact data marker.
    for line in lines[
        marker_index + 1:
    ]:

        stripped = line.strip()

        if not stripped:
            continue

        # Remove array indexes such as:
        #
        # [0][0][0],
        #
        clean = re.sub(
            r"\[[0-9]+\]",
            "",
            stripped
        )

        clean = clean.strip()

        # Remove leading comma if present.
        clean = clean.lstrip(",")

        values = parse_numbers(clean)

        if values:

            return values[0]

    raise RuntimeError(
        f"No numeric value found after "
        f"{variable}.{variable} marker."
    )


# ============================================================
# QUERY ONE HYCOM VARIABLE
# ============================================================

def query_variable(
    filename,
    variable,
    expression
):

    text = request_ascii(
        filename,
        expression
    )

    return parse_exact_variable_value(
        text,
        variable
    )


# ============================================================
# QUERY COMPLETE HYCOM CELL
# ============================================================

def query_single_cell(
    filename,
    time_index,
    lat_index,
    lon_index
):

    expressions = {

        "SSH":
            f"SSH[{time_index}]"
            f"[{lat_index}]"
            f"[{lon_index}]",

        "TEMP":
            f"TEMP[{time_index}]"
            f"[0]"
            f"[{lat_index}]"
            f"[{lon_index}]",

        "SALN":
            f"SALN[{time_index}]"
            f"[0]"
            f"[{lat_index}]"
            f"[{lon_index}]",

        "UVEL":
            f"UVEL[{time_index}]"
            f"[0]"
            f"[{lat_index}]"
            f"[{lon_index}]",

        "VVEL":
            f"VVEL[{time_index}]"
            f"[0]"
            f"[{lat_index}]"
            f"[{lon_index}]",

        "MLD":
            f"MLD[{time_index}]"
            f"[{lat_index}]"
            f"[{lon_index}]",

        "TCHP":
            f"TCHP[{time_index}]"
            f"[{lat_index}]"
            f"[{lon_index}]",
    }

    result = {}

    for variable, expression in expressions.items():

        try:

            value = query_variable(
                filename,
                variable,
                expression
            )

            result[variable] = value

        except Exception as error:

            print(
                f"      {variable}: "
                f"query failed - {error}"
            )

            result[variable] = None

    return result


# ============================================================
# VALID DATA CHECK
# ============================================================

def valid_value(
    value
):

    if value is None:
        return False

    if not math.isfinite(value):
        return False

    if abs(value) >= MISSING_VALUE_LIMIT:
        return False

    return True


# ============================================================
# FIND VALID CELL
# ============================================================

def find_valid_cell(
    filename,
    time_index,
    lat_values,
    lon_values,
    target_lat,
    target_lon
):

    center_lat_index = nearest_index(
        lat_values,
        target_lat
    )

    center_lon_index = nearest_index(
        lon_values,
        target_lon
    )

    print(
        f"Initial grid cell: "
        f"LAT index {center_lat_index}, "
        f"LON index {center_lon_index}"
    )

    print(
        f"Initial coordinates: "
        f"{lat_values[center_lat_index]}, "
        f"{lon_values[center_lon_index]}"
    )

    checked = set()

    for radius in range(
        SEARCH_RADIUS + 1
    ):

        candidates = []

        if radius == 0:

            candidates.append(
                (
                    center_lat_index,
                    center_lon_index
                )
            )

        else:

            candidates.extend(
                [
                    (
                        center_lat_index - radius,
                        center_lon_index
                    ),
                    (
                        center_lat_index + radius,
                        center_lon_index
                    ),
                    (
                        center_lat_index,
                        center_lon_index - radius
                    ),
                    (
                        center_lat_index,
                        center_lon_index + radius
                    ),

                    (
                        center_lat_index - radius,
                        center_lon_index - radius
                    ),
                    (
                        center_lat_index - radius,
                        center_lon_index + radius
                    ),
                    (
                        center_lat_index + radius,
                        center_lon_index - radius
                    ),
                    (
                        center_lat_index + radius,
                        center_lon_index + radius
                    ),
                ]
            )

        for lat_index, lon_index in candidates:

            if (
                lat_index,
                lon_index
            ) in checked:

                continue

            checked.add(
                (
                    lat_index,
                    lon_index
                )
            )

            if not (
                0 <= lat_index < len(lat_values)
                and
                0 <= lon_index < len(lon_values)
            ):

                continue

            grid_lat = lat_values[
                lat_index
            ]

            grid_lon = lon_values[
                lon_index
            ]

            print(
                f"Checking cell "
                f"LAT {lat_index}, "
                f"LON {lon_index} "
                f"({grid_lat:.6f}, "
                f"{grid_lon:.6f})"
            )

            # ------------------------------------------------
            # First check ONLY SSH.
            # This avoids wasting requests on missing cells.
            # ------------------------------------------------

            try:

                ssh = query_variable(
                    filename,
                    "SSH",
                    (
                        f"SSH[{time_index}]"
                        f"[{lat_index}]"
                        f"[{lon_index}]"
                    )
                )

            except Exception as error:

                print(
                    f"   -> SSH query failed: "
                    f"{error}"
                )

                continue

            if not valid_value(ssh):

                print(
                    "   -> SSH NO_DATA"
                )

                continue

            print(
                f"   -> VALID SSH: {ssh}"
            )

            # ------------------------------------------------
            # Now retrieve the remaining variables.
            # ------------------------------------------------

            data = query_single_cell(
                filename,
                time_index,
                lat_index,
                lon_index
            )

            # Use the already verified SSH.
            data["SSH"] = ssh

            distance = math.sqrt(
                (
                    grid_lat - target_lat
                ) ** 2
                +
                (
                    grid_lon - target_lon
                ) ** 2
            )

            return {
                "latitude": grid_lat,
                "longitude": grid_lon,
                "lat_index": lat_index,
                "lon_index": lon_index,
                "distance": distance,
                "data": data,
            }

    return None


# ============================================================
# COLLECT ONE STATE
# ============================================================

def collect_state(
    filename,
    time_index,
    lat_values,
    lon_values,
    state,
    coordinates,
    forecast_time
):

    target_lat = coordinates[
        "latitude"
    ]

    target_lon = coordinates[
        "longitude"
    ]

    print()
    print(
        "=" * 65
    )

    print(state)

    print(
        f"Target: "
        f"{target_lat}, "
        f"{target_lon}"
    )

    result = find_valid_cell(
        filename,
        time_index,
        lat_values,
        lon_values,
        target_lat,
        target_lon
    )

    if result is None:

        print(
            f"{state}: "
            f"NO VALID HYCOM CELL FOUND."
        )

        return {
            "state": state,
            "status": "NO_DATA",
            "source": "INCOIS RSMC / HYCOM",
            "latitude": None,
            "longitude": None,
            "forecast_time": forecast_time,
            "ssh_m": None,
            "temperature_c": None,
            "salinity_psu": None,
            "u_current_ms": None,
            "v_current_ms": None,
            "current_speed_ms": None,
            "mld_m": None,
            "tchp": None,
        }

    data = result["data"]

    ssh = data.get("SSH")
    temp = data.get("TEMP")
    saln = data.get("SALN")
    u = data.get("UVEL")
    v = data.get("VVEL")
    mld = data.get("MLD")
    tchp = data.get("TCHP")

    # If primary coastal cell has missing MLD sentinel, step offshore to capture valid hydrodynamics
    if not valid_value(mld):
        mld_offsets = {
            "Tamil Nadu": (0, 1),
            "Kerala": (0, -1),
            "Karnataka": (0, -1),
            "Gujarat": (-1, 0),
        }
        d_lat, d_lon = mld_offsets.get(state, (0, 1))
        c_lat_idx = result["lat_index"]
        c_lon_idx = result["lon_index"]
        for step in range(1, 10):
            cand_lat = c_lat_idx + step * d_lat
            cand_lon = c_lon_idx + step * d_lon
            if 0 <= cand_lat < len(lat_values) and 0 <= cand_lon < len(lon_values):
                try:
                    cand_mld = query_variable(
                        filename,
                        "MLD",
                        f"MLD[{time_index}][{cand_lat}][{cand_lon}]"
                    )
                    if valid_value(cand_mld):
                        mld = cand_mld
                        print(f"   -> Offshore MLD recovered at step {step}: {mld:.2f} m")
                        break
                except Exception:
                    pass

    current_speed = None

    if (
        valid_value(u)
        and
        valid_value(v)
    ):

        current_speed = math.sqrt(
            (u ** 2) + (v ** 2)
        )

    return {
        "state": state,
        "status": "FORECAST",
        "source": "INCOIS RSMC / HYCOM",

        "latitude":
            result["latitude"],

        "longitude":
            result["longitude"],

        "forecast_time":
            forecast_time,

        "ssh_m":
            ssh if valid_value(ssh)
            else None,

        "temperature_c":
            temp if valid_value(temp)
            else None,

        "salinity_psu":
            saln if valid_value(saln)
            else None,

        "u_current_ms":
            u if valid_value(u)
            else None,

        "v_current_ms":
            v if valid_value(v)
            else None,

        "current_speed_ms":
            current_speed,

        "mld_m":
            mld if valid_value(mld)
            else None,

        "tchp":
            tchp if valid_value(tchp)
            else None,
    }


# ============================================================
# MAIN COLLECTION
# ============================================================

def collect_hycom():

    print()
    print(
        "=" * 70
    )

    print(
        "ORCA INCOIS HYCOM COLLECTION"
    )

    print(
        "REAL INCOIS RSMC DATA"
    )

    print(
        "=" * 70
    )

    # --------------------------------------------------------
    # Latest dataset
    # --------------------------------------------------------

    filename = find_latest_dataset()

    print(
        f"Dataset URL: "
        f"{dataset_url(filename)}"
    )

    # --------------------------------------------------------
    # Coordinates
    # --------------------------------------------------------

    lat_values = get_coordinate_array(
        filename,
        "LAT",
        1384
    )

    lon_values = get_coordinate_array(
        filename,
        "LON",
        1665
    )

    print(
        f"Latitude points: "
        f"{len(lat_values)}"
    )

    print(
        f"Longitude points: "
        f"{len(lon_values)}"
    )

    # --------------------------------------------------------
    # Time
    # --------------------------------------------------------

    time_values = get_time_values(
        filename,
        28
    )

    latest_time_index = (
        len(time_values) - 1
    )

    latest_time_value = (
        time_values[latest_time_index]
    )

    latest_datetime = (
        convert_hycom_time(
            latest_time_value
        )
    )

    forecast_time = (
        latest_datetime.isoformat()
    )

    print(
        f"Latest HYCOM time index: "
        f"{latest_time_index}"
    )

    print(
        f"Latest HYCOM time: "
        f"{forecast_time}"
    )

    # --------------------------------------------------------
    # Collect all four states
    # --------------------------------------------------------

    results = []

    for state, coordinates in (
        STATE_COORDINATES.items()
    ):

        result = collect_state(
            filename,
            latest_time_index,
            lat_values,
            lon_values,
            state,
            coordinates,
            forecast_time
        )

        results.append(result)

    # --------------------------------------------------------
    # Final summary
    # --------------------------------------------------------

    print()
    print(
        "=" * 70
    )

    print(
        "HYCOM COLLECTION SUMMARY"
    )

    print(
        "=" * 70
    )

    for result in results:

        print()
        print(
            f"{result['state']}: "
            f"{result['status']} | "
            f"{result['latitude']} | "
            f"{result['longitude']}"
        )

        print(
            f"  SSH: "
            f"{result['ssh_m']}"
        )

        print(
            f"  Temperature: "
            f"{result['temperature_c']}"
        )

        print(
            f"  Salinity: "
            f"{result['salinity_psu']}"
        )

        print(
            f"  U Current: "
            f"{result['u_current_ms']}"
        )

        print(
            f"  V Current: "
            f"{result['v_current_ms']}"
        )

        print(
            f"  Current Speed: "
            f"{result['current_speed_ms']}"
        )

        print(
            f"  MLD: "
            f"{result['mld_m']}"
        )

        print(
            f"  TCHP: "
            f"{result['tchp']}"
        )

        print(
            f"  Forecast Time: "
            f"{result['forecast_time']}"
        )

        print(
            f"  Source: "
            f"{result['source']}"
        )

    print()
    print(
        "ORCA INCOIS HYCOM COLLECTION COMPLETED"
    )

    return results


# ============================================================
# SAVE HYCOM FORECAST RESULTS TO POSTGRESQL
# ============================================================

def save_hycom_data(results):

    if not results:
        print("\nNo HYCOM ocean records to save.")
        return

    connection = get_connection()

    try:
        cursor = connection.cursor()

        retrieved_at = datetime.now(timezone.utc).replace(
            tzinfo=None
        )

        saved_count = 0
        inserted_count = 0
        updated_count = 0
        skipped_count = 0

        for item in results:

            # ----------------------------------------------------
            # Forecast timestamp conversion:
            # item["forecast_time"] is ISO string in UTC.
            # Convert to UTC-naive datetime because column is
            # TIMESTAMP WITHOUT TIME ZONE in PostgreSQL.
            # ----------------------------------------------------
            forecast_str = item.get("forecast_time")
            if not forecast_str:
                continue

            dt_utc = datetime.fromisoformat(forecast_str)
            if dt_utc.tzinfo is not None:
                data_time = dt_utc.astimezone(timezone.utc).replace(tzinfo=None)
            else:
                data_time = dt_utc

            region = item.get("state")
            source = item.get("source") or "INCOIS RSMC / HYCOM"
            data_status = item.get("status") or "FORECAST"
            latitude = item.get("latitude")
            longitude = item.get("longitude")
            sst_c = item.get("temperature_c")
            ssh_m = item.get("ssh_m")
            salinity = item.get("salinity_psu")
            current_speed_ms = item.get("current_speed_ms")
            mld_m = item.get("mld_m")

            # Missing measurements remain SQL NULL (never zero)
            # wind_speed_ms and wave_height_m are not from HYCOM (NULL)

            # Check if record already exists for (region, data_time, source)
            cursor.execute(
                """
                SELECT id
                FROM public.ocean_observation
                WHERE region = %s
                  AND data_time = %s
                  AND source = %s
                LIMIT 1
                """,
                (region, data_time, source)
            )

            existing = cursor.fetchone()

            if existing is not None:
                # Update existing forecast step in-place (idempotent update)
                cursor.execute(
                    """
                    UPDATE public.ocean_observation
                    SET
                        data_status = %s,
                        latitude = %s,
                        longitude = %s,
                        sst_c = %s,
                        ssh_m = %s,
                        salinity = %s,
                        current_speed_ms = %s,
                        mld_m = %s,
                        retrieved_at = %s
                    WHERE id = %s
                    """,
                    (
                        data_status,
                        latitude,
                        longitude,
                        sst_c,
                        ssh_m,
                        salinity,
                        current_speed_ms,
                        mld_m,
                        retrieved_at,
                        existing[0]
                    )
                )
                saved_count += 1
                updated_count += 1
            else:
                # Use a PostgreSQL SAVEPOINT to ensure the transaction remains
                # completely valid even if a concurrent worker or existing record
                # triggers the (region, data_time, sst_c) unique index.
                cursor.execute("SAVEPOINT sp_insert_hycom;")
                try:
                    cursor.execute(
                        """
                        INSERT INTO public.ocean_observation
                        (
                            data_time,
                            region,
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
                            wave_height_m,
                            retrieved_at
                        )
                        VALUES
                        (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                        )
                        """,
                        (
                            data_time,
                            region,
                            source,
                            data_status,
                            latitude,
                            longitude,
                            sst_c,
                            ssh_m,
                            salinity,
                            current_speed_ms,
                            mld_m,
                            None,
                            None,
                            retrieved_at
                        )
                    )
                    cursor.execute("RELEASE SAVEPOINT sp_insert_hycom;")
                    saved_count += 1
                    inserted_count += 1
                except Exception as insert_err:
                    # Safely recover the transaction from savepoint
                    cursor.execute("ROLLBACK TO SAVEPOINT sp_insert_hycom;")
                    cursor.execute("RELEASE SAVEPOINT sp_insert_hycom;")

                    # Fall back to updating the row that triggered the unique index
                    # ONLY if it belongs to HYCOM or an unassigned/forecast ocean record.
                    # Do not overwrite unrelated historical observations (e.g. drifting buoy, MODIS).
                    cursor.execute(
                        """
                        SELECT id, source
                        FROM public.ocean_observation
                        WHERE region = %s
                          AND data_time = %s
                          AND sst_c = %s
                        LIMIT 1
                        """,
                        (region, data_time, sst_c)
                    )
                    conflict_row = cursor.fetchone()
                    if conflict_row:
                        conflicting_id, existing_source = conflict_row
                        # If existing source is unrelated historical data, do not overwrite it
                        if existing_source and "HYCOM" not in existing_source and existing_source != source:
                            print(
                                f"Skipping HYCOM overwrite of unrelated source "
                                f"'{existing_source}' on region {region} at {data_time}."
                            )
                            skipped_count += 1
                        else:
                            cursor.execute(
                                """
                                UPDATE public.ocean_observation
                                SET
                                    source = %s,
                                    data_status = %s,
                                    latitude = %s,
                                    longitude = %s,
                                    ssh_m = %s,
                                    salinity = %s,
                                    current_speed_ms = %s,
                                    mld_m = %s,
                                    retrieved_at = %s
                                WHERE id = %s
                                """,
                                (
                                    source,
                                    data_status,
                                    latitude,
                                    longitude,
                                    ssh_m,
                                    salinity,
                                    current_speed_ms,
                                    mld_m,
                                    retrieved_at,
                                    conflicting_id
                                )
                            )
                            saved_count += 1
                            updated_count += 1
                    else:
                        raise insert_err

        connection.commit()

        print(
            f"\nSaved {saved_count} HYCOM ocean forecast records to PostgreSQL "
            f"(inserted={inserted_count}, updated={updated_count}, skipped={skipped_count})."
        )

        return {
            "total_saved": saved_count,
            "inserted": inserted_count,
            "updated": updated_count,
            "skipped": skipped_count
        }

    finally:

        if cursor is not None:
            try:
                cursor.close()
            except Exception:
                pass

        connection.close()


# ============================================================
# DIRECT EXECUTION
# ============================================================

if __name__ == "__main__":

    try:

        collect_hycom()

    except Exception as error:

        print()
        print(
            "HYCOM COLLECTION FAILED."
        )

        print(
            f"Error: {error}"
        )