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
        published_message = persistence_service.enqueue_message(
            content=message.content,
            queue_durable=message.queue_durable,
            message_persistent=message.message_persistent,
            publisher_confirm=message.publisher_confirm,
        )

        return MessagePublishResponse.model_validate(published_message)


    except PersistencePublishError as exc:
        logger.exception(
            f'Failed to enqueue message: '
            f'queue_durable={message.queue_durable} - '
            f'message_persistent={message.message_persistent} - '
            f'publisher_confirm={message.publisher_confirm}'

        )

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail='RabbitMQ did not accept the message. Please try again later'
        ) from exc


