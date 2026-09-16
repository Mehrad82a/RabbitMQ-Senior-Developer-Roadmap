from functools import lru_cache
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


@lru_cache(maxsize=1)
def get_task_service() -> TaskService:
    return TaskService()


@router.post(
    '/create',
    response_model=TaskResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary='Publish a task to the auto ack or manual ack queue',
    responses={
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            'model': ErrorResponse,
            'description': 'The task could not be handed over to RabbitMQ.',
        }
    }
)
def publish_task(payload: TaskRequest, task_service: TaskService = Depends(get_task_service)) -> TaskResponse:
    """
    Publishes a task and returns as soon as the broker accepts it.
    202 is the honest status code here: the task is queued, not processed.
    """

    try:
        result = task_service.send_task(
            mode=payload.mode,
            task_name=payload.task_name,
            processing_outcome=payload.processing_outcome.value,
        )


    except TaskPublishError as exc:
        logger.exception(
            f'[api] Task publishing failed: task_name=<{payload.task_name}> | '
            f'mode=<{payload.mode}>'
        )

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail='The task could not be published. Please retry.',
        ) from exc



    logger.info(
        f'[api] Task accepted: task_id=<{result["task_id"]}> | '
        f'mode=<{result["mode"]}> | queue=<{result["queue_name"]}>'
    )

    return TaskResponse(**result)













