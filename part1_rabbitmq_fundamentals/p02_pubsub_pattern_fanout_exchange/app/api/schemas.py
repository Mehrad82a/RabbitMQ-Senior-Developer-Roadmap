from pydantic import BaseModel


class Event(BaseModel):
    user_id: str
    title: str
    message: str