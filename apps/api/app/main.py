from __future__ import annotations

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse

from app.api.v1.router import router as v1_router
from app.core.config import settings
from app.demo_console import demo_console
from app.core.errors import install_exception_handlers
from app.core.middleware import BodySizeLimitMiddleware, RequestIdMiddleware, SecurityHeadersMiddleware
from app.core.logging import logger


def _enforce_production_safety() -> None:
    """Refuse to boot in production with development credentials."""
    from app.core.security import is_production

    if not is_production():
        return
    problems = []
    if settings.api_key_pepper == "dev-pepper":
        problems.append("API_KEY_PEPPER is still the development default")
    if settings.debug:
        problems.append("DEBUG must be disabled in production")
    if problems:
        raise RuntimeError(
            "Refusing to start in production: " + "; ".join(problems)
        )


def _restore_demo_organization_pointer() -> None:
    """Point the demo principal at the latest persisted organization.

    The demo principal scope is a process-global; with the persistent
    sqlalchemy profile the data survives restarts, so the pointer must too.
    """
    if settings.resource_repository_backend != "sqlalchemy":
        return
    try:
        from app.core.security import set_demo_organization_id
        from app.services.core_repositories import core_repository

        latest = core_repository.latest_organization_id()
        if latest is not None:
            set_demo_organization_id(latest)
    except Exception:
        logger.warning("Could not restore the demo organization pointer", exc_info=True)


def create_app() -> FastAPI:
    _enforce_production_safety()
    app = FastAPI(
        title="CreativeLift AI API",
        description="Open-source AI marketing measurement platform API.",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )
    app.logger = logger  # type: ignore[attr-defined]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "DELETE", "PATCH", "PUT", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "Idempotency-Key", "X-Request-ID", "X-API-Key"],
    )
    app.add_middleware(RequestIdMiddleware)
    app.add_middleware(BodySizeLimitMiddleware)
    app.add_middleware(SecurityHeadersMiddleware)
    install_exception_handlers(app)

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
        return JSONResponse(
            status_code=400,
            content={"error": "bad_request", "detail": str(exc), "request_id": getattr(request.state, "request_id", None)},
        )

    @app.get("/healthz", tags=["system"])
    async def healthz() -> dict[str, str]:
        return {"status": "ok", "service": settings.app_name}

    @app.get("/readyz", tags=["system"])
    async def readyz(response: Response) -> dict[str, str]:
        database = "not_required"
        if settings.resource_repository_backend == "sqlalchemy":
            try:
                from sqlalchemy import text

                from app.db.session import engine

                with engine.connect() as connection:
                    connection.execute(text("SELECT 1"))
                database = "ok"
            except Exception:
                response.status_code = 503
                return {"status": "not_ready", "database": "unavailable", "redis": "configured"}
        return {"status": "ready", "database": database, "redis": "configured"}

    @app.get("/metrics", tags=["system"], response_class=PlainTextResponse)
    async def metrics() -> str:
        return "# HELP creativelift_up Service availability\n# TYPE creativelift_up gauge\ncreativelift_up 1\n"

    @app.get("/demo", tags=["system"])
    async def demo() -> HTMLResponse:
        return demo_console()

    app.include_router(v1_router, prefix="/v1")
    _restore_demo_organization_pointer()
    return app


app = create_app()
