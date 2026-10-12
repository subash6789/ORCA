import os

import xarray as xr
import numpy as np


# ============================================================
# ORCA SATELLITE AGENT
# Real MODIS Aqua Chlorophyll-a data (multi-day composites)
# ============================================================

MODIS_DIR = os.path.dirname(os.path.abspath(__file__))

# Authoritative INCOIS MODIS Aqua 8-day composite files on disk
# Checked in chronological order (most recent first)
MODIS_COMPOSITE_FILES = [
    os.path.join(MODIS_DIR, "A-Oct2026-d08-1KM-Entire-CHL.nc"),
    os.path.join(MODIS_DIR, "A-Oct2026-d05-1KM-Entire-CHL.nc"),
    os.path.join(MODIS_DIR, "A-Oct2026-d01-1KM-Entire-CHL.nc"),
    os.path.join(MODIS_DIR, "A-Sep2026-d27-1KM-Entire-CHL.nc"),
]

# Primary default file
CHL_FILE = MODIS_COMPOSITE_FILES[0]


import json

# ============================================================
# CANONICAL DISTRICT PARTITIONING (ALL 114 DISTRICTS)
# ============================================================

DISTRICT_COORDS_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "district_canonical_coords.json"
)

COASTAL_DISTRICTS = {
    "Gujarat": {
        "Kachchh", "Jamnagar", "Devbhumi Dwarka", "Porbandar",
        "Junagadh", "Gir Somnath", "Amreli", "Bhavnagar",
        "Bharuch", "Surat", "Navsari", "Valsad", "Morbi"
    },
    "Karnataka": {
        "Uttara Kannada", "Udupi", "Dakshina Kannada"
    },
    "Kerala": {
        "Kasaragod", "Kannur", "Kozhikode", "Malappuram",
        "Thrissur", "Ernakulam", "Alappuzha", "Kollam",
        "Thiruvananthapuram"
    },
    "Tamil Nadu": {
        "Thiruvallur", "Chennai", "Chengalpattu", "Villupuram",
        "Cuddalore", "Nagapattinam", "Thiruvarur", "Thanjavur",
        "Pudukkottai", "Ramanathapuram", "Tuticorin", "Tirunelveli",
        "Kanniyakumari"
    }
}


def _load_canonical_district_coords():
    if os.path.exists(DISTRICT_COORDS_FILE):
        try:
            with open(DISTRICT_COORDS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


CANONICAL_DISTRICT_COORDS = _load_canonical_district_coords()


# ============================================================
# STATE / MARINE REGION
# ============================================================

REGION_MAP = {

    "Tamil Nadu":
        "Tamil Nadu / Bay of Bengal",

    "Kerala":
        "Kerala / Arabian Sea",

    "Karnataka":
        "Karnataka / Arabian Sea",

    "Gujarat":
        "Gujarat / Arabian Sea"
}


# ============================================================
# STATE REFERENCE LOCATIONS
#
# These are reference locations used to search the satellite
# dataset for state-level queries. For Kerala, (11.50, 72.20)
# points to the SE Arabian Sea / Lakshadweep Sea swath.
# ============================================================

STATE_REFERENCE_COORDINATES = {

    "Tamil Nadu": {
        "latitude": 13.08,
        "longitude": 80.27
    },

    "Kerala": {
        "latitude": 10.00,
        "longitude": 75.50
    },

    "Karnataka": {
        "latitude": 14.50,
        "longitude": 73.80
    },

    "Gujarat": {
        "latitude": 21.50,
        "longitude": 69.00
    }
}


# ============================================================
# ISRO OCEANSAT-3 (EOS-06) COMPLEMENTARY DATASETS
# ============================================================

EOS06_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "mosdac_downloads"
)

EOS06_FILES = {
    "Karnataka": os.path.join(
        EOS06_DIR,
        "E06OCML2OC_20260925_074358_051_014_360m_LAC_v1.0.0.nc"
    ),
    "Gujarat": os.path.join(
        EOS06_DIR,
        "E06OCML2OC_20260925_074039_051_013_360m_LAC_v1.0.0.nc"
    ),
    "Kerala": os.path.join(
        EOS06_DIR,
        "E06OCML2OC_20260925_074358_051_014_360m_LAC_v1.0.0.nc"
    ),
    "Tamil Nadu": os.path.join(
        EOS06_DIR,
        "E06OCML2OC_20260925_060423_064_014_360m_LAC_v1.0.0.nc"
    ),
}


def _format_eos06_timestamp(ds):
    """
    Construct ISO observation timestamp from EOS-06 metadata.
    """
    dop = ds.attrs.get("DateOfPass")
    sst = ds.attrs.get("Scene_Start_Time")
    if dop and sst:
        try:
            # dop format: "25-SEP-2026", sst format: "07:43:58:2591890890"
            parts = str(dop).split("-")
            if len(parts) == 3:
                day, mon_str, year = parts
                months = {
                    "JAN": "01", "FEB": "02", "MAR": "03", "APR": "04",
                    "MAY": "05", "JUN": "06", "JUL": "07", "AUG": "08",
                    "SEP": "09", "OCT": "10", "NOV": "11", "DEC": "12"
                }
                mm = months.get(mon_str.upper(), "09")
                time_parts = str(sst).split(":")
                hh = time_parts[0] if len(time_parts) > 0 else "00"
                mi = time_parts[1] if len(time_parts) > 1 else "00"
                ss = time_parts[2] if len(time_parts) > 2 else "00"
                return f"{year}-{mm}-{day.zfill(2)}T{hh}:{mi}:{ss}Z"
        except Exception:
            pass
    return ds.attrs.get("time_coverage_start") or ds.attrs.get("start_time") or "2026-09-25T07:43:00Z"


def extract_eos06_data(state, latitude, longitude, search_radius=2.0):
    eos_file = EOS06_FILES.get(state)
    if not eos_file or not os.path.exists(eos_file):
        return None
    try:
        ds = xr.open_dataset(eos_file)
        if "CHL" not in ds:
            ds.close()
            return None
        chl = ds["CHL"]
        lat_slice = slice(latitude + search_radius, latitude - search_radius)
        lon_slice = slice(longitude - search_radius, longitude + search_radius)
        nearby = chl.sel(latitude=lat_slice, longitude=lon_slice)
        vals = np.asarray(nearby.values, dtype=float)

        # STRICT QUALITY CONTROL:
        # Exclude NaN, infinite, out-of-range values, and ISRO OCM-3
        # unvalidated minimum boundary fill (0.0200 mg/m3).
        finite_mask = np.isfinite(vals) & (vals >= 0.001) & (vals <= 100.0)
        valid = vals[finite_mask & (~np.isclose(vals, 0.0200, atol=1e-4))]

        obs_time = _format_eos06_timestamp(ds)
        ds.close()

        if valid.size == 0:
            return None

        return {
            "satellite": "ISRO Oceansat-3 (EOS-06)",
            "agency": "ISRO / MOSDAC",
            "source": "ISRO Oceansat-3 (EOS-06) / MOSDAC",
            "value": float(np.mean(valid)),
            "valid_pixels": int(valid.size),
            "observation_time": str(obs_time),
            "message": "Real satellite-derived Chlorophyll-a observation retrieved from ISRO Oceansat-3 (EOS-06) dataset."
        }
    except Exception:
        return None


def extract_modis_data(latitude, longitude, search_radius=1.8):
    """
    Search available authoritative MODIS Aqua 8-day composite files
    in chronological order (most recent first) for valid unclouded
    marine observations.
    """
    for file_path in MODIS_COMPOSITE_FILES:
        if not os.path.exists(file_path):
            continue
        try:
            ds = xr.open_dataset(file_path)
            if "chlor_a" not in ds:
                ds.close()
                continue
            chl = ds["chlor_a"]
            nearby = chl.sel(
                lat=slice(latitude + search_radius, latitude - search_radius),
                lon=slice(longitude - search_radius, longitude + search_radius)
            )
            nearby_vals = np.asarray(nearby.values, dtype=float)

            # STRICT QUALITY CONTROL:
            # Exclude NaN, infinite, negative, out-of-range (>100), and
            # unvalidated 0.0200 boundary fill artifacts.
            finite_mask = (
                np.isfinite(nearby_vals)
                & (nearby_vals >= 0.001)
                & (nearby_vals <= 100.0)
            )
            valid = nearby_vals[
                finite_mask & (~np.isclose(nearby_vals, 0.0200, atol=1e-4))
            ]

            if valid.size > 0:
                obs_time = get_observation_time(ds)
                val = float(np.mean(valid))
                px_count = int(valid.size)
                ds.close()
                return {
                    "satellite": "MODIS Aqua",
                    "agency": "NASA Ocean Biology / INCOIS",
                    "source": "NASA Ocean Biology / MODIS Aqua",
                    "value": val,
                    "valid_pixels": px_count,
                    "observation_time": obs_time,
                    "message": "Real satellite-derived Chlorophyll-a observation retrieved from authoritative MODIS Aqua composite."
                }
            ds.close()
        except Exception:
            pass
    return None


# ============================================================
# OBSERVATION TIME HELPER
# ============================================================

def get_observation_time(ds):

    # --------------------------------------------------------
    # Try standard time coordinate
    # --------------------------------------------------------

    try:

        if "time" in ds.coords:

            time_value = ds["time"].values

            if np.size(time_value) > 0:

                return str(
                    np.asarray(time_value).reshape(-1)[0]
                )

    except Exception:
        pass

    # --------------------------------------------------------
    # Try common dataset attributes
    # --------------------------------------------------------

    possible_attributes = [

        "time_coverage_start",

        "time_coverage_end",

        "start_time",

        "end_time",

        "date_created",

        "time_start",

        "time_end"

    ]

    for attribute in possible_attributes:

        try:

            value = ds.attrs.get(attribute)

            if value:

                return str(value)

        except Exception:
            pass

    # --------------------------------------------------------
    # Search variable attributes
    # --------------------------------------------------------

    try:

        for variable_name in ds.variables:

            variable = ds[variable_name]

            for attribute in possible_attributes:

                value = variable.attrs.get(attribute)

                if value:

                    return str(value)

    except Exception:
        pass

    return None


def satellite_agent(
    state="Tamil Nadu",
    district=None,
    latitude=None,
    longitude=None
):

    # ========================================================
    # VALIDATE STATE
    # ========================================================

    if state not in REGION_MAP:

        return {

            "agent":
                "Satellite Agent",

            "status":
                "UNAVAILABLE",

            "data_status":
                "UNAVAILABLE",

            "state":
                state,

            "district":
                district,

            "message":
                "Unsupported region."
        }

    region = REGION_MAP[state]

    # Normalize district string
    if district is not None:
        district_str = str(district).strip()
        if not district_str or district_str.lower() in ("none", "null", "undefined", ""):
            district = None
        else:
            district = district_str

    # ========================================================
    # INLAND DISTRICT VERIFICATION (NO MARINE WATERS)
    #
    # Inland districts do NOT have marine waters or offshore
    # chlorophyll observations.
    # ========================================================

    if district is not None:
        state_coastal_set = COASTAL_DISTRICTS.get(state, set())
        if district not in state_coastal_set:
            return {
                "agent":
                    "Satellite Agent",

                "status":
                    "NO_VALID_OBSERVATION",

                "data_status":
                    "INLAND_DISTRICT",

                "state":
                    state,

                "district":
                    district,

                "region":
                    region,

                "chlorophyll_a_mg_m3":
                    None,

                "source":
                    "NASA Ocean Biology / MODIS Aqua & ISRO EOS-06",

                "message":
                    f"Inland district ({district}); no marine chlorophyll observation applicable."
            }

    # ========================================================
    # SELECT LOCATION COORDINATES
    #
    # If district is provided, lookup canonical coordinates.
    # Otherwise fallback to state-level reference location.
    # ========================================================

    if latitude is None or longitude is None:
        if district is not None and state in CANONICAL_DISTRICT_COORDS:
            district_coords = CANONICAL_DISTRICT_COORDS[state].get(district)
            if district_coords and len(district_coords) == 2:
                latitude, longitude = district_coords[0], district_coords[1]

    if latitude is None or longitude is None:
        reference = STATE_REFERENCE_COORDINATES[state]
        latitude = reference["latitude"]
        longitude = reference["longitude"]

    latitude = float(latitude)
    longitude = float(longitude)

    # Search radius:
    # For district-level marine queries: 1.5 degrees (~160 km) ensures
    # sampling of the local coastal marine zone without bleeding into
    # other states' offshore domains.
    # For state-level regional queries: 3.0 degrees for MODIS, 1.8 degrees for EOS-06.
    if district is not None:
        search_radius = 1.5
        eos_search_radius = 1.5
    else:
        search_radius = 3.0
        eos_search_radius = 1.8

    # ========================================================
    # SATELLITE DATA EXTRACTION (AUTHORITATIVE OBSERVATIONS)
    #
    # 1. Search available INCOIS / NASA MODIS Aqua 8-day composites
    #    in chronological order (Oct 08, Oct 05, Oct 01, Sep 27).
    # 2. If all MODIS composites are cloud-masked at this location,
    #    fallback to ISRO Oceansat-3 (EOS-06) optical swath.
    # 3. Strictly reject unvalidated 0.0200 boundary fill values.
    # ========================================================

    try:
        modis_res = extract_modis_data(latitude, longitude, search_radius=search_radius)

        if modis_res is not None:
            return {
                "agent":
                    "Satellite Agent",

                "status":
                    "SUCCESS",

                "data_status":
                    "REAL_SATELLITE_DATA",

                "state":
                    state,

                "district":
                    district,

                "region":
                    region,

                "satellite":
                    modis_res["satellite"],

                "agency":
                    modis_res["agency"],

                "parameter":
                    "Chlorophyll-a",

                "chlorophyll_a_mg_m3":
                    round(modis_res["value"], 4),

                "latitude":
                    latitude,

                "longitude":
                    longitude,

                "valid_pixels":
                    modis_res["valid_pixels"],

                "observation_time":
                    modis_res["observation_time"],

                "source":
                    modis_res["source"],

                "message":
                    modis_res["message"]
            }

        # Check complementary ISRO Oceansat-3 (EOS-06) dataset
        eos_result = extract_eos06_data(state, latitude, longitude, search_radius=eos_search_radius)

        if eos_result is not None:
            return {
                "agent":
                    "Satellite Agent",

                "status":
                    "SUCCESS",

                "data_status":
                    "REAL_SATELLITE_DATA",

                "state":
                    state,

                "district":
                    district,

                "region":
                    region,

                "satellite":
                    eos_result["satellite"],

                "agency":
                    eos_result["agency"],

                "parameter":
                    "Chlorophyll-a",

                "chlorophyll_a_mg_m3":
                    round(eos_result["value"], 4),

                "latitude":
                    latitude,

                "longitude":
                    longitude,

                "valid_pixels":
                    eos_result["valid_pixels"],

                "observation_time":
                    eos_result["observation_time"],

                "source":
                    eos_result["source"],

                "message":
                    eos_result["message"]
            }

        # Honest NO_VALID_OBSERVATION when truly obscured by clouds / no valid pixels
        return {
            "agent":
                "Satellite Agent",

            "status":
                "NO_VALID_OBSERVATION",

            "data_status":
                "NO_VALID_OBSERVATION",

            "state":
                state,

            "district":
                district,

            "region":
                region,

            "chlorophyll_a_mg_m3":
                None,

            "latitude":
                latitude,

            "longitude":
                longitude,

            "source":
                "MODIS Aqua / NASA Ocean Biology & ISRO EOS-06",

            "message":
                (
                    "No valid unclouded marine Chlorophyll-a observation "
                    "was found around the selected location in available "
                    "satellite passes (MODIS Aqua and ISRO EOS-06). "
                    "Cloud-masked and unvalidated boundary values were excluded; "
                    "no value was substituted or invented."
                )
        }

    # ========================================================
    # ERROR HANDLING
    # ========================================================

    except Exception as e:

        return {

            "agent":
                "Satellite Agent",

            "status":
                "ERROR",

            "data_status":
                "READ_ERROR",

            "state":
                state,

            "district":
                district,

            "region":
                region,

            "latitude":
                latitude,

            "longitude":
                longitude,

            "message":
                str(e)
        }


# ============================================================
# DIRECT TEST
# ============================================================

if __name__ == "__main__":

    print(
        "=============================================="
    )

    print(
        "ORCA SATELLITE AGENT TEST"
    )

    print(
        "=============================================="
    )

    for state in [
        "Tamil Nadu",
        "Kerala",
        "Karnataka",
        "Gujarat"
    ]:

        print()
        print(
            "----------------------------------------------"
        )

        print(
            f"Testing: {state}"
        )

        result = satellite_agent(
            state
        )

        for key, value in result.items():

            print(
                f"{key}: {value}"
            )

    print()
    print(
        "=============================================="
    )