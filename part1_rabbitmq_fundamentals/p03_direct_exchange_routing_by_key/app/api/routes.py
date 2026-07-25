from fastapi import APIRouter, BackgroundTasks, status
from app.services.message_service import MessageService
from app.api.schemas import Message

router = APIRouter()



@router.post('/send-log-message')
def broadcast_message(message: Message, background_tasks: BackgroundTasks):
    background_tasks.add_task(MessageService.send_message, level=message.level, message=message.message)
    return {
        'status': 'sent',
        'level': message.level,
        'message': message.body
    }