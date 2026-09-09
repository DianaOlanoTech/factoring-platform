from datetime import date

import pytest

from app.adapters.risk.exceptions import RiskProviderError
from app.application.factoring_application_service import (
    FactoringApplicationService,
)
from app.domain.models import (
    DecisionStatus,
    FactoringApplication,
    RiskResult,
    RiskStatus,
)


class FakeRiskProvider:
    def __init__(self, result=None, error=None):
        self.result = result
        self.error = error

    def evaluate(self, application):
        if self.error:
            raise self.error

        return self.result


class FakeApplicationRepository:
    def __init__(self):
        self.saved_records = []

    def save(self, application, decision):
        self.saved_records.append((application, decision))

    def get_by_application_id(self, application_id):
        for application, decision in self.saved_records:
            if application.application_id == application_id:
                return decision

        return None


@pytest.fixture
def application():
    return FactoringApplication(
        application_id="FAC-1001",
        customer_id="CUS-101",
        invoice_amount_cents=125000,
        requested_advance_cents=90000,
        due_date=date(2026, 10, 15),
    )


def test_create_application_returns_eligible_when_requested_is_within_limit(
    application,
):
    risk_result = RiskResult(
        status=RiskStatus.APPROVED,
        max_advance_percent=80,
        provider_reference="RISK-9001",
    )

    risk_provider = FakeRiskProvider(result=risk_result)
    repository = FakeApplicationRepository()

    service = FactoringApplicationService(
        risk_provider=risk_provider,
        repository=repository,
    )

    decision = service.create_application(application)

    assert decision.decision == DecisionStatus.ELIGIBLE
    assert decision.available_advance_cents == 100000
    assert decision.requested_advance_cents == 90000
    assert decision.provider_reference == "RISK-9001"
    assert decision.application_id == "FAC-1001"

    assert len(repository.saved_records) == 1

    saved_application, saved_decision = repository.saved_records[0]

    assert saved_application == application
    assert saved_decision == decision


def test_create_application_returns_needs_review_when_requested_exceeds_limit(
    application,
):
    application.requested_advance_cents = 110000

    risk_result = RiskResult(
        status=RiskStatus.APPROVED,
        max_advance_percent=80,
        provider_reference="RISK-9001",
    )

    risk_provider = FakeRiskProvider(result=risk_result)
    repository = FakeApplicationRepository()

    service = FactoringApplicationService(
        risk_provider=risk_provider,
        repository=repository,
    )

    decision = service.create_application(application)

    assert decision.decision == DecisionStatus.NEEDS_REVIEW
    assert decision.available_advance_cents == 100000
    assert decision.requested_advance_cents == 110000
    assert decision.provider_reference == "RISK-9001"


def test_create_application_returns_needs_review_when_risk_requires_review(
    application,
):
    risk_result = RiskResult(
        status=RiskStatus.REVIEW,
        max_advance_percent=None,
        provider_reference="RISK-9002",
    )

    risk_provider = FakeRiskProvider(result=risk_result)
    repository = FakeApplicationRepository()

    service = FactoringApplicationService(
        risk_provider=risk_provider,
        repository=repository,
    )

    decision = service.create_application(application)

    assert decision.decision == DecisionStatus.NEEDS_REVIEW
    assert decision.available_advance_cents is None
    assert decision.provider_reference == "RISK-9002"


def test_create_application_returns_rejected_when_risk_is_declined(
    application,
):
    risk_result = RiskResult(
        status=RiskStatus.DECLINED,
        max_advance_percent=None,
        provider_reference="RISK-9003",
    )

    risk_provider = FakeRiskProvider(result=risk_result)
    repository = FakeApplicationRepository()

    service = FactoringApplicationService(
        risk_provider=risk_provider,
        repository=repository,
    )

    decision = service.create_application(application)

    assert decision.decision == DecisionStatus.REJECTED
    assert decision.available_advance_cents is None
    assert decision.provider_reference == "RISK-9003"


def test_create_application_returns_integration_error_when_risk_provider_fails(
    application,
):
    risk_provider = FakeRiskProvider(
        error=RiskProviderError("Risk provider unavailable")
    )
    repository = FakeApplicationRepository()

    service = FactoringApplicationService(
        risk_provider=risk_provider,
        repository=repository,
    )

    decision = service.create_application(application)

    assert decision.decision == DecisionStatus.INTEGRATION_ERROR
    assert decision.available_advance_cents is None
    assert decision.provider_reference is None
    assert decision.application_id == "FAC-1001"

    assert len(repository.saved_records) == 1

    saved_application, saved_decision = repository.saved_records[0]

    assert saved_application == application
    assert saved_decision == decision


def test_create_application_floors_available_advance(
    application,
):
    application.invoice_amount_cents = 100001
    application.requested_advance_cents = 75000

    risk_result = RiskResult(
        status=RiskStatus.APPROVED,
        max_advance_percent=75,
        provider_reference="RISK-9004",
    )

    risk_provider = FakeRiskProvider(result=risk_result)
    repository = FakeApplicationRepository()

    service = FactoringApplicationService(
        risk_provider=risk_provider,
        repository=repository,
    )

    decision = service.create_application(application)

    assert decision.decision == DecisionStatus.ELIGIBLE
    assert decision.available_advance_cents == 75000