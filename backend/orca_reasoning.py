from coordinator_agent import coordinator_agent


def orca_reasoning(question=""):

    result = coordinator_agent(question)

    ocean = result["agent_results"].get("ocean")
    weather = result["agent_results"].get("weather")
    gis = result["agent_results"].get("gis")
    safety = result["agent_results"].get("safety")
    pfz = result["agent_results"].get("pfz")

    reasoning_points = []

    # -----------------------------
    # OCEAN REASONING
    # -----------------------------

    if ocean:

        sst = ocean.get("sea_surface_temperature_c")
        current = ocean.get("current_speed_ms")
        salinity = ocean.get("salinity")

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
                f"Average ocean current speed is {current} m/s."
            )

        if salinity is not None:

            reasoning_points.append(
                f"Sea-water salinity is {salinity}."
            )


    # -----------------------------
    # WEATHER REASONING
    # -----------------------------

    if weather:

        temperature = weather.get("temperature_c")
        wind = weather.get("wind_speed_kmh")
        rain = weather.get("precipitation_mm")

        if temperature is not None:

            reasoning_points.append(
                f"Current air temperature is {temperature} °C."
            )

        if wind is not None:

            if wind >= 40:

                reasoning_points.append(
                    f"Strong wind detected at {wind} km/h."
                )

            else:

                reasoning_points.append(
                    f"Wind speed is {wind} km/h."
                )

        if rain is not None:

            if rain > 0:

                reasoning_points.append(
                    f"Precipitation is {rain} mm."
                )

            else:

                reasoning_points.append(
                    "No precipitation is currently reported."
                )


    # -----------------------------
    # GIS REASONING
    # -----------------------------

    if gis:

        reasoning_points.append(
            f"Location identified as {gis.get('location')} "
            f"in the {gis.get('marine_region')}."
        )


    # -----------------------------
    # SAFETY REASONING
    # -----------------------------

    safety_status = "No safety data available."

    if safety:

        alerts = safety.get("alerts", [])

        if alerts:

            safety_status = " ".join(alerts)

        else:

            safety_status = (
                "No immediate warning condition detected."
            )

        reasoning_points.append(
            f"Safety assessment: {safety_status}"
        )


    # -----------------------------
    # PFZ REASONING
    # -----------------------------

    pfz_status = "PFZ information not available."

    if pfz:

        pfz_available = pfz.get(
            "pfz_available",
            "Information unavailable"
        )

        pfz_message = pfz.get(
            "message",
            ""
        )

        pfz_status = (
            f"PFZ status: {pfz_available}. "
            f"{pfz_message}"
        )

        reasoning_points.append(
            pfz_status
        )


    # -----------------------------
    # FINAL ASSESSMENT
    # -----------------------------

    if safety and any(
        "warning" in str(alert).lower()
        or "danger" in str(alert).lower()
        or "risk" in str(alert).lower()
        for alert in safety.get("alerts", [])
    ):

        final_assessment = (
            "ORCA identifies a potential safety concern. "
            "Users should verify official marine warnings "
            "before making decisions."
        )

    else:

        final_assessment = (
            "ORCA combines ocean, weather, GIS, PFZ and "
            "safety information to provide a marine "
            "decision-support assessment. No immediate "
            "warning condition was detected by the current "
            "demo safety rules."
        )


    # -----------------------------
    # RETURN RESULT
    # -----------------------------

    return {

        "agent": "ORCA Reasoning Layer",

        "status": "SUCCESS",

        "question": question,

        "selected_agents": result["selected_agents"],

        "reasoning_points": reasoning_points,

        "safety_assessment": safety_status,

        "pfz_assessment": pfz_status,

        "final_assessment": final_assessment,

        "source_note": (
            "ORCA reasoning is decision support based on "
            "the connected data sources. Safety results "
            "are not official government warnings."
        )
    }