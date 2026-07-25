import time
from app.core.logger import logger



class LogService:

    @staticmethod
    def process_log(data: dict):
        level = data.get('level')
        message = data.get('message')

        if level == 'error':
            logger.info(f'[ROUTER] Sending alert for error: {message}')

        elif level == 'warning':
            logger.info(f'[ROUTER] Logging warning: {message}')

        elif level == 'info':
            logger.info(f'[ROUTER] Storing info: {message}')


    @staticmethod
    def process_info(data: dict) -> dict:
        logger.info(f'[Info Worker] Received info; sending message for: {data}')

        time.sleep(3)  # For work simulation

        result = {
            'message_id': data.get('message_id'),
            'worker': 'info',
            'payload': data
        }

        logger.info('[Info worker] Done')
        return result



    @staticmethod
    def process_warning(data: dict) -> dict:
        logger.info(f'[Warning Worker] Received warning; sending message for: {data}')

        time.sleep(3)  # For work simulation

        result = {
            'message_id': data.get('message_id'),
            'worker': 'warning',
            'payload': data
        }

        logger.info('[Warning worker] Done')
        return result



    @staticmethod
    def process_error(data: dict) -> dict:
        logger.info(f'[Error Worker] Received error; sending message for: {data}')

        time.sleep(3)   # For work simulation


        result = {
            'message_id': data.get('message_id'),
            'worker': 'error',
            'payload': data
        }

        logger.info('[Error worker] Done')
        return result


