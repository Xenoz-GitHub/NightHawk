"""Exception → HTTP mapping. Every error path returns an ErrorResponse."""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from nighthawk.config.config import get_config
from nighthawk.core.exceptions import (
    CampaignNotFoundError,
    ConfigurationError,
    DatabaseError,
    DuplicateCampaignError,
    InvalidStateTransitionError,
    NightHawkError,
    ScopeViolationError,
    ValidationError,
)
from nighthawk.logging.setup import get_logger

logger = get_logger("api.errors")


def _error(
    status_code: int,
    error: str,
    detail: str | None = None,
    **extra: str,
) -> JSONResponse:
    body: dict = {"error": error, "detail": detail}
    body.update({k: v for k, v in extra.items() if v is not None})
    return JSONResponse(status_code=status_code, content=body)


def register_error_handlers(app: FastAPI) -> None:
    """Attach structured error handlers to the app."""

    @app.exception_handler(ScopeViolationError)
    async def scope_violation_handler(request: Request, exc: ScopeViolationError):
        return _error(403, "scope_violation", str(exc), target=exc.target)

    @app.exception_handler(CampaignNotFoundError)
    async def campaign_not_found_handler(request: Request, exc: CampaignNotFoundError):
        return _error(404, "campaign_not_found", str(exc))

    @app.exception_handler(DuplicateCampaignError)
    async def duplicate_campaign_handler(request: Request, exc: DuplicateCampaignError):
        return _error(409, "duplicate_campaign", str(exc), name=exc.name)

    @app.exception_handler(InvalidStateTransitionError)
    async def invalid_transition_handler(request: Request, exc: InvalidStateTransitionError):
        return _error(
            409,
            "invalid_state_transition",
            str(exc),
            current_state=exc.current,
            requested_state=exc.requested,
        )

    @app.exception_handler(ValidationError)
    async def validation_error_handler(request: Request, exc: ValidationError):
        return _error(422, "validation_error", str(exc))

    @app.exception_handler(ConfigurationError)
    async def configuration_error_handler(request: Request, exc: ConfigurationError):
        return _error(500, "configuration_error", str(exc))

    @app.exception_handler(DatabaseError)
    async def database_error_handler(request: Request, exc: DatabaseError):
        return _error(500, "database_error", str(exc))

    @app.exception_handler(NightHawkError)
    async def nighthawk_error_handler(request: Request, exc: NightHawkError):
        return _error(400, "nighthawk_error", str(exc))

    @app.exception_handler(RequestValidationError)
    async def request_validation_handler(request: Request, exc: RequestValidationError):
        return _error(422, "request_validation_error", str(exc.errors()))

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        return _error(exc.status_code, "http_error", str(exc.detail))

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        """Last-resort 500: never leak internals. Detailed only in debug."""
        logger.exception("unhandled_api_error", path=request.url.path)
        detail = str(exc) if get_config().api_debug else "Internal server error."
        return _error(500, "internal_error", detail)
