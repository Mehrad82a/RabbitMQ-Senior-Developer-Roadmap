import time
from app.core.logger import logger
from app.producer.producer import publish

class TaskService:


    @staticmethod
    def create_task(task_data: dict) -> dict:
        task_payload = {
            'payload': task_data,
            'created_at': time.time(),
            'status': 'queued'
        }

        published = publish(task_payload)

        if not published:
            raise RuntimeError('Failed to publish task')

        logger.info(f'Task queued successfully: {task_payload}')



    @staticmethod
    def process_task(task: dict) -> dict:
        logger.info(f'Worker received task: {task}')

        time.sleep(3)   # For task simulation

        result = {
            'task_id': task.get('id'),
            'status': 'Completed',
        }

        logger.info(f'Task processed successfully: {result}')
        return result




