from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator



class TaskRequest(BaseModel):
    """
    Information supplied by the client when creating a task.
    """

    model_config = ConfigDict(
        extra='forbid',
        json_schema_extra={
            'examples': [
                {
                    'task_name': 'generate-report',
                }
            ]
        },
    )

    task_name: str = Field(
        min_length=1,
        max_length=200,
        description='Name of the task to process.',
    )

    @field_validator('task_name')
    @classmethod
    def validate_task_name(cls, value: str) -> str:
        cleaned = value.strip()

        if not cleaned:
            raise ValueError('Task name must not be blank.')

        return cleaned



class TaskResponse(BaseModel):
    """
    Confirmation that RabbitMQ accepted the task for delivery.
    """
    task_id: str
    task_name: str
    created_at: str
    queue_name: str
    status: Literal['queued']



class ErrorResponse(BaseModel):
    """
    Error returned when the task cannot be published.
    """
    detail: str