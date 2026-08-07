from pydantic import BaseModel, Field
from typing import Dict, Any


class Task(BaseModel):
    name: str = Field(
        ...,
        examples=['generate_report']
    )
    body: Dict[str, Any] = Field(
        ...,
        examples=[
            {
                'format': 'pdf',
                'user_id': 'user_123',
                'department': 'finance'
            }
        ]
    )