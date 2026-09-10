"""
Exceptions exposed by application ports.

These exceptions represent failures at an application boundary
without exposing infrastructure-specific exceptions to the core.
"""


class RiskProviderError(Exception):
    """
    Raised when the risk provider cannot provide a valid result.

    The exception abstracts failures such as HTTP errors, timeouts,
    invalid JSON, or unexpected provider payloads so the application
    core does not need to depend on HTTP client implementation details.
    """