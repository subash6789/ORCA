/* =========================================================
   ORCA MARINE INTELLIGENCE
   PFZ / FISHING MODULE
   Separate from dashboard.js
========================================================= */


/* ---------------------------------------------------------
   PFZ Value Helper
--------------------------------------------------------- */

function pfzFindValue(data, keys) {

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
   PFZ Display Helper
--------------------------------------------------------- */

function pfzDisplay(elementId, value) {

    const element =
        document.getElementById(elementId);

    if (!element) return;

    if (
        value === undefined ||
        value === null ||
        value === ""
    ) {
        element.textContent = "—";
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


/* ---------------------------------------------------------
   PFZ HTML Escape
--------------------------------------------------------- */

function pfzEscapeHtml(value) {

    const div =
        document.createElement("div");

    div.textContent =
        String(value ?? "");

    return div.innerHTML;
}


/* ---------------------------------------------------------
   Update PFZ Page
--------------------------------------------------------- */

function updatePFZModule(data) {

    if (!data || typeof data !== "object") {

        pfzDisplay("pfzAdvisory", null);
        pfzDisplay("pfzSst", null);
        pfzDisplay("pfzChlorophyll", null);

        updatePFZDetails(null);

        return;
    }


    const advisory =
        pfzFindValue(
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


    const sst =
        pfzFindValue(
            data,
            [
                "sst",
                "SST",
                "sea_surface_temperature_c",
                "seaSurfaceTemperature"
            ]
        );


    const chlorophyll =
        pfzFindValue(
            data,
            [
                "chlorophyll",
                "chlorophyll_a",
                "chlorophyllA"
            ]
        );


    const source =
        pfzFindValue(
            data,
            [
                "source",
                "data_source",
                "dataSource"
            ]
        );


    const timestamp =
        pfzFindValue(
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


    pfzDisplay(
        "pfzAdvisory",
        advisory
    );


    pfzDisplay(
        "pfzSst",
        sst
    );


    pfzDisplay(
        "pfzChlorophyll",
        chlorophyll
    );


    const advisoryMeta =
        document.getElementById(
            "pfzAdvisoryMeta"
        );


    if (advisoryMeta) {

        if (source && timestamp) {

            advisoryMeta.textContent =
                `${source} • ${timestamp}`;

        }

        else if (timestamp) {

            advisoryMeta.textContent =
                `Timestamp: ${timestamp}`;

        }

        else if (source) {

            advisoryMeta.textContent =
                `Source: ${source}`;

        }

        else {

            advisoryMeta.textContent =
                "Backend response";

        }

    }


    const sourceNotice =
        document.getElementById(
            "pfzSourceNotice"
        );


    if (sourceNotice) {

        sourceNotice.textContent =
            source
                ? `Backend source: ${source}`
                : "PFZ response received from backend. Source not provided.";

    }


    updatePFZDetails(data);

}


/* ---------------------------------------------------------
   PFZ Details
--------------------------------------------------------- */

function updatePFZDetails(data) {

    const details =
        document.getElementById(
            "pfzDetails"
        );

    if (!details) return;


    if (!data || typeof data !== "object") {

        details.innerHTML = `

            <div class="empty-state">

                <div class="empty-icon">
                    ⌖
                </div>

                <h4>
                    No PFZ information loaded
                </h4>

                <p>
                    No validated PFZ response is available.
                </p>

            </div>

        `;

        return;
    }


    const region =
        pfzFindValue(
            data,
            [
                "region",
                "Region",
                "area",
                "location"
            ]
        );


    const advisory =
        pfzFindValue(
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


    const latitude =
        pfzFindValue(
            data,
            [
                "latitude",
                "lat"
            ]
        );


    const longitude =
        pfzFindValue(
            data,
            [
                "longitude",
                "lon",
                "lng"
            ]
        );


    const timestamp =
        pfzFindValue(
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
        pfzFindValue(
            data,
            [
                "source",
                "data_source",
                "dataSource"
            ]
        );


    const hasUsefulData =
        region !== null ||
        advisory !== null ||
        latitude !== null ||
        longitude !== null ||
        timestamp !== null ||
        source !== null;


    if (!hasUsefulData) {

        details.innerHTML = `

            <div class="empty-state">

                <div class="empty-icon">
                    ⌖
                </div>

                <h4>
                    PFZ response received
                </h4>

                <p>
                    The backend responded, but no recognized PFZ fields were provided.
                </p>

            </div>

        `;

        return;
    }


    details.innerHTML = `

        <div class="data-detail-grid">

            <div class="data-detail-item">

                <span>
                    Region
                </span>

                <strong>
                    ${
                        region !== null
                            ? pfzEscapeHtml(String(region))
                            : "—"
                    }
                </strong>

            </div>


            <div class="data-detail-item">

                <span>
                    PFZ Advisory
                </span>

                <strong>
                    ${
                        advisory !== null
                            ? pfzEscapeHtml(String(advisory))
                            : "—"
                    }
                </strong>

            </div>


            <div class="data-detail-item">

                <span>
                    Latitude
                </span>

                <strong>
                    ${
                        latitude !== null
                            ? pfzEscapeHtml(String(latitude))
                            : "—"
                    }
                </strong>

            </div>


            <div class="data-detail-item">

                <span>
                    Longitude
                </span>

                <strong>
                    ${
                        longitude !== null
                            ? pfzEscapeHtml(String(longitude))
                            : "—"
                    }
                </strong>

            </div>


            <div class="data-detail-item">

                <span>
                    Timestamp
                </span>

                <strong>
                    ${
                        timestamp !== null
                            ? pfzEscapeHtml(String(timestamp))
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
                            ? pfzEscapeHtml(String(source))
                            : "Backend response"
                    }
                </strong>

            </div>

        </div>

    `;

}


/* ---------------------------------------------------------
   Load PFZ Data
--------------------------------------------------------- */

async function loadPFZModule() {

    const regionSelect =
        document.getElementById(
            "regionSelect"
        );


    const region =
        regionSelect
            ? regionSelect.value
            : "North Tamil Nadu";


    const refreshButton =
        document.getElementById(
            "refreshPfz"
        );


    const sourceNotice =
        document.getElementById(
            "pfzSourceNotice"
        );


    if (refreshButton) {

        refreshButton.disabled = true;

        refreshButton.textContent =
            "Loading...";

    }


    if (sourceNotice) {

        sourceNotice.textContent =
            `Checking PFZ backend data for ${region}...`;

    }


    try {

        const result =
            await safeApiCall(
                getPFZData,
                region
            );


        if (!result.success) {

            pfzDisplay(
                "pfzAdvisory",
                null
            );

            pfzDisplay(
                "pfzSst",
                null
            );

            pfzDisplay(
                "pfzChlorophyll",
                null
            );


            const advisoryMeta =
                document.getElementById(
                    "pfzAdvisoryMeta"
                );


            if (advisoryMeta) {

                advisoryMeta.textContent =
                    "PFZ data unavailable";

            }


            if (sourceNotice) {

                sourceNotice.textContent =
                    "PFZ backend data is unavailable.";

            }


            updatePFZDetails(null);

            return;
        }


        updatePFZModule(
            result.data
        );


    }

    finally {

        if (refreshButton) {

            refreshButton.disabled =
                false;

            refreshButton.textContent =
                "↻ Refresh PFZ";

        }

    }

}


/* ---------------------------------------------------------
   PFZ Events
--------------------------------------------------------- */

function setupPFZModule() {

    const refreshButton =
        document.getElementById(
            "refreshPfz"
        );


    if (refreshButton) {

        refreshButton.addEventListener(
            "click",
            loadPFZModule
        );

    }


    const regionSelect =
        document.getElementById(
            "regionSelect"
        );


    if (regionSelect) {

        regionSelect.addEventListener(
            "change",
            loadPFZModule
        );

    }

}


/* ---------------------------------------------------------
   Initialize PFZ Module
--------------------------------------------------------- */

document.addEventListener(
    "DOMContentLoaded",
    () => {

        setupPFZModule();

        loadPFZModule();

    }
);