/* =========================================================
   ORCA MARINE INTELLIGENCE
   GIS / MAP MODULE
   Backend GIS + Leaflet
========================================================= */

let orcaMainMap = null;
let orcaMainMarker = null;

let orcaDashboardMap = null;


/* =========================================================
   HELPERS
========================================================= */

function gisFindValue(data, keys) {
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

function gisEscapeHtml(value) {
    const div = document.createElement("div");
    div.textContent = String(value ?? "");
    return div.innerHTML;
}


/* =========================================================
   MAIN GIS MAP
========================================================= */

function initializeMainGISMap(latitude, longitude) {

    const mapElement = document.getElementById("mainMap");

    if (!mapElement) return;

    if (typeof L === "undefined") {
        console.error("Leaflet is not loaded.");
        return;
    }

    if (!Number.isFinite(latitude) || !Number.isFinite(longitude)) {
        console.error("Invalid GIS coordinates.");
        return;
    }


    /* Create map only once */

    if (!orcaMainMap) {

        orcaMainMap = L.map("mainMap").setView(
            [latitude, longitude],
            8
        );


        L.tileLayer(
            "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
            {
                attribution:
                    "&copy; OpenStreetMap contributors"
            }
        ).addTo(orcaMainMap);

    } else {

        orcaMainMap.setView(
            [latitude, longitude],
            8
        );

    }


    /* Remove old marker */

    if (orcaMainMarker) {

        orcaMainMap.removeLayer(
            orcaMainMarker
        );

    }


    /* Add new marker */

    orcaMainMarker = L.marker(
        [latitude, longitude]
    ).addTo(orcaMainMap);


    orcaMainMarker.bindPopup(
        `
        <strong>ORCA Marine Intelligence</strong><br>
        Latitude: ${latitude}<br>
        Longitude: ${longitude}
        `
    );


    orcaMainMarker.openPopup();


    /* Fix Leaflet size when page becomes visible */

    setTimeout(() => {

        if (orcaMainMap) {
            orcaMainMap.invalidateSize();
        }

    }, 300);
}


/* =========================================================
   DASHBOARD MAP
========================================================= */

function initializeDashboardMap(latitude, longitude) {

    const mapElement =
        document.getElementById("dashboardMap");

    if (!mapElement) return;

    if (typeof L === "undefined") return;


    if (!orcaDashboardMap) {

        orcaDashboardMap = L.map(
            "dashboardMap"
        ).setView(
            [latitude, longitude],
            7
        );


        L.tileLayer(
            "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
            {
                attribution:
                    "&copy; OpenStreetMap contributors"
            }
        ).addTo(
            orcaDashboardMap
        );

    } else {

        orcaDashboardMap.setView(
            [latitude, longitude],
            7
        );

    }


    setTimeout(() => {

        if (orcaDashboardMap) {
            orcaDashboardMap.invalidateSize();
        }

    }, 300);
}


/* =========================================================
   UPDATE GIS INFORMATION
========================================================= */

function updateGISInformation(data) {

    if (!data || typeof data !== "object") {
        return;
    }


    const location = gisFindValue(
        data,
        [
            "location",
            "city",
            "place"
        ]
    );


    const latitude = gisFindValue(
        data,
        [
            "latitude",
            "lat"
        ]
    );


    const longitude = gisFindValue(
        data,
        [
            "longitude",
            "lon",
            "lng"
        ]
    );


    const marineRegion = gisFindValue(
        data,
        [
            "marine_region",
            "marineRegion"
        ]
    );


    const country = gisFindValue(
        data,
        [
            "country"
        ]
    );


    const status = gisFindValue(
        data,
        [
            "status"
        ]
    );


    console.log(
        "ORCA GIS data:",
        data
    );


    /*
       Existing coordinate inputs
    */

    const latitudeInput =
        document.getElementById(
            "latitudeInput"
        );

    const longitudeInput =
        document.getElementById(
            "longitudeInput"
        );


    if (
        latitudeInput &&
        latitude !== null
    ) {
        latitudeInput.value = latitude;
    }


    if (
        longitudeInput &&
        longitude !== null
    ) {
        longitudeInput.value = longitude;
    }


    /*
       Create / update map
    */

    if (
        latitude !== null &&
        longitude !== null
    ) {

        const lat =
            Number(latitude);

        const lon =
            Number(longitude);


        if (
            Number.isFinite(lat) &&
            Number.isFinite(lon)
        ) {

            initializeMainGISMap(
                lat,
                lon
            );

            initializeDashboardMap(
                lat,
                lon
            );

        }

    }


    /*
       Add information to the GIS page
       without changing your HTML structure.
    */

    updateGISInfoPanel(
        location,
        latitude,
        longitude,
        marineRegion,
        country,
        status
    );
}


/* =========================================================
   GIS INFORMATION PANEL
========================================================= */

function updateGISInfoPanel(
    location,
    latitude,
    longitude,
    marineRegion,
    country,
    status
) {

    const mapPage =
        document.getElementById(
            "page-maps"
        );

    if (!mapPage) return;


    let infoPanel =
        document.getElementById(
            "gisBackendInfo"
        );


    /*
       Create the information panel
       only once.
    */

    if (!infoPanel) {

        infoPanel =
            document.createElement(
                "article"
            );

        infoPanel.id =
            "gisBackendInfo";

        infoPanel.className =
            "panel";


        const fullMapPanel =
            mapPage.querySelector(
                ".full-map-panel"
            );


        if (fullMapPanel) {

            fullMapPanel.after(
                infoPanel
            );

        } else {

            mapPage.appendChild(
                infoPanel
            );

        }

    }


    infoPanel.innerHTML = `

        <div class="panel-header">

            <div>

                <span class="panel-kicker">
                    GIS BACKEND DATA
                </span>

                <h3>
                    Geospatial Information
                </h3>

            </div>

            <span class="data-badge">
                ${
                    status !== null
                        ? gisEscapeHtml(status)
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
                                ? gisEscapeHtml(location)
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
                                ? gisEscapeHtml(latitude)
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
                                ? gisEscapeHtml(longitude)
                                : "—"
                        }
                    </strong>

                </div>


                <div class="data-detail-item">

                    <span>
                        Marine Region
                    </span>

                    <strong>
                        ${
                            marineRegion !== null
                                ? gisEscapeHtml(
                                      marineRegion
                                  )
                                : "—"
                        }
                    </strong>

                </div>


                <div class="data-detail-item">

                    <span>
                        Country
                    </span>

                    <strong>
                        ${
                            country !== null
                                ? gisEscapeHtml(country)
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
                                ? gisEscapeHtml(status)
                                : "—"
                        }
                    </strong>

                </div>


            </div>

        </div>
    `;
}


/* =========================================================
   LOAD GIS BACKEND DATA
========================================================= */

async function loadGISBackendData() {

    const regionSelect =
        document.getElementById(
            "regionSelect"
        );


    const region =
        regionSelect
            ? regionSelect.value
            : "North Tamil Nadu";


    try {

        const result =
            await safeApiCall(
                getGISData,
                region
            );


        if (!result.success) {

            console.error(
                "GIS backend error:",
                result.error
            );

            return;
        }


        window.ORCA_LATEST_GIS_DATA =
            result.data;


        updateGISInformation(
            result.data
        );


    } catch (error) {

        console.error(
            "GIS loading error:",
            error
        );

    }
}


/* =========================================================
   LOCATE BUTTON
========================================================= */

function setupLocateButton() {

    const button =
        document.getElementById(
            "locateButton"
        );


    if (!button) return;


    button.addEventListener(
        "click",
        () => {

            const latitudeInput =
                document.getElementById(
                    "latitudeInput"
                );

            const longitudeInput =
                document.getElementById(
                    "longitudeInput"
                );


            if (
                !latitudeInput ||
                !longitudeInput
            ) {
                return;
            }


            const latitude =
                Number(
                    latitudeInput.value
                );


            const longitude =
                Number(
                    longitudeInput.value
                );


            if (
                !Number.isFinite(latitude) ||
                !Number.isFinite(longitude)
            ) {

                alert(
                    "Please enter valid latitude and longitude."
                );

                return;
            }


            if (
                latitude < -90 ||
                latitude > 90 ||
                longitude < -180 ||
                longitude > 180
            ) {

                alert(
                    "Latitude or longitude is outside the valid range."
                );

                return;
            }


            initializeMainGISMap(
                latitude,
                longitude
            );

        }
    );
}


/* =========================================================
   REGION CHANGE
========================================================= */

function setupGISRegionChange() {

    const regionSelect =
        document.getElementById(
            "regionSelect"
        );


    if (!regionSelect) return;


    regionSelect.addEventListener(
        "change",
        () => {

            loadGISBackendData();

        }
    );
}


/* =========================================================
   PAGE VISIBILITY FIX
========================================================= */

function setupGISNavigationFix() {

    document.addEventListener(
        "click",
        (event) => {

            const navigationButton =
                event.target.closest(
                    ".nav-item"
                );


            if (!navigationButton) {
                return;
            }


            const page =
                navigationButton.dataset.page;


            if (page === "maps") {

                setTimeout(() => {

                    if (orcaMainMap) {

                        orcaMainMap.invalidateSize();

                    }

                    if (
                        window.ORCA_LATEST_GIS_DATA
                    ) {

                        updateGISInformation(
                            window.ORCA_LATEST_GIS_DATA
                        );

                    }

                }, 300);

            }

        }
    );
}


/* =========================================================
   INITIALIZATION
========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    () => {

        setupLocateButton();

        setupGISRegionChange();

        setupGISNavigationFix();

        loadGISBackendData();

    }
);