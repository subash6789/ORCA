from ocean_agent import ocean_agent
from weather_agent import weather_agent
from gis_agent import gis_agent
from pfz_agent import pfz_agent
from safety_agent import safety_agent


def coordinator_agent(question=""):
    question_lower = question.lower()

    ocean_keywords = [
        "ocean", "sea", "sst", "salinity",
        "current", "sea height", "sea surface",
        "mld", "marine condition", "ocean condition"
    ]

    weather_keywords = [
        "weather", "rain", "wind", "humidity",
        "forecast", "temperature", "climate"
    ]

    gis_keywords = [
        "location", "map", "where", "coordinates",
        "latitude", "longitude", "near chennai"
    ]

    pfz_keywords = [
        "pfz", "fishing", "fish", "fishing zone"
    ]

    safety_keywords = [
        "safe", "safety", "danger", "warning",
        "alert", "storm", "risk"
    ]

    broad_condition_keywords = [
        "condition", "status", "situation"
    ]

    selected_agents = []

    # Ocean Agent
    if any(word in question_lower for word in ocean_keywords):
        selected_agents.append("Ocean Agent")

    # Weather Agent
    if any(word in question_lower for word in weather_keywords):
        selected_agents.append("Weather Agent")

    # GIS Agent
    if any(word in question_lower for word in gis_keywords):
        selected_agents.append("GIS Agent")

    # PFZ Agent
    if any(word in question_lower for word in pfz_keywords):
        selected_agents.append("PFZ Agent")

    # Safety Agent
    if any(word in question_lower for word in safety_keywords):
        selected_agents.append("Safety Agent")

    # Broad marine condition questions
    if any(word in question_lower for word in broad_condition_keywords):
        selected_agents = [
            "Ocean Agent",
            "Weather Agent",
            "GIS Agent",
            "Safety Agent"
        ]

    # If nothing matches, use the main marine agents
    if not selected_agents:
        selected_agents = [
            "Ocean Agent",
            "Weather Agent",
            "GIS Agent"
        ]

    results = {}

    if "Ocean Agent" in selected_agents:
        results["ocean"] = ocean_agent()

    if "Weather Agent" in selected_agents:
        results["weather"] = weather_agent()

    if "GIS Agent" in selected_agents:
        results["gis"] = gis_agent()

    if "PFZ Agent" in selected_agents:
        results["pfz"] = pfz_agent()

    if "Safety Agent" in selected_agents:
        results["safety"] = safety_agent()

    return {
        "agent": "Coordinator / Planner Agent",
        "status": "SUCCESS",
        "question": question,
        "selected_agents": selected_agents,
        "agent_results": results
    }