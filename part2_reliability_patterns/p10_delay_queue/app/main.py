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
    title='P10 - Delay Queue',
    description=(
        'Publish tasks for immediate or delayed asynchronous processing '
        'using message TTL and dead-letter routing.'
    ),
    version='1.0.0',
    lifespan=lifespan,
)


app.include_router(router)



@app.get('/health', tags=['health'])
def health() -> dict[str, str]:
    return {'status': 'ok'}



