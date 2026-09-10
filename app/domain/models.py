"""
Domain models for the factoring decision service.

This module contains the business concepts used by the application core.
These models are intentionally independent of FastAPI, HTTP clients,
databases, and external provider-specific representations.
"""

from dataclasses import dataclass
from datetime import date
from enum import Enum


class RiskStatus(Enum):
    """Normalized risk statuses returned by a risk provider."""

    APPROVED = "approved"
    REVIEW = "review"
    DECLINED = "declined"


class DecisionStatus(Enum):
    """Final factoring decisions produced by the application."""

    ELIGIBLE = "eligible"
    NEEDS_REVIEW = "needs_review"
    REJECTED = "rejected"
    INTEGRATION_ERROR = "integration_error"


@dataclass
class FactoringApplication:
    """
    Represents a factoring application submitted for evaluation.

    This is a domain model, so it contains business-level data rather
    than HTTP request-specific or provider-specific fields.

    Attributes:
        application_id: Unique identifier of the factoring application.
        customer_id: Identifier of the customer requesting factoring.
        invoice_amount_cents: Invoice amount expressed in cents.
        requested_advance_cents: Advance amount requested by the customer,
            expressed in cents.
        due_date: Due date of the invoice.
    """

    application_id: str
    customer_id: str
    invoice_amount_cents: int
    requested_advance_cents: int
    due_date: date

    def __post_init__(self):
        """Validate the basic invariants of a factoring application."""
        if self.invoice_amount_cents <= 0:
            raise ValueError(
                "Invoice amount cents must be greater than 0"
            )

        if self.requested_advance_cents <= 0:
            raise ValueError(
                "Requested advance cents must be greater than 0"
            )


@dataclass
class RiskResult:
    """
    Represents the normalized result returned by a risk provider.

    Provider-specific response fields and representations should be
    translated into this model by the corresponding provider adapter.

    Attributes:
        status: Normalized risk status.
        max_advance_percent: Maximum advance percentage allowed by the
            provider. This may be None when the risk status is REVIEW.
        provider_reference: Opaque reference assigned by the external
            risk provider.
    """

    status: RiskStatus
    max_advance_percent: int | None
    provider_reference: str

    def __post_init__(self):
        """Validate the maximum advance percentage when provided."""
        if (
            self.max_advance_percent is not None
            and not 0 < self.max_advance_percent <= 100
        ):
            raise ValueError(
                "Max advance percent must be between 1 and 100"
            )


@dataclass
class FactoringDecision:
    """
    Represents the final normalized decision for a factoring application.

    This model is produced by the application service after applying
    the business rules to the normalized risk result.

    Attributes:
        application_id: Identifier of the evaluated application.
        decision: Final business decision.
        requested_advance_cents: Advance amount originally requested.
        available_advance_cents: Maximum advance available according to
            the risk provider. None when no advance can be calculated.
        provider_reference: External provider reference, when available.
    """

    application_id: str
    decision: DecisionStatus
    requested_advance_cents: int
    available_advance_cents: int | None
    provider_reference: str | None