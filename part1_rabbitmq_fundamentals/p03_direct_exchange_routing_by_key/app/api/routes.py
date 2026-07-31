from fastapi import APIRouter, BackgroundTasks, status
from app.services.message_handler import MessageService
from app.api.schemas import Message

router = APIRouter()



@router.post('/send-log')
def send_message(message: Message, background_tasks: BackgroundTasks):
    background_tasks.add_task(MessageService.send_message, level=message.level, message=message.message)
    return {
        'status': 'sent',
        'level': message.level,
        'message': message.message
    }