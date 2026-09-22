from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator



AckMode = Literal['auto', 'manual']


class TaskRequest(BaseModel):
    """
     Incoming request describing which task to publish and how it should behave.
    """

    model_config = ConfigDict(
        extra='forbid',
        json_schema_extra={
            'examples': [
                {
                    'task_name': 'generate_invoice',
                    'mode': 'manual',
                }
            ]
        }
    )

    task_name: str = Field(
        min_length=1,
        max_length=200,
        description='The name of the task to publish.',
    )

    mode: AckMode = Field(
        default='manual',
        description='Acknowledgement mode that decides the target queue.',
    )

    @field_validator('task_name')
    @classmethod
    def validate_task_name(cls, value: str) -> str:
        task_name = value.strip()

        if not task_name:
            raise ValueError('Task name must not be blank.')

        return task_name




class TaskResponse(BaseModel):
    """
    Confirmation that the task was handed over to RabbitMQ.
    """

    task_id: str
    task_name: str
    created_at: str
    mode: AckMode
    queue_name: str
    status: str




class ErrorResponse(BaseModel):
    """Error body returned when a task cannot be published."""

    detail: str















