from typing import Protocol

from app.domain.models import (
    FactoringApplication,
    FactoringDecision,
    RiskResult,
)


class RiskProvider(Protocol):
    def evaluate(self, application: FactoringApplication) -> RiskResult:
        ...


class ApplicationRepository(Protocol):
    def save(
        self,
        application: FactoringApplication,
        decision: FactoringDecision,
    ) -> None:
        ...

    def get_by_application_id(
        self,
        application_id: str,
    ) -> FactoringDecision | None:
        ...