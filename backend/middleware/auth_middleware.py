from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from jose import jwt, JWTError
from typing import Optional
import logging
import os

from backend.models.models import User

# Configure logger for authentication events
logger = logging.getLogger("token_usage_dashboard.auth_middleware")

# JWT settings (should be loaded securely from env/config in production)
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "supersecretkey")
JWT_ALGORITHM = os.environ.get("JWT_ALGORITHM", "HS256")

class AuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware for authenticating requests using JWT and enforcing RBAC.
    Sets request.state.user to the authenticated user object.
    """

    async def dispatch(self, request: Request, call_next):
        # Allow unauthenticated access to docs and openapi
        if request.url.path.startswith("/docs") or \
           request.url.path.startswith("/openapi") or \
           request.url.path.startswith("/redoc"):
            return await call_next(request)

        # Extract JWT from Authorization header
        auth_header: Optional[str] = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            logger.warning("Missing or invalid Authorization header.")
            return JSONResponse(
                status_code=401,
                content={"detail": "Not authenticated"},
            )

        token = auth_header.split(" ", 1)[1]
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            user_id = payload.get("sub")
            username = payload.get("username")
            roles = payload.get("roles", [])
            if not user_id or not username:
                logger.warning("JWT missing required claims.")
                return JSONResponse(
                    status_code=401,
                    content={"detail": "Invalid authentication token."},
                )
            # RBAC: Only allow users with 'user' or 'admin' roles
            if not any(role in roles for role in ["user", "admin"]):
                logger.warning(f"User '{username}' lacks required roles: {roles}")
                return JSONResponse(
                    status_code=403,
                    content={"detail": "Insufficient permissions."},
                )
            # Attach user to request.state
            request.state.user = User(id=user_id, username=username, roles=roles)
            return await call_next(request)
        except JWTError as e:
            logger.warning(f"JWT decode error: {e}")
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid or expired authentication token."},
            )
        except Exception as e:
            logger.error(f"Unexpected authentication error: {e}")
            return JSONResponse(
                status_code=500,
                content={"detail": "Authentication system error."},
            )

# Exports
__all__ = ["AuthMiddleware"]