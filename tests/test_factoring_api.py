"""
Tests for the factoring HTTP API.

This module verifies request validation, domain validation, normalized
API responses, application retrieval, not-found handling, and the
representation of risk provider integration errors.

The API tests use test doubles where appropriate to keep the HTTP layer
isolated from the application business logic.
"""

from datetime import date

import pytest
from fastapi.testclient import TestClient

from app.adapters.repositories.in_memory_application_repository import (
    InMemoryApplicationRepository,
)
from app.api.dependencies import (
    get_application_repository,
    get_factoring_service,
)
from app.domain.models import (
    DecisionStatus,
    FactoringApplication,
    FactoringDecision,
)
from app.main import app


@pytest.fixture
def client():
    client = TestClient(app)

    yield client

    app.dependency_overrides.clear()


class FakeFactoringApplicationService:
    """
    Test double for the factoring application service.

    Used to isolate the API layer from the application business logic
    when testing HTTP request and response handling.
    """
    def create_application(self, application):
        return FactoringDecision(
            application_id=application.application_id,
            decision=DecisionStatus.ELIGIBLE,
            requested_advance_cents=application.requested_advance_cents,
            available_advance_cents=100000,
            provider_reference="RISK-9001",
        )


class FakeIntegrationErrorFactoringApplicationService:
    """
    Test double for the factoring application service that returns
    an integration error decision.

    Used to verify how the API represents provider integration failures.
    """
    def create_application(self, application):
        return FactoringDecision(
            application_id=application.application_id,
            decision=DecisionStatus.INTEGRATION_ERROR,
            requested_advance_cents=application.requested_advance_cents,
            available_advance_cents=None,
            provider_reference=None,
        )


def test_create_application_endpoint_returns_normalized_decision(
    client,
):
    fake_service = FakeFactoringApplicationService()

    app.dependency_overrides[get_factoring_service] = (
        lambda: fake_service
    )

    response = client.post(
        "/api/factoring/applications",
        json={
            "application_id": "FAC-1001",
            "customer_id": "CUS-101",
            "invoice_amount_cents": 125000,
            "requested_advance_cents": 90000,
            "due_date": "2026-10-15",
        },
    )

    assert response.status_code == 200

    assert response.json() == {
        "application_id": "FAC-1001",
        "decision": "eligible",
        "requested_advance_cents": 90000,
        "available_advance_cents": 100000,
        "provider_reference": "RISK-9001",
    }


def test_create_application_endpoint_rejects_invalid_request(
    client,
):
    fake_service = FakeFactoringApplicationService()

    app.dependency_overrides[get_factoring_service] = (
        lambda: fake_service
    )

    response = client.post(
        "/api/factoring/applications",
        json={
            "application_id": "FAC-1001",
            "customer_id": "CUS-101",
            "invoice_amount_cents": "invalid",
            "requested_advance_cents": 90000,
            "due_date": "2026-10-15",
        },
    )

    assert response.status_code == 422


def test_create_application_endpoint_rejects_invalid_domain_data(
    client,
):
    fake_service = FakeFactoringApplicationService()

    app.dependency_overrides[get_factoring_service] = (
        lambda: fake_service
    )

    response = client.post(
        "/api/factoring/applications",
        json={
            "application_id": "FAC-1001",
            "customer_id": "CUS-101",
            "invoice_amount_cents": 0,
            "requested_advance_cents": 90000,
            "due_date": "2026-10-15",
        },
    )

    assert response.status_code == 422


def test_get_application_endpoint_returns_saved_decision(
    client,
):
    repository = InMemoryApplicationRepository()

    decision = FactoringDecision(
        application_id="FAC-1001",
        decision=DecisionStatus.ELIGIBLE,
        requested_advance_cents=90000,
        available_advance_cents=100000,
        provider_reference="RISK-9001",
    )

    application = FactoringApplication(
        application_id="FAC-1001",
        customer_id="CUS-101",
        invoice_amount_cents=125000,
        requested_advance_cents=90000,
        due_date=date(2026, 10, 15),
    )

    repository.save(application, decision)

    app.dependency_overrides[get_application_repository] = (
        lambda: repository
    )

    response = client.get(
        "/api/factoring/applications/FAC-1001"
    )

    assert response.status_code == 200

    assert response.json() == {
        "application_id": "FAC-1001",
        "decision": "eligible",
        "requested_advance_cents": 90000,
        "available_advance_cents": 100000,
        "provider_reference": "RISK-9001",
    }


def test_get_application_endpoint_returns_404_when_application_does_not_exist(
    client,
):
    repository = InMemoryApplicationRepository()

    app.dependency_overrides[get_application_repository] = (
        lambda: repository
    )

    response = client.get(
        "/api/factoring/applications/FAC-9999"
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": "Application not found"
    }


def test_create_application_endpoint_returns_integration_error(
    client,
):
    fake_service = FakeIntegrationErrorFactoringApplicationService()

    app.dependency_overrides[get_factoring_service] = (
        lambda: fake_service
    )

    response = client.post(
        "/api/factoring/applications",
        json={
            "application_id": "FAC-1005",
            "customer_id": "CUS-101",
            "invoice_amount_cents": 125000,
            "requested_advance_cents": 90000,
            "due_date": "2026-10-15",
        },
    )

    assert response.status_code == 200

    assert response.json() == {
        "application_id": "FAC-1005",
        "decision": "integration_error",
        "requested_advance_cents": 90000,
        "available_advance_cents": None,
        "provider_reference": None,
    }