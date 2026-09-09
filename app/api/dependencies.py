from fastapi import Request

from app.application.factoring_application_service import FactoringApplicationService
from app.ports.ports import ApplicationRepository


def get_factoring_service(request: Request) -> FactoringApplicationService:
    return request.app.state.factoring_service


def get_application_repository(request: Request) -> ApplicationRepository:
    return request.app.state.application_repository