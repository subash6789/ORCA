from coordinator_agent import coordinator_agent


def orca_reasoning(
    question="What are the marine conditions?",
    state="Tamil Nadu"
):
    # =========================================================
    # 1. RUN ORCA COORDINATOR
    # =========================================================

    result = coordinator_agent(
        question,
        state
    )

    if not isinstance(result, dict):
        return {
            "agent": "ORCA Reasoning Layer",
            "status": "ERROR",
            "question": question,
            "message": "Invalid coordinator response."
        }
    # =========================================================
    # 2. GET COORDINATOR RESULTS
    # =========================================================

    agent_results = result.get(
        "results",
        {}
    )

    ocean = agent_results.get("ocean")
    weather = agent_results.get("weather")
    gis = agent_results.get("gis")
    pfz = agent_results.get("pfz")
    safety = agent_results.get("safety")
    satellite = agent_results.get("satellite")


    # =========================================================
    # 3. SELECTED AGENTS
    # =========================================================

    selected_agents = result.get(
        "selected_agents",
        []
    )


    # =========================================================
    # 4. REASONING POINTS
    # =========================================================

    reasoning_points = []


    # ---------------------------------------------------------
    # OCEAN REASONING
    # ---------------------------------------------------------

    if ocean:

        sst = ocean.get(
            "sea_surface_temperature_c"
        )

        current = ocean.get(
            "current_speed_ms"
        )

        salinity = ocean.get(
            "salinity"
        )

        mld = ocean.get(
            "mixed_layer_depth_m"
        )

        if sst is not None:

            if sst < 20:

                reasoning_points.append(
                    f"Ocean temperature is relatively low at {sst} °C."
                )

            elif sst < 28:

                reasoning_points.append(
                    f"Ocean temperature is moderate at {sst} °C."
                )

            else:

                reasoning_points.append(
                    f"Ocean temperature is relatively high at {sst} °C."
                )


        if current is not None:

            reasoning_points.append(
                f"Observed ocean current speed is {current} m/s."
            )


        if salinity is not None:

            reasoning_points.append(
                f"Observed sea-water salinity is {salinity}."
            )


        if mld is not None:

            reasoning_points.append(
                f"Observed mixed layer depth is {mld} m."
            )


    # ---------------------------------------------------------
    # WEATHER REASONING
    # ---------------------------------------------------------

    if weather:

        temperature = weather.get(
            "temperature_c"
        )

        wind = weather.get(
            "wind_speed_kmh"
        )

        rain = weather.get(
            "precipitation_mm"
        )


        if temperature is not None:

            reasoning_points.append(
                f"Current weather temperature is {temperature} °C."
            )


        if wind is not None:

            if wind >= 40:

                reasoning_points.append(
                    f"High wind speed is reported at {wind} km/h."
                )

            else:

                reasoning_points.append(
                    f"Current wind speed is {wind} km/h."
                )


        if rain is not None:

            if rain > 0:

                reasoning_points.append(
                    f"Current precipitation is {rain} mm."
                )

            else:

                reasoning_points.append(
                    "No current precipitation is reported."
                )


    # ---------------------------------------------------------
    # GIS REASONING
    # ---------------------------------------------------------

    if gis:

        location = gis.get(
            "location"
        )

        marine_region = gis.get(
            "marine_region"
        )

        if location or marine_region:

            reasoning_points.append(
                f"GIS context: location={location}, "
                f"marine region={marine_region}."
            )


    # ---------------------------------------------------------
    # PFZ REASONING
    # ---------------------------------------------------------

    pfz_status = (
        "PFZ information not available."
    )

    if pfz:

        pfz_sector = pfz.get(
            "pfz_sector"
        )

        pfz_data_status = pfz.get(
            "data_status",
            "UNAVAILABLE"
        )

        pfz_message = pfz.get(
            "message",
            ""
        )

        pfz_status = (
            f"PFZ data status: "
            f"{pfz_data_status}."
        )

        if pfz_sector:

            pfz_status += (
                f" Sector: {pfz_sector}."
            )

        if pfz_message:

            pfz_status += (
                f" {pfz_message}"
            )

        reasoning_points.append(
            pfz_status
        )


    # ---------------------------------------------------------
    # SATELLITE REASONING
    # ---------------------------------------------------------

    satellite_status = (
        "Satellite information not available."
    )

    if satellite:

        satellite_data_status = satellite.get(
            "data_status",
            "UNAVAILABLE"
        )

        satellite_name = satellite.get(
            "satellite",
            "Satellite source"
        )

        satellite_status = (
            f"Satellite data status: "
            f"{satellite_data_status}. "
            f"Source: {satellite_name}."
        )

        reasoning_points.append(
            satellite_status
        )


    # ---------------------------------------------------------
    # SAFETY REASONING
    # ---------------------------------------------------------

    safety_status = (
        "Safety data not available."
    )

    alerts = []

    if safety:

        safety_state = safety.get(
            "safety_status",
            "UNAVAILABLE"
        )

        alerts = safety.get(
            "alerts",
            []
        )

        if alerts:

            safety_status = (
                f"Safety status: {safety_state}. "
                + " ".join(alerts)
            )

        else:

            safety_status = (
                f"Safety status: {safety_state}. "
                "No current ORCA demo-rule alert was triggered."
            )

        reasoning_points.append(
            safety_status
        )


    # =========================================================
    # 5. EVIDENCE SUMMARY
    # =========================================================

    evidence_summary = result.get(
        "evidence_summary",
        {}
    )

    observed = evidence_summary.get(
        "OBSERVED",
        0
    )

    current_weather = evidence_summary.get(
        "CURRENT_WEATHER",
        0
    )

    forecast = evidence_summary.get(
        "FORECAST",
        0
    )

    mapped = evidence_summary.get(
        "MAPPED",
        0
    )

    integration_ready = evidence_summary.get(
        "INTEGRATION READY",
        0
    )

    demo_rule = evidence_summary.get(
        "DEMO_RULE",
        0
    )

    unavailable = evidence_summary.get(
        "UNAVAILABLE",
        0
    )


    evidence_point = (
        "Evidence summary: "
        f"{observed} observed source(s), "
        f"{current_weather} current-weather source(s), "
        f"{forecast} forecast source(s), "
        f"{integration_ready} integration-ready source(s), "
        f"{demo_rule} demo-rule source(s), "
        f"{unavailable} unavailable source(s)."
    )

    reasoning_points.append(
        evidence_point
    )


    # =========================================================
    # 6. EVIDENCE COLLECTION
    # =========================================================

    evidence = result.get(
        "evidence",
        []
    )


    # =========================================================
    # 7. CONFIDENCE CALCULATION
    # =========================================================

    total_agents = 0
    successful_agents = 0


    # Coordinator returns six specialized agents.
    # We also include their actual result availability.

    specialized_results = [
        ocean,
        weather,
        gis,
        pfz,
        safety,
        satellite
    ]


    for agent_result in specialized_results:

        total_agents += 1

        if (
            isinstance(agent_result, dict)
            and agent_result.get("status") == "SUCCESS"
        ):

            successful_agents += 1


    # Language information is not counted as one of
    # the six marine specialized agents.

    if total_agents > 0:

        agent_success_percentage = round(
            (
                successful_agents
                / total_agents
            ) * 100
        )

    else:

        agent_success_percentage = 0


    # ---------------------------------------------------------
    # Evidence score
    # ---------------------------------------------------------

    total_evidence = (
        observed
        + mapped
        + integration_ready
        + demo_rule
    )


    if total_evidence > 0:

        evidence_score = round(

            (
                (observed * 1.0)
                +
                (mapped * 0.8)
                +
                (integration_ready * 0.5)
                +
                (demo_rule * 0.4)
            )
            /
            total_evidence
            * 100

        )

    else:

        evidence_score = 0


    # ---------------------------------------------------------
    # Overall confidence
    # ---------------------------------------------------------

    confidence_percentage = round(

        (
            agent_success_percentage
            * 0.6
        )
        +
        (
            evidence_score
            * 0.4
        )

    )


    if confidence_percentage >= 85:

        confidence_level = "High"

    elif confidence_percentage >= 65:

        confidence_level = "Moderate"

    else:

        confidence_level = "Limited"


    confidence = {

        "successful_agents":
            successful_agents,

        "total_agents":
            total_agents,

        "agent_success_percentage":
            agent_success_percentage,

        "evidence_score":
            evidence_score,

        "confidence_percentage":
            confidence_percentage,

        "confidence_level":
            confidence_level,

        "method": (
            "Confidence combines successful "
            "specialized-agent execution with "
            "evidence quality. Observed data "
            "receives stronger evidence weight "
            "than mapped, integration-ready, "
            "or demo-rule information."
        )
    }


    # =========================================================
    # 8. FINAL ASSESSMENT
    # =========================================================

    if alerts:

        final_assessment = (

            "ORCA combined the available ocean, "
            "weather, GIS, PFZ, satellite and "
            "safety information through the "
            "collaborative agent system. "

            "One or more conditions triggered "
            "the current ORCA demo safety rules. "

            "This is decision support and is "
            "not an official government warning."

        )

    else:

        final_assessment = (

            "ORCA combined the available ocean, "
            "weather, GIS, PFZ, satellite and "
            "safety information through the "
            "collaborative agent system. "

            "No current ORCA demo-rule safety "
            "alert was triggered by the "
            "available data."

        )


    # =========================================================
    # 9. FINAL RESPONSE
    # =========================================================

    return {

        "agent":
            "ORCA Reasoning Layer",

        "status":
            "SUCCESS",

        "question":
            question,

        "selected_agents":
            selected_agents,

        "reasoning_points":
            reasoning_points,

        "safety_assessment":
            safety_status,

        "pfz_assessment":
            pfz_status,

        "satellite_assessment":
            satellite_status,

        "evidence_summary":
            evidence_summary,

        "evidence":
            evidence,

        "confidence":
            confidence,

        "final_assessment":
            final_assessment,

        "source_note": (

            "ORCA reasoning is decision support "
            "based on connected data sources and "
            "their reported data-status categories. "

            "Observed ocean and weather information "
            "is distinguished from forecast, mapped, "
            "integration-ready and demo-rule evidence. "

            "Safety results are generated from ORCA "
            "demo rules and are not official "
            "government warnings."

        )
    }


# =========================================================
# DIRECT TEST
# =========================================================

if __name__ == "__main__":

    result = orca_reasoning(
        "What is the overall marine condition?"
    )

    print()
    print("==========================================")
    print("ORCA AI REASONING LAYER")
    print("==========================================")

    print()
    print("STATUS:")
    print(result["status"])

    print()
    print("SELECTED AGENTS:")
    print(result["selected_agents"])

    print()
    print("REASONING POINTS:")

    for point in result["reasoning_points"]:

        print("-", point)

    print()
    print("EVIDENCE SUMMARY:")
    print(result["evidence_summary"])

    print()
    print("CONFIDENCE:")
    print(result["confidence"])

    print()
    print("FINAL ASSESSMENT:")
    print(result["final_assessment"])

    print()
    print("==========================================")
    print("TEST COMPLETE")
    print("==========================================")