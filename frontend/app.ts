interface FactoringApplicationRequest {
    application_id: string;
    customer_id: string;
    invoice_amount_cents: number;
    requested_advance_cents: number;
    due_date: string;
}

interface FactoringDecisionResponse {
    application_id: string;
    decision: string;
    requested_advance_cents: number;
    available_advance_cents: number | null;
    provider_reference: string | null;
}

interface ApiErrorResponse {
    detail?: string;
}

const form = document.getElementById(
    "application-form"
) as HTMLFormElement;

const result = document.getElementById(
    "result"
) as HTMLElement;

const error = document.getElementById(
    "error"
) as HTMLElement;

form.addEventListener("submit", async (event) => {
    event.preventDefault();

    result.hidden = true;
    error.hidden = true;

    const application: FactoringApplicationRequest = {
        application_id: (
            document.getElementById(
                "application-id"
            ) as HTMLInputElement
        ).value,

        customer_id: (
            document.getElementById(
                "customer-id"
            ) as HTMLInputElement
        ).value,

        invoice_amount_cents: Number(
            (
                document.getElementById(
                    "invoice-amount"
                ) as HTMLInputElement
            ).value
        ),

        requested_advance_cents: Number(
            (
                document.getElementById(
                    "requested-advance"
                ) as HTMLInputElement
            ).value
        ),

        due_date: (
            document.getElementById(
                "due-date"
            ) as HTMLInputElement
        ).value,
    };

    try {
        const response = await fetch(
            "/api/factoring/applications",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(application),
            }
        );

        const data: unknown = await response.json();

        if (!response.ok) {
            const errorData = data as ApiErrorResponse;

            throw new Error(
                errorData.detail ||
                "Failed to create application"
            );
        }

        const decision = data as FactoringDecisionResponse;

        document.getElementById(
            "result-application-id"
        )!.textContent = decision.application_id;

        document.getElementById(
            "result-decision"
        )!.textContent = decision.decision;

        document.getElementById(
            "result-requested"
        )!.textContent =
            String(decision.requested_advance_cents);

        document.getElementById(
            "result-available"
        )!.textContent =
            decision.available_advance_cents !== null
                ? String(decision.available_advance_cents)
                : "N/A";

        document.getElementById(
            "result-provider-reference"
        )!.textContent =
            decision.provider_reference ?? "N/A";

        result.hidden = false;
    } catch (err) {
        error.textContent =
            err instanceof Error
                ? err.message
                : "An unexpected error occurred";

        error.hidden = false;
    }
});