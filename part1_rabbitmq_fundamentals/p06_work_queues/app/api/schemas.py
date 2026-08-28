from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class TaskCreateRequest(BaseModel):

    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra='forbid',
    )

    task_name: str = Field(
        ...,
        min_length=3,
        max_length=100,
        examples=['generate-monthly-report'],
        description='Descriptive name of the task.',
    )

    duration_seconds: int = Field(
        default=1,
        ge=1,
        le=30,
        examples=[5],
        description='Simulated task processing duration in seconds.',
    )



class TaskQueuedResponse(BaseModel):

    model_config = ConfigDict(extra='forbid')

    task_id: UUID
    task_name: str
    duration_seconds: int
    status: Literal['queued']
    created_at: datetime