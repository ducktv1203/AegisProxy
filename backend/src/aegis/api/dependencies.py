"""FastAPI dependencies for request handling."""

from typing import Annotated

from fastapi import Depends, Header, HTTPException, Request

from aegis.config import Settings, get_settings


async def get_request_id(request: Request) -> str:
    """Extract or generate a unique request ID."""
    request_id = request.headers.get("X-Request-ID")
    if not request_id:
        import uuid

        request_id = str(uuid.uuid4())
    return request_id


async def verify_api_key(
    authorization: Annotated[str | None, Header()] = None,
    settings: Settings = Depends(get_settings),
) -> str | None:
    """
    Extract and optionally verify the API key from Authorization header.

    For pass-through mode, we just extract the key to forward to the LLM.
    Future: Add AegisProxy-specific auth if needed.
    """
    if authorization is None:
        return None

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail={"message": "Invalid authorization header format",
                    "type": "invalid_auth"},
        )

    return authorization[7:]  # Strip "Bearer "


async def get_client_info(request: Request) -> dict[str, str | None]:
    """Extract client metadata for logging."""
    return {
        "client_ip": request.client.host if request.client else None,
        "user_agent": request.headers.get("User-Agent"),
        "origin": request.headers.get("Origin"),
    }


# Type aliases for dependency injection
RequestId = Annotated[str, Depends(get_request_id)]
ApiKey = Annotated[str | None, Depends(verify_api_key)]
ClientInfo = Annotated[dict[str, str | None], Depends(get_client_info)]
SettingsDep = Annotated[Settings, Depends(get_settings)]
