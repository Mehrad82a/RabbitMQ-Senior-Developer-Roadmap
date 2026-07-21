from pydantic import BaseModel


class Task(BaseModel):
    name: str
    body: str