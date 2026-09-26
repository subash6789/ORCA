def satellite_agent(state="Tamil Nadu"):

    region_map = {
        "Tamil Nadu": "Tamil Nadu / Bay of Bengal",
        "Kerala": "Kerala / Arabian Sea",
        "Karnataka": "Karnataka / Arabian Sea",
        "Gujarat": "Gujarat / Arabian Sea"
    }

    if state not in region_map:
        return {
            "agent": "Satellite Agent",
            "status": "UNAVAILABLE",
            "data_status": "UNAVAILABLE",
            "state": state,
            "message": "Unsupported region"
        }

    region = region_map[state]

    return {
        "agent": "Satellite Agent",
        "status": "SUCCESS",
        "data_status": "INTEGRATION READY",

        "state": state,
        "region": region,

        "satellite": "EOS-06 (Oceansat-3)",
        "agency": "ISRO",

        "mission": "Ocean observation and ocean colour monitoring",

        "data_types": [
            "Ocean Colour",
            "Ocean Surface Wind"
        ],

        "satellite_observation": None,

        "source": "ISRO / MOSDAC EOS-06",

        "message": (
            "EOS-06 satellite data is identified as an authorized "
            "integration source. No live satellite observation is "
            "claimed until the authorized data product is retrieved."
        )
    }


if __name__ == "__main__":

    result = satellite_agent("Tamil Nadu")

    print("===== ORCA SATELLITE AGENT =====")

    for key, value in result.items():
        print(f"{key}: {value}")