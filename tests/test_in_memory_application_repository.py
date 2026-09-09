from datetime import date

from app.adapters.repositories.in_memory_application_repository import (
    InMemoryApplicationRepository,
)
from app.domain.models import (
    DecisionStatus,
    FactoringApplication,
    FactoringDecision,
)


def test_save_and_get_by_application_id():
    application = FactoringApplication(
        application_id="FAC-1001",
        customer_id="CUS-101",
        invoice_amount_cents=125000,
        requested_advance_cents=90000,
        due_date=date(2026, 10, 15),
    )

    decision = FactoringDecision(
        application_id="FAC-1001",
        decision=DecisionStatus.ELIGIBLE,
        requested_advance_cents=90000,
        available_advance_cents=100000,
        provider_reference="RISK-9001",
    )

    repository = InMemoryApplicationRepository()

    repository.save(application, decision)

    result = repository.get_by_application_id("FAC-1001")

    assert result == decision


def test_get_by_application_id_returns_none_when_application_does_not_exist():
    repository = InMemoryApplicationRepository()

    result = repository.get_by_application_id("FAC-9999")

    assert result is None


def test_save_replaces_existing_decision_for_same_application_id():
    application = FactoringApplication(
        application_id="FAC-1001",
        customer_id="CUS-101",
        invoice_amount_cents=125000,
        requested_advance_cents=90000,
        due_date=date(2026, 10, 15),
    )

    first_decision = FactoringDecision(
        application_id="FAC-1001",
        decision=DecisionStatus.NEEDS_REVIEW,
        requested_advance_cents=90000,
        available_advance_cents=80000,
        provider_reference="RISK-9001",
    )

    second_decision = FactoringDecision(
        application_id="FAC-1001",
        decision=DecisionStatus.ELIGIBLE,
        requested_advance_cents=90000,
        available_advance_cents=100000,
        provider_reference="RISK-9002",
    )

    repository = InMemoryApplicationRepository()

    repository.save(application, first_decision)
    repository.save(application, second_decision)

    result = repository.get_by_application_id("FAC-1001")

    assert result == second_decision