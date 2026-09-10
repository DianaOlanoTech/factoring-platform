"use strict";
/**
 * Frontend client for the factoring application API.
 *
 * This module handles form submission, communicates with the backend API,
 * and displays normalized factoring decisions or API errors.
 *
 * Business rules are intentionally kept in the backend. The frontend only
 * collects user input, sends the API request, and renders the response.
 */
/*
 * Retrieve the main elements from the HTML document.
 *
 * Type assertions tell TypeScript the specific DOM element types we expect.
 * These elements are defined in frontend/index.html.
 */
const form = document.getElementById("application-form");
const result = document.getElementById("result");
const error = document.getElementById("error");
/*
 * Handle form submission asynchronously because the application
 * communicates with the backend through an HTTP request.
 */
form.addEventListener("submit", async (event) => {
    event.preventDefault();
    /*
     * Hide previous results or errors before processing a new submission.
     * This prevents an old result from remaining visible while a new
     * request is being processed.
     */
    result.hidden = true;
    error.hidden = true;
    /*
     * Build the API request from the values entered in the form.
     *
     * Values obtained from HTML inputs are strings, so numeric fields
     * are explicitly converted to numbers before creating the payload.
     */
    const application = {
        application_id: document.getElementById("application-id").value,
        customer_id: document.getElementById("customer-id").value,
        invoice_amount_cents: Number(document.getElementById("invoice-amount").value),
        requested_advance_cents: Number(document.getElementById("requested-advance").value),
        due_date: document.getElementById("due-date").value,
    };
    try {
        /*
         * Send the application to the backend API.
         *
         * The frontend does not communicate directly with the risk provider.
         * The backend owns the factoring workflow and the external
         * risk-provider integration.
         */
        const response = await fetch("/api/factoring/applications", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(application),
        });
        /*
         * Treat the response body as unknown until we determine whether
         * the request succeeded or failed.
         *
         * Data received from an HTTP response should not automatically
         * be assumed to have a specific TypeScript type.
         */
        const data = await response.json();
        /*
         * response.ok is true for successful HTTP status codes
         * in the 200-299 range.
         *
         * For expected API errors, FastAPI returns a JSON object
         * containing a detail message.
         */
        if (!response.ok) {
            const errorData = data;
            throw new Error(errorData.detail ||
                "Failed to create application");
        }
        /*
         * The successful response follows the normalized API contract.
         *
         * The frontend does not need to know which risk provider was used
         * or how the business decision was calculated. It only renders
         * the normalized result returned by the backend.
         */
        const decision = data;
        document.getElementById("result-application-id").textContent = decision.application_id;
        document.getElementById("result-decision").textContent = decision.decision;
        document.getElementById("result-requested").textContent =
            String(decision.requested_advance_cents);
        /*
         * Some decisions do not have an available advance.
         *
         * For example, review, rejected, and integration_error responses
         * can contain null for available_advance_cents.
         */
        document.getElementById("result-available").textContent =
            decision.available_advance_cents !== null
                ? String(decision.available_advance_cents)
                : "N/A";
        /*
         * The provider reference is also nullable because an integration
         * failure may occur before the provider returns a reference.
         */
        document.getElementById("result-provider-reference").textContent =
            decision.provider_reference ?? "N/A";
        /*
         * Show the normalized decision after all response fields
         * have been rendered.
         */
        result.hidden = false;
    }
    catch (err) {
        /*
         * Handle both API errors converted above and unexpected
         * client-side errors.
         *
         * instanceof Error ensures that we only access the message
         * property when the caught value is actually an Error object.
         */
        error.textContent =
            err instanceof Error
                ? err.message
                : "An unexpected error occurred";
        error.hidden = false;
    }
});
