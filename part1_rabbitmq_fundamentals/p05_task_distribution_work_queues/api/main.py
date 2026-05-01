from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from producer import publish_task


app = FastAPI()


class Task(BaseModel):
    title: str
    message: str


@app.post('/create-task')
def create_task(task: Task, background_tasks: BackgroundTasks):
    background_tasks.add_task(publish_task, task.dict())
    return {'status': 'Task created', 'task': task.title}



@app.post('/create-async-task')
async def create_async_task(task: Task, background_tasks: BackgroundTasks):
    background_tasks.add_task(publish_task, task.dict())
    return {'status': 'Async task created', 'task': task.title}