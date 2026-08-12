from typing import Any
from pydantic import BaseModel, Field


class Event(BaseModel):

    body: dict[str, Any] = Field(
        ...,
        examples=[
            {
                'action': 'generate_report',
                'user_id': 'user_123',
                'format': 'pdf'
            }
        ]
    )

    headers: dict[str, str] = Field(
        ...,
        examples=[
            {
                'department': 'finance',
                'priority': 'high'
            }
        ]
    )





