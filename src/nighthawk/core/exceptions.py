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
