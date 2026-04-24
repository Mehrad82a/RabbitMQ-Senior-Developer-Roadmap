from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from typing import Literal
from producer import publish_message


app = FastAPI()




class Message(BaseModel):
    """
    level must be one of these values:
    info - warning - error
    """
    level: str
    body: str


@app.post('/log')
def broadcast_message(message: Message, background_tasks: BackgroundTasks):
    background_tasks.add_task(publish_message, level=message.level, body=message.body)
    return {'status': 'Message sent', 'level': message.level, 'message': message.body}
