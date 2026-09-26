/* =========================================================
   ORCA MARINE INTELLIGENCE
   DASHBOARD CONTROLLER
   Phase 6.6 - Observation & Retrieval Metadata
========================================================= */


/* =========================================================
   REGION
========================================================= */

function getSelectedRegion() {

    const regionSelect =
        document.getElementById("regionSelect");

    return regionSelect
        ? regionSelect.value
        : "Tamil Nadu";
}


/* =========================================================
   CONNECTION STATUS
========================================================= */

function updateConnectionStatus(connected, message) {

    const status =
        document.getElementById("connectionStatus");

    const footerStatus =
        document.getElementById("footerStatus");

    if (!status) return;

    const dot =
        status.querySelector(".status-dot");

    const text =
        status.querySelector("span:last-child");

    if (connected) {

        dot?.classList.remove("offline");

        if (text) {
            text.textContent =
                message || "Backend connected";
        }

        if (footerStatus) {
            footerStatus.textContent =
                "Connected";
        }

    } else {

        dot?.classList.add("offline");

        if (text) {
            text.textContent =
                message || "Backend unavailable";
        }

        if (footerStatus) {
            footerStatus.textContent =
                "Unavailable";
        }
    }
}


/* =========================================================
   DISPLAY VALUE
========================================================= */

function displayValue(
    elementId,
    value,
    fallback = "—"
) {

    const element =
        document.getElementById(elementId);

    if (!element) return;

    if (
        value === undefined ||
        value === null ||
        value === ""
    ) {

        element.textContent =
            fallback;

        return;
    }

    if (typeof value === "object") {

        element.textContent =
            JSON.stringify(value);

        return;
    }

    element.textContent =
        String(value);
}


/* =========================================================
   FIND VALUE
========================================================= */

function findMarineValue(
    data,
    possibleKeys
) {

    if (
        !data ||
        typeof data !== "object"
    ) {
        return null;
    }

    for (const key of possibleKeys) {

        if (
            data[key] !== undefined &&
            data[key] !== null &&
            data[key] !== ""
        ) {

            return data[key];
        }
    }

    return null;
}


/* =========================================================
   HTML ESCAPE
========================================================= */

function escapeHtml(value) {

    const div =
        document.createElement("div");

    div.textContent =
        String(value ?? "");

    return div.innerHTML;
}


/* =========================================================
   CONFIDENCE FORMATTER
========================================================= */

function formatConfidence(value) {

    if (
        value === undefined ||
        value === null ||
        value === ""
    ) {
        return null;
    }

    if (typeof value === "number") {

        if (!Number.isFinite(value)) {
            return null;
        }

        if (value <= 1) {
            return `${Math.round(value * 100)}%`;
        }

        return `${Math.round(value)}%`;
    }

    if (typeof value === "string") {

        const trimmed =
            value.trim();

        if (!trimmed) {
            return null;
        }

        return trimmed;
    }

    if (typeof value === "object") {

        const nestedValue =
            findMarineValue(
                value,
                [
                    "score",
                    "value",
                    "confidence",
                    "confidence_score",
                    "confidenceScore",
                    "percentage",
                    "percent",
                    "level",
                    "label"
                ]
            );

        if (
            nestedValue !== null &&
            nestedValue !== value
        ) {

            return formatConfidence(
                nestedValue
            );
        }

        const quality =
            findMarineValue(
                value,
                [
                    "quality",
                    "evidence_quality",
                    "evidenceQuality"
                ]
            );

        if (quality !== null) {
            return String(quality);
        }

        return null;
    }

    return null;
}


/* =========================================================
   METADATA
   Supports:
   observation_time
   retrieved_at
========================================================= */

function updateMetricMetadata(
    elementId,
    data,
    defaultText = "Backend response"
) {

    const element =
        document.getElementById(elementId);

    if (!element) return;


    const observationTime =
        findMarineValue(
            data,
            [
                "observation_time",
                "observationTime"
            ]
        );


    const retrievedAt =
        findMarineValue(
            data,
            [
                "retrieved_at",
                "retrievedAt"
            ]
        );


    const timestamp =
        findMarineValue(
            data,
            [
                "timestamp",
                "time",
                "datetime",
                "updated_at",
                "updatedAt",
                "date"
            ]
        );


    const source =
        findMarineValue(
            data,
            [
                "source",
                "data_source",
                "dataSource"
            ]
        );


    /* Real ocean observation metadata */

    if (
        observationTime &&
        retrievedAt
    ) {

        element.textContent =
            `Observed: ${observationTime} • Retrieved: ${retrievedAt}`;

        return;
    }


    if (observationTime) {

        element.textContent =
            `Observed: ${observationTime}`;

        return;
    }


    if (retrievedAt) {

        element.textContent =
            `Retrieved: ${retrievedAt}`;

        return;
    }


    /* Other backend timestamp */

    if (
        timestamp &&
        source
    ) {

        element.textContent =
            `${source} • ${timestamp}`;

    } else if (timestamp) {

        element.textContent =
            `Timestamp: ${timestamp}`;

    } else if (source) {

        element.textContent =
            `Source: ${source}`;

    } else {

        element.textContent =
            defaultText;
    }
}


/* =========================================================
   OCEAN DASHBOARD
========================================================= */

function updateMarineDashboard(data) {

    const sst =
        findMarineValue(
            data,
            [
                "sst",
                "SST",
                "sea_surface_temperature_c",
                "seaSurfaceTemperature"
            ]
        );


    /*
       IMPORTANT:
       sea_surface_height_m is NOT wave height.
    */

    const wave =
        findMarineValue(
            data,
            [
                "wave_height",
                "waveHeight",
                "significant_wave_height_m",
                "significantWaveHeight"
            ]
        );


    const current =
        findMarineValue(
            data,
            [
                "ocean_current",
                "oceanCurrent",
                "current",
                "surface_current",
                "current_speed_ms"
            ]
        );


    const chlorophyll =
        findMarineValue(
            data,
            [
                "chlorophyll",
                "chlorophyll_a",
                "chlorophyllA"
            ]
        );


    const mixedLayerDepth =
        findMarineValue(
            data,
            [
                "mixed_layer_depth_m",
                "mixedLayerDepth",
                "mixed_layer_depth"
            ]
        );


    displayValue(
        "sstValue",
        sst
    );


    displayValue(
        "waveValue",
        wave
    );


    displayValue(
        "currentValue",
        current
    );


    displayValue(
        "chlorophyllValue",
        chlorophyll
    );


    displayValue(
        "oceanSst",
        sst
    );


    displayValue(
        "oceanWave",
        wave
    );


    displayValue(
        "oceanCurrent",
        current
    );


    displayValue(
        "oceanMixedLayerDepth",
        mixedLayerDepth
    );


    updateMetricMetadata(
        "sstMeta",
        data
    );


    updateMetricMetadata(
        "waveMeta",
        wave !== null
            ? data
            : null,
        "No confirmed wave-height data"
    );


    updateMetricMetadata(
        "currentMeta",
        data
    );


    updateMetricMetadata(
        "chlorophyllMeta",
        chlorophyll !== null
            ? data
            : null,
        "No chlorophyll observation available"
    );


    updateOceanVisualization(
        data
    );
}


/* =========================================================
   WEATHER DATA
========================================================= */

async function loadDashboardWeather() {

    const region =
        getSelectedRegion();

    try {

        const result =
            await safeApiCall(
                getWeatherData,
                region
            );


        if (!result.success) {

            displayValue(
                "windValue",
                null
            );


            const windMeta =
                document.getElementById(
                    "windMeta"
                );


            if (windMeta) {

                windMeta.textContent =
                    "Weather data unavailable";
            }

            return;
        }


        const data =
            result.data;


        const wind =
            findMarineValue(
                data,
                [
                    "wind_speed",
                    "windSpeed",
                    "wind_speed_kmh",
                    "windSpeedKmh"
                ]
            );


        displayValue(
            "windValue",
            wind !== null
                ? `${wind} km/h`
                : null
        );


        updateMetricMetadata(
            "windMeta",
            data,
            "Weather backend response"
        );


        window.ORCA_LATEST_WEATHER_DATA =
            data;


    } catch (error) {

        console.error(
            "Dashboard Weather Error:",
            error
        );


        displayValue(
            "windValue",
            null
        );


        const windMeta =
            document.getElementById(
                "windMeta"
            );


        if (windMeta) {

            windMeta.textContent =
                "Weather data unavailable";
        }
    }
}


/* =========================================================
   PFZ DASHBOARD
========================================================= */

async function loadDashboardPFZ() {

    const region =
        getSelectedRegion();


    const pfzValue =
        document.getElementById(
            "pfzValue"
        );


    const pfzMeta =
        document.getElementById(
            "pfzMeta"
        );


    if (pfzValue) {

        pfzValue.textContent =
            "Loading...";
    }


    if (pfzMeta) {

        pfzMeta.textContent =
            "Checking PFZ backend";
    }


    try {

        const result =
            await safeApiCall(
                getPFZData,
                region
            );


        if (!result.success) {

            if (pfzValue) {

                pfzValue.textContent =
                    "—";
            }


            if (pfzMeta) {

                pfzMeta.textContent =
                    "PFZ data unavailable";
            }

            return;
        }


        const data =
            result.data;


        const advisory =
            findMarineValue(
                data,
                [
                    "pfz",
                    "PFZ",
                    "pfz_status",
                    "pfzStatus",
                    "pfz_advisory",
                    "pfzAdvisory",
                    "advisory",
                    "status"
                ]
            );


        const source =
            findMarineValue(
                data,
                [
                    "source",
                    "data_source",
                    "dataSource"
                ]
            );


        const responseRegion =
            findMarineValue(
                data,
                [
                    "region",
                    "Region",
                    "area",
                    "location"
                ]
            );


        if (pfzValue) {

            pfzValue.textContent =
                advisory !== null
                    ? String(advisory)
                    : "—";
        }


        if (pfzMeta) {

            if (
                source &&
                responseRegion
            ) {

                pfzMeta.textContent =
                    `${source} • ${responseRegion}`;

            } else if (source) {

                pfzMeta.textContent =
                    String(source);

            } else if (responseRegion) {

                pfzMeta.textContent =
                    String(responseRegion);

            } else {

                pfzMeta.textContent =
                    "Backend PFZ response";
            }
        }


        window.ORCA_LATEST_PFZ_DATA =
            data;


    } catch (error) {

        console.error(
            "Dashboard PFZ Error:",
            error
        );


        if (pfzValue) {

            pfzValue.textContent =
                "—";
        }


        if (pfzMeta) {

            pfzMeta.textContent =
                "PFZ data unavailable";
        }
    }
}


/* =========================================================
   AI REASONING / INSIGHT
========================================================= */

async function loadDashboardInsight() {

    const region =
        getSelectedRegion();


    const insight =
        document.getElementById(
            "dashboardInsight"
        );


    if (!insight) return;


    try {

        const result =
            await safeApiCall(
                getReasoningData,
                region,
                "What are the current marine conditions?",
                ""
            );


        if (!result.success) {

            insight.innerHTML = `

                <div class="empty-state">

                    <div class="empty-icon">
                        ✦
                    </div>

                    <h4>
                        AI Insight unavailable
                    </h4>

                    <p>
                        Reasoning backend could not be reached.
                    </p>

                </div>

            `;

            return;
        }


        const data =
            result.data;


        const finalAssessment =
            findMarineValue(
                data,
                [
                    "final_assessment",
                    "finalAssessment",
                    "assessment",
                    "summary",
                    "response"
                ]
            );


        const rawConfidence =
            findMarineValue(
                data,
                [
                    "confidence",
                    "confidence_score",
                    "confidenceScore"
                ]
            );


        const confidence =
            formatConfidence(
                rawConfidence
            );


        const selectedAgents =
            findMarineValue(
                data,
                [
                    "selected_agents",
                    "selectedAgents"
                ]
            );


        let agentsText = "";


        if (Array.isArray(selectedAgents)) {

            agentsText =
                selectedAgents.join(
                    " • "
                );

        } else if (
            selectedAgents &&
            typeof selectedAgents === "object"
        ) {

            agentsText =
                JSON.stringify(
                    selectedAgents
                );

        } else if (selectedAgents) {

            agentsText =
                String(selectedAgents);
        }


        insight.innerHTML = `

            <div style="
                padding:20px;
                box-sizing:border-box;
            ">

                <div style="
                    font-size:12px;
                    opacity:.7;
                    margin-bottom:8px;
                ">
                    ORCA REASONING
                </div>


                <h4 style="
                    margin:0 0 12px 0;
                ">
                    Marine Intelligence Assessment
                </h4>


                <p style="
                    line-height:1.6;
                    margin-bottom:16px;
                ">
                    ${
                        finalAssessment
                            ? escapeHtml(
                                String(finalAssessment)
                            )
                            : "Reasoning response received from backend."
                    }
                </p>


                ${
                    agentsText
                        ? `

                            <div style="
                                font-size:12px;
                                opacity:.75;
                                margin-bottom:8px;
                            ">
                                Agents:
                            </div>


                            <div style="
                                font-size:13px;
                                line-height:1.6;
                            ">
                                ${
                                    escapeHtml(
                                        agentsText
                                    )
                                }
                            </div>

                          `
                        : ""
                }


                ${
                    confidence !== null
                        ? `

                            <div style="
                                margin-top:14px;
                                font-size:12px;
                                opacity:.75;
                            ">

                                Confidence:
                                ${
                                    escapeHtml(
                                        confidence
                                    )
                                }

                            </div>

                          `
                        : ""
                }


            </div>

        `;


        window.ORCA_LATEST_REASONING_DATA =
            data;


    } catch (error) {

        console.error(
            "Dashboard Reasoning Error:",
            error
        );


        insight.innerHTML = `

            <div class="empty-state">

                <div class="empty-icon">
                    ✦
                </div>

                <h4>
                    AI Insight unavailable
                </h4>

                <p>
                    Unable to load reasoning data.
                </p>

            </div>

        `;
    }
}


/* =========================================================
   OCEAN PARAMETER CONFIG
========================================================= */

function getOceanParameterConfig(
    parameter
) {

    const configs = {

        sst: {

            label:
                "Sea Surface Temperature",

            keys: [
                "sst",
                "SST",
                "sea_surface_temperature_c",
                "seaSurfaceTemperature"
            ],

            unit:
                "°C"
        },


        wave: {

            label:
                "Significant Wave Height",

            keys: [
                "wave_height",
                "waveHeight",
                "significant_wave_height_m",
                "significantWaveHeight"
            ],

            unit:
                "m"
        },


        current: {

            label:
                "Surface Current",

            keys: [
                "ocean_current",
                "oceanCurrent",
                "current",
                "surface_current",
                "current_speed_ms"
            ],

            unit:
                "m/s"
        },


        chlorophyll: {

            label:
                "Chlorophyll",

            keys: [
                "chlorophyll",
                "chlorophyll_a",
                "chlorophyllA"
            ],

            unit:
                ""
        },


        mld: {

            label:
                "Mixed Layer Depth",

            keys: [
                "mixed_layer_depth_m",
                "mixedLayerDepth",
                "mixed_layer_depth"
            ],

            unit:
                "m"
        }
    };


    return configs[parameter] ||
           configs.sst;
}


/* =========================================================
   OCEAN VISUALIZATION
   Supports observation_time + retrieved_at
========================================================= */

function updateOceanVisualization(
    data
) {

    const chart =
        document.getElementById(
            "oceanChart"
        );


    if (!chart) return;


    const parameterSelect =
        document.getElementById(
            "oceanParameter"
        );


    const parameter =
        parameterSelect
            ? parameterSelect.value
            : "sst";


    const config =
        getOceanParameterConfig(
            parameter
        );


    const value =
        findMarineValue(
            data,
            config.keys
        );


    const observationTime =
        findMarineValue(
            data,
            [
                "observation_time",
                "observationTime"
            ]
        );


    const retrievedAt =
        findMarineValue(
            data,
            [
                "retrieved_at",
                "retrievedAt"
            ]
        );


    const timestamp =
        findMarineValue(
            data,
            [
                "timestamp",
                "time",
                "datetime",
                "updated_at",
                "updatedAt",
                "date"
            ]
        );


    const source =
        findMarineValue(
            data,
            [
                "source",
                "data_source",
                "dataSource"
            ]
        );


    if (
        value === null ||
        value === undefined ||
        value === ""
    ) {

        chart.innerHTML = `

            <div class="empty-state">

                <div>
                    —
                </div>

                <h4>
                    ${
                        escapeHtml(
                            config.label
                        )
                    }
                </h4>

                <p>
                    No validated backend value is
                    available for this parameter.
                </p>

                <small>
                    ORCA is not displaying a fabricated value.
                </small>

            </div>

        `;

        return;
    }


    const numericValue =
        Number(value);


    const barWidth =
        Number.isFinite(
            numericValue
        )

            ? Math.min(
                100,
                Math.max(
                    8,
                    Math.log10(
                        Math.abs(
                            numericValue
                        ) + 1
                    ) * 35
                )
            )

            : 8;


    const unitText =
        config.unit
            ? ` ${config.unit}`
            : "";


    let metadataText =
        "Timestamp unavailable";


    if (
        observationTime &&
        retrievedAt
    ) {

        metadataText =
            `Observed: ${observationTime} • Retrieved: ${retrievedAt}`;

    } else if (observationTime) {

        metadataText =
            `Observed: ${observationTime}`;

    } else if (retrievedAt) {

        metadataText =
            `Retrieved: ${retrievedAt}`;

    } else if (timestamp) {

        metadataText =
            `Timestamp: ${timestamp}`;
    }


    chart.innerHTML = `

        <div style="
            width:100%;
            padding:24px;
            box-sizing:border-box;
        ">

            <div style="
                display:flex;
                justify-content:space-between;
                gap:16px;
                align-items:flex-end;
                margin-bottom:18px;
                flex-wrap:wrap;
            ">

                <div>

                    <div style="
                        font-size:12px;
                        opacity:.7;
                        margin-bottom:6px;
                    ">
                        SELECTED PARAMETER
                    </div>


                    <h4 style="
                        margin:0;
                    ">
                        ${
                            escapeHtml(
                                config.label
                            )
                        }
                    </h4>

                </div>


                <div style="
                    font-size:28px;
                    font-weight:700;
                ">

                    ${
                        escapeHtml(
                            String(value)
                        )
                    }

                    ${unitText}

                </div>

            </div>


            <div style="
                width:100%;
                height:14px;
                border-radius:999px;
                background:rgba(127,127,127,.16);
                overflow:hidden;
            ">

                <div style="
                    width:${barWidth}%;
                    height:100%;
                    border-radius:999px;
                    background:currentColor;
                "></div>

            </div>


            <div style="
                display:flex;
                justify-content:space-between;
                gap:12px;
                margin-top:14px;
                font-size:12px;
                opacity:.72;
                flex-wrap:wrap;
            ">

                <span>
                    Backend data
                </span>


                <span>
                    ${
                        escapeHtml(
                            metadataText
                        )
                    }
                </span>


                <span>
                    ${
                        source
                            ? `Source: ${
                                escapeHtml(
                                    String(
                                        source
                                    )
                                )
                              }`
                            : "Source unavailable"
                    }
                </span>

            </div>

        </div>

    `;
}


/* =========================================================
   OCEAN VISUALIZATION SETUP
========================================================= */

function setupOceanVisualization() {

    const parameterSelect =
        document.getElementById(
            "oceanParameter"
        );


    if (!parameterSelect) return;


    parameterSelect.addEventListener(
        "change",
        () => {

            if (
                window.ORCA_LATEST_OCEAN_DATA
            ) {

                updateOceanVisualization(
                    window.ORCA_LATEST_OCEAN_DATA
                );
            }
        }
    );
}


/* =========================================================
   RECENT UPDATES
   Supports observation_time + retrieved_at
========================================================= */

function updateRecentUpdates(
    oceanData,
    weatherData,
    pfzData,
    region
) {

    const container =
        document.getElementById(
            "recentUpdates"
        );


    if (!container) return;


    const oceanObservationTime =
        findMarineValue(
            oceanData,
            [
                "observation_time",
                "observationTime"
            ]
        );


    const oceanRetrievedAt =
        findMarineValue(
            oceanData,
            [
                "retrieved_at",
                "retrievedAt"
            ]
        );


    const oceanTimestamp =
        findMarineValue(
            oceanData,
            [
                "timestamp",
                "time",
                "datetime",
                "updated_at",
                "updatedAt"
            ]
        );


    const oceanSource =
        findMarineValue(
            oceanData,
            [
                "source",
                "data_source",
                "dataSource"
            ]
        );


    const weatherSource =
        findMarineValue(
            weatherData,
            [
                "source",
                "data_source",
                "dataSource"
            ]
        );


    const pfzSource =
        findMarineValue(
            pfzData,
            [
                "source",
                "data_source",
                "dataSource"
            ]
        );


    let oceanMetadata =
        "Timestamp unavailable";


    if (
        oceanObservationTime &&
        oceanRetrievedAt
    ) {

        oceanMetadata =
            `Observed: ${oceanObservationTime} • Retrieved: ${oceanRetrievedAt}`;

    } else if (oceanObservationTime) {

        oceanMetadata =
            `Observed: ${oceanObservationTime}`;

    } else if (oceanRetrievedAt) {

        oceanMetadata =
            `Retrieved: ${oceanRetrievedAt}`;

    } else if (oceanTimestamp) {

        oceanMetadata =
            String(oceanTimestamp);
    }


    container.innerHTML = `

        <div class="update-item">

            <div>

                <strong>
                    Ocean data fetched
                </strong>

                <span>
                    Region:
                    ${
                        escapeHtml(region)
                    }
                </span>

            </div>


            <span>
                ${
                    escapeHtml(
                        oceanMetadata
                    )
                }
            </span>

        </div>


        <div class="update-item">

            <div>

                <strong>
                    Weather data
                </strong>

                <span>
                    Backend response
                </span>

            </div>


            <span>
                ${
                    escapeHtml(
                        weatherSource ||
                        "Weather backend"
                    )
                }
            </span>

        </div>


        <div class="update-item">

            <div>

                <strong>
                    PFZ data
                </strong>

                <span>
                    Backend response
                </span>

            </div>


            <span>
                ${
                    escapeHtml(
                        pfzSource ||
                        "PFZ backend"
                    )
                }
            </span>

        </div>

    `;
}


/* =========================================================
   DASHBOARD ERROR
========================================================= */

function showDashboardError(
    errorMessage
) {

    const ids = [

        "sstValue",
        "waveValue",
        "windValue",
        "currentValue",
        "chlorophyllValue",

        "oceanSst",
        "oceanWave",
        "oceanCurrent",
        "oceanMixedLayerDepth"
    ];


    ids.forEach(
        id =>
            displayValue(
                id,
                null
            )
    );


    const updates =
        document.getElementById(
            "recentUpdates"
        );


    if (updates) {

        updates.innerHTML = `

            <div class="empty-state compact">

                <p>
                    Marine data could not be loaded.
                </p>

                <small>
                    ${
                        escapeHtml(
                            errorMessage ||
                            "Unknown error"
                        )
                    }
                </small>

            </div>

        `;
    }
}


/* =========================================================
   LOAD DASHBOARD DATA
========================================================= */

async function loadDashboardData() {

    const region =
        getSelectedRegion();


    const refreshButton =
        document.getElementById(
            "refreshDashboard"
        );


    if (refreshButton) {

        refreshButton.disabled =
            true;

        refreshButton.textContent =
            "Loading...";
    }


    try {

        /* =================================================
           OCEAN
        ================================================= */

        const oceanResult =
            await safeApiCall(
                getOceanData,
                region
            );


        if (!oceanResult.success) {

            updateConnectionStatus(
                false,
                "Marine data unavailable"
            );


            showDashboardError(
                oceanResult.error
            );


            return;
        }


        updateConnectionStatus(
            true,
            "Backend connected"
        );


        window.ORCA_LATEST_OCEAN_DATA =
            oceanResult.data;


        updateMarineDashboard(
            oceanResult.data
        );


        /* =================================================
           WEATHER
        ================================================= */

        await loadDashboardWeather();


        /* =================================================
           PFZ
        ================================================= */

        await loadDashboardPFZ();


        /* =================================================
           AI REASONING
        ================================================= */

        await loadDashboardInsight();


        /* =================================================
           RECENT UPDATES
        ================================================= */

        updateRecentUpdates(

            oceanResult.data,

            window.ORCA_LATEST_WEATHER_DATA,

            window.ORCA_LATEST_PFZ_DATA,

            region

        );


    } catch (error) {

        console.error(
            "Dashboard Load Error:",
            error
        );


        showDashboardError(
            error.message ||
            "Unable to load dashboard data."
        );


    } finally {

        if (refreshButton) {

            refreshButton.disabled =
                false;

            refreshButton.textContent =
                "↻ Refresh Data";
        }
    }
}


/* =========================================================
   DASHBOARD SETUP
========================================================= */

function setupDashboard() {

    const refreshButton =
        document.getElementById(
            "refreshDashboard"
        );


    if (refreshButton) {

        refreshButton.addEventListener(
            "click",
            loadDashboardData
        );
    }


    const regionSelect =
        document.getElementById(
            "regionSelect"
        );


    if (regionSelect) {

        regionSelect.addEventListener(
            "change",
            () => {

                loadDashboardData();

            }
        );
    }
}


/* =========================================================
   START DASHBOARD
========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    () => {

        setupDashboard();

        setupOceanVisualization();

        loadDashboardData();

    }
);