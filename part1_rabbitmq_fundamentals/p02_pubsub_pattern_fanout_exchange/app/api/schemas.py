from pydantic import BaseModel, Field


class Event(BaseModel):
    user_id: str = Field(
        ...,
        examples=['user_123']
    )

    title: str = Field(
        ...,
        examples=['Payment Successful']
    )

    message: str = Field(
        ...,
        examples=['Your invoice has been paid successfully.']
    )