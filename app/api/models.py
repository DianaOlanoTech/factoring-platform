"""
Pydantic models used by the HTTP API.

These models represent the external HTTP contract of the application.
They are intentionally separate from domain models so changes to the
API representation do not require changes to the business domain.
"""

from datetime import date

from pydantic import BaseModel


class FactoringApplicationRequest(BaseModel):
    """
    HTTP request body for creating a factoring application.

    This model handles structural validation of incoming API data before
    the request is converted into the domain FactoringApplication model.
    """

    application_id: str
    customer_id: str
    invoice_amount_cents: int
    requested_advance_cents: int
    due_date: date


class FactoringDecisionResponse(BaseModel):
    """
    HTTP response containing the normalized factoring decision.

    This model defines the public API representation returned to clients.
    """

    application_id: str
    decision: str
    requested_advance_cents: int
    available_advance_cents: int | None
    provider_reference: str | None