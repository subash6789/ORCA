```javascript
/* =========================================================
   ORCA AI REASONING
   Phase 7 - Live Backend Reasoning + Evidence
========================================================= */

document.addEventListener("DOMContentLoaded", () => {

    const reasoningPage =
        document.getElementById("page-reasoning");

    if (!reasoningPage) {
        console.warn("ORCA Reasoning page not found.");
        return;
    }

    function getSelectedRegion() {

        const regionSelect =
            document.getElementById("regionSelect");

        return regionSelect && regionSelect.value
            ? regionSelect.value
            : "Tamil Nadu";
    }

    function setStatus(message, success = true) {

        let statusBox =
            document.getElementById("orcaReasoningStatus");

        if (!statusBox) {

            statusBox =
                document.createElement("div");

            statusBox.id =
                "orcaReasoningStatus";

            statusBox.style.margin = "12px 0";
            statusBox.style.padding = "10px 14px";
            statusBox.style.borderRadius = "8px";

            reasoningPage.prepend(statusBox);
        }

        statusBox.textContent = message;

        statusBox.style.background =
            success ? "#e8f5e9" : "#ffebee";

        statusBox.style.color =
            success ? "#1b5e20" : "#b71c1c";
    }

    function createReasoningPanel() {

        let panel =
            document.getElementById(
                "orcaLiveReasoningPanel"
            );

        if (panel) {
            return panel;
        }

        panel =
            document.createElement("div");

        panel.id =
            "orcaLiveReasoningPanel";

        panel.className =
            "panel";

        panel.style.marginTop = "20px";

        reasoningPage.appendChild(panel);

        return panel;
    }

    function escapeHTML(value) {

        const div =
            document.createElement("div");

        div.textContent =
            value ?? "";

        return div.innerHTML;
    }

    function renderEvidenceSummary(summary) {

        if (!summary) {
            return `
                <p>No evidence summary available.</p>
            `;
        }

        return `
            <div style="
                display:grid;
                grid-template-columns:
                repeat(auto-fit,minmax(180px,1fr));
                gap:12px;
                margin:15px 0;
            ">

                <div class="panel">
                    <strong>Observed</strong>
                    <p>${summary.OBSERVED ?? 0}</p>
                </div>

                <div class="panel">
                    <strong>Current Weather</strong>
                    <p>${summary.CURRENT_WEATHER ?? 0}</p>
                </div>

                <div class="panel">
                    <strong>Forecast</strong>
                    <p>${summary.FORECAST ?? 0}</p>
                </div>

                <div class="panel">
                    <strong>Mapped</strong>
                    <p>${summary.MAPPED ?? 0}</p>
                </div>

                <div class="panel">
                    <strong>Integration Ready</strong>
                    <p>${summary["INTEGRATION READY"] ?? 0}</p>
                </div>

                <div class="panel">
                    <strong>Demo Rule</strong>
                    <p>${summary.DEMO_RULE ?? 0}</p>
                </div>

                <div class="panel">
                    <strong>Unavailable</strong>
                    <p>${summary.UNAVAILABLE ?? 0}</p>
                </div>

            </div>
        `;
    }

    function renderReasoning(data) {

        const panel =
            createReasoningPanel();

        const agents =
            Array.isArray(data.selected_agents)
                ? data.selected_agents
                : [];

        const reasoningPoints =
            Array.isArray(data.reasoning_points)
                ? data.reasoning_points
                : [];

        const evidence =
            Array.isArray(data.evidence)
                ? data.evidence
                : [];

        const evidenceSummary =
            data.evidence_summary || {};

        panel.innerHTML = `

            <div class="panel-header">

                <div>

                    <h3>
                        Live ORCA AI Reasoning
                    </h3>

                    <p>
                        Reasoning data loaded directly
                        from the ORCA backend.
                    </p>

                </div>

            </div>

            <div style="
                display:grid;
                grid-template-columns:
                repeat(auto-fit,minmax(180px,1fr));
                gap:15px;
                margin:15px 0;
            ">

                <div class="panel">

                    <strong>Status</strong>

                    <p>
                        ${escapeHTML(
                            data.status || "—"
                        )}
                    </p>

                </div>

                <div class="panel">

                    <strong>Selected Agents</strong>

                    <p>
                        ${agents.length}
                    </p>

                </div>

                <div class="panel">

                    <strong>Reasoning Points</strong>

                    <p>
                        ${reasoningPoints.length}
                    </p>

                </div>

                <div class="panel">

                    <strong>Evidence Sources</strong>

                    <p>
                        ${evidence.length}
                    </p>

                </div>

            </div>

            <h4>
                Selected Agents
            </h4>

            <ul>

                ${
                    agents.length

                        ? agents.map(agent =>
                            `<li>
                                ${escapeHTML(
                                    typeof agent === "string"
                                        ? agent
                                        : agent.name || "Agent"
                                )}
                            </li>`
                        ).join("")

                        : "<li>—</li>"
                }

            </ul>

            <h4>
                Reasoning Points
            </h4>

            <ul>

                ${
                    reasoningPoints.length

                        ? reasoningPoints.map(point =>
                            `<li>
                                ${escapeHTML(
                                    String(point)
                                )}
                            </li>`
                        ).join("")

                        : "<li>—</li>"
                }

            </ul>

            <h4>
                Evidence Summary
            </h4>

            ${renderEvidenceSummary(
                evidenceSummary
            )}

            <h4>
                Evidence Sources
            </h4>

            <ul>

                ${
                    evidence.length

                        ? evidence.map(item => {

                            if (
                                typeof item === "string"
                            ) {

                                return `
                                    <li>
                                        ${escapeHTML(item)}
                                    </li>
                                `;
                            }

                            const agent =
                                item.agent || "Agent";

                            const status =
                                item.data_status ||
                                "UNAVAILABLE";

                            const source =
                                Array.isArray(item.source)
                                    ? item.source.join(
                                        " + "
                                    )
                                    : (
                                        item.source ||
                                        "Source unavailable"
                                    );

                            return `
                                <li>

                                    <strong>
                                        ${escapeHTML(agent)}
                                    </strong>

                                    —
                                    ${escapeHTML(status)}

                                    —
                                    ${escapeHTML(source)}

                                </li>
                            `;

                        }).join("")

                        : "<li>—</li>"
                }

            </ul>

            <h4>
                Final Assessment
            </h4>

            <p>
                ${escapeHTML(
                    data.final_assessment ||
                    "No final assessment available."
                )}
            </p>

            <small>

                ${escapeHTML(
                    data.source_note ||
                    "ORCA reasoning is based on connected data sources."
                )}

            </small>

        `;
    }

    async function loadReasoning() {

        try {

            setStatus(
                "Loading ORCA reasoning from backend..."
            );

            const region =
                getSelectedRegion();

            const result =
                await getReasoningData(
                    region,
                    "What is the overall marine condition?"
                );

            if (!result) {

                throw new Error(
                    "Empty reasoning response."
                );

            }

            renderReasoning(result);

            setStatus(
                "✅ ORCA reasoning loaded successfully.",
                true
            );

            console.log(
                "ORCA Live Reasoning:",
                result
            );

        }
        catch (error) {

            console.error(
                "ORCA Reasoning Error:",
                error
            );

            setStatus(
                "❌ Unable to load ORCA reasoning from backend.",
                false
            );
        }
    }

    window.loadORCAReasoning =
        loadReasoning;

    const reasoningNav =
        document.querySelector(
            '[data-page="reasoning"]'
        );

    if (reasoningNav) {

        reasoningNav.addEventListener(
            "click",
            () => {

                setTimeout(
                    loadReasoning,
                    100
                );

            }
        );

    }

    console.log(
        "ORCA AI Reasoning connected successfully."
    );

});
```
