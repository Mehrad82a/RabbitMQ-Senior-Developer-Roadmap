from pydantic import BaseModel, Field




class Message(BaseModel):
    """
    level must be one of these values:
    info - warning - error
    """
    level: str = Field(
        ...,
        examples=['warning']
    )

    message: str = Field(
        ...,
        examples=['CPU usage exceeded 90%']
    )
