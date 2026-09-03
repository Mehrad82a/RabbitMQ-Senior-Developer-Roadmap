from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status



from app.api.schemas import MessagePublishRequest, MessagePublishResponse
from app.core.logger import logger
from app.services.persistence_service import PersistencePublishError, PersistenceService




router = APIRouter(
    tags=['Message Persistence'],
)


def get_persistence_service() -> PersistenceService:
    return PersistenceService()


PersistenceServiceDependency = Annotated[
    PersistenceService,
    Depends(get_persistence_service),
]


@router.post(
'/send-message',
    response_model=MessagePublishResponse,
    status_code=status.HTTP_202_ACCEPTED
)
def enqueue_message(message: MessagePublishRequest, persistence_service: PersistenceServiceDependency) -> MessagePublishResponse:
    try:
        pass



    except PersistencePublishError as exc:
        pass


