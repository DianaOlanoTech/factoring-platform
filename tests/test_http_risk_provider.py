from datetime import date
from unittest.mock import Mock, patch

import httpx
import pytest

from app.adapters.risk.exceptions import RiskProviderError
from app.adapters.risk.http_risk_provider import HttpRiskProvider
from app.domain.models import (
    FactoringApplication,
    RiskStatus,
)


def test_evaluate_returns_approved_risk_result():
    application = FactoringApplication(
        application_id="FAC-1001",
        customer_id="CUS-101",
        invoice_amount_cents=125000,
        requested_advance_cents=90000,
        due_date=date(2026, 10, 15),
    )

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "provider_reference": "RISK-9001",
        "status": "approved",
        "max_advance_percent": 80,
    }

    provider = HttpRiskProvider("http://localhost:8000")

    with patch("httpx.post", return_value=mock_response) as mock_post:
        result = provider.evaluate(application)

    assert result.status == RiskStatus.APPROVED
    assert result.max_advance_percent == 80
    assert result.provider_reference == "RISK-9001"

    mock_post.assert_called_once_with(
        "http://localhost:8000/mock/risk/decision",
        json={
            "customer_id": "CUS-101",
            "invoice_amount_cents": 125000,
        },
        timeout=5.0,
    )

def test_evaluate_raises_error_when_provider_returns_non_2xx():
    application = FactoringApplication(
        application_id="FAC-1001",
        customer_id="CUS-101",
        invoice_amount_cents=125000,
        requested_advance_cents=90000,
        due_date=date(2026, 10, 15),
    )

    mock_response = Mock()
    mock_response.status_code = 500

    provider = HttpRiskProvider("http://localhost:8000")

    with patch("httpx.post", return_value=mock_response):
        with pytest.raises(RiskProviderError):
            provider.evaluate(application)

def test_evaluate_raises_error_when_provider_times_out():
    application = FactoringApplication(
        application_id="FAC-1001",
        customer_id="CUS-101",
        invoice_amount_cents=125000,
        requested_advance_cents=90000,
        due_date=date(2026, 10, 15),
    )

    provider = HttpRiskProvider("http://localhost:8000")

    with patch(
        "httpx.post",
        side_effect=httpx.TimeoutException("Request timed out"),
    ):
        with pytest.raises(RiskProviderError):
            provider.evaluate(application)

def test_evaluate_raises_error_when_provider_returns_invalid_json():
    application = FactoringApplication(
        application_id="FAC-1001",
        customer_id="CUS-101",
        invoice_amount_cents=125000,
        requested_advance_cents=90000,
        due_date=date(2026, 10, 15),
    )

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.side_effect = ValueError("Invalid JSON")

    provider = HttpRiskProvider("http://localhost:8000")

    with patch("httpx.post", return_value=mock_response):
        with pytest.raises(RiskProviderError):
            provider.evaluate(application)

def test_evaluate_raises_error_when_provider_returns_incomplete_payload():
    application = FactoringApplication(
        application_id="FAC-1001",
        customer_id="CUS-101",
        invoice_amount_cents=125000,
        requested_advance_cents=90000,
        due_date=date(2026, 10, 15),
    )

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "status": "approved",
    }

    provider = HttpRiskProvider("http://localhost:8000")

    with patch("httpx.post", return_value=mock_response):
        with pytest.raises(RiskProviderError):
            provider.evaluate(application)

def test_evaluate_raises_error_when_provider_returns_unknown_status():
    application = FactoringApplication(
        application_id="FAC-1001",
        customer_id="CUS-101",
        invoice_amount_cents=125000,
        requested_advance_cents=90000,
        due_date=date(2026, 10, 15),
    )

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "provider_reference": "RISK-9001",
        "status": "unknown",
        "max_advance_percent": 80,
    }

    provider = HttpRiskProvider("http://localhost:8000")

    with patch("httpx.post", return_value=mock_response):
        with pytest.raises(RiskProviderError):
            provider.evaluate(application)

def test_evaluate_raises_error_when_approved_result_has_no_max_advance_percent():
    application = FactoringApplication(
        application_id="FAC-1001",
        customer_id="CUS-101",
        invoice_amount_cents=125000,
        requested_advance_cents=90000,
        due_date=date(2026, 10, 15),
    )

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "provider_reference": "RISK-9001",
        "status": "approved",
        "max_advance_percent": None,
    }

    provider = HttpRiskProvider("http://localhost:8000")

    with patch("httpx.post", return_value=mock_response):
        with pytest.raises(RiskProviderError):
            provider.evaluate(application)

def test_evaluate_raises_error_when_provider_returns_invalid_percentage():
    application = FactoringApplication(
        application_id="FAC-1001",
        customer_id="CUS-101",
        invoice_amount_cents=125000,
        requested_advance_cents=90000,
        due_date=date(2026, 10, 15),
    )

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "provider_reference": "RISK-9001",
        "status": "approved",
        "max_advance_percent": 150,
    }

    provider = HttpRiskProvider("http://localhost:8000")

    with patch("httpx.post", return_value=mock_response):
        with pytest.raises(RiskProviderError):
            provider.evaluate(application)

def test_evaluate_raises_error_when_provider_returns_non_object_json():
    application = FactoringApplication(
        application_id="FAC-1001",
        customer_id="CUS-101",
        invoice_amount_cents=125000,
        requested_advance_cents=90000,
        due_date=date(2026, 10, 15),
    )

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = ["approved", 80]

    provider = HttpRiskProvider("http://localhost:8000")

    with patch("httpx.post", return_value=mock_response):
        with pytest.raises(RiskProviderError):
            provider.evaluate(application)