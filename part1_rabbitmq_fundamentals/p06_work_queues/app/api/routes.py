from app.core.logger import logger
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status


from app.api.schemas import TaskCreateRequest, TaskQueuedResponse
from app.services.task_service import TaskPublishError, TaskService



router = APIRouter(
    tags=['Tasks']

)

def get_task_service() -> TaskService:
    return TaskService()


TaskServiceDependency = Annotated[
    TaskService,
    Depends(get_task_service)
]



@router.post(
    '/send-task',
    response_model=TaskQueuedResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def enqueue_task(task: TaskCreateRequest, task_service: TaskServiceDependency) -> TaskQueuedResponse:
    try:
        queued_task = task_service.enqueue_task(
            task.task_name,
            duration_seconds=task.duration_seconds,
        )

        return TaskQueuedResponse.model_validate(queued_task)


    except TaskPublishError as exc:
        logger.exception('Failed to enqueue task: task_name=%s', task.task_name)

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail='The task could not be queued. Please try again later.'
        ) from exc


