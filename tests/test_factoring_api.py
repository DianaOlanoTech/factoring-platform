from datetime import date

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
    FactoringDecision,
    FactoringApplication,
)
from app.main import app


class FakeFactoringApplicationService:
    def create_application(self, application):
        return FactoringDecision(
            application_id=application.application_id,
            decision=DecisionStatus.ELIGIBLE,
            requested_advance_cents=application.requested_advance_cents,
            available_advance_cents=100000,
            provider_reference="RISK-9001",
        )

class FakeIntegrationErrorFactoringApplicationService:

    def create_application(self, application):

        return FactoringDecision(
            application_id=application.application_id,
            decision=DecisionStatus.INTEGRATION_ERROR,
            requested_advance_cents=application.requested_advance_cents,
            available_advance_cents=None,
            provider_reference=None,
        )


def test_create_application_endpoint_returns_normalized_decision():
    fake_service = FakeFactoringApplicationService()

    app.dependency_overrides[get_factoring_service] = (
        lambda: fake_service
    )

    client = TestClient(app)

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

    app.dependency_overrides.clear()

def test_create_application_endpoint_rejects_invalid_request():
    fake_service = FakeFactoringApplicationService()

    app.dependency_overrides[get_factoring_service] = (
        lambda: fake_service
    )

    client = TestClient(app)

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

    app.dependency_overrides.clear()

def test_create_application_endpoint_rejects_invalid_domain_data():
    fake_service = FakeFactoringApplicationService()

    app.dependency_overrides[get_factoring_service] = (
        lambda: fake_service
    )

    client = TestClient(app)

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

    app.dependency_overrides.clear()

def test_get_application_endpoint_returns_saved_decision():
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

    client = TestClient(app)

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

    app.dependency_overrides.clear()

def test_get_application_endpoint_returns_404_when_application_does_not_exist():
    repository = InMemoryApplicationRepository()

    app.dependency_overrides[get_application_repository] = (
        lambda: repository
    )

    client = TestClient(app)

    response = client.get(
        "/api/factoring/applications/FAC-9999"
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Application not found"
    }

    app.dependency_overrides.clear()

def test_create_application_endpoint_returns_integration_error():
    fake_service = FakeIntegrationErrorFactoringApplicationService()

    app.dependency_overrides[get_factoring_service] = (
        lambda: fake_service
    )

    client = TestClient(app)

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

    app.dependency_overrides.clear()