from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.health import router as health_router
from app.api.auth import router as auth_router
from app.api.ai.router import router as ai_router
from app.api.trading.backtest_router import router as backtest_router
from app.core.config.settings import settings
from app.core.rate_limit import limiter
from app.tasks.schedulers.market_scheduler import market_scheduler


@asynccontextmanager
async def lifespan(application: FastAPI):
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

    cors_origins = [origin.strip() for origin in settings.BACKEND_CORS_ORIGINS.split(",") if origin.strip()]
    if not cors_origins:
        cors_origins = ["http://localhost:3000"]
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

    return application


app = create_app()
