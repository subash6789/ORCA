/* =========================================================
   ORCA AI ASSISTANT
   Phase 7 - Detailed Reasoning Response
========================================================= */

document.addEventListener("DOMContentLoaded", () => {

    const chatForm = document.getElementById("chatForm");
    const chatInput = document.getElementById("chatInput");
    const chatMessages = document.getElementById("chatMessages");
    const suggestions = document.querySelectorAll(".suggestion");

    if (!chatForm || !chatInput || !chatMessages) {
        console.warn("ORCA Assistant elements not found.");
        return;
    }


    /* =====================================================
       GET SELECTED REGION
    ===================================================== */

    function getSelectedRegion() {

        const regionSelect =
            document.getElementById("regionSelect");

        if (regionSelect && regionSelect.value) {
            return regionSelect.value;
        }

        return "Tamil Nadu";
    }


    /* =====================================================
       ADD USER MESSAGE
    ===================================================== */

    function addUserMessage(message) {

        const messageDiv =
            document.createElement("div");

        messageDiv.className = "user-message";

        messageDiv.innerHTML = `
            <div class="message-content">
                <strong>You</strong>
                <p>${escapeHTML(message)}</p>
            </div>
        `;

        chatMessages.appendChild(messageDiv);

        scrollToBottom();
    }


    /* =====================================================
       ADD ASSISTANT MESSAGE
    ===================================================== */

    function addAssistantMessage(
        message,
        status = "Backend connected"
    ) {

        const messageDiv =
            document.createElement("div");

        messageDiv.className = "assistant-message";

        messageDiv.innerHTML = `
            <div class="message-avatar">O</div>

            <div class="message-content">
                <strong>ORCA Assistant</strong>
                <p>${escapeHTML(message)}</p>
                <small>${escapeHTML(status)}</small>
            </div>
        `;

        chatMessages.appendChild(messageDiv);

        scrollToBottom();
    }


    /* =====================================================
       LOADING MESSAGE
    ===================================================== */

    function addLoadingMessage() {

        const messageDiv =
            document.createElement("div");

        messageDiv.className = "assistant-message";
        messageDiv.id = "orcaLoadingMessage";

        messageDiv.innerHTML = `
            <div class="message-avatar">O</div>

            <div class="message-content">
                <strong>ORCA Assistant</strong>
                <p>Analyzing marine information...</p>
                <small>Connecting to ORCA reasoning backend</small>
            </div>
        `;

        chatMessages.appendChild(messageDiv);

        scrollToBottom();
    }


    /* =====================================================
       REMOVE LOADING MESSAGE
    ===================================================== */

    function removeLoadingMessage() {

        const loadingMessage =
            document.getElementById("orcaLoadingMessage");

        if (loadingMessage) {
            loadingMessage.remove();
        }
    }


    /* =====================================================
       SCROLL
    ===================================================== */

    function scrollToBottom() {

        chatMessages.scrollTop =
            chatMessages.scrollHeight;
    }


    /* =====================================================
       HTML ESCAPE
    ===================================================== */

    function escapeHTML(text) {

        const div =
            document.createElement("div");

        div.textContent =
            String(text ?? "");

        return div.innerHTML;
    }


    /* =====================================================
       FIND RELEVANT REASONING POINT
    ===================================================== */

    function findRelevantReasoning(
        reasoningPoints,
        question
    ) {

        if (
            !Array.isArray(reasoningPoints) ||
            reasoningPoints.length === 0
        ) {
            return null;
        }

        const q =
            question.toLowerCase();


        /* Ocean temperature */

        if (
            q.includes("temperature") ||
            q.includes("sst")
        ) {

            const point =
                reasoningPoints.find(
                    item =>
                        item.toLowerCase().includes(
                            "ocean temperature"
                        )
                );

            if (point) {
                return point;
            }
        }


        /* Salinity */

        if (q.includes("salinity")) {

            const point =
                reasoningPoints.find(
                    item =>
                        item.toLowerCase().includes(
                            "salinity"
                        )
                );

            if (point) {
                return point;
            }
        }


        /* Current */

        if (q.includes("current")) {

            const point =
                reasoningPoints.find(
                    item =>
                        item.toLowerCase().includes(
                            "ocean current"
                        )
                );

            if (point) {
                return point;
            }
        }


        /* Mixed layer depth */

        if (
            q.includes("mixed layer") ||
            q.includes("mld")
        ) {

            const point =
                reasoningPoints.find(
                    item =>
                        item.toLowerCase().includes(
                            "mixed layer depth"
                        )
                );

            if (point) {
                return point;
            }
        }


        /* Wind */

        if (q.includes("wind")) {

            const point =
                reasoningPoints.find(
                    item =>
                        item.toLowerCase().includes(
                            "wind speed"
                        )
                );

            if (point) {
                return point;
            }
        }


        /* Rain / precipitation */

        if (
            q.includes("rain") ||
            q.includes("precipitation")
        ) {

            const point =
                reasoningPoints.find(
                    item =>
                        item.toLowerCase().includes(
                            "precipitation"
                        )
                );

            if (point) {
                return point;
            }
        }


        return null;
    }


    /* =====================================================
       BUILD ASSISTANT ANSWER
    ===================================================== */

    function buildAssistantAnswer(
        result,
        question,
        region
    ) {

        if (
            result &&
            Array.isArray(result.reasoning_points)
        ) {

            const relevantPoint =
                findRelevantReasoning(
                    result.reasoning_points,
                    question
                );

            if (relevantPoint) {
                return relevantPoint;
            }
        }


        /* Fallback */

        if (result.final_assessment) {
            return result.final_assessment;
        }

        if (result.answer) {
            return result.answer;
        }

        if (result.message) {
            return result.message;
        }

        return `ORCA completed the analysis for ${region}.`;
    }


    /* =====================================================
       ASK ORCA BACKEND
    ===================================================== */

    async function askORCABackend(question) {

        const region =
            getSelectedRegion();

        try {

            const result =
                await askORCA(
                    question,
                    region
                );

            if (!result) {

                throw new Error(
                    "Empty response from ORCA backend."
                );
            }


            console.log(
                "ORCA Assistant Backend Response:",
                result
            );


            const answer =
                buildAssistantAnswer(
                    result,
                    question,
                    region
                );


            let status =
                "AI reasoning completed successfully.";

            if (result.status) {

                status =
                    `Backend status: ${result.status}`;
            }


            addAssistantMessage(
                answer,
                status
            );

        }

        catch (error) {

            console.error(
                "ORCA Assistant Error:",
                error
            );

            addAssistantMessage(
                "I could not connect to the ORCA reasoning backend. Please make sure the ORCA backend is running.",
                "Backend connection error"
            );
        }
    }


    /* =====================================================
       HANDLE QUESTION
    ===================================================== */

    async function handleQuestion(question) {

        question =
            question.trim();

        if (!question) {
            return;
        }

        addUserMessage(question);

        chatInput.value = "";

        addLoadingMessage();

        try {

            await askORCABackend(
                question
            );

        }

        finally {

            removeLoadingMessage();
        }
    }


    /* =====================================================
       FORM SUBMIT
    ===================================================== */

    chatForm.addEventListener(
        "submit",
        async (event) => {

            event.preventDefault();

            const question =
                chatInput.value.trim();

            await handleQuestion(
                question
            );
        }
    );


    /* =====================================================
       SUGGESTIONS
    ===================================================== */

    suggestions.forEach(
        (button) => {

            button.addEventListener(
                "click",
                async () => {

                    const question =
                        button.textContent.trim();

                    await handleQuestion(
                        question
                    );
                }
            );
        }
    );


    console.log(
        "ORCA AI Assistant connected successfully."
    );

});