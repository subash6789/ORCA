from db_connection import get_connection


# =========================================================
# ORCA PFZ SECTOR DEFINITIONS & COASTAL DISTRICT MAPPING
#
# INCOIS Marine Fisheries Advisory defines specific coastal
# sectors for peninsular India (SEC001-SEC014).
# In Tamil Nadu, INCOIS partitions the coastline into:
# - North Tamil Nadu (Coromandel coast from Chennai south to Cuddalore)
# - South Tamil Nadu (Palk Strait & Gulf of Mannar down to Kanniyakumari)
# =========================================================

NORTH_TN_COASTAL_DISTRICTS = {
    "Thiruvallur",
    "Chennai",
    "Chengalpattu",
    "Villupuram",
    "Cuddalore"
}

SOUTH_TN_COASTAL_DISTRICTS = {
    "Nagapattinam",
    "Mayiladuthurai",
    "Thiruvarur",
    "Thanjavur",
    "Pudukkottai",
    "Ramanathapuram",
    "Tuticorin",
    "Tirunelveli",
    "Kanniyakumari"
}

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
    "Tamil Nadu": NORTH_TN_COASTAL_DISTRICTS | SOUTH_TN_COASTAL_DISTRICTS
}

PFZ_REGION_MAP = {
    "Tamil Nadu": "North Tamil Nadu",
    "Kerala": "Kerala",
    "Karnataka": "Karnataka",
    "Gujarat": "Gujarat",
}


# =========================================================
# GET PFZ SECTOR
# =========================================================

def get_pfz_sector(state, district=None):

    if state == "Tamil Nadu" and district:
        if district in SOUTH_TN_COASTAL_DISTRICTS:
            return "South Tamil Nadu"
        elif district in NORTH_TN_COASTAL_DISTRICTS:
            return "North Tamil Nadu"

    return PFZ_REGION_MAP.get(
        state,
        state
    )


# =========================================================
# GET PFZ ADVISORY DATA (CURRENT / VALID ADVISORIES ONLY)
# =========================================================

def get_pfz_data(sector):

    conn = get_connection()
    cur = conn.cursor()

    try:

        # Select only active advisories matching the latest advisory date
        # for this sector. This separates historical records from current ones.
        cur.execute(
            """
            SELECT
                latitude,
                longitude,
                advisory_date,
                source,
                retrieved_at,
                valid_upto
            FROM pfz_advisory
            WHERE sector = %s
              AND advisory_date = (
                  SELECT MAX(advisory_date)
                  FROM pfz_advisory
                  WHERE sector = %s
              )
            ORDER BY retrieved_at DESC, id DESC
            """,
            (sector, sector)
        )

        rows = cur.fetchall()

    finally:

        cur.close()
        conn.close()

    locations = []

    for row in rows:

        locations.append({
            "latitude": row[0],
            "longitude": row[1],
            "advisory_date": row[2].isoformat() if hasattr(row[2], "isoformat") else str(row[2]),
            "source": row[3],
            "retrieved_at": row[4].isoformat() if hasattr(row[4], "isoformat") else str(row[4]),
            "valid_upto": row[5].isoformat() if hasattr(row[5], "isoformat") else str(row[5]) if row[5] else None
        })

    return locations


# =========================================================
# ORCA PFZ AGENT
# =========================================================

def pfz_agent(
    state="Tamil Nadu",
    district=""
):

    try:

        state = str(state or "").strip()
        district = str(district or "").strip() if district else None

        # -------------------------------------------------
        # Verify inland vs coastal status
        # -------------------------------------------------
        if district:
            state_coastal = COASTAL_DISTRICTS.get(state, set())
            if district not in state_coastal:
                return {
                    "agent": "PFZ Agent",
                    "status": "NO_VALID_OBSERVATION",
                    "data_status": "INLAND_DISTRICT",
                    "state": state,
                    "district": district,
                    "pfz_sector": None,
                    "region": state,
                    "pfz_available": False,
                    "pfz_count": 0,
                    "locations": [],
                    "source": "INCOIS Potential Fishing Zone Advisory",
                    "message": (
                        f"Inland district ({district}); Potential Fishing Zone marine advisories "
                        "do not apply to non-coastal areas."
                    )
                }

        # -------------------------------------------------
        # Resolve PFZ sector
        # -------------------------------------------------

        sector = get_pfz_sector(state, district)

        # -------------------------------------------------
        # Retrieve real, active PFZ advisory records
        # -------------------------------------------------

        locations = get_pfz_data(sector)

        # -------------------------------------------------
        # No PFZ data for this sector
        # -------------------------------------------------

        if not locations:

            return {
                "agent": "PFZ Agent",
                "status": "NO_DATA",
                "data_status": "UNAVAILABLE",
                "state": state,
                "district": district if district else None,
                "pfz_sector": sector,
                "region": state,
                "pfz_available": False,
                "pfz_count": 0,
                "locations": [],
                "source":
                    "INCOIS Potential Fishing Zone Advisory",
                "message":
                    (
                        f"No currently valid PFZ advisory data is "
                        f"available for {sector}."
                    )
            }

        # -------------------------------------------------
        # Latest advisory information
        # -------------------------------------------------

        latest = locations[0]

        latest_date = latest.get(
            "advisory_date"
        )

        valid_upto = latest.get(
            "valid_upto"
        )

        latest_source = latest.get(
            "source"
        )

        latest_retrieved = latest.get(
            "retrieved_at"
        )

        # -------------------------------------------------
        # Successful PFZ response (Current valid bulletin)
        # -------------------------------------------------

        return {

            "agent":
                "PFZ Agent",

            "status":
                "SUCCESS",

            "data_status":
                "CURRENT_ADVISORY",

            "state":
                state,

            "district":
                district if district else None,

            "region":
                state,

            "pfz_sector":
                sector,

            "pfz_available":
                True,

            "pfz_count":
                len(locations),

            "locations":
                locations,

            "latest_advisory_date":
                latest_date,

            "valid_upto":
                valid_upto,

            "source":
                latest_source
                or "INCOIS Potential Fishing Zone Advisory",

            "retrieved_at":
                latest_retrieved,

            "message":
                (
                    f"INCOIS PFZ advisory data retrieved "
                    f"successfully for {sector}. "
                    f"{len(locations)} active PFZ locations available."
                )
        }

    # -----------------------------------------------------
    # Database / system error
    # -----------------------------------------------------

    except Exception as e:

        return {

            "agent":
                "PFZ Agent",

            "status":
                "ERROR",

            "data_status":
                "UNAVAILABLE",

            "state":
                state,

            "district":
                district if district else None,

            "pfz_sector":
                get_pfz_sector(state, district),

            "pfz_available":
                False,

            "pfz_count":
                0,

            "locations":
                [],

            "source":
                "INCOIS Potential Fishing Zone Advisory",

            "message":
                "Unable to retrieve PFZ advisory data.",

            "error":
                str(e)
        }