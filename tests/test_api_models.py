"""
Tests for the API models.

This module verifies that the Pydantic request and response models
accept valid data and reject invalid input according to the API contract.
"""

from datetime import date

import pytest
from pydantic import ValidationError

from app.api.models import (
    FactoringApplicationRequest,
    FactoringDecisionResponse,
)


def test_factoring_application_request_accepts_valid_data():
    request = FactoringApplicationRequest(
        application_id="FAC-1001",
        customer_id="CUS-101",
        invoice_amount_cents=125000,
        requested_advance_cents=90000,
        due_date="2026-10-15",
    )

    assert request.application_id == "FAC-1001"
    assert request.customer_id == "CUS-101"
    assert request.invoice_amount_cents == 125000
    assert request.requested_advance_cents == 90000
    assert request.due_date == date(2026, 10, 15)


def test_factoring_application_request_rejects_invalid_date():
    with pytest.raises(ValidationError):
        FactoringApplicationRequest(
            application_id="FAC-1001",
            customer_id="CUS-101",
            invoice_amount_cents=125000,
            requested_advance_cents=90000,
            due_date="not-a-date",
        )


def test_factoring_decision_response_accepts_optional_fields():
    response = FactoringDecisionResponse(
        application_id="FAC-1001",
        decision="rejected",
        requested_advance_cents=90000,
        available_advance_cents=None,
        provider_reference=None,
    )

    assert response.decision == "rejected"
    assert response.available_advance_cents is None
    assert response.provider_reference is None