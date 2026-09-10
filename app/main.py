"""
Application entry point and dependency composition root.

This module creates the FastAPI application, instantiates the concrete
adapters, wires them into the application service, registers API
routers, and serves the frontend.

Concrete infrastructure dependencies are assembled here so the core
application remains independent from FastAPI and infrastructure
implementations.
"""

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.adapters.repositories.in_memory_application_repository import (
    InMemoryApplicationRepository,
)
from app.adapters.risk.http_risk_provider import HttpRiskProvider
from app.api.factoring import router as factoring_router
from app.api.mock_risk import router as mock_risk_router
from app.application.factoring_application_service import (
    FactoringApplicationService,
)


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


frontend_path = Path(__file__).resolve().parent.parent / "frontend"

app.mount(
    "/",
    StaticFiles(directory=frontend_path, html=True),
    name="frontend",
)