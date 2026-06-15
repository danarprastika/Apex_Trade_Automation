import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.ai.router import router as ai_router
from app.api.auth.router import router as auth_router
from app.api.health.router import router as health_router
from app.api.intelligence.router import router as intelligence_router
from app.api.market.router import router as market_router
from app.api.trading.backtest_router import router as backtest_router
from app.core.rate_limit import limiter
from app.database.session import ensure_runtime_indexes
from app.startup_tasks import run_startup_tasks
from app.tasks.schedulers.market_scheduler import market_scheduler
from app.core.config.settings import settings

logger = logging.getLogger(__name__)


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    logger.warning("http_exception", path=request.url.path, status_code=exc.status_code, detail=exc.detail)
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    logger.warning("request_validation_error", path=request.url.path, errors=exc.errors())
    return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content={"detail": exc.errors()})


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("unhandled_request_exception", path=request.url.path)
    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"detail": "Internal server error"})


@asynccontextmanager
async def lifespan(application: FastAPI):
    run_startup_tasks()
    
    try:
        ensure_runtime_indexes()
    except Exception:
        logger.exception("database_index_initialization_failed")
    
    market_scheduler.start()
    yield
    market_scheduler.shutdown()


def create_app() -> FastAPI:
    application = FastAPI(
        title=settings.APP_NAME,
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    application.state.limiter = limiter
    application.add_exception_handler(HTTPException, http_exception_handler)
    application.add_exception_handler(RequestValidationError, validation_exception_handler)
    application.add_exception_handler(Exception, unhandled_exception_handler)

    cors_origins = [origin.strip() for origin in settings.BACKEND_CORS_ORIGINS.split(",") if origin.strip()]
    application.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
        max_age=600,
    )

    application.include_router(health_router)
    application.include_router(auth_router, prefix="/api/v1")
    application.include_router(backtest_router, prefix="/api/v1")
    application.include_router(ai_router, prefix="/api/v1")
    application.include_router(market_router, prefix="/api/v1")
    application.include_router(intelligence_router, prefix="/api/v1")

    return application


app = create_app()
