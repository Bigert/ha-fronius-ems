class FroniusApiError(Exception):
    """Base exception for HA Fronius EMS."""


class FroniusAuthenticationError(FroniusApiError):
    """Authentication failed."""
