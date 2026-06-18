from pydantic import BaseModel
from typing import Dict, Any


class Job(BaseModel):
    job_type: str
    title: str
    payload: Dict[str, Any]


