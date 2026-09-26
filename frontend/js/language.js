/* =========================================================
   ORCA MARINE INTELLIGENCE
   Language Controller
========================================================= */

const ORCA_TRANSLATIONS = {

    en: {

        dashboard: "Dashboard",
        assistant: "ORCA AI Assistant",
        ocean: "Ocean Intelligence",
        weather: "Weather Intelligence",
        maps: "GIS & Maps",
        fishing: "Fishing / PFZ",
        satellite: "Satellite Intelligence",
        safety: "Marine Safety",
        agents: "Collaborative Agents",
        reasoning: "AI Reasoning",
        sources: "Data Sources",
        settings: "Settings",

        region: "Region",
        refresh: "↻ Refresh Data",
        refreshPfz: "↻ Refresh PFZ",

        marineOverview: "Ocean Overview",
        backendConnected: "Backend connected",
        backendUnavailable: "Backend unavailable",

        integrationReady: "Integration Ready",
        notConnected: "Not Connected"

    },


    ta: {

        dashboard: "டாஷ்போர்டு",
        assistant: "ORCA AI உதவியாளர்",
        ocean: "கடல் நுண்ணறிவு",
        weather: "வானிலை நுண்ணறிவு",
        maps: "GIS & வரைபடங்கள்",
        fishing: "மீன்பிடி / PFZ",
        satellite: "செயற்கைக்கோள் நுண்ணறிவு",
        safety: "கடல் பாதுகாப்பு",
        agents: "கூட்டு AI Agents",
        reasoning: "AI Reasoning",
        sources: "தரவு ஆதாரங்கள்",
        settings: "அமைப்புகள்",

        region: "பகுதி",
        refresh: "↻ தரவை புதுப்பிக்கவும்",
        refreshPfz: "↻ PFZ புதுப்பிக்கவும்",

        marineOverview: "கடல் நிலவரம்",
        backendConnected: "Backend இணைக்கப்பட்டுள்ளது",
        backendUnavailable: "Backend கிடைக்கவில்லை",

        integrationReady: "Integration Ready",
        notConnected: "இணைக்கப்படவில்லை"

    }

};


/* ---------------------------------------------------------
   Current Language
--------------------------------------------------------- */

let orcaLanguage = "en";


/* ---------------------------------------------------------
   Get Translation
--------------------------------------------------------- */

function translate(key) {

    return (
        ORCA_TRANSLATIONS[orcaLanguage]?.[key] ||
        ORCA_TRANSLATIONS.en[key] ||
        key
    );

}


/* ---------------------------------------------------------
   Change Language
--------------------------------------------------------- */

function setORCALanguage(language) {

    if (!ORCA_TRANSLATIONS[language]) {

        language = "en";

    }


    orcaLanguage = language;


    document.documentElement.lang =
        language === "ta"
            ? "ta"
            : "en";


    updateStaticTranslations();

}


/* ---------------------------------------------------------
   Update Navigation
--------------------------------------------------------- */

function updateStaticTranslations() {

    const pageMap = {

        dashboard: "dashboard",
        assistant: "assistant",
        ocean: "ocean",
        weather: "weather",
        maps: "maps",
        fishing: "fishing",
        satellite: "satellite",
        safety: "safety",
        agents: "agents",
        reasoning: "reasoning",
        sources: "sources",
        settings: "settings"

    };


    Object.entries(pageMap).forEach(
        ([page, key]) => {

            const item =
                document.querySelector(
                    `.nav-item[data-page="${page}"]`
                );


            if (!item) return;


            const text =
                item.querySelector(
                    "span:last-child"
                );


            if (text) {

                text.textContent =
                    translate(key);

            }

        }
    );


    /* Region label */

    const regionLabel =
        document.querySelector(
            ".region-selector label"
        );


    if (regionLabel) {

        regionLabel.textContent =
            translate("region");

    }


    /* Refresh buttons */

    const refreshButton =
        document.getElementById(
            "refreshDashboard"
        );


    if (
        refreshButton &&
        !refreshButton.disabled
    ) {

        refreshButton.textContent =
            translate("refresh");

    }


    const pfzButton =
        document.getElementById(
            "refreshPfz"
        );


    if (
        pfzButton &&
        !pfzButton.disabled
    ) {

        pfzButton.textContent =
            translate("refreshPfz");

    }

}


/* ---------------------------------------------------------
   Language Selector
--------------------------------------------------------- */

function setupLanguageSelector() {

    const selector =
        document.getElementById(
            "languageSelector"
        );


    const settingsSelector =
        document.getElementById(
            "settingsLanguage"
        );


    if (selector) {

        selector.value =
            orcaLanguage;


        selector.addEventListener(
            "change",
            () => {

                setORCALanguage(
                    selector.value
                );


                if (settingsSelector) {

                    settingsSelector.value =
                        selector.value;

                }

            }
        );

    }


    if (settingsSelector) {

        settingsSelector.value =
            orcaLanguage;


        settingsSelector.addEventListener(
            "change",
            () => {

                setORCALanguage(
                    settingsSelector.value
                );


                if (selector) {

                    selector.value =
                        settingsSelector.value;

                }

            }
        );

    }

}


/* ---------------------------------------------------------
   Initialize
--------------------------------------------------------- */

document.addEventListener(
    "DOMContentLoaded",
    () => {

        setupLanguageSelector();

        updateStaticTranslations();

    }
);