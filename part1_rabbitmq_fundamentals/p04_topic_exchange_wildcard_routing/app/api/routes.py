from fastapi import APIRouter, BackgroundTasks, status


from app.api.schemas import Event
from app.services.event_service import EventService


router = APIRouter()

@router.post('/send-event', status_code=status.HTTP_202_ACCEPTED)
def send_event(event: Event, background_tasks: BackgroundTasks):
    background_tasks.add_task(EventService.send_event, event.dict())
    return {
        'message': 'Event accepted',
        'status': 'queued'
    }



