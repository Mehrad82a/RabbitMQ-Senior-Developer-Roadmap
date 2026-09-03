from datetime import datetime
from typing import Literal
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field





class MessagePublishRequest(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra='forbid',
    )

    content: str = Field(
        ...,
        min_length=1,
        max_length=300,
        examples=['Message persistence experiment'],
    )

    queue_durable: bool = Field(
        ...,
        examples=[True],
        description='Determines whether the queue metadata survives a broker restart.',

    )

    message_persistent: bool = Field(
        ...,
        examples=[True],
        description='Requests RabbitMQ to persist the message to disk.',
    )

    publisher_confirm: bool = Field(
        default=False,
        examples=[True],
        description='Enables broker confirmation for this publish operation.',
    )





class MessagePublishResponse(BaseModel):
    model_config = ConfigDict(extra='forbid')

    message_id: UUID
    content: str
    queue_name: str
    queue_durable: bool
    message_persistent: bool
    publisher_confirm: bool
    broker_confirmed: bool | None
    status: Literal['published']
    created_at: datetime




