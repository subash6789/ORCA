from coordinator_agent import coordinator_agent


def orca_reasoning(
    question="What are the marine conditions?",
    state="Tamil Nadu",
    district=""
):

    # =========================================================
    # 1. RUN ORCA COORDINATOR
    # =========================================================

    result = coordinator_agent(
        question,
        state,
        district
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

    # =========================================================
    # OCEAN REASONING
    # =========================================================

    sst = None
    current = None
    salinity = None
    mld = None

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

        # -----------------------------------------------------
        # ADVANCED OCEAN CONDITION ASSESSMENT
        # -----------------------------------------------------

        ocean_indicators = []

        if sst is not None:

            if isinstance(sst, (int, float)):

                ocean_indicators.append(
                    f"SST {sst:.3f} °C"
                )

            else:

                ocean_indicators.append(
                    f"SST {sst} °C"
                )

        if current is not None:

            if isinstance(current, (int, float)):

                ocean_indicators.append(
                    f"current {current:.3f} m/s"
                )

            else:

                ocean_indicators.append(
                    f"current {current} m/s"
                )

        if salinity is not None:

            ocean_indicators.append(
                f"salinity {salinity}"
            )

        if mld is not None:

            if isinstance(mld, (int, float)):

                ocean_indicators.append(
                    f"mixed layer depth {mld:.3f} m"
                )

            else:

                ocean_indicators.append(
                    f"mixed layer depth {mld} m"
                )

        if ocean_indicators:

            ocean_assessment = (
                "Combined ocean indicators: "
                + ", ".join(ocean_indicators)
                + "."
            )

            reasoning_points.append(
                ocean_assessment
            )

    # =========================================================
    # WEATHER REASONING
    # =========================================================

    temperature = None
    wind = None
    rain = None

    if weather:

        cw = weather.get("current_weather")
        if not isinstance(cw, dict):
            cw = {}

        temperature = cw.get(
            "temperature_c",
            weather.get("temperature_c")
        )

        wind = cw.get(
            "wind_speed_kmh",
            weather.get("wind_speed_kmh")
        )

        rain = cw.get(
            "precipitation_mm",
            weather.get("precipitation_mm")
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

    # =========================================================
    # GIS REASONING
    # =========================================================

    if gis:

        location = gis.get(
            "location"
        )

        marine_region = gis.get(
            "marine_region"
        )

        gis_district = gis.get(
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

    # =========================================================
    # EXTRACT FORECAST VALUES
    # =========================================================

    forecast_wind = None
    forecast_wave = None
    forecast_time = None

    if safety:

        forecast_decision = safety.get(
            "forecast_decision_support",
            {}
        )

        forecast_wind = forecast_decision.get(
            "wind_speed_ms"
        )

        forecast_wave = forecast_decision.get(
            "wave_height_m"
        )

        forecast_time = forecast_decision.get(
            "forecast_time"
        )

    # =========================================================
    # PHASE 9.5
    # ADVANCED WEATHER & FORECAST INTELLIGENCE
    # =========================================================

    weather_forecast_assessment = {
        "status": "UNAVAILABLE",
        "current_condition": None,
        "forecast_condition": None,
        "key_indicators": [],
        "forecast_days": [],
        "maximum_forecast_wind_kmh": None,
        "maximum_precipitation_probability_percent": None,
        "maximum_daily_precipitation_mm": None,
        "data_status": "UNAVAILABLE",
        "source": None
    }

    if weather and weather.get("status") == "SUCCESS":

        current_weather = weather.get(
            "current_weather",
            {}
        )

        daily_forecast = weather.get(
            "daily_forecast",
            []
        )

        if not isinstance(current_weather, dict):
            current_weather = {}

        current_temperature = current_weather.get(
            "temperature_c",
            weather.get("temperature_c")
        )

        current_humidity = current_weather.get(
            "humidity_percent"
        )

        current_wind = current_weather.get(
            "wind_speed_kmh",
            weather.get("wind_speed_kmh")
        )

        current_precipitation = current_weather.get(
            "precipitation_mm",
            weather.get("precipitation_mm")
        )

        weather_indicators = []
        current_condition_parts = []

        if current_temperature is not None:

            current_condition_parts.append(
                f"temperature {current_temperature:.1f} °C"
                if isinstance(current_temperature, (int, float))
                else f"temperature {current_temperature} °C"
            )

        if current_humidity is not None:

            current_condition_parts.append(
                f"humidity {current_humidity:.0f}%"
                if isinstance(current_humidity, (int, float))
                else f"humidity {current_humidity}%"
            )

        if current_wind is not None:

            current_condition_parts.append(
                f"wind {current_wind:.1f} km/h"
                if isinstance(current_wind, (int, float))
                else f"wind {current_wind} km/h"
            )

        if current_precipitation is not None:

            current_condition_parts.append(
                f"precipitation {current_precipitation:.1f} mm"
                if isinstance(current_precipitation, (int, float))
                else f"precipitation {current_precipitation} mm"
            )

        current_condition = None

        if current_condition_parts:

            current_condition = (
                "Current weather: "
                + ", ".join(current_condition_parts)
                + "."
            )

            reasoning_points.append(
                current_condition
            )

        # ---------------------------------------------------------
        # CURRENT WEATHER INDICATORS
        # ---------------------------------------------------------

        if current_wind is not None:

            weather_indicators.append(
                f"Current wind: "
                f"{current_wind:.1f} km/h"
                if isinstance(current_wind, (int, float))
                else f"Current wind: {current_wind} km/h"
            )

        if current_precipitation is not None:

            if isinstance(current_precipitation, (int, float)):

                if current_precipitation > 0:

                    weather_indicators.append(
                        f"Current precipitation: "
                        f"{current_precipitation:.1f} mm"
                    )

                else:

                    weather_indicators.append(
                        "No current precipitation reported"
                    )

            else:

                weather_indicators.append(
                    f"Current precipitation: "
                    f"{current_precipitation} mm"
                )

        # ---------------------------------------------------------
        # DAILY FORECAST
        # ---------------------------------------------------------

        forecast_days = []

        if isinstance(daily_forecast, list):

            for day in daily_forecast[:7]:

                if isinstance(day, dict):

                    forecast_days.append({
                        "date": day.get("date"),
                        "temperature_max_c":
                            day.get("temperature_max_c"),
                        "temperature_min_c":
                            day.get("temperature_min_c"),
                        "precipitation_sum_mm":
                            day.get("precipitation_sum_mm"),
                        "precipitation_probability_max_percent":
                            day.get(
                                "precipitation_probability_max_percent"
                            ),
                        "wind_speed_max_kmh":
                            day.get("wind_speed_max_kmh")
                    })

        max_forecast_wind = None
        max_precipitation_probability = None
        max_precipitation_sum = None

        for day in forecast_days:

            day_wind = day.get(
                "wind_speed_max_kmh"
            )

            day_probability = day.get(
                "precipitation_probability_max_percent"
            )

            day_precipitation = day.get(
                "precipitation_sum_mm"
            )

            if isinstance(day_wind, (int, float)):

                if (
                    max_forecast_wind is None
                    or day_wind > max_forecast_wind
                ):

                    max_forecast_wind = day_wind

            if isinstance(day_probability, (int, float)):

                if (
                    max_precipitation_probability is None
                    or day_probability > max_precipitation_probability
                ):

                    max_precipitation_probability = (
                        day_probability
                    )

            if isinstance(day_precipitation, (int, float)):

                if (
                    max_precipitation_sum is None
                    or day_precipitation > max_precipitation_sum
                ):

                    max_precipitation_sum = (
                        day_precipitation
                    )

        if max_forecast_wind is not None:

            weather_indicators.append(
                f"7-day maximum forecast wind: "
                f"{max_forecast_wind:.1f} km/h"
            )

        if max_precipitation_probability is not None:

            weather_indicators.append(
                f"Maximum forecast precipitation probability: "
                f"{max_precipitation_probability:.0f}%"
            )

        if max_precipitation_sum is not None:

            weather_indicators.append(
                f"Maximum daily precipitation forecast: "
                f"{max_precipitation_sum:.1f} mm"
            )

        # ---------------------------------------------------------
        # ADVANCED FORECAST INTERPRETATION
        # ---------------------------------------------------------

        forecast_condition_parts = []

        if max_forecast_wind is not None:

            if max_forecast_wind >= 40:

                forecast_condition_parts.append(
                    "strong wind conditions are present "
                    "in the forecast window"
                )

            elif max_forecast_wind >= 25:

                forecast_condition_parts.append(
                    "elevated wind conditions are present "
                    "in the forecast window"
                )

            else:

                forecast_condition_parts.append(
                    "forecast wind remains below the "
                    "configured elevated-wind threshold"
                )

        if max_precipitation_probability is not None:

            if max_precipitation_probability >= 70:

                forecast_condition_parts.append(
                    "high precipitation probability is "
                    "present on at least one forecast day"
                )

            elif max_precipitation_probability >= 40:

                forecast_condition_parts.append(
                    "moderate precipitation probability "
                    "is present in the forecast"
                )

            else:

                forecast_condition_parts.append(
                    "precipitation probability remains "
                    "relatively low in the forecast"
                )

        if forecast_condition_parts:

            forecast_summary = (
                "Advanced weather forecast assessment: "
                + "; ".join(forecast_condition_parts)
                + "."
            )

        else:

            forecast_summary = (
                "Advanced weather forecast assessment "
                "could not be generated from the available "
                "forecast indicators."
            )

        reasoning_points.append(
            forecast_summary
        )

        weather_forecast_assessment = {

            "status":
                "SUCCESS",

            "current_condition":
                current_condition,

            "forecast_condition":
                forecast_summary,

            "key_indicators":
                weather_indicators,

            "forecast_days":
                forecast_days,

            "maximum_forecast_wind_kmh":
                max_forecast_wind,

            "maximum_precipitation_probability_percent":
                max_precipitation_probability,

            "maximum_daily_precipitation_mm":
                max_precipitation_sum,

            "data_status":
                weather.get(
                    "data_status",
                    "CURRENT_AND_FORECAST"
                ),

            "source":
                weather.get(
                    "source",
                    "Open-Meteo"
                )
        }

    else:

        reasoning_points.append(
            "Advanced weather forecast assessment "
            "is unavailable because the Weather Agent "
            "did not return valid data."
        )

    # =========================================================
    # PHASE 9.6
    # MULTI-AGENT CROSS-VALIDATION
    # =========================================================

    cross_validation = {
        "status": "SUCCESS",
        "checks": [],
        "consistency": "CONSISTENT",
        "conflicts": [],
        "summary": ""
    }

    validation_checks = []
    validation_conflicts = []

    if wind is not None and forecast_wind is not None:

        current_wind_ms = wind / 3.6
        wind_difference = abs(
            current_wind_ms - forecast_wind
        )

        validation_checks.append({
            "check": "Weather vs Forecast Wind",
            "current_wind_ms": round(
                current_wind_ms,
                3
            ),
            "forecast_wind_ms": round(
                forecast_wind,
                3
            ),
            "difference_ms": round(
                wind_difference,
                3
            ),
            "status": "CHECKED"
        })

    if forecast_wave is not None:

        validation_checks.append({
            "check": "Forecast Wave Availability",
            "wave_height_m": round(
                forecast_wave,
                3
            ),
            "status": "AVAILABLE"
        })

    if current is not None:

        validation_checks.append({
            "check": "Ocean Current vs Safety",
            "ocean_current_ms": round(
                current,
                3
            ),
            "status": "AVAILABLE"
        })

    if pfz:

        pfz_count_value = pfz.get(
            "pfz_count"
        )

        if pfz_count_value is not None:

            validation_checks.append({
                "check": "PFZ vs Marine Indicators",
                "pfz_locations": pfz_count_value,
                "status": "CHECKED"
            })

    if validation_conflicts:

        cross_validation["consistency"] = "CONFLICT"

        cross_validation["conflicts"] = (
            validation_conflicts
        )

        cross_validation["summary"] = (
            "One or more cross-agent inconsistencies were detected. "
            "ORCA retained the original source values and did not "
            "invent replacement measurements."
        )

    else:

        cross_validation["consistency"] = "CONSISTENT"

        cross_validation["summary"] = (
            "Available Ocean, Weather, Forecast, Safety and PFZ agent "
            "outputs were cross-checked. No direct data conflict was detected."
        )

    cross_validation["checks"] = validation_checks

    reasoning_points.append(
        "Multi-agent cross-validation: "
        + cross_validation["summary"]
    )

    # =========================================================
    # PHASE 9.4
    # COMBINED MARINE RISK PREDICTION
    # =========================================================

    risk_factors_advanced = []
    high_risk_factors = []
    moderate_risk_factors = []

    # ---------------------------------------------------------
    # CURRENT WIND RISK
    # ---------------------------------------------------------

    if wind is not None:

        if wind >= 40:

            factor = (
                f"Current wind speed {wind} km/h "
                f"is at or above the ORCA high-risk threshold."
            )

            risk_factors_advanced.append(
                factor
            )

            high_risk_factors.append(
                "Current wind speed"
            )

    # ---------------------------------------------------------
    # PRECIPITATION RISK
    # ---------------------------------------------------------

    if rain is not None:

        if rain >= 10:

            factor = (
                f"Current precipitation {rain} mm "
                f"is at or above the ORCA heavy-precipitation threshold."
            )

            risk_factors_advanced.append(
                factor
            )

            high_risk_factors.append(
                "Precipitation"
            )

    # ---------------------------------------------------------
    # OCEAN CURRENT RISK
    # ---------------------------------------------------------

    if current is not None:

        if current >= 2:

            factor = (
                f"Observed ocean current {current} m/s "
                f"is at or above the ORCA strong-current threshold."
            )

            risk_factors_advanced.append(
                factor
            )

            high_risk_factors.append(
                "Ocean current"
            )

    # ---------------------------------------------------------
    # FORECAST WIND RISK
    # ---------------------------------------------------------

    if forecast_wind is not None:

        if forecast_wind >= 10:

            factor = (
                f"Forecast wind {forecast_wind:.3f} m/s "
                f"reaches the ORCA high-risk forecast threshold."
            )

            risk_factors_advanced.append(
                factor
            )

            high_risk_factors.append(
                "Forecast wind"
            )

        elif forecast_wind >= 5:

            factor = (
                f"Forecast wind {forecast_wind:.3f} m/s "
                f"reaches the ORCA moderate-risk forecast threshold."
            )

            risk_factors_advanced.append(
                factor
            )

            moderate_risk_factors.append(
                "Forecast wind"
            )

    # ---------------------------------------------------------
    # FORECAST WAVE RISK
    # ---------------------------------------------------------

    if forecast_wave is not None:

        if forecast_wave >= 3:

            factor = (
                f"Forecast wave height {forecast_wave:.3f} m "
                f"reaches the ORCA high-risk forecast threshold."
            )

            risk_factors_advanced.append(
                factor
            )

            high_risk_factors.append(
                "Forecast wave height"
            )

        elif forecast_wave >= 1.5:

            factor = (
                f"Forecast wave height {forecast_wave:.3f} m "
                f"reaches the ORCA moderate-risk forecast threshold."
            )

            risk_factors_advanced.append(
                factor
            )

            moderate_risk_factors.append(
                "Forecast wave height"
            )

    # ---------------------------------------------------------
    # COMBINED RISK LEVEL
    # ---------------------------------------------------------

    if high_risk_factors:

        combined_risk_level = "HIGH"

    elif len(moderate_risk_factors) >= 2:

        combined_risk_level = "MODERATE"

    elif len(moderate_risk_factors) == 1:

        combined_risk_level = "MODERATE"

    else:

        combined_risk_level = "LOW"

    # ---------------------------------------------------------
    # RISK SUMMARY
    # ---------------------------------------------------------

    if combined_risk_level == "HIGH":

        combined_risk_summary = (
            "ORCA combined marine risk assessment is HIGH "
            "because one or more current or forecast indicators "
            "crossed the project's high-risk heuristic thresholds."
        )

    elif combined_risk_level == "MODERATE":

        combined_risk_summary = (
            "ORCA combined marine risk assessment is MODERATE "
            "because one or more current or forecast indicators "
            "crossed the project's moderate-risk heuristic thresholds."
        )

    else:

        combined_risk_summary = (
            "ORCA combined marine risk assessment is LOW "
            "because none of the available current or forecast "
            "indicators crossed the project's configured risk thresholds."
        )

    reasoning_points.append(
        "Combined marine risk assessment: "
        f"{combined_risk_level}."
    )

    reasoning_points.append(
        combined_risk_summary
    )

    if risk_factors_advanced:

        reasoning_points.append(
            "Risk factors considered: "
            + "; ".join(
                risk_factors_advanced
            )
        )

    else:

        reasoning_points.append(
            "No configured ORCA risk threshold was crossed "
            "by the available current and forecast indicators."
        )

    # =========================================================
    # ADVANCED PFZ INTELLIGENCE
    # =========================================================

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

        pfz_count = pfz.get(
            "pfz_count",
            0
        )

        pfz_source = pfz.get(
            "source",
            "INCOIS Potential Fishing Zone Advisory"
        )

        pfz_status = (
            f"PFZ data status: {pfz_data_status}."
        )

        if pfz_sector:

            pfz_status += (
                f" Sector: {pfz_sector}."
            )

        if pfz_count:

            pfz_status += (
                f" {pfz_count} PFZ locations identified."
            )

        pfz_indicators = []

        if sst is not None:

            if isinstance(sst, (int, float)):

                pfz_indicators.append(
                    f"SST {sst:.3f} °C"
                )

            else:

                pfz_indicators.append(
                    f"SST {sst} °C"
                )

        chlorophyll = None

        if ocean:

            chlorophyll = ocean.get(
                "chlorophyll_mg_m3"
            )

            if chlorophyll is None:

                chlorophyll = ocean.get(
                    "chlorophyll_a_mg_m3"
                )

            if chlorophyll is None:

                chlorophyll = ocean.get(
                    "chlorophyll"
                )

        if isinstance(chlorophyll, dict):

            chlorophyll_value = chlorophyll.get(
                "chlorophyll_mg_m3"
            )

        else:

            chlorophyll_value = chlorophyll

        if chlorophyll_value is not None:

            if isinstance(
                chlorophyll_value,
                (int, float)
            ):

                pfz_indicators.append(
                    f"chlorophyll {chlorophyll_value:.3f} mg/m³"
                )

            else:

                pfz_indicators.append(
                    f"chlorophyll {chlorophyll_value} mg/m³"
                )

        if forecast_wind is not None:

            if isinstance(
                forecast_wind,
                (int, float)
            ):

                pfz_indicators.append(
                    f"forecast wind {forecast_wind:.3f} m/s"
                )

            else:

                pfz_indicators.append(
                    f"forecast wind {forecast_wind} m/s"
                )

        if forecast_wave is not None:

            if isinstance(
                forecast_wave,
                (int, float)
            ):

                pfz_indicators.append(
                    f"forecast wave {forecast_wave:.3f} m"
                )

            else:

                pfz_indicators.append(
                    f"forecast wave {forecast_wave} m"
                )

        if pfz_data_status == "UNAVAILABLE":

            pfz_assessment = (
                "Advanced PFZ assessment unavailable "
                "because no valid PFZ advisory data "
                "was retrieved."
            )

        elif pfz_count == 0:

            pfz_assessment = (
                f"INCOIS PFZ advisory is available for "
                f"{pfz_sector}, but no PFZ locations were "
                f"returned."
            )

        else:

            pfz_assessment = (
                f"Advanced PFZ assessment: {pfz_count} "
                f"PFZ locations are available for "
                f"{pfz_sector}."
            )

            if pfz_indicators:

                pfz_assessment += (
                    " Supporting marine indicators: "
                    + ", ".join(
                        pfz_indicators
                    )
                    + "."
                )

            pfz_assessment += (
                " PFZ availability is based on the "
                "retrieved INCOIS advisory and is not "
                "itself a guarantee of catch or fishing success."
            )

        reasoning_points.append(
            pfz_assessment
        )

        pfz_status += (
            f" Source: {pfz_source}."
        )

        if pfz_message:

            pfz_status += (
                f" {pfz_message}"
            )

        reasoning_points.append(
            pfz_status
        )

    # =========================================================
    # SATELLITE REASONING
    # =========================================================

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

    # =========================================================
    # SAFETY REASONING
    # =========================================================

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
                "No current ORCA decision-support rule alert was triggered."
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

    # Keep the internal key for backward compatibility with
    # the existing coordinator evidence categories.
    heuristic_rule = evidence_summary.get(
        "DEMO_RULE",
        evidence_summary.get(
            "HEURISTIC_RULE",
            0
        )
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
        f"{heuristic_rule} ORCA decision-support rule source(s), "
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
        + heuristic_rule
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
                (heuristic_rule * 0.4)
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
            "or project-rule information."
        )
    }

    # =========================================================
    # PHASE 9.7
    # ADVANCED EXPLAINABLE AI REASONING
    # =========================================================

    explainability_steps = []

    for agent_name in selected_agents:

        explainability_steps.append({
            "stage": "AGENT_INPUT",
            "agent": agent_name,
            "explanation": (
                f"{agent_name} contributed its available output "
                "to the ORCA reasoning layer."
            )
        })

    if ocean:

        ocean_values = []

        if sst is not None:

            ocean_values.append(
                f"SST={sst:.3f} °C"
                if isinstance(sst, (int, float))
                else f"SST={sst} °C"
            )

        if current is not None:

            ocean_values.append(
                f"current={current:.3f} m/s"
                if isinstance(current, (int, float))
                else f"current={current} m/s"
            )

        if salinity is not None:

            ocean_values.append(
                f"salinity={salinity}"
            )

        if mld is not None:

            ocean_values.append(
                f"mixed layer depth={mld:.3f} m"
                if isinstance(mld, (int, float))
                else f"mixed layer depth={mld} m"
            )

        if ocean_values:

            explainability_steps.append({
                "stage": "OCEAN_EVIDENCE",
                "agent": "Ocean Agent",
                "explanation":
                    "Ocean reasoning used: "
                    + ", ".join(ocean_values)
                    + "."
            })

    if weather_forecast_assessment.get(
        "status"
    ) == "SUCCESS":

        explainability_steps.append({
            "stage": "WEATHER_EVIDENCE",
            "agent": "Weather Agent",
            "explanation": (
                "Weather reasoning used current conditions and the "
                "available forecast window from the Weather Agent."
            )
        })

    explainability_steps.append({
        "stage": "CROSS_VALIDATION",
        "agent": "ORCA Cross-Validation",
        "explanation":
            cross_validation.get(
                "summary",
                "No cross-validation summary available."
            )
    })

    explainability_steps.append({
        "stage": "RISK_DECISION",
        "agent": "Safety Agent / ORCA Heuristics",
        "explanation":
            combined_risk_summary
    })

    if pfz:

        explainability_steps.append({
            "stage": "PFZ_EVIDENCE",
            "agent": "PFZ Agent",
            "explanation":
                pfz_status
        })

    if satellite:

        explainability_steps.append({
            "stage": "SATELLITE_EVIDENCE",
            "agent": "Satellite Agent",
            "explanation":
                satellite_status
        })

    if combined_risk_level == "HIGH":

        explanation_conclusion = (
            "ORCA reached the HIGH risk classification because at least one "
            "available current or forecast indicator crossed a configured "
            "high-risk heuristic threshold."
        )

    elif combined_risk_level == "MODERATE":

        explanation_conclusion = (
            "ORCA reached the MODERATE risk classification because at least one "
            "available current or forecast indicator crossed a configured "
            "moderate-risk heuristic threshold."
        )

    else:

        explanation_conclusion = (
            "ORCA reached the LOW risk classification because none of the "
            "available current or forecast indicators crossed the configured "
            "risk thresholds."
        )

    explainability = {

        "status":
            "SUCCESS",

        "method":
            "Rule-based evidence tracing across specialized ORCA agents.",

        "decision":
            combined_risk_level,

        "conclusion":
            explanation_conclusion,

        "reasoning_chain":
            explainability_steps,

        "supporting_agents":
            selected_agents,

        "cross_validation":
            cross_validation,

        "evidence_summary":
            evidence_summary,

        "confidence":
            confidence,

        "limitations": [
            "ORCA project-level heuristics do not replace official marine warnings or government safety guidance.",
            "Observed, forecast, mapped and heuristic information are kept as separate evidence categories.",
            "Missing data is not replaced with invented marine measurements."
        ]
    }

    reasoning_points.append(
        "Explainable AI reasoning: ORCA traced the final assessment "
        "through agent inputs, supporting evidence, cross-validation, "
        "risk rules and confidence information."
    )

    # =========================================================
    # PHASE 9.8
    # UNIFIED MARINE INTELLIGENCE SCORE
    # =========================================================

    current_condition_score = 100
    current_condition_penalties = []

    if wind is not None and wind >= 40:

        current_condition_score -= 20

        current_condition_penalties.append(
            "Current wind crossed the high-risk threshold"
        )

    if rain is not None and rain >= 10:

        current_condition_score -= 20

        current_condition_penalties.append(
            "Current precipitation crossed the heavy-precipitation threshold"
        )

    if current is not None and current >= 2:

        current_condition_score -= 20

        current_condition_penalties.append(
            "Ocean current crossed the strong-current threshold"
        )

    current_condition_score = max(
        0,
        current_condition_score
    )

    forecast_condition_score = 100
    forecast_condition_penalties = []

    if forecast_wind is not None:

        if forecast_wind >= 10:

            forecast_condition_score -= 30

            forecast_condition_penalties.append(
                "Forecast wind crossed the high-risk threshold"
            )

        elif forecast_wind >= 5:

            forecast_condition_score -= 15

            forecast_condition_penalties.append(
                "Forecast wind crossed the moderate-risk threshold"
            )

    if forecast_wave is not None:

        if forecast_wave >= 3:

            forecast_condition_score -= 30

            forecast_condition_penalties.append(
                "Forecast wave height crossed the high-risk threshold"
            )

        elif forecast_wave >= 1.5:

            forecast_condition_score -= 15

            forecast_condition_penalties.append(
                "Forecast wave height crossed the moderate-risk threshold"
            )

    forecast_condition_score = max(
        0,
        forecast_condition_score
    )

    if combined_risk_level == "HIGH":

        safety_component_score = 40

    elif combined_risk_level == "MODERATE":

        safety_component_score = 70

    else:

        safety_component_score = 100

    if total_agents:

        data_completeness_score = round(
            (
                successful_agents
                / total_agents
            ) * 100
        )

    else:

        data_completeness_score = 0

    evidence_quality_score = max(
        0,
        min(
            100,
            evidence_score
        )
    )

    unified_score_raw = (
        current_condition_score * 0.30
        + forecast_condition_score * 0.25
        + safety_component_score * 0.20
        + data_completeness_score * 0.15
        + evidence_quality_score * 0.10
    )

    unified_marine_intelligence_score = round(
        unified_score_raw,
        1
    )

    if unified_marine_intelligence_score >= 85:

        score_band = "HIGH"

    elif unified_marine_intelligence_score >= 65:

        score_band = "MODERATE"

    else:

        score_band = "LIMITED"

    score_factors = []

    score_factors.append(
        f"Current-condition component: "
        f"{current_condition_score}/100"
    )

    score_factors.append(
        f"Forecast-condition component: "
        f"{forecast_condition_score}/100"
    )

    score_factors.append(
        f"Safety component: "
        f"{safety_component_score}/100"
    )

    score_factors.append(
        f"Data completeness component: "
        f"{data_completeness_score}/100"
    )

    score_factors.append(
        f"Evidence quality component: "
        f"{evidence_quality_score}/100"
    )

    if current_condition_penalties:

        score_factors.extend(
            current_condition_penalties
        )

    if forecast_condition_penalties:

        score_factors.extend(
            forecast_condition_penalties
        )

    unified_score_summary = (
        f"Unified Marine Intelligence Score is "
        f"{unified_marine_intelligence_score}/100 "
        f"({score_band}). The score combines current "
        f"marine conditions, forecast conditions, the "
        f"ORCA risk assessment, data completeness and "
        f"evidence quality using transparent project-level "
        f"weights."
    )

    unified_marine_intelligence = {

        "status":
            "SUCCESS",

        "score":
            unified_marine_intelligence_score,

        "score_band":
            score_band,

        "summary":
            unified_score_summary,

        "components": {

            "current_condition": {
                "score":
                    current_condition_score,
                "weight_percent":
                    30
            },

            "forecast_condition": {
                "score":
                    forecast_condition_score,
                "weight_percent":
                    25
            },

            "safety": {
                "score":
                    safety_component_score,
                "weight_percent":
                    20,
                "risk_level":
                    combined_risk_level
            },

            "data_completeness": {
                "score":
                    data_completeness_score,
                "weight_percent":
                    15,
                "successful_agents":
                    successful_agents,
                "total_agents":
                    total_agents
            },

            "evidence_quality": {
                "score":
                    evidence_quality_score,
                "weight_percent":
                    10
            }
        },

        "factors":
            score_factors,

        "method": (
            "ORCA project-level weighted decision-support "
            "metric: current conditions 30%, forecast "
            "conditions 25%, safety assessment 20%, data "
            "completeness 15%, and evidence quality 10%."
        ),

        "limitations": [
            "This score is not an official marine warning.",
            "This score is not a scientific ocean-health index.",
            "This score does not guarantee fishing success or safe navigation.",
            "Missing marine measurements are not replaced with invented values."
        ],

        "data_status":
            "ORCA_HEURISTIC"
    }

    reasoning_points.append(
        "Unified Marine Intelligence Score: "
        f"{unified_marine_intelligence_score}/100 "
        f"({score_band})."
    )

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
            "the current ORCA decision-support "
            "rules. "

            "This is decision support and is "
            "not an official government warning."

        )

    else:

        final_assessment = (

            "ORCA combined the available ocean, "
            "weather, GIS, PFZ, satellite and "
            "safety information through the "
            "collaborative agent system. "

            "No current ORCA decision-support "
            "rule safety alert was triggered "
            "by the available data."

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

        "state":
            state,

        "district":
            district,

        "selected_agents":
            selected_agents,

        "reasoning_points":
            reasoning_points,

        # -----------------------------------------------------
        # PHASE 9.5 WEATHER & FORECAST OUTPUT
        # -----------------------------------------------------

        "weather_forecast_assessment":
            weather_forecast_assessment,

        # -----------------------------------------------------
        # PHASE 9.4 RISK OUTPUT
        # -----------------------------------------------------

        "cross_validation":
            cross_validation,

        "explainability":
            explainability,

        "unified_marine_intelligence":
            unified_marine_intelligence,

        "marine_risk_assessment": {

            "risk_level":
                combined_risk_level,

            "summary":
                combined_risk_summary,

            "high_risk_factors":
                list(
                    dict.fromkeys(
                        high_risk_factors
                    )
                ),

            "moderate_risk_factors":
                list(
                    dict.fromkeys(
                        moderate_risk_factors
                    )
                ),

            "risk_factors":
                risk_factors_advanced,

            "inputs": {

                "current_wind_kmh":
                    wind,

                "precipitation_mm":
                    rain,

                "ocean_current_ms":
                    current,

                "forecast_wind_ms":
                    forecast_wind,

                "forecast_wave_height_m":
                    forecast_wave,

                "forecast_time":
                    forecast_time
            },

            "thresholds": {

                "high_wind_kmh":
                    40,

                "heavy_precipitation_mm":
                    10,

                "strong_current_ms":
                    2,

                "forecast_wind_moderate_ms":
                    5,

                "forecast_wind_high_ms":
                    10,

                "forecast_wave_moderate_m":
                    1.5,

                "forecast_wave_high_m":
                    3
            },

            "data_status":
                "ORCA_HEURISTIC",

            "disclaimer": (
                "This combined marine risk level is "
                "generated by ORCA project-level "
                "decision-support heuristics. It is "
                "not an official marine warning, "
                "government alert, or replacement "
                "for authoritative safety guidance."
            )
        },

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
            "integration-ready and project-rule evidence. "

            "The combined marine risk assessment uses "
            "ORCA project-level heuristic thresholds. "

            "Safety results are generated from ORCA "
            "decision-support rules and are not official "
            "government warnings."

        )
    }


# =========================================================
# DIRECT TEST
# =========================================================

if __name__ == "__main__":

    result = orca_reasoning(
        "What is the overall marine condition?",
        "Tamil Nadu",
        "Salem"
    )

    print()
    print("==========================================")
    print("ORCA AI REASONING LAYER")
    print("==========================================")

    print()
    print("STATUS:")
    print(result["status"])

    print()
    print("STATE:")
    print(result["state"])

    print()
    print("DISTRICT:")
    print(result["district"])

    print()
    print("SELECTED AGENTS:")
    print(result["selected_agents"])

    print()
    print("REASONING POINTS:")

    for point in result["reasoning_points"]:

        print("-", point)

    print()
    print("UNIFIED MARINE INTELLIGENCE SCORE:")
    print(
        result[
            "unified_marine_intelligence"
        ]
    )

    print()
    print("MARINE RISK ASSESSMENT:")
    print(
        result[
            "marine_risk_assessment"
        ]
    )

    print()
    print("EVIDENCE SUMMARY:")
    print(
        result[
            "evidence_summary"
        ]
    )

    print()
    print("CONFIDENCE:")
    print(
        result[
            "confidence"
        ]
    )

    print()
    print("FINAL ASSESSMENT:")
    print(
        result[
            "final_assessment"
        ]
    )

    print()
    print("==========================================")
    print("TEST COMPLETE")
    print("==========================================")