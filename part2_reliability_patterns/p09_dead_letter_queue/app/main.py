from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import router
from app.core.logger import get_logger


logger = get_logger(__name__)



@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    logger.info('[api] Application starting.')

    yield

    logger.info('[api] Application shutting down.')




app = FastAPI(
    title='P09 - Dead Letter Queue',
    description=(
        'Publish tasks for asynchronous processing and inspect '
        'failed messages in a dead-letter queue.'
    ),
    version='1.0.0',
    lifespan=lifespan,
)

app.include_router(router)

@app.get('/health', tags=['health'])
def health() -> dict[str, str]:
    return {'status': 'ok'}

