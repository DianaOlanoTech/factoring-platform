"""
In-memory repository adapter for factoring applications.

This adapter provides a lightweight implementation of the
ApplicationRepository port without requiring a database.

Data is stored only for the lifetime of the application process.
"""

from app.domain.models import (
    FactoringApplication,
    FactoringDecision,
)


class InMemoryApplicationRepository:
    """
    Stores factoring application decisions in memory.

    This implementation is intentionally simple and is suitable for
    the scope of the take-home assessment.

    Stored data is lost when the application process stops.
    """

    def __init__(self):
        """Initialize an empty in-memory application store."""
        self._applications = {}

    def save(
        self,
        application: FactoringApplication,
        decision: FactoringDecision,
    ) -> None:
        """
        Store the decision associated with an application.

        If the application ID already exists, its previous decision
        is replaced.

        Args:
            application: Application being stored.
            decision: Decision associated with the application.
        """
        self._applications[application.application_id] = decision

    def get_by_application_id(
        self,
        application_id: str,
    ) -> FactoringDecision | None:
        """
        Retrieve a stored decision by application ID.

        Args:
            application_id: Identifier of the application.

        Returns:
            The stored decision, or None when no decision exists.
        """
        return self._applications.get(application_id)