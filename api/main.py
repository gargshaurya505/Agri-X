"""FastAPI application entrypoint for AGRI-X."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.services.model_service import container
from api.routes.api import router

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("agrix.api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context loading the model once upon server startup."""
    logger.info("Initializing AGRI-X local AI service...")
    try:
        container.load()
        logger.info(f"AGRI-X Model ready on device: {container.device}")
    except Exception as e:
        logger.error(f"Failed to load AGRI-X model on startup: {e}")
    yield
    logger.info("Shutting down AGRI-X local AI service.")


app = FastAPI(
    title="AGRI-X Local AI Service",
    description="Local inference and Grad-CAM explainability service for tomato disease detection",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:[0-9]+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="127.0.0.1", port=8000, reload=False)
