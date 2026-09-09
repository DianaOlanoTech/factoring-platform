from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import (
    get_application_repository,
    get_factoring_service,
)
from app.api.models import (
    FactoringApplicationRequest,
    FactoringDecisionResponse,
)
from app.application.factoring_application_service import (
    FactoringApplicationService,
)
from app.domain.models import FactoringApplication
from app.ports.ports import ApplicationRepository

router = APIRouter(
    prefix="/api/factoring",
    tags=["factoring"],
)


@router.post(
    "/applications",
    response_model=FactoringDecisionResponse,
)
def create_application(
    request: FactoringApplicationRequest,
    service: FactoringApplicationService = Depends(get_factoring_service),
    repository: ApplicationRepository = Depends(get_application_repository),
) -> FactoringDecisionResponse:
    try:
        application = FactoringApplication(
            application_id=request.application_id,
            customer_id=request.customer_id,
            invoice_amount_cents=request.invoice_amount_cents,
            requested_advance_cents=request.requested_advance_cents,
            due_date=request.due_date,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    decision = service.create_application(application)

    return FactoringDecisionResponse(
        application_id=decision.application_id,
        decision=decision.decision.value,
        requested_advance_cents=decision.requested_advance_cents,
        available_advance_cents=decision.available_advance_cents,
        provider_reference=decision.provider_reference,
    )

@router.get(
    "/applications/{application_id}",
    response_model=FactoringDecisionResponse,
)
def get_application(
    application_id: str,
    repository: ApplicationRepository = Depends(get_application_repository),
) -> FactoringDecisionResponse:
    decision = repository.get_by_application_id(application_id)

    if decision is None:
        raise HTTPException(
            status_code=404,
            detail="Application not found",
        )

    return FactoringDecisionResponse(
        application_id=decision.application_id,
        decision=decision.decision.value,
        requested_advance_cents=decision.requested_advance_cents,
        available_advance_cents=decision.available_advance_cents,
        provider_reference=decision.provider_reference,
    )