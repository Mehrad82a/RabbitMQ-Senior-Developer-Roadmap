from fastapi import APIRouter, Depends, HTTPException, status

from app.api.schemas import ErrorResponse, TaskRequest, TaskResponse
from app.core.logger import get_logger
from app.services.exceptions import TaskPublishError
from app.services.task_service import TaskService


logger = get_logger(__name__)


router = APIRouter(
    prefix='/tasks',
    tags=['tasks']
)


def get_task_service() -> TaskService:
    return TaskService()


@router.post(
    '/create',
    response_model=TaskResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary='Publish a task for asynchronous processing',
    responses={
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            'model': ErrorResponse,
            'description': 'The task could not be published to RabbitMQ.',
        }
    },
)
def publish_task(
        payload: TaskRequest,
        task_service: TaskService = Depends(get_task_service),
) -> TaskResponse:

    try:
        result = task_service.send_task(
            task_name=payload.task_name,
        )

    except TaskPublishError as exc:
        logger.exception(
            '[api] Task publishing failed: '
            f'task_name=<{payload.task_name}>'
        )

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail='The task could not be published. Please retry.',
        ) from exc



    logger.info(
        '[api] Task accepted: '
        f'task_id=<{result["task_id"]}> | '
        f'queue=<{result["queue_name"]}>'
    )

    return TaskResponse(**result)
