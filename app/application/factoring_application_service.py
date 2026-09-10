"""
Application service for the factoring decision use case.

This module contains the main business workflow for evaluating a
factoring application.

The service depends only on domain models and ports. It does not know
about FastAPI, HTTP, databases, or provider-specific response formats.
"""

from math import floor

from app.domain.models import (
    DecisionStatus,
    FactoringApplication,
    FactoringDecision,
    RiskResult,
    RiskStatus,
)
from app.ports.exceptions import RiskProviderError
from app.ports.ports import ApplicationRepository, RiskProvider


class FactoringApplicationService:
    """
    Coordinates the factoring application decision workflow.

    The service obtains a risk evaluation through the RiskProvider port,
    applies the business decision rules, and persists the resulting
    decision through the ApplicationRepository port.

    Args:
        risk_provider: Port used to obtain a normalized risk evaluation.
        repository: Port used to persist and retrieve application results.
    """

    def __init__(
        self,
        risk_provider: RiskProvider,
        repository: ApplicationRepository,
    ):
        self.risk_provider = risk_provider
        self.repository = repository

    def create_application(
        self,
        application: FactoringApplication,
    ) -> FactoringDecision:
        """
        Evaluate and persist a factoring application.

        If the risk provider fails, the integration failure is converted
        into an INTEGRATION_ERROR decision and persisted instead of
        propagating an infrastructure-specific exception.

        Args:
            application: Factoring application to evaluate.

        Returns:
            The normalized factoring decision.
        """
        try:
            risk_result = self.risk_provider.evaluate(application)

        except RiskProviderError:
            decision = FactoringDecision(
                application_id=application.application_id,
                decision=DecisionStatus.INTEGRATION_ERROR,
                requested_advance_cents=application.requested_advance_cents,
                available_advance_cents=None,
                provider_reference=None,
            )

            self.repository.save(application, decision)

            return decision

        decision = self._build_decision(
            application,
            risk_result,
        )

        self.repository.save(application, decision)

        return decision

    def _build_decision(
        self,
        application: FactoringApplication,
        risk_result: RiskResult,
    ) -> FactoringDecision:
        """
        Apply the factoring business rules to a risk result.

        Approved applications calculate the available advance using
        the provider's maximum advance percentage. The requested amount
        is then compared with that available amount.

        REVIEW results become NEEDS_REVIEW decisions, while DECLINED
        results become REJECTED decisions.

        Args:
            application: Application being evaluated.
            risk_result: Normalized risk evaluation.

        Returns:
            The final normalized factoring decision.
        """
        if risk_result.status == RiskStatus.APPROVED:
            available_advance_cents = floor(
                application.invoice_amount_cents
                * risk_result.max_advance_percent
                / 100
            )

            if (
                application.requested_advance_cents
                <= available_advance_cents
            ):
                decision_status = DecisionStatus.ELIGIBLE
            else:
                decision_status = DecisionStatus.NEEDS_REVIEW

            return FactoringDecision(
                application_id=application.application_id,
                decision=decision_status,
                requested_advance_cents=application.requested_advance_cents,
                available_advance_cents=available_advance_cents,
                provider_reference=risk_result.provider_reference,
            )

        elif risk_result.status == RiskStatus.REVIEW:
            return FactoringDecision(
                application_id=application.application_id,
                decision=DecisionStatus.NEEDS_REVIEW,
                requested_advance_cents=application.requested_advance_cents,
                available_advance_cents=None,
                provider_reference=risk_result.provider_reference,
            )

        else:
            return FactoringDecision(
                application_id=application.application_id,
                decision=DecisionStatus.REJECTED,
                requested_advance_cents=application.requested_advance_cents,
                available_advance_cents=None,
                provider_reference=risk_result.provider_reference,
            )