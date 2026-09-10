"""
FastAPI dependency functions used by the API layer.

These functions retrieve application components that were wired in
main.py. They keep dependency construction outside the route handlers.
"""

from fastapi import Request

from app.application.factoring_application_service import (
    FactoringApplicationService,
)
from app.ports.ports import ApplicationRepository


def get_factoring_service(
    request: Request,
) -> FactoringApplicationService:
    """
    Retrieve the configured factoring application service.

    Args:
        request: Current FastAPI request.

    Returns:
        The application service configured in app.state.
    """
    return request.app.state.factoring_service


def get_application_repository(
    request: Request,
) -> ApplicationRepository:
    """
    Retrieve the configured application repository.

    Args:
        request: Current FastAPI request.

    Returns:
        The repository configured in app.state.
    """
    return request.app.state.application_repository