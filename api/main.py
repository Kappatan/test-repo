from __future__ import annotations

import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from api.router import api_router
from config import get_settings
from consumer import RabbitMQConsumer
from repositories.session import create_database

settings = get_settings()
consumer = RabbitMQConsumer()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    create_database()
    consumer.start()
    yield


logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

app = FastAPI(title=settings.app_name, debug=settings.debug, lifespan=lifespan)
app.include_router(api_router)


@app.get("/health", tags=["health"])
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
