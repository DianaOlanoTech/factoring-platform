from math import floor

from app.adapters.risk.exceptions import RiskProviderError
from app.domain.models import (
    DecisionStatus,
    FactoringApplication,
    FactoringDecision,
    RiskResult,
    RiskStatus,
)
from app.ports.ports import ApplicationRepository, RiskProvider


class FactoringApplicationService:
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

        decision = self._build_decision(application, risk_result)

        self.repository.save(application, decision)

        return decision

    def _build_decision(
        self,
        application: FactoringApplication,
        risk_result: RiskResult,
    ) -> FactoringDecision:
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