from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import JSONResponse
import logging
import uvicorn

from backend.routes.token_usage import router as token_usage_router
from backend.middleware.auth_middleware import AuthMiddleware
from backend.middleware.audit_logger import AuditLoggerMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s"
)
logger = logging.getLogger("token_usage_dashboard.backend")

def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    Returns:
        FastAPI: Configured FastAPI app instance.
    """
    app = FastAPI(
        title="Token Usage Dashboard API",
        description="Secure API for token usage analytics.",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # Enforce HTTPS (TLS) for all requests
    app.add_middleware(HTTPSRedirectMiddleware)

    # CORS: Only allow frontend origin (adjust as needed)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["https://dashboard.token-dashboard.local"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Session middleware (for secure cookies if needed)
    app.add_middleware(SessionMiddleware, secret_key="supersecretkey")

    # Custom authentication and RBAC middleware
    app.add_middleware(AuthMiddleware)

    # Audit logging middleware
    app.add_middleware(AuditLoggerMiddleware)

    # Include API routers
    app.include_router(token_usage_router, prefix="/api", tags=["Token Usage"])

    # Global exception handler for 500 errors
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception: {exc}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error."},
        )

    return app

app = create_app()

if __name__ == "__main__":
    # Run with uvicorn for local development
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        ssl_keyfile="/etc/ssl/private/server.key",  # Path to TLS key
        ssl_certfile="/etc/ssl/certs/server.crt",   # Path to TLS cert
    )