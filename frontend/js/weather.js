/* =========================================================
   ORCA MARINE INTELLIGENCE
   WEATHER INTELLIGENCE MODULE
========================================================= */

function weatherFindValue(data, keys) {
    if (!data || typeof data !== "object") return null;

    for (const key of keys) {
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

function weatherEscapeHtml(value) {
    const div = document.createElement("div");
    div.textContent = String(value ?? "");
    return div.innerHTML;
}

function updateWeatherPage(data) {
    const page = document.getElementById("page-weather");

    if (!page || !data) return;

    const temperature = weatherFindValue(data, [
        "temperature_c",
        "temperature",
        "temp_c"
    ]);

    const humidity = weatherFindValue(data, [
        "humidity_percent",
        "humidity"
    ]);

    const windSpeed = weatherFindValue(data, [
        "wind_speed_kmh",
        "wind_speed",
        "windSpeed"
    ]);

    const windDirection = weatherFindValue(data, [
        "wind_direction_degrees",
        "wind_direction",
        "windDirection"
    ]);

    const precipitation = weatherFindValue(data, [
        "precipitation_mm",
        "precipitation",
        "rain_mm"
    ]);

    const location = weatherFindValue(data, [
        "location",
        "city",
        "region"
    ]);

    const source = weatherFindValue(data, [
        "source",
        "data_source",
        "dataSource"
    ]);

    const status = weatherFindValue(data, [
        "status"
    ]);


    page.innerHTML = `

        <div class="page-intro">

            <div>

                <span class="eyebrow">
                    ATMOSPHERIC CONDITIONS
                </span>

                <h2>
                    Weather Intelligence
                </h2>

                <p>
                    Weather information returned by the
                    connected backend.
                </p>

            </div>

            <button
                class="btn primary"
                id="refreshWeather"
            >
                ↻ Refresh Weather
            </button>

        </div>


        <div class="data-notice">

            <span class="notice-icon">
                ⓘ
            </span>

            <div>

                <strong>
                    Backend Weather Data
                </strong>

                <p>
                    Values shown below are taken directly
                    from the ORCA weather endpoint.
                </p>

            </div>

        </div>


        <div class="metrics-grid">


            <article class="metric-card">

                <div class="metric-header">
                    Temperature
                    <span class="metric-icon">🌡</span>
                </div>

                <div class="metric-value">
                    ${
                        temperature !== null
                            ? weatherEscapeHtml(temperature) + " °C"
                            : "—"
                    }
                </div>

                <div class="metric-meta">
                    ${location
                        ? "Location: " +
                          weatherEscapeHtml(location)
                        : "Location unavailable"}
                </div>

            </article>


            <article class="metric-card">

                <div class="metric-header">
                    Humidity
                    <span class="metric-icon">💧</span>
                </div>

                <div class="metric-value">
                    ${
                        humidity !== null
                            ? weatherEscapeHtml(humidity) + " %"
                            : "—"
                    }
                </div>

                <div class="metric-meta">
                    Relative humidity
                </div>

            </article>


            <article class="metric-card">

                <div class="metric-header">
                    Wind Speed
                    <span class="metric-icon">↝</span>
                </div>

                <div class="metric-value">
                    ${
                        windSpeed !== null
                            ? weatherEscapeHtml(windSpeed) +
                              " km/h"
                            : "—"
                    }
                </div>

                <div class="metric-meta">
                    ${
                        windDirection !== null
                            ? "Direction: " +
                              weatherEscapeHtml(
                                  windDirection
                              ) +
                              "°"
                            : "Direction unavailable"
                    }
                </div>

            </article>


            <article class="metric-card">

                <div class="metric-header">
                    Precipitation
                    <span class="metric-icon">☔</span>
                </div>

                <div class="metric-value">
                    ${
                        precipitation !== null
                            ? weatherEscapeHtml(
                                  precipitation
                              ) +
                              " mm"
                            : "—"
                    }
                </div>

                <div class="metric-meta">
                    Backend precipitation value
                </div>

            </article>

        </div>


        <article class="panel">

            <div class="panel-header">

                <div>

                    <span class="panel-kicker">
                        WEATHER DATA
                    </span>

                    <h3>
                        Weather Observation
                    </h3>

                </div>

                <span class="data-badge">
                    ${
                        status
                            ? weatherEscapeHtml(status)
                            : "Backend"
                    }
                </span>

            </div>


            <div class="data-details">

                <div class="data-detail-grid">


                    <div class="data-detail-item">

                        <span>
                            Location
                        </span>

                        <strong>
                            ${
                                location !== null
                                    ? weatherEscapeHtml(
                                          location
                                      )
                                    : "—"
                            }
                        </strong>

                    </div>


                    <div class="data-detail-item">

                        <span>
                            Temperature
                        </span>

                        <strong>
                            ${
                                temperature !== null
                                    ? weatherEscapeHtml(
                                          temperature
                                      ) +
                                      " °C"
                                    : "—"
                            }
                        </strong>

                    </div>


                    <div class="data-detail-item">

                        <span>
                            Humidity
                        </span>

                        <strong>
                            ${
                                humidity !== null
                                    ? weatherEscapeHtml(
                                          humidity
                                      ) +
                                      " %"
                                    : "—"
                            }
                        </strong>

                    </div>


                    <div class="data-detail-item">

                        <span>
                            Wind Speed
                        </span>

                        <strong>
                            ${
                                windSpeed !== null
                                    ? weatherEscapeHtml(
                                          windSpeed
                                      ) +
                                      " km/h"
                                    : "—"
                            }
                        </strong>

                    </div>


                    <div class="data-detail-item">

                        <span>
                            Wind Direction
                        </span>

                        <strong>
                            ${
                                windDirection !== null
                                    ? weatherEscapeHtml(
                                          windDirection
                                      ) +
                                      "°"
                                    : "—"
                            }
                        </strong>

                    </div>


                    <div class="data-detail-item">

                        <span>
                            Precipitation
                        </span>

                        <strong>
                            ${
                                precipitation !== null
                                    ? weatherEscapeHtml(
                                          precipitation
                                      ) +
                                      " mm"
                                    : "—"
                            }
                        </strong>

                    </div>


                    <div class="data-detail-item">

                        <span>
                            Source
                        </span>

                        <strong>
                            ${
                                source !== null
                                    ? weatherEscapeHtml(
                                          source
                                      )
                                    : "—"
                            }
                        </strong>

                    </div>


                    <div class="data-detail-item">

                        <span>
                            Status
                        </span>

                        <strong>
                            ${
                                status !== null
                                    ? weatherEscapeHtml(
                                          status
                                      )
                                    : "—"
                            }
                        </strong>

                    </div>


                </div>

            </div>

        </article>
    `;
}


async function loadWeatherModule() {

    const regionSelect =
        document.getElementById("regionSelect");

    const region =
        regionSelect
            ? regionSelect.value
            : "North Tamil Nadu";


    try {

        const result =
            await safeApiCall(
                getWeatherData,
                region
            );


        if (!result.success) {

            console.error(
                "Weather backend error:",
                result.error
            );

            return;
        }


        window.ORCA_LATEST_WEATHER_DATA =
            result.data;


        updateWeatherPage(
            result.data
        );


        const refreshButton =
            document.getElementById(
                "refreshWeather"
            );


        if (refreshButton) {

            refreshButton.addEventListener(
                "click",
                loadWeatherModule
            );
        }


    } catch (error) {

        console.error(
            "Weather module error:",
            error
        );
    }
}


function setupWeatherModule() {

    const regionSelect =
        document.getElementById(
            "regionSelect"
        );

    if (regionSelect) {

        regionSelect.addEventListener(
            "change",
            () => {
                loadWeatherModule();
            }
        );
    }
}


document.addEventListener(
    "DOMContentLoaded",
    () => {

        setupWeatherModule();

        loadWeatherModule();

    }
);