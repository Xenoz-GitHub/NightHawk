"""Optional bearer-token authentication for the API.

Auth is opt-in: enabling it is a single env var (`NIGHTHAWK_API_TOKEN`).
When the token is unset the dependency is a no-op, keeping local development
and the test suite frictionless.
"""

from __future__ import annotations

import hmac

from fastapi import HTTPException, Request

from nighthawk.config.config import get_config


def require_auth(request: Request) -> None:
    """FastAPI dependency guarding routes behind a bearer token."""
    token = get_config().api_token
    if not token:
        return
    header = request.headers.get("Authorization", "")
    provided = header[7:] if header.startswith("Bearer ") else ""
    if not provided or not hmac.compare_digest(provided.encode(), token.encode()):
        raise HTTPException(
            status_code=401, detail="Invalid or missing API token."
        )