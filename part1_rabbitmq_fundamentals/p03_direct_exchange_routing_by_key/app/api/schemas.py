from pydantic import BaseModel




class Message(BaseModel):
    """
    level must be one of these values:
    info - warning - error
    """
    level: str
    message: str
