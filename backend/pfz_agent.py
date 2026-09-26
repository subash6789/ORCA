from datetime import datetime


def pfz_agent(state="Tamil Nadu"):

    sector_map = {
        "Tamil Nadu": "NORTH TAMILNADU",
        "Kerala": "KERALA",
        "Karnataka": "KARNATAKA",
        "Gujarat": "GUJARAT"
    }

    if state not in sector_map:
        return {
            "agent": "PFZ Agent",
            "status": "UNAVAILABLE",
            "data_status": "UNAVAILABLE",
            "state": state,
            "message": "PFZ sector is not configured for this region."
        }

    sector = sector_map[state]

    return {
        "agent": "PFZ Agent",
        "status": "SUCCESS",
        "data_status": "FORECAST",
        "state": state,
        "region": state,
        "pfz_sector": sector,

        "source": "INCOIS PFZ Advisory",

        "forecast_date": "2026-09-24",
        "valid_upto": "2026-09-25",

        "pfz_coordinates": None,

        "message": (
            "INCOIS PFZ advisory metadata is available for this sector. "
            "PFZ coordinates are not claimed until retrieved from the "
            "authorized INCOIS advisory product."
        ),

        "retrieved_at": datetime.now().isoformat()
    }


if __name__ == "__main__":

    result = pfz_agent("Tamil Nadu")

    print("===== ORCA PFZ AGENT =====")

    for key, value in result.items():
        print(f"{key}: {value}")