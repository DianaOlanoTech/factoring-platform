from fastapi import FastAPI

from app.adapters.repositories.in_memory_application_repository import (
    InMemoryApplicationRepository,
)
from app.adapters.risk.http_risk_provider import HttpRiskProvider
from app.api.factoring import router as factoring_router
from app.application.factoring_application_service import (
    FactoringApplicationService,
)
from app.api.mock_risk import router as mock_risk_router


app = FastAPI(
    title="Factoring Decision Service",
    version="1.0.0",
)


risk_provider = HttpRiskProvider(
    base_url="http://localhost:8000",
)

repository = InMemoryApplicationRepository()

factoring_service = FactoringApplicationService(
    risk_provider=risk_provider,
    repository=repository,
)

app.state.factoring_service = factoring_service
app.state.application_repository = repository

app.include_router(factoring_router)
app.include_router(mock_risk_router)