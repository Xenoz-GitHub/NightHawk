"""NIGHTHAWK exception hierarchy."""


class NightHawkError(Exception):
    """Base exception for the NIGHTHAWK platform."""

    pass


class ScopeViolationError(NightHawkError):
    """Raised when a scanner targets something outside authorized scope."""

    def __init__(self, message: str, target: str) -> None:
        super().__init__(message)
        self.target = target


class ScannerTimeoutError(NightHawkError):
    """Raised when a scanner exceeds its configured timeout."""

    pass


class UnsupportedTargetError(NightHawkError):
    """Raised when a target format or type is not supported."""

    pass


class FingerprintError(NightHawkError):
    """Raised during fingerprint matching or database access."""

    pass


class CredentialExposureError(NightHawkError):
    """Raised when a potential secret is detected (does not confirm validity)."""

    pass


class ConfigurationError(NightHawkError):
    """Raised when configuration is invalid or missing required values."""

    pass


class DatabaseError(NightHawkError):
    """Raised for database-level failures."""

    pass


class CampaignError(NightHawkError):
    """Base class for campaign lifecycle errors."""
    pass


class CampaignNotFoundError(CampaignError):
    """Raised when a referenced campaign does not exist."""

    def __init__(self, campaign_id: str) -> None:
        super().__init__(f"Campaign '{campaign_id}' not found.")
        self.campaign_id = campaign_id


class InvalidStateTransitionError(CampaignError):
    """Raised when a lifecycle transition is not allowed."""

    def __init__(self, current: str, requested: str) -> None:
        super().__init__(
            f"Cannot transition campaign from '{current}' to '{requested}'."
        )
        self.current = current
        self.requested = requested


class DuplicateCampaignError(CampaignError):
    """Raised when creating a campaign with an existing name."""

    def __init__(self, name: str) -> None:
        super().__init__(f"Campaign '{name}' already exists.")
        self.name = name


class ValidationError(NightHawkError):
    """Raised when user-supplied input fails semantic validation."""
    pass

