from fastapi import APIRouter, BackgroundTasks, status
from app.api.schemas import Event
from app.services.broadcast_service import BroadcastService


router = APIRouter()


@router.post('/broadcast-event', status_code=status.HTTP_202_ACCEPTED)
def broadcast_event(event: Event, background_tasks: BackgroundTasks):
    background_tasks.add_task(BroadcastService.broadcast_message, event.dict())
    return {
        'message': 'Notification sent successfully',
        'status': 'sent'
    }