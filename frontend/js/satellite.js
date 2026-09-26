/* =========================================================
   ORCA MARINE INTELLIGENCE
   SATELLITE INTELLIGENCE MODULE
========================================================= */

function satelliteFindValue(data, keys) {

    if (!data || typeof data !== "object") {
        return null;
    }

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


/* ---------------------------------------------------------
   DISPLAY VALUE
--------------------------------------------------------- */

function satelliteDisplay(elementId, value) {

    const element =
        document.getElementById(elementId);

    if (!element) {
        return;
    }

    if (
        value === undefined ||
        value === null ||
        value === ""
    ) {
        element.textContent = "—";
        return;
    }

    element.textContent = String(value);
}


/* ---------------------------------------------------------
   ESCAPE HTML
--------------------------------------------------------- */

function satelliteEscapeHtml(value) {

    const div =
        document.createElement("div");

    div.textContent =
        String(value ?? "");

    return div.innerHTML;
}


/* ---------------------------------------------------------
   UPDATE SATELLITE PAGE
--------------------------------------------------------- */

function updateSatelliteModule(data) {

    if (!data || typeof data !== "object") {

        showSatelliteUnavailable();

        return;
    }


    const agent =
        satelliteFindValue(
            data,
            ["agent"]
        );


    const status =
        satelliteFindValue(
            data,
            ["status"]
        );


    const satellite =
        satelliteFindValue(
            data,
            ["satellite"]
        );


    const agency =
        satelliteFindValue(
            data,
            ["agency"]
        );


    const mission =
        satelliteFindValue(
            data,
            ["mission"]
        );


    const integrationStatus =
        satelliteFindValue(
            data,
            [
                "integration_status",
                "integrationStatus"
            ]
        );


    const source =
        satelliteFindValue(
            data,
            [
                "source",
                "data_source",
                "dataSource"
            ]
        );


    const message =
        satelliteFindValue(
            data,
            ["message"]
        );


    const dataTypes =
        satelliteFindValue(
            data,
            [
                "data_types",
                "dataTypes"
            ]
        );


    satelliteDisplay(
        "satelliteName",
        satellite
    );


    satelliteDisplay(
        "satelliteAgency",
        agency
    );


    satelliteDisplay(
        "satelliteStatus",
        status
    );


    satelliteDisplay(
        "satelliteIntegrationStatus",
        integrationStatus
    );


    satelliteDisplay(
        "satelliteMessage",
        message
    );


    satelliteDisplay(
        "satelliteAgent",
        agent
    );


    satelliteDisplay(
        "satelliteSource",
        source
    );


    /* -----------------------------------------------------
       DATA TYPES
    ----------------------------------------------------- */

    const dataTypesElement =
        document.getElementById(
            "satelliteDataTypes"
        );


    if (dataTypesElement) {

        if (Array.isArray(dataTypes)) {

            dataTypesElement.innerHTML =
                dataTypes
                    .map(
                        item => `
                            <span class="data-tag">
                                ${satelliteEscapeHtml(item)}
                            </span>
                        `
                    )
                    .join("");

        } else {

            dataTypesElement.textContent =
                dataTypes || "—";

        }

    }


    /* -----------------------------------------------------
       DETAILS
    ----------------------------------------------------- */

    updateSatelliteDetails(data);
}


/* ---------------------------------------------------------
   SATELLITE DETAILS
--------------------------------------------------------- */

function updateSatelliteDetails(data) {

    const container =
        document.getElementById(
            "satelliteDetails"
        );


    if (!container) {
        return;
    }


    const satellite =
        satelliteFindValue(
            data,
            ["satellite"]
        );


    const agency =
        satelliteFindValue(
            data,
            ["agency"]
        );


    const mission =
        satelliteFindValue(
            data,
            ["mission"]
        );


    const integrationStatus =
        satelliteFindValue(
            data,
            [
                "integration_status",
                "integrationStatus"
            ]
        );


    const status =
        satelliteFindValue(
            data,
            ["status"]
        );


    const source =
        satelliteFindValue(
            data,
            [
                "source",
                "data_source",
                "dataSource"
            ]
        );


    container.innerHTML = `

        <div class="data-detail-grid">

            <div class="data-detail-item">

                <span>
                    Satellite
                </span>

                <strong>
                    ${
                        satellite !== null
                            ? satelliteEscapeHtml(satellite)
                            : "—"
                    }
                </strong>

            </div>


            <div class="data-detail-item">

                <span>
                    Agency
                </span>

                <strong>
                    ${
                        agency !== null
                            ? satelliteEscapeHtml(agency)
                            : "—"
                    }
                </strong>

            </div>


            <div class="data-detail-item">

                <span>
                    Mission
                </span>

                <strong>
                    ${
                        mission !== null
                            ? satelliteEscapeHtml(mission)
                            : "—"
                    }
                </strong>

            </div>


            <div class="data-detail-item">

                <span>
                    Integration Status
                </span>

                <strong>
                    ${
                        integrationStatus !== null
                            ? satelliteEscapeHtml(
                                integrationStatus
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
                            ? satelliteEscapeHtml(status)
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
                            ? satelliteEscapeHtml(source)
                            : "—"
                    }
                </strong>

            </div>

        </div>

    `;
}


/* ---------------------------------------------------------
   UNAVAILABLE STATE
--------------------------------------------------------- */

function showSatelliteUnavailable() {

    satelliteDisplay(
        "satelliteName",
        null
    );


    satelliteDisplay(
        "satelliteAgency",
        null
    );


    satelliteDisplay(
        "satelliteStatus",
        null
    );


    satelliteDisplay(
        "satelliteIntegrationStatus",
        null
    );


    satelliteDisplay(
        "satelliteMessage",
        null
    );


    satelliteDisplay(
        "satelliteAgent",
        null
    );


    satelliteDisplay(
        "satelliteSource",
        null
    );


    const dataTypesElement =
        document.getElementById(
            "satelliteDataTypes"
        );


    if (dataTypesElement) {
        dataTypesElement.textContent = "—";
    }


    const details =
        document.getElementById(
            "satelliteDetails"
        );


    if (details) {

        details.innerHTML = `

            <div class="empty-state">

                <div class="empty-icon">
                    ◌
                </div>

                <h4>
                    Satellite data unavailable
                </h4>

                <p>
                    No validated satellite backend
                    response is currently available.
                </p>

            </div>

        `;
    }
}


/* ---------------------------------------------------------
   LOAD SATELLITE DATA
--------------------------------------------------------- */

async function loadSatelliteModule() {

    const refreshButton =
        document.getElementById(
            "refreshSatellite"
        );


    if (refreshButton) {

        refreshButton.disabled = true;

        refreshButton.textContent =
            "Loading...";

    }


    try {

        const regionSelect =
            document.getElementById(
                "regionSelect"
            );


        const region =
            regionSelect
                ? regionSelect.value
                : "North Tamil Nadu";


        const result =
            await safeApiCall(
                getSatelliteData,
                region
            );


        if (!result.success) {

            showSatelliteUnavailable();

            return;
        }


        window.ORCA_LATEST_SATELLITE_DATA =
            result.data;


        updateSatelliteModule(
            result.data
        );


    } finally {

        if (refreshButton) {

            refreshButton.disabled = false;

            refreshButton.textContent =
                "↻ Refresh Satellite";

        }

    }

}


/* ---------------------------------------------------------
   SETUP EVENTS
--------------------------------------------------------- */

function setupSatelliteModule() {

    const refreshButton =
        document.getElementById(
            "refreshSatellite"
        );


    if (refreshButton) {

        refreshButton.addEventListener(
            "click",
            loadSatelliteModule
        );

    }


    const regionSelect =
        document.getElementById(
            "regionSelect"
        );


    if (regionSelect) {

        regionSelect.addEventListener(
            "change",
            loadSatelliteModule
        );

    }

}


/* ---------------------------------------------------------
   INITIALIZE
--------------------------------------------------------- */

document.addEventListener(
    "DOMContentLoaded",
    () => {

        setupSatelliteModule();

        loadSatelliteModule();

    }
);