def gis_agent():
    # ORCA GIS information for Chennai / Bay of Bengal

    return {
        "agent": "GIS Agent",
        "status": "SUCCESS",
        "location": "Chennai",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "marine_region": "Bay of Bengal",
        "country": "India"
    }


if __name__ == "__main__":
    result = gis_agent()

    print("===== ORCA GIS AGENT =====")

    for key, value in result.items():
        print(f"{key}: {value}")