/* =========================================================
   ORCA MARINE INTELLIGENCE
   Main Application Controller
========================================================= */

document.addEventListener("DOMContentLoaded", () => {

    const navItems =
        document.querySelectorAll(".nav-item");

    const pages =
        document.querySelectorAll(".page-section");

    const pageTitle =
        document.getElementById("pageTitle");

    const mobileMenu =
        document.getElementById("mobileMenu");

    const sidebar =
        document.getElementById("sidebar");

    const sidebarClose =
        document.getElementById("sidebarClose");


    /* -----------------------------------------------------
       Page Names
    ----------------------------------------------------- */

    const pageNames = {

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

        settings: "Settings"

    };


    /* -----------------------------------------------------
       Show Page
    ----------------------------------------------------- */

    function showPage(pageName) {

        const targetPage =
            document.getElementById(
                `page-${pageName}`
            );


        if (!targetPage) {

            console.warn(
                `ORCA: Page "${pageName}" not found.`
            );

            return;

        }


        /* Remove active state */

        navItems.forEach((item) => {

            item.classList.remove("active");

        });


        pages.forEach((page) => {

            page.classList.remove("active");

        });


        /* Activate selected page */

        targetPage.classList.add("active");


        const selectedNav =
            document.querySelector(
                `.nav-item[data-page="${pageName}"]`
            );


        if (selectedNav) {

            selectedNav.classList.add("active");

        }


        /* Update title */

        if (pageTitle) {

            pageTitle.textContent =
                pageNames[pageName] || pageName;

        }


        /* Close mobile sidebar */

        if (sidebar) {

            sidebar.classList.remove("open");

        }


        /* Update browser title */

        document.title =
            `${pageNames[pageName] || "ORCA"} | ORCA Marine Intelligence`;

    }


    /* -----------------------------------------------------
       Sidebar Navigation
    ----------------------------------------------------- */

    navItems.forEach((item) => {

        item.addEventListener(
            "click",
            () => {

                const pageName =
                    item.dataset.page;

                if (pageName) {

                    showPage(pageName);

                }

            }
        );

    });


    /* -----------------------------------------------------
       Internal Page Links
    ----------------------------------------------------- */

    const pageLinks =
        document.querySelectorAll(
            "[data-page-link]"
        );


    pageLinks.forEach((link) => {

        link.addEventListener(
            "click",
            () => {

                const pageName =
                    link.dataset.pageLink;

                if (pageName) {

                    showPage(pageName);

                }

            }
        );

    });


    /* -----------------------------------------------------
       Mobile Menu
    ----------------------------------------------------- */

    if (mobileMenu && sidebar) {

        mobileMenu.addEventListener(
            "click",
            () => {

                sidebar.classList.add("open");

            }
        );

    }


    /* -----------------------------------------------------
       Mobile Sidebar Close
    ----------------------------------------------------- */

    if (sidebarClose && sidebar) {

        sidebarClose.addEventListener(
            "click",
            () => {

                sidebar.classList.remove("open");

            }
        );

    }


    /* -----------------------------------------------------
       Close Sidebar When Clicking Outside
    ----------------------------------------------------- */

    document.addEventListener(
        "click",
        (event) => {

            if (
                window.innerWidth <= 850 &&
                sidebar &&
                sidebar.classList.contains("open") &&
                !sidebar.contains(event.target) &&
                !mobileMenu?.contains(event.target)
            ) {

                sidebar.classList.remove("open");

            }

        }
    );


    /* -----------------------------------------------------
       ESC Key
    ----------------------------------------------------- */

    document.addEventListener(
        "keydown",
        (event) => {

            if (event.key === "Escape") {

                sidebar?.classList.remove("open");

            }

        }
    );


    /* -----------------------------------------------------
       Region Selection
    ----------------------------------------------------- */

    const regionSelect =
        document.getElementById(
            "regionSelect"
        );


    if (regionSelect) {

        regionSelect.addEventListener(
            "change",
            () => {

                console.log(
                    "ORCA region selected:",
                    regionSelect.value
                );

            }
        );

    }


    /* -----------------------------------------------------
       Initial Page
    ----------------------------------------------------- */

    showPage("dashboard");

});