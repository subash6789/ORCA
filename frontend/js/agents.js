/* =========================================================
   ORCA MARINE INTELLIGENCE
   COLLABORATIVE AGENTS MODULE
========================================================= */

function agentFindValue(data, keys) {
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


function agentEscapeHtml(value) {
    const div = document.createElement("div");
    div.textContent = String(value ?? "");
    return div.innerHTML;
}


function updateAgentPage(data) {

    const container = document.getElementById("page-agents");

    if (!container) return;


    if (!data || typeof data !== "object") {
        showAgentsUnavailable();
        return;
    }


    const globalStatus = agentFindValue(data, [
        "status",
        "overall_status",
        "system_status"
    ]);


    const source = agentFindValue(data, [
        "source",
        "data_source",
        "dataSource"
    ]);


    const agentList = agentFindValue(data, [
        "agents",
        "agent_status",
        "agentStatus"
    ]);


    /*
       If the backend returns an agents array,
       update the existing cards with real information.
    */

    if (Array.isArray(agentList)) {

        agentList.forEach(agent => {

            if (!agent || typeof agent !== "object") {
                return;
            }


            const name = agentFindValue(agent, [
                "name",
                "agent",
                "agent_name",
                "agentName"
            ]);


            const status = agentFindValue(agent, [
                "status",
                "state",
                "availability"
            ]);


            if (!name) return;


            const cards =
                document.querySelectorAll(".agent-card");


            cards.forEach(card => {

                const heading =
                    card.querySelector("h3");


                if (!heading) return;


                if (
                    heading.textContent
                        .trim()
                        .toLowerCase() ===
                    String(name)
                        .trim()
                        .toLowerCase()
                ) {

                    const statusElement =
                        card.querySelector(".agent-status");


                    if (statusElement) {

                        statusElement.textContent =
                            status || "Backend response";
                    }

                }

            });

        });

    }


    /*
       Create a backend information panel
       only when the backend actually provides
       useful information.
    */

    let backendPanel =
        document.getElementById("agentsBackendInfo");


    if (!backendPanel) {

        backendPanel =
            document.createElement("article");

        backendPanel.id =
            "agentsBackendInfo";

        backendPanel.className =
            "panel";

        container.appendChild(backendPanel);
    }


    backendPanel.innerHTML = `

        <div class="panel-header">

            <div>

                <span class="panel-kicker">
                    COLLABORATIVE AGENT BACKEND
                </span>

                <h3>
                    Agent System Status
                </h3>

            </div>

        </div>


        <div class="data-detail-grid">

            <div class="data-detail-item">

                <span>
                    Backend Status
                </span>

                <strong>
                    ${
                        globalStatus !== null
                        ? agentEscapeHtml(globalStatus)
                        : "Backend response received"
                    }
                </strong>

            </div>


            <div class="data-detail-item">

                <span>
                    Agent Data
                </span>

                <strong>
                    ${
                        Array.isArray(agentList)
                        ? `${agentList.length} agent records`
                        : "Not provided"
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
                        ? agentEscapeHtml(source)
                        : "Not provided"
                    }
                </strong>

            </div>

        </div>

    `;
}


function showAgentsUnavailable() {

    const container =
        document.getElementById("page-agents");

    if (!container) return;


    let backendPanel =
        document.getElementById("agentsBackendInfo");


    if (!backendPanel) {

        backendPanel =
            document.createElement("article");

        backendPanel.id =
            "agentsBackendInfo";

        backendPanel.className =
            "panel";

        container.appendChild(backendPanel);
    }


    backendPanel.innerHTML = `

        <div class="panel-header">

            <div>

                <span class="panel-kicker">
                    COLLABORATIVE AGENT BACKEND
                </span>

                <h3>
                    Agent System Status
                </h3>

            </div>

        </div>


        <div class="empty-state">

            <div class="empty-icon">
                ◎
            </div>

            <h4>
                Agent backend unavailable
            </h4>

            <p>
                ORCA could not retrieve a validated collaborative
                agent response.
            </p>

        </div>

    `;
}


async function loadAgentsModule() {

    try {

        const result =
            await safeApiCall(
                getAgentsData
            );


        if (!result.success) {

            showAgentsUnavailable();

            return;
        }


        updateAgentPage(result.data);

    }
    catch (error) {

        console.error(
            "ORCA Agents Error:",
            error
        );

        showAgentsUnavailable();
    }
}


function setupAgentsModule() {

    const regionSelect =
        document.getElementById("regionSelect");


    if (regionSelect) {

        regionSelect.addEventListener(
            "change",
            loadAgentsModule
        );
    }
}


document.addEventListener(
    "DOMContentLoaded",
    () => {

        setupAgentsModule();

        loadAgentsModule();

    }
);