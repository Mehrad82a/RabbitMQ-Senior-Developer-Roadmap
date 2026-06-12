from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any
from producer import broadcast_event


app = FastAPI()

class Event(BaseModel):
    """
    routing key must be in one of these formats:
    user.<anything>
    order.<anything>
    <anything>.error
    """
    routing_key: str
    message: Dict[str, Any]



"""
API request body example:

{
  "routing_key": "user.signup",
  "message": {
    "event_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
    "timestamp": "2026-04-27T20:35:15Z",
    "data": {
      "user_id": 456,
      "username": "new_user_123",
      "email": "newuser@example.com",
      "signup_date": "2026-04-27T20:35:15Z"
    }
  }
}
"""

@app.post('/publish')
def broadcast_message(event: Event, background_tasks: BackgroundTasks):
    background_tasks.add_task(broadcast_event, routing_key=event.routing_key, message=event.message)
    return {'status': 'Event published', 'routing_key': event.routing_key, 'message': event.message}