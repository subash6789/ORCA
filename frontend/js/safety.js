/* =========================================================
   ORCA MARINE INTELLIGENCE
   MARINE SAFETY MODULE
========================================================= */

function safetyFindValue(data, keys) {
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


function safetyDisplay(elementId, value) {
    const element = document.getElementById(elementId);

    if (!element) return;

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


function safetyEscapeHtml(value) {
    const div = document.createElement("div");
    div.textContent = String(value ?? "");
    return div.innerHTML;
}


function updateSafetyModule(data) {

    if (!data || typeof data !== "object") {
        showSafetyUnavailable();
        return;
    }


    const status = safetyFindValue(data, [
        "status",
        "safety_status",
        "safetyStatus",
        "marine_safety_status",
        "marineSafetyStatus"
    ]);


    const alertLevel = safetyFindValue(data, [
        "alert_level",
        "alertLevel",
        "risk_level",
        "riskLevel",
        "severity",
        "level"
    ]);


    const region = safetyFindValue(data, [
        "region",
        "Region",
        "location",
        "area"
    ]);


    const source = safetyFindValue(data, [
        "source",
        "data_source",
        "dataSource"
    ]);


    const agent = safetyFindValue(data, [
        "agent",
        "Agent"
    ]);


    const message = safetyFindValue(data, [
        "message",
        "advisory",
        "alert",
        "description",
        "details",
        "safety_message"
    ]);


    const timestamp = safetyFindValue(data, [
        "timestamp",
        "time",
        "datetime",
        "updated_at",
        "updatedAt",
        "date"
    ]);


    safetyDisplay("safetyStatus", status);
    safetyDisplay("safetyAlertLevel", alertLevel);
    safetyDisplay("safetyRegion", region);
    safetyDisplay("safetySource", source);


    const statusMeta =
        document.getElementById("safetyStatusMeta");

    if (statusMeta) {

        if (source && timestamp) {
            statusMeta.textContent =
                `${source} • ${timestamp}`;
        }
        else if (timestamp) {
            statusMeta.textContent =
                `Timestamp: ${timestamp}`;
        }
        else if (source) {
            statusMeta.textContent =
                `Source: ${source}`;
        }
        else {
            statusMeta.textContent =
                "Backend response";
        }
    }


    const sourceNotice =
        document.getElementById("safetySourceNotice");

    if (sourceNotice) {

        if (source) {
            sourceNotice.textContent =
                `Backend source: ${source}`;
        }
        else {
            sourceNotice.textContent =
                "Safety response received from backend. Source not provided.";
        }
    }


    updateSafetyDetails({
        status,
        alertLevel,
        region,
        source,
        agent,
        message,
        timestamp
    });
}


function updateSafetyDetails(data) {

    const details =
        document.getElementById("safetyDetails");

    if (!details) return;


    const hasUsefulData =
        data.status !== null ||
        data.alertLevel !== null ||
        data.region !== null ||
        data.source !== null ||
        data.agent !== null ||
        data.message !== null ||
        data.timestamp !== null;


    if (!hasUsefulData) {

        details.innerHTML = `
            <div class="empty-state">

                <div class="empty-icon">
                    !
                </div>

                <h4>
                    Safety response received
                </h4>

                <p>
                    The backend responded, but no recognized
                    marine safety fields were provided.
                </p>

            </div>
        `;

        return;
    }


    details.innerHTML = `

        <div class="data-detail-grid">

            <div class="data-detail-item">

                <span>
                    Safety Status
                </span>

                <strong>
                    ${
                        data.status !== null
                        ? safetyEscapeHtml(data.status)
                        : "—"
                    }
                </strong>

            </div>


            <div class="data-detail-item">

                <span>
                    Alert Level
                </span>

                <strong>
                    ${
                        data.alertLevel !== null
                        ? safetyEscapeHtml(data.alertLevel)
                        : "—"
                    }
                </strong>

            </div>


            <div class="data-detail-item">

                <span>
                    Region
                </span>

                <strong>
                    ${
                        data.region !== null
                        ? safetyEscapeHtml(data.region)
                        : "—"
                    }
                </strong>

            </div>


            <div class="data-detail-item">

                <span>
                    Agent
                </span>

                <strong>
                    ${
                        data.agent !== null
                        ? safetyEscapeHtml(data.agent)
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
                        data.timestamp !== null
                        ? safetyEscapeHtml(data.timestamp)
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
                        data.source !== null
                        ? safetyEscapeHtml(data.source)
                        : "—"
                    }
                </strong>

            </div>

        </div>


        <div
            style="
                margin-top:20px;
                padding:16px;
                border-radius:12px;
                background:rgba(127,127,127,.08);
            "
        >

            <strong>
                Safety Information
            </strong>

            <p style="margin-top:8px;">

                ${
                    data.message !== null
                    ? safetyEscapeHtml(data.message)
                    : "No additional safety message was provided by the backend."
                }

            </p>

        </div>

    `;
}


function showSafetyUnavailable() {

    safetyDisplay("safetyStatus", null);
    safetyDisplay("safetyAlertLevel", null);
    safetyDisplay("safetyRegion", null);
    safetyDisplay("safetySource", null);


    const statusMeta =
        document.getElementById("safetyStatusMeta");

    if (statusMeta) {
        statusMeta.textContent =
            "Safety data unavailable";
    }


    const sourceNotice =
        document.getElementById("safetySourceNotice");

    if (sourceNotice) {
        sourceNotice.textContent =
            "Marine safety backend data is unavailable.";
    }


    const details =
        document.getElementById("safetyDetails");

    if (details) {

        details.innerHTML = `
            <div class="empty-state">

                <div class="empty-icon">
                    !
                </div>

                <h4>
                    Marine safety information unavailable
                </h4>

                <p>
                    ORCA could not retrieve a validated safety
                    response from the backend.
                </p>

            </div>
        `;
    }
}


async function loadSafetyModule() {

    const regionSelect =
        document.getElementById("regionSelect");

    const region =
        regionSelect
        ? regionSelect.value
        : "North Tamil Nadu";


    const refreshButton =
        document.getElementById("refreshSafety");


    const sourceNotice =
        document.getElementById("safetySourceNotice");


    if (refreshButton) {

        refreshButton.disabled = true;

        refreshButton.textContent =
            "Loading...";
    }


    if (sourceNotice) {

        sourceNotice.textContent =
            `Checking marine safety backend for ${region}...`;
    }


    try {

        const result =
            await safeApiCall(
                getSafetyData,
                region
            );


        if (!result.success) {

            showSafetyUnavailable();

            return;
        }


        updateSafetyModule(result.data);

    }
    finally {

        if (refreshButton) {

            refreshButton.disabled = false;

            refreshButton.textContent =
                "↻ Refresh Safety";
        }
    }
}


function setupSafetyModule() {

    const refreshButton =
        document.getElementById("refreshSafety");


    if (refreshButton) {

        refreshButton.addEventListener(
            "click",
            loadSafetyModule
        );
    }


    const regionSelect =
        document.getElementById("regionSelect");


    if (regionSelect) {

        regionSelect.addEventListener(
            "change",
            loadSafetyModule
        );
    }
}


document.addEventListener(
    "DOMContentLoaded",
    () => {

        setupSafetyModule();

        loadSafetyModule();

    }
);