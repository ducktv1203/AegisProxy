"""AegisProxy application entry point."""

import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from aegis import __version__
from aegis.api.router import router as api_router
from aegis.config import get_settings
from aegis.filters.pipeline import initialize_filters
from aegis.proxy.handler import get_proxy_handler
from aegis.telemetry.logger import configure_logging, get_logger
from aegis.telemetry.metrics import app_info, init_metrics, request_duration_seconds
from prometheus_client import make_asgi_app


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle manager."""
    # Startup
    configure_logging()
    logger = get_logger()
    settings = get_settings()
    
    logger.info("startup", version=__version__, settings=settings.model_dump(mode="json"))
    
    # Initialize components
    initialize_filters()
    init_metrics(__version__)
    
    logger.info("components_initialized")
    
    yield
    
    # Shutdown
    logger.info("shutdown")
    await get_proxy_handler().close()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()
    
    app = FastAPI(
        title="AegisProxy",
        description="Secure AI Gateway for LLM traffic inspection",
        version=__version__,
        lifespan=lifespan,
    )

    # CORS Configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Restrict in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Telemetry Middleware
    @app.middleware("http")
    async def telemetry_middleware(request: Request, call_next):
        start_time = time.time()
        
        try:
            response = await call_next(request)
            status = response.status_code
        except Exception:
            status = 500
            raise
        finally:
            duration = time.time() - start_time
            request_duration_seconds.labels(endpoint=request.url.path).observe(duration)
            
        return response

    # Mount Prometheus metrics
    if settings.metrics_enabled:
        metrics_app = make_asgi_app()
        app.mount("/metrics", metrics_app)

    # Register routers
    app.include_router(api_router)

    # Root endpoint
    @app.get("/")
    async def root():
        return {
            "name": "AegisProxy",
            "version": __version__,
            "status": "running",
            "docs_url": "/docs",
        }

    return app


app = create_app()


def run():
    """Run the application using uvicorn."""
    import uvicorn
    settings = get_settings()
    
    uvicorn.run(
        "aegis.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )


if __name__ == "__main__":
    run()
