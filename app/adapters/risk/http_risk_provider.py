import httpx

from app.adapters.risk.exceptions import RiskProviderError
from app.domain.models import (
    FactoringApplication,
    RiskResult,
    RiskStatus,
)


class HttpRiskProvider:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def evaluate(self, application: FactoringApplication) -> RiskResult:
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

        if status == RiskStatus.APPROVED and data["max_advance_percent"] is None:
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