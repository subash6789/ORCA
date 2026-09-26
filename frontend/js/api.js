/* =========================================================
   ORCA MARINE INTELLIGENCE
   LOCAL BACKEND API CONNECTION
========================================================= */

const ORCA_API_BASE_URL = "http://127.0.0.1:8000";


/* =========================================================
   COMMON API GET FUNCTION
========================================================= */

async function orcaGet(endpoint, params = {}) {

    const url = new URL(
        `${ORCA_API_BASE_URL}${endpoint}`
    );

    Object.entries(params).forEach(([key, value]) => {

        if (
            value !== undefined &&
            value !== null &&
            value !== ""
        ) {
            url.searchParams.set(key, value);
        }

    });

    const response = await fetch(url.toString());

    if (!response.ok) {

        throw new Error(
            `ORCA API request failed: ${response.status}`
        );

    }

    return await response.json();
}


/* =========================================================
   BACKEND HEALTH
========================================================= */

async function checkBackendHealth() {

    return await orcaGet("/health");

}


/* =========================================================
   OCEAN AGENT
========================================================= */

async function getOceanData(state = "Tamil Nadu") {

    return await orcaGet("/ocean", {
        state: state
    });

}


/* =========================================================
   PFZ / FISHING AGENT
========================================================= */

async function getPFZData(state = "Tamil Nadu") {

    return await orcaGet("/pfz", {
        state: state
    });

}


/* =========================================================
   WEATHER AGENT
========================================================= */

async function getWeatherData(state = "Tamil Nadu") {

    return await orcaGet("/weather", {
        state: state
    });

}


/* =========================================================
   GIS AGENT
========================================================= */

async function getGISData(
    state = "Tamil Nadu",
    district = ""
) {

    return await orcaGet("/gis", {
        state: state,
        district: district
    });

}


/* =========================================================
   SAFETY AGENT
========================================================= */

async function getSafetyData(state = "Tamil Nadu") {

    return await orcaGet("/safety", {
        state: state
    });

}


/* =========================================================
   SATELLITE AGENT
========================================================= */

async function getSatelliteData(state = "Tamil Nadu") {

    return await orcaGet("/satellite", {
        state: state
    });

}


/* =========================================================
   COLLABORATIVE AGENTS
========================================================= */

async function getAgentsData() {

    return await orcaGet("/agents");

}


/* =========================================================
   ORCA AI REASONING
========================================================= */

async function getReasoningData(
    state = "Tamil Nadu",
    question = "What are the marine conditions?",
    district = ""
) {

    return await orcaGet("/reasoning", {

        question: question,

        state: state,

        district: district

    });

}


/* =========================================================
   ORCA QUESTION / LANGUAGE
========================================================= */

async function askORCA(
    question,
    state = "Tamil Nadu",
    district = ""
) {

    return await orcaGet("/ask", {

        question: question,

        state: state,

        district: district

    });

}


/* =========================================================
   SAFE API CALL
========================================================= */

async function safeApiCall(
    apiFunction,
    ...args
) {

    try {

        const data = await apiFunction(
            ...args
        );

        return {

            success: true,

            data: data,

            error: null

        };

    }

    catch (error) {

        console.error(
            "ORCA API Error:",
            error
        );

        return {

            success: false,

            data: null,

            error:
                error.message ||
                "Unable to connect to ORCA backend."

        };

    }

}


/* =========================================================
   ORCA CONNECTION TEST
========================================================= */

async function testORCAConnection() {

    try {

        const result =
            await checkBackendHealth();

        console.log(
            "ORCA Backend Connected:",
            result
        );

        return true;

    }

    catch (error) {

        console.error(
            "ORCA Backend Connection Failed:",
            error
        );

        return false;

    }

}


/* =========================================================
   AUTO CONNECTION CHECK
========================================================= */

window.addEventListener(
    "DOMContentLoaded",
    () => {

        testORCAConnection();

    }
);