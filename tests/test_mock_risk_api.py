from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_mock_risk_returns_approved():
    response = client.post(
        "/mock/risk/decision",
        json={
            "customer_id": "CUS-101",
            "invoice_amount_cents": 125000,
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "provider_reference": "RISK-9001",
        "status": "approved",
        "max_advance_percent": 80,
    }

def test_mock_risk_returns_review():
    response = client.post(
        "/mock/risk/decision",
        json={
            "customer_id": "CUS-102",
            "invoice_amount_cents": 125000,
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "provider_reference": "RISK-9002",
        "status": "review",
        "max_advance_percent": None,
    }

def test_mock_risk_returns_declined():
    response = client.post(
        "/mock/risk/decision",
        json={
            "customer_id": "CUS-103",
            "invoice_amount_cents": 125000,
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "provider_reference": "RISK-9003",
        "status": "declined",
        "max_advance_percent": None,
    }