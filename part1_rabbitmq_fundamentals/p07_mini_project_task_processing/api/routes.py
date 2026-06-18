from fastapi import APIRouter, BackgroundTasks

from api.schemas import Job
from api.producer import publish



router = APIRouter()


@router.post(f'/create-job')
async def create_job(job: Job, background_tasks: BackgroundTasks):
    background_tasks.add_task(publish, job.dict())
    return {
        'status': 'queued',
        'job_type': job.job_type,
        'job_title': job.title,
    }


