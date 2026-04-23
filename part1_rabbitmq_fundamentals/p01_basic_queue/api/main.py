from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from producer import send_to_queue


app = FastAPI()


class Task(BaseModel):
    name: str
    body: str


@app.post('/send-task/')
def send_task(task: Task, background_tasks: BackgroundTasks):
    background_tasks.add_task(send_to_queue, task.dict())
    return {'status': 'Task sent', 'task': task}