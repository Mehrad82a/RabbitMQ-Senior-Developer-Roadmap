from pydantic import BaseModel, Field



class Event(BaseModel):
    routing_key: str = Field(
        ...,
        examples=['user.created']
    )


    message: str = Field(
        ...,
        min_length=1,
        examples=['New user registered']
    )


