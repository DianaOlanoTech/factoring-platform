from app.domain.models import FactoringApplication, FactoringDecision


class InMemoryApplicationRepository:
    def __init__(self):
        self._applications = {}

    def save(
        self,
        application: FactoringApplication,
        decision: FactoringDecision,
    ) -> None:
        self._applications[application.application_id] = decision

    def get_by_application_id(
        self,
        application_id: str,
    ) -> FactoringDecision | None:
        return self._applications.get(application_id)