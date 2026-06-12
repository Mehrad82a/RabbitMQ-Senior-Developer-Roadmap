from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from producer import publish


app = FastAPI()

class Job(BaseModel):
    title: str
    description: str

@app.post('/create-job')
def create_job(job: Job, background_tasks: BackgroundTasks):
    background_tasks.add_task(publish, job.dict())
    return {'success':True, 'message': 'Job successfully created and queued', 'job': job.dict()}




