"""
HTTP adapter for the external risk provider.

This module translates between the external provider's HTTP/JSON
contract and the normalized RiskResult domain model.

HTTP details, provider field names, URLs, status codes, and httpx
exceptions are intentionally kept inside this adapter.
"""

import httpx

from app.domain.models import (
    FactoringApplication,
    RiskResult,
    RiskStatus,
)
from app.ports.exceptions import RiskProviderError


class HttpRiskProvider:
    """
    Concrete RiskProvider adapter that communicates over HTTP.

    Args:
        base_url: Base URL of the external risk provider.
    """

    def __init__(self, base_url: str):
        self.base_url = base_url

    def evaluate(
        self,
        application: FactoringApplication,
    ) -> RiskResult:
        """
        Send an application to the risk provider and normalize its response.

        Args:
            application: Factoring application to evaluate.

        Returns:
            A normalized RiskResult.

        Raises:
            RiskProviderError: If the provider request fails, returns a
                non-2xx response, returns invalid JSON, or returns a
                payload that does not satisfy the expected contract.
        """
        payload = {
            "customer_id": application.customer_id,
            "invoice_amount_cents": application.invoice_amount_cents,
        }

        try:
            response = httpx.post(
                f"{self.base_url}/mock/risk/decision",
                json=payload,
                timeout=5.0,
            )

        except httpx.RequestError as exc:
            raise RiskProviderError(
                "Risk provider request failed"
            ) from exc

        if not 200 <= response.status_code < 300:
            raise RiskProviderError(
                f"Risk provider returned status {response.status_code}"
            )

        try:
            data = response.json()

        except ValueError as exc:
            raise RiskProviderError(
                "Risk provider returned invalid JSON"
            ) from exc

        if not isinstance(data, dict):
            raise RiskProviderError(
                "Risk provider returned an unexpected payload"
            )

        required_fields = {
            "provider_reference",
            "status",
            "max_advance_percent",
        }

        if not required_fields.issubset(data):
            raise RiskProviderError(
                "Risk provider returned an unexpected payload"
            )

        try:
            status = RiskStatus(data["status"])

        except ValueError as exc:
            raise RiskProviderError(
                "Risk provider returned an unknown status"
            ) from exc

        if (
            status == RiskStatus.APPROVED
            and data["max_advance_percent"] is None
        ):
            raise RiskProviderError(
                "Approved risk result must include max_advance_percent"
            )

        try:
            return RiskResult(
                status=status,
                max_advance_percent=data["max_advance_percent"],
                provider_reference=data["provider_reference"],
            )

        except (TypeError, ValueError) as exc:
            raise RiskProviderError(
                "Risk provider returned an invalid payload"
            ) from exc