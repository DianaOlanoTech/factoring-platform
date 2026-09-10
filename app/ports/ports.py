"""
Ports used by the application core.

Ports define the contracts required by the core without specifying
how those contracts are implemented. Concrete implementations live
in the adapter layer.
"""

from typing import Protocol

from app.domain.models import (
    FactoringApplication,
    FactoringDecision,
    RiskResult,
)


class RiskProvider(Protocol):
    """
    Port for obtaining a risk evaluation for a factoring application.

    The application service depends on this abstraction rather than
    depending on a concrete HTTP client or external risk provider.

    Any adapter implementing this protocol can be used by the core.
    """

    def evaluate(
        self,
        application: FactoringApplication,
    ) -> RiskResult:
        """
        Evaluate an application using a risk provider.

        Args:
            application: Application to evaluate.

        Returns:
            A normalized RiskResult.
        """
        ...


class ApplicationRepository(Protocol):
    """
    Port for storing and retrieving factoring application decisions.

    The core depends on this abstraction instead of depending on a
    particular storage technology such as an in-memory dictionary,
    SQLite, or PostgreSQL.
    """

    def save(
        self,
        application: FactoringApplication,
        decision: FactoringDecision,
    ) -> None:
        """
        Persist an application and its resulting decision.

        Args:
            application: Factoring application being persisted.
            decision: Normalized decision associated with the application.
        """
        ...

    def get_by_application_id(
        self,
        application_id: str,
    ) -> FactoringDecision | None:
        """
        Retrieve a decision by application ID.

        Args:
            application_id: Identifier of the application to retrieve.

        Returns:
            The stored decision, or None if the application does not exist.
        """
        ...