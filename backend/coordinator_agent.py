from ocean_agent import ocean_agent
from weather_agent import weather_agent
from gis_agent import gis_agent
from pfz_agent import pfz_agent
from safety_agent import safety_agent
from satellite_agent import satellite_agent
from language_agent import language_agent


# ============================================================
# ORCA PHASE 8 — COORDINATOR / REASONING AGENT
# ============================================================


def coordinator_agent(
    question="",
    state="Tamil Nadu",
    district=""
):

    question = question or ""
    state = state or "Tamil Nadu"
    district = district or ""
    question_lower = question.lower()

    # ========================================================
    # LANGUAGE DETECTION
    # ========================================================

    language_result = language_agent(question)

    detected_language = language_result.get(
        "detected_language",
        "English"
    )

    # ========================================================
    # KEYWORD GROUPS
    # ========================================================

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
        "fishing zone",
        "potential fishing zone"
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
        "ocean color",
        "remote sensing",
        "chlorophyll"
    ]

    broad_condition_keywords = [
        "condition",
        "status",
        "situation",
        "marine condition",
        "overall condition",
        "marine status",
        "overall status"
    ]

    # ========================================================
    # SELECT AGENTS
    # ========================================================

    selected_agents = []

    if any(word in question_lower for word in ocean_keywords):
        selected_agents.append("Ocean Agent")

    if any(word in question_lower for word in weather_keywords):
        selected_agents.append("Weather Agent")

    if any(word in question_lower for word in gis_keywords):
        selected_agents.append("GIS Agent")

    if any(word in question_lower for word in pfz_keywords):
        selected_agents.append("PFZ Agent")

    if any(word in question_lower for word in safety_keywords):
        selected_agents.append("Safety Agent")

    if any(word in question_lower for word in satellite_keywords):
        selected_agents.append("Satellite Agent")

    # ========================================================
    # BROAD MARINE QUESTION
    # ========================================================

    if any(
        word in question_lower
        for word in broad_condition_keywords
    ):

        selected_agents = [
            "Ocean Agent",
            "Weather Agent",
            "GIS Agent",
            "PFZ Agent",
            "Safety Agent",
            "Satellite Agent"
        ]

    # ========================================================
    # DEFAULT — RUN ALL SPECIALIZED AGENTS
    # ========================================================

    if not selected_agents:

        selected_agents = [
            "Ocean Agent",
            "Weather Agent",
            "GIS Agent",
            "PFZ Agent",
            "Safety Agent",
            "Satellite Agent"
        ]

    # Remove duplicates while preserving order

    selected_agents = list(
        dict.fromkeys(selected_agents)
    )

    # ========================================================
    # RUN SPECIALIZED AGENTS
    # ========================================================

    results = {}

    # District-aware agents
    if "Ocean Agent" in selected_agents:

        results["ocean"] = ocean_agent(
            state,
            district
        )

    if "Weather Agent" in selected_agents:

        results["weather"] = weather_agent(
            state,
            district
        )

    if "GIS Agent" in selected_agents:

        results["gis"] = gis_agent(
            state,
            district
        )

    if "PFZ Agent" in selected_agents:

        results["pfz"] = pfz_agent(
            state,
            district
        )

    # State-level agents
    if "Safety Agent" in selected_agents:

        results["safety"] = safety_agent(
            state,
            district
        )

    if "Satellite Agent" in selected_agents:

        results["satellite"] = satellite_agent(
            state,
            district
        )

    # ========================================================
    # EVIDENCE COLLECTION
    # ========================================================

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

                source = "ORCA Ocean Agent / INCOIS"

            elif agent_name == "weather":

                source = "Open-Meteo"

            elif agent_name == "gis":

                source = "ORCA GIS Agent"

            elif agent_name == "pfz":

                source = "INCOIS Potential Fishing Zone Advisory"

            elif agent_name == "satellite":

                source = "NASA Ocean Biology / MODIS Aqua"

            elif agent_name == "safety":

                source = [
                    "ORCA Ocean Agent",
                    "ORCA Weather Agent",
                    "INCOIS RSMC / WW3"
                ]

        evidence.append({

            "agent": agent_result.get(
                "agent",
                agent_name
            ),

            "status": agent_result.get(
                "status",
                "UNKNOWN"
            ),

            "data_status": data_status,

            "source": source
        })

    # ========================================================
    # EVIDENCE SUMMARY
    #
    # Frontend categories preserved:
    # OBSERVED, CURRENT_WEATHER, FORECAST, MAPPED,
    # INTEGRATION READY, DEMO_RULE, UNAVAILABLE.
    # Each evaluated agent is counted exactly once.
    # ========================================================

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

        status = item.get(
            "data_status",
            "UNAVAILABLE"
        )

        agent_run_status = item.get(
            "status",
            "UNKNOWN"
        )

        # Check for genuine failure / unavailable source first
        if agent_run_status in ("ERROR", "NO_DATA", "FAILED") or status in ("UNAVAILABLE", "ERROR", "NO_DATA"):

            evidence_summary["UNAVAILABLE"] += 1

        elif status in ("OBSERVED", "REAL_SATELLITE_DATA"):

            evidence_summary["OBSERVED"] += 1

        elif status in ("CURRENT_WEATHER", "OBSERVED_AND_FORECAST"):

            evidence_summary["CURRENT_WEATHER"] += 1

        elif status == "FORECAST":

            evidence_summary["FORECAST"] += 1

        elif status in ("MAPPED", "CURRENT_ADVISORY", "INLAND_DISTRICT"):

            evidence_summary["MAPPED"] += 1

        elif status == "INTEGRATION READY":

            evidence_summary["INTEGRATION READY"] += 1

        elif status in ("DEMO_RULE", "ORCA_HEURISTIC", "HEURISTIC_RULE"):

            evidence_summary["DEMO_RULE"] += 1

        else:

            evidence_summary["UNAVAILABLE"] += 1

    # ========================================================
    # EXTRACT SAFETY INFORMATION
    # ========================================================

    safety_result = results.get(
        "safety",
        {}
    )

    safety_status = safety_result.get(
        "safety_status"
    )

    forecast_decision = safety_result.get(
        "forecast_decision_support",
        {}
    )

    # ========================================================
    # EXTRACT REAL INCOIS FORECAST FROM OCEAN AGENT
    # ========================================================
    #
    # Ocean Agent returns forecast data as:
    #
    # incois_wind_forecast
    # incois_wave_forecast
    #
    # Do not expect a generic "forecast" object.
    # ========================================================

    ocean_result = results.get(
        "ocean",
        {}
    )

    incois_wind_forecast = {}

    incois_wave_forecast = {}

    if isinstance(ocean_result, dict):

        incois_wind_forecast = ocean_result.get(
            "incois_wind_forecast",
            {}
        )

        incois_wave_forecast = ocean_result.get(
            "incois_wave_forecast",
            {}
        )

    if not isinstance(incois_wind_forecast, dict):

        incois_wind_forecast = {}

    if not isinstance(incois_wave_forecast, dict):

        incois_wave_forecast = {}

    forecast_wind = incois_wind_forecast.get(
        "wind_speed_ms"
    )

    forecast_wave = incois_wave_forecast.get(
        "wave_height_m"
    )

    forecast_time = (
        incois_wind_forecast.get("forecast_time")
        or incois_wave_forecast.get("forecast_time")
    )

    wind_source = incois_wind_forecast.get(
        "source"
    )

    wave_source = incois_wave_forecast.get(
        "source"
    )

    # Safety Agent can still provide forecast values.
    # Use them only as fallback if Ocean Agent forecast
    # values are unavailable.

    if forecast_wind is None:

        forecast_wind = forecast_decision.get(
            "wind_speed_ms"
        )

    if forecast_wave is None:

        forecast_wave = forecast_decision.get(
            "wave_height_m"
        )

    if forecast_time is None:

        forecast_time = forecast_decision.get(
            "forecast_time"
        )

    if wind_source is None:

        wind_source = forecast_decision.get(
            "wind_source"
        )

    if wave_source is None:

        wave_source = forecast_decision.get(
            "wave_source"
        )

    # ========================================================
    # BUILD EXPLAINABLE REASONING
    # ========================================================

    reasoning_points = []

    # --------------------------------------------------------
    # Ocean reasoning
    # --------------------------------------------------------

    if ocean_result.get("status") == "SUCCESS":

        sst = ocean_result.get(
            "sea_surface_temperature_c"
        )

        current = ocean_result.get(
            "current_speed_ms"
        )

        chlorophyll = ocean_result.get(
            "chlorophyll"
        )

        if sst is not None:

            reasoning_points.append(
                f"Ocean observation reports SST "
                f"of {sst} °C."
            )

        if current is not None:

            reasoning_points.append(
                f"Observed ocean current is "
                f"{current} m/s."
            )

        if isinstance(chlorophyll, dict):

            chl_value = chlorophyll.get(
                "chlorophyll_mg_m3"
            )

            if chl_value is not None:

                reasoning_points.append(
                    f"Satellite-derived chlorophyll "
                    f"data is available at "
                    f"{chl_value} mg/m³."
                )

    # --------------------------------------------------------
    # Weather reasoning
    # --------------------------------------------------------

    weather_result = results.get(
        "weather",
        {}
    )

    if weather_result.get("status") == "SUCCESS":

        current_weather = weather_result.get(
            "current_weather",
            {}
        )

        temperature = current_weather.get(
            "temperature_c"
        )

        wind = current_weather.get(
            "wind_speed_kmh"
        )

        precipitation = current_weather.get(
            "precipitation_mm"
        )

        if temperature is not None:

            reasoning_points.append(
                f"Current weather temperature is "
                f"{temperature} °C."
            )

        if wind is not None:

            reasoning_points.append(
                f"Current weather wind speed is "
                f"{wind} km/h."
            )

        if precipitation is not None:

            reasoning_points.append(
                f"Current precipitation is "
                f"{precipitation} mm."
            )

    # --------------------------------------------------------
    # GIS reasoning
    # --------------------------------------------------------

    gis_result = results.get(
        "gis",
        {}
    )

    if gis_result.get("status") == "SUCCESS":

        location = gis_result.get(
            "location"
        )

        marine_region = gis_result.get(
            "marine_region"
        )

        gis_district = gis_result.get(
            "district",
            district
        )

        if location or marine_region:

            if gis_district:

                reasoning_points.append(
                    f"GIS context: district={gis_district}, "
                    f"location={location}, "
                    f"marine region={marine_region}."
                )

            else:

                reasoning_points.append(
                    f"GIS context: location={location}, "
                    f"marine region={marine_region}."
                )

    # --------------------------------------------------------
    # PFZ reasoning
    # --------------------------------------------------------

    pfz_result = results.get(
        "pfz",
        {}
    )

    if pfz_result.get("status") == "SUCCESS":

        pfz_count = pfz_result.get(
            "pfz_count",
            0
        )

        reasoning_points.append(
            f"INCOIS PFZ advisory data is available "
            f"with {pfz_count} PFZ location(s)."
        )

    elif pfz_result:

        reasoning_points.append(
            "No confirmed PFZ advisory data is "
            "available from the PFZ Agent."
        )

    # --------------------------------------------------------
    # Forecast reasoning
    # --------------------------------------------------------

    if forecast_wind is not None:

        reasoning_points.append(
            f"INCOIS forecast wind is "
            f"{forecast_wind} m/s."
        )

    if forecast_wave is not None:

        reasoning_points.append(
            f"INCOIS forecast wave height is "
            f"{forecast_wave} m."
        )

    # --------------------------------------------------------
    # Safety reasoning
    # --------------------------------------------------------

    if safety_status == "WARNING":

        reasoning_points.append(
            "Safety Agent triggered a warning "
            "condition based on ORCA project-level "
            "decision-support rules."
        )

    elif safety_status == "CAUTION":

        reasoning_points.append(
            "Safety Agent identified a caution "
            "condition based on ORCA project-level "
            "decision-support rules."
        )

    elif safety_status == "NO_RULE_TRIGGERED":

        reasoning_points.append(
            "No configured ORCA project-level safety "
            "rule was triggered by the available "
            "current and forecast values."
        )

    # ========================================================
    # FINAL REASONING STATUS
    # ========================================================

    if safety_status == "WARNING":

        reasoning_status = "WARNING"

    elif safety_status == "CAUTION":

        reasoning_status = "CAUTION"

    elif reasoning_points:

        reasoning_status = "INFORMATION_AVAILABLE"

    else:

        reasoning_status = "INSUFFICIENT_DATA"

    # ========================================================
    # EXPLAINABLE REASONING MESSAGE
    # ========================================================

    if reasoning_points:

        area_text = state

        if district:

            area_text = f"{district}, {state}"

        reasoning_summary = (
            f"ORCA analyzed {len(results)} specialized "
            f"agent result(s) for {area_text}. "
            f"The combined evidence indicates: "
            + " ".join(reasoning_points)
        )

    else:

        reasoning_summary = (
            "ORCA could not generate a detailed reasoning "
            "summary because sufficient agent data was "
            "not available."
        )

    # ========================================================
    # TRANSPARENCY / DISCLAIMER
    # ========================================================

    disclaimer = (
        "ORCA reasoning is a decision-support layer based "
        "on available agent data and configured project "
        "rules. It does not replace official government, "
        "INCOIS or other authorized marine warnings."
    )

    # ========================================================
    # FINAL COORDINATOR RESPONSE
    # ========================================================

    return {

        "agent": "ORCA Coordinator",

        "status": "SUCCESS",

        "data_status": "MULTI_AGENT_INTEGRATED",

        "question": question,

        "state": state,

        "district": district,

        # ----------------------------------------------------
        # LANGUAGE
        # ----------------------------------------------------

        "language": {

            "detected_language": detected_language,

            "supported_languages":
                language_result.get(
                    "supported_languages",
                    [
                        "English",
                        "Tamil"
                    ]
                )
        },

        # ----------------------------------------------------
        # AGENT SELECTION
        # ----------------------------------------------------

        "selected_agents": selected_agents,

        "agent_count": len(results),

        # ----------------------------------------------------
        # RAW AGENT RESULTS
        # ----------------------------------------------------

        "results": results,

        # ----------------------------------------------------
        # EVIDENCE
        # ----------------------------------------------------

        "evidence": evidence,

        "evidence_summary": evidence_summary,

        # ----------------------------------------------------
        # PHASE 8 REASONING
        # ----------------------------------------------------

        "reasoning": {

            "status": reasoning_status,

            "summary": reasoning_summary,

            "points": reasoning_points,

            "safety_status": safety_status,

            "forecast": {

                "wind_speed_ms":
                    forecast_wind,

                "wave_height_m":
                    forecast_wave,

                "forecast_time":
                    forecast_time,

                "wind_source":
                    wind_source,

                "wave_source":
                    wave_source
            }
        },

        # ----------------------------------------------------
        # TRANSPARENCY
        # ----------------------------------------------------

        "disclaimer": disclaimer,

        "message": (
            "ORCA Coordinator successfully combined "
            "specialized marine agents, collected evidence, "
            "and generated an explainable decision-support "
            "reasoning summary."
        )
    }


# ============================================================
# DIRECT TEST
# ============================================================

if __name__ == "__main__":

    print("==============================================")
    print("ORCA PHASE 8 COORDINATOR TEST")
    print("==============================================")

    result = coordinator_agent(
        question="What are the overall marine conditions?",
        state="Tamil Nadu",
        district="Salem"
    )

    print()
    print("STATUS:")
    print(result.get("status"))

    print()
    print("LANGUAGE:")
    print(result.get("language"))

    print()
    print("SELECTED AGENTS:")
    print(result.get("selected_agents"))

    print()
    print("AGENT COUNT:")
    print(result.get("agent_count"))

    print()
    print("DISTRICT:")
    print(result.get("district"))

    print()
    print("EVIDENCE SUMMARY:")
    print(result.get("evidence_summary"))

    print()
    print("REASONING STATUS:")
    print(
        result.get("reasoning", {}).get(
            "status"
        )
    )

    print()
    print("REASONING SUMMARY:")
    print(
        result.get("reasoning", {}).get(
            "summary"
        )
    )

    print()
    print("FORECAST:")
    print(
        result.get("reasoning", {}).get(
            "forecast"
        )
    )

    print()
    print("DISCLAIMER:")
    print(result.get("disclaimer"))

    print()
    print("==============================================")
    print("COORDINATOR TEST COMPLETED")
    print("==============================================")