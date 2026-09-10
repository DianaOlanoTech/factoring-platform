"""
Tests for the domain models.

This module verifies that the core domain models can be created correctly
and that their business invariants reject invalid values.
"""

from datetime import date

import pytest

from app.domain.models import (
    DecisionStatus,
    FactoringApplication,
    FactoringDecision,
    RiskResult,
    RiskStatus,
)


def test_factoring_application_can_be_created():
    application = FactoringApplication(
        application_id="FAC-1001",
        customer_id="CUS-101",
        invoice_amount_cents=125000,
        requested_advance_cents=90000,
        due_date=date(2026, 10, 15),
    )

    assert application.application_id == "FAC-1001"
    assert application.customer_id == "CUS-101"


def test_invoice_amount_must_be_greater_than_zero():
    with pytest.raises(ValueError):
        FactoringApplication(
            application_id="FAC-1001",
            customer_id="CUS-101",
            invoice_amount_cents=0,
            requested_advance_cents=90000,
            due_date=date(2026, 10, 15),
        )


def test_requested_advance_must_be_greater_than_zero():
    with pytest.raises(ValueError):
        FactoringApplication(
            application_id="FAC-1001",
            customer_id="CUS-101",
            invoice_amount_cents=125000,
            requested_advance_cents=0,
            due_date=date(2026, 10, 15),
        )


def test_risk_result_accepts_valid_advance_percent():
    risk = RiskResult(
        status=RiskStatus.APPROVED,
        max_advance_percent=80,
        provider_reference="RISK-9001",
    )

    assert risk.status == RiskStatus.APPROVED
    assert risk.max_advance_percent == 80


@pytest.mark.parametrize("percentage", [-1, 0, 101])
def test_risk_result_rejects_invalid_advance_percent(percentage):
    with pytest.raises(ValueError):
        RiskResult(
            status=RiskStatus.APPROVED,
            max_advance_percent=percentage,
            provider_reference="RISK-9001",
        )


def test_risk_result_can_have_no_advance_percent():
    risk = RiskResult(
        status=RiskStatus.REVIEW,
        max_advance_percent=None,
        provider_reference="RISK-9002",
    )

    assert risk.max_advance_percent is None


def test_factoring_decision_can_be_created():
    decision = FactoringDecision(
        application_id="FAC-1001",
        decision=DecisionStatus.ELIGIBLE,
        requested_advance_cents=90000,
        available_advance_cents=100000,
        provider_reference="RISK-9001",
    )

    assert decision.decision == DecisionStatus.ELIGIBLE
    assert decision.available_advance_cents == 100000