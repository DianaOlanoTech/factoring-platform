from dataclasses import dataclass
from datetime import date
from enum import Enum


class RiskStatus(Enum):
    APPROVED = "approved"
    REVIEW = "review"
    DECLINED = "declined"


class DecisionStatus(Enum):
    ELIGIBLE = "eligible"
    NEEDS_REVIEW = "needs_review"
    REJECTED = "rejected"
    INTEGRATION_ERROR = "integration_error"


@dataclass
class FactoringApplication:
    application_id: str
    customer_id: str
    invoice_amount_cents: int
    requested_advance_cents: int
    due_date: date

    def __post_init__(self):
        if self.invoice_amount_cents <= 0:
            raise ValueError("Invoice amount cents must be greater than 0")

        if self.requested_advance_cents <= 0:
            raise ValueError("Requested advance cents must be greater than 0")


@dataclass
class RiskResult:
    status: RiskStatus
    max_advance_percent: int | None
    provider_reference: str

    def __post_init__(self):
        if self.max_advance_percent is not None and not 0 < self.max_advance_percent <= 100:
            raise ValueError("Max advance percent must be between 0 and 100")


@dataclass
class FactoringDecision:
    application_id: str
    decision: DecisionStatus
    requested_advance_cents: int
    available_advance_cents: int | None
    provider_reference: str | None