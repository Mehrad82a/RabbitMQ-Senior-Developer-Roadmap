from pydantic import BaseModel
from typing import Dict, Any, Literal


class Job(BaseModel):
    job: str
    body: Dict[str, Any]
    headers: Dict[Literal['department', 'priority'], str]


