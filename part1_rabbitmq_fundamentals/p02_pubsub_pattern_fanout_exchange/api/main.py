from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from producer import publish_event


app = FastAPI()


class Event(BaseModel):
    title: str
    body: str


@app.post("/broadcast-event")
def broadcast_event(event: Event, background_tasks: BackgroundTasks):
    background_tasks.add_task(publish_event, event.dict())
    return {'status': 'Broadcast sent', 'event': event}