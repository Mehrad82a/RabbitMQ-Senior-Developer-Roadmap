from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel


app = FastAPI()


class Event(BaseModel):
    title: str
    body: str


@app.post("/broadcast-event")
def broadcast_event(event: Event, background_tasks: BackgroundTasks):
    return {'status': 'Broadcast sent', 'event': event.dict()}