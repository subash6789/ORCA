def gis_agent(state="Tamil Nadu"):

    region_map = {
        "Tamil Nadu": {
            "location": "Chennai",
            "latitude": 13.0827,
            "longitude": 80.2707,
            "marine_region": "Bay of Bengal"
        },

        "Kerala": {
            "location": "Thiruvananthapuram",
            "latitude": 8.5241,
            "longitude": 76.9366,
            "marine_region": "Arabian Sea"
        },

        "Karnataka": {
            "location": "Mangaluru",
            "latitude": 12.9141,
            "longitude": 74.8560,
            "marine_region": "Arabian Sea"
        },

        "Gujarat": {
            "location": "Ahmedabad",
            "latitude": 23.0225,
            "longitude": 72.5714,
            "marine_region": "Arabian Sea"
        }
    }

    if state not in region_map:
        return {
            "agent": "GIS Agent",
            "status": "UNAVAILABLE",
            "data_status": "UNAVAILABLE",
            "state": state,
            "message": "GIS region is not configured."
        }

    data = region_map[state]

    return {
        "agent": "GIS Agent",
        "status": "SUCCESS",
        "data_status": "MAPPED",

        "state": state,

        "location": data["location"],
        "latitude": data["latitude"],
        "longitude": data["longitude"],
        "marine_region": data["marine_region"],
        "country": "India",

        "source": "ORCA GIS Agent",

        "message": (
            "GIS location and marine-region mapping is available "
            "for the selected region."
        )
    }


if __name__ == "__main__":

    for state in [
        "Tamil Nadu",
        "Kerala",
        "Karnataka",
        "Gujarat"
    ]:
        print(gis_agent(state))