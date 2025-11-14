from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from loguru import logger
from typing import Optional
import time

class AuditLoggerMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging dashboard access and data retrieval for audit purposes.
    Logs user ID, endpoint, method, status, and timing for each API request.
    """

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        user_id: Optional[str] = None
        username: Optional[str] = None

        # Attempt to extract user info from request.state (set by AuthMiddleware)
        user = getattr(request.state, "user", None)
        if user:
            user_id = getattr(user, "id", None)
            username = getattr(user, "username", None)

        # Proceed with request
        response: Response = await call_next(request)
        process_time = (time.time() - start_time) * 1000  # ms

        # Build audit log entry
        log_data = {
            "event": "api_access",
            "user_id": user_id or "anonymous",
            "username": username or "anonymous",
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "process_time_ms": round(process_time, 2),
            "client_host": request.client.host if request.client else None,
        }

        # Only log API and dashboard access (not static/docs)
        if request.url.path.startswith("/api") or request.url.path.startswith("/dashboard"):
            logger.info(f"AUDIT_LOG | {log_data}")

        return response

# Exports
__all__ = ["AuditLoggerMiddleware"]