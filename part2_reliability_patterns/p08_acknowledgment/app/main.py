from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from typing import Any

from fastapi import FastAPI

from app.api.routes import get_task_service, router
from app.core.logger import get_logger
from app.core.rabbitmq import RabbitMQConnection


logger = get_logger(__name__)



@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    logger.info('[api] Application starting...')
    yield

    logger.info('[api] Application shutting down...')
    RabbitMQConnection().close()
    get_task_service.cache_clear()



app = FastAPI(
    title='P08 - Message Acknowledgment',
    description=(
        'Publishes tasks to an auto ack queue or a manual ack queue so the two '
        'acknowledgement strategies can be compared under the same failures.'
    ),
    version='1.0.0',
    lifespan=lifespan,

)

app.include_router(router)

app.get('/health', tags=['health'])
def health() -> dict[str, str]:
    return {'status': 'ok'}


