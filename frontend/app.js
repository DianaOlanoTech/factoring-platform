"use strict";
const form = document.getElementById("application-form");
const result = document.getElementById("result");
const error = document.getElementById("error");
form.addEventListener("submit", async (event) => {
    event.preventDefault();
    result.hidden = true;
    error.hidden = true;
    const application = {
        application_id: document.getElementById("application-id").value,
        customer_id: document.getElementById("customer-id").value,
        invoice_amount_cents: Number(document.getElementById("invoice-amount").value),
        requested_advance_cents: Number(document.getElementById("requested-advance").value),
        due_date: document.getElementById("due-date").value,
    };
    try {
        const response = await fetch("/api/factoring/applications", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(application),
        });
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.decision || "Failed to create application");
        }
        document.getElementById("result-application-id").textContent = data.application_id;
        document.getElementById("result-decision").textContent = data.decision;
        document.getElementById("result-requested").textContent =
            String(data.requested_advance_cents);
        document.getElementById("result-available").textContent =
            data.available_advance_cents !== null
                ? String(data.available_advance_cents)
                : "N/A";
        document.getElementById("result-provider-reference").textContent =
            data.provider_reference ?? "N/A";
        result.hidden = false;
    }
    catch (err) {
        error.textContent =
            err instanceof Error
                ? err.message
                : "An unexpected error occurred";
        error.hidden = false;
    }
});
