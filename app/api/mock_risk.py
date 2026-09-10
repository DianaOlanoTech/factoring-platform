"""
Mock risk provider endpoint used by the take-home application.

This module simulates the external risk provider described in the
assessment. It allows the HTTP risk adapter to be exercised locally
without requiring a real third-party service.
"""

from fastapi import APIRouter
from pydantic import BaseModel


class MockRiskRequest(BaseModel):
    """Request body expected by the mock risk provider."""

    customer_id: str
    invoice_amount_cents: int


class MockRiskResponse(BaseModel):
    """Response body returned by the mock risk provider."""

    provider_reference: str
    status: str
    max_advance_percent: int | None


router = APIRouter(
    prefix="/mock/risk",
    tags=["mock-risk"],
)


@router.post(
    "/decision",
    response_model=MockRiskResponse,
)
def risk_decision(
    request: MockRiskRequest,
) -> MockRiskResponse:
    """
    Return a deterministic risk response for testing.

    The customer ID determines the simulated provider outcome:

    - CUS-101: approved with an 80% maximum advance.
    - CUS-102: review.
    - CUS-103: declined.
    - Any other customer: approved with an 80% maximum advance.

    Args:
        request: Validated mock provider request.

    Returns:
        A deterministic mock risk response.
    """
    if request.customer_id == "CUS-102":
        return MockRiskResponse(
            provider_reference="RISK-9002",
            status="review",
            max_advance_percent=None,
        )

    if request.customer_id == "CUS-103":
        return MockRiskResponse(
            provider_reference="RISK-9003",
            status="declined",
            max_advance_percent=None,
        )

    return MockRiskResponse(
        provider_reference="RISK-9001",
        status="approved",
        max_advance_percent=80,
    )