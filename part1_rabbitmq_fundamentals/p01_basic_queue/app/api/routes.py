from fastapi import APIRouter, BackgroundTasks, status
from app.api.schemas import Task
from app.services.task_service import TaskService


router = APIRouter()


@router.post('/send-task/', status_code=status.HTTP_202_ACCEPTED)

def send_task(task: Task, background_tasks: BackgroundTasks):
    background_tasks.add_task(TaskService.create_task, task.model_dump())
    return {{
        'message': 'Task accepted',
        'status': 'accepted'
    }}