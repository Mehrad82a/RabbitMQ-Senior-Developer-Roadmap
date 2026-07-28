from fastapi import APIRouter, BackgroundTasks

from api.schemas import Job
from api.producer import publish


router = APIRouter()

"""
API request body example:

Normal Priority Jobs:

{
  "job": "Quarterly Report",
  "body": {
    "invoice_id": 101,
    "customer": "Mehrad",
    "amount": 158750,
    "currency": "USD"
  },
  "headers": {
    "department": "finance",
    "priority": "normal"
  }
}


High Priority Jobs

{
  "job": "Quarterly Report",
  "body": {
    "invoice_id": 102,
    "customer": "Alice",
    "amount": 12500,
    "currency": "USD"
  },
  "headers": {
    "department": "finance",
    "priority": "high"
  }
}

"""


@router.post('/publish')
async def publish_job(job: Job, background_tasks: BackgroundTasks):
    background_tasks.add_task(publish, job.dict())
    return {
        'status': 'published',
        'job': job.dict(),

    }