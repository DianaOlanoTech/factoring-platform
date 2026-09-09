from datetime import date

from pydantic import BaseModel


class FactoringApplicationRequest(BaseModel):
    application_id: str
    customer_id: str
    invoice_amount_cents: int
    requested_advance_cents: int
    due_date: date

class FactoringDecisionResponse(BaseModel):
    application_id: str
    decision: str
    requested_advance_cents: int
    available_advance_cents: int | None
    provider_reference: str | None