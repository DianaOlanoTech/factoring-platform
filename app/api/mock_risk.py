from fastapi import APIRouter
from pydantic import BaseModel


class MockRiskRequest(BaseModel):
    customer_id: str
    invoice_amount_cents: int


class MockRiskResponse(BaseModel):
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
def risk_decision(request: MockRiskRequest) -> MockRiskResponse:
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