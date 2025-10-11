from fastapi import FastAPI
from app.core.logger import get_logger
from app.core.config import settings
from app.api.routes.urls import router as url_router

logger = get_logger(__name__)

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
    )

    app.include_router(url_router, prefix="/api")


    async def startup_event():
        logger.info("Starting FastAPI application")

    async def shutdown_event():
        logger.info("Shutting down application")

    app.add_event_handler("startup", startup_event)
    app.add_event_handler("shutdown", shutdown_event)

    return app

app = create_app()
