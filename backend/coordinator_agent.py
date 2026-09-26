from ocean_agent import ocean_agent
from weather_agent import weather_agent
from gis_agent import gis_agent
from pfz_agent import pfz_agent
from safety_agent import safety_agent
from satellite_agent import satellite_agent


def coordinator_agent(
    question="",
    state="Tamil Nadu"
):

    question_lower = question.lower()

    ocean_keywords = [
        "ocean",
        "sea",
        "sst",
        "salinity",
        "current",
        "sea height",
        "sea surface",
        "mld",
        "marine condition",
        "ocean condition"
    ]

    weather_keywords = [
        "weather",
        "rain",
        "wind",
        "humidity",
        "forecast",
        "temperature",
        "climate"
    ]

    gis_keywords = [
        "location",
        "map",
        "where",
        "coordinates",
        "latitude",
        "longitude",
        "near chennai"
    ]

    pfz_keywords = [
        "pfz",
        "fishing",
        "fish",
        "fishing zone"
    ]

    safety_keywords = [
        "safe",
        "safety",
        "danger",
        "warning",
        "alert",
        "storm",
        "risk"
    ]

    satellite_keywords = [
        "satellite",
        "isro",
        "eos-06",
        "oceansat",
        "ocean colour",
        "remote sensing"
    ]

    broad_condition_keywords = [
        "condition",
        "status",
        "situation",
        "marine condition",
        "overall condition"
    ]

    selected_agents = []

    if any(word in question_lower for word in ocean_keywords):
        selected_agents.append("Ocean Agent")

    if any(word in question_lower for word in weather_keywords):
        selected_agents.append("Weather Agent")

    if any(word in question_lower for word in gis_keywords):
        selected_agents.append("GIS Agent")

    if any(word in question_lower for word in pfz_keywords):
        selected_agents.append("Fishing Agent")

    if any(word in question_lower for word in safety_keywords):
        selected_agents.append("Safety Agent")

    if any(word in question_lower for word in satellite_keywords):
        selected_agents.append("Satellite Agent")

    if any(word in question_lower for word in broad_condition_keywords):

        selected_agents = [
            "Ocean Agent",
            "Weather Agent",
            "GIS Agent",
            "Fishing Agent",
            "Safety Agent",
            "Satellite Agent"
        ]

    if not selected_agents:

        selected_agents = [
            "Ocean Agent",
            "Weather Agent",
            "GIS Agent",
            "Fishing Agent",
            "Safety Agent",
            "Satellite Agent"
        ]

    selected_agents = list(
        dict.fromkeys(selected_agents)
    )

    # =========================================================
    # RUN SPECIALIZED AGENTS USING SELECTED REGION
    # =========================================================

    results = {}

    if "Ocean Agent" in selected_agents:
        results["ocean"] = ocean_agent(state)

    if "Weather Agent" in selected_agents:
        results["weather"] = weather_agent(state)

    if "GIS Agent" in selected_agents:
        results["gis"] = gis_agent(state)

    if "Fishing Agent" in selected_agents:
        results["pfz"] = pfz_agent(state)

    if "Safety Agent" in selected_agents:
        results["safety"] = safety_agent(state)

    if "Satellite Agent" in selected_agents:
        results["satellite"] = satellite_agent(state)

    # =========================================================
    # EVIDENCE COLLECTION
    # =========================================================

    evidence = []

    for agent_name, agent_result in results.items():

        if not isinstance(agent_result, dict):
            continue

        data_status = agent_result.get(
            "data_status",
            "UNAVAILABLE"
        )

        source = agent_result.get("source")

        if source is None:

            if agent_name == "ocean":
                source = "ORCA Ocean Database"

            elif agent_name == "weather":
                source = "Open-Meteo"

            elif agent_name == "pfz":
                source = "INCOIS PFZ Advisory"

            elif agent_name == "satellite":
                source = "ISRO / MOSDAC EOS-06"

            elif agent_name == "safety":
                source = [
                    "ORCA Ocean Agent",
                    "ORCA Weather Agent"
                ]

            elif agent_name == "gis":
                source = "ORCA GIS Agent"

        evidence.append({
            "agent": agent_result.get(
                "agent",
                agent_name
            ),
            "data_status": data_status,
            "source": source
        })

    # =========================================================
    # EVIDENCE SUMMARY
    # =========================================================

    evidence_summary = {
        "OBSERVED": 0,
        "CURRENT_WEATHER": 0,
        "FORECAST": 0,
        "MAPPED": 0,
        "INTEGRATION READY": 0,
        "DEMO_RULE": 0,
        "UNAVAILABLE": 0
    }

    for item in evidence:

        status = item["data_status"]

        if status in evidence_summary:

            evidence_summary[status] += 1

        else:

            evidence_summary["UNAVAILABLE"] += 1

    # =========================================================
    # FINAL COORDINATOR RESPONSE
    # =========================================================

    return {

        "agent": "ORCA Coordinator",

        "status": "SUCCESS",

        "question": question,

        "state": state,

        "selected_agents": selected_agents,

        "results": results,

        "evidence": evidence,

        "evidence_summary": evidence_summary,

        "message": (
            "ORCA Coordinator combined the selected "
            "specialized agent results for the requested "
            "region and tracked their data-source status. "
            "Unavailable or unverified information is not "
            "presented as a confirmed live observation."
        )
    }