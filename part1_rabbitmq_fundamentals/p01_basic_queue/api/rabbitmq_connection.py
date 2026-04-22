import os, pika

class RabbitMQConnection:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.__init__()
        return cls._instance


    def __init__(self):
        rabbitmq_host = os.getenv("RABBITMQ_HOST", "rabbitmq")
        rabbitmq_port = int(os.getenv("RABBITMQ_PORT", 5672))
        rabbitmq_user = os.getenv("RABBITMQ_USER", "admin_user")
        rabbitmq_pass = os.getenv("RABBITMQ_PASS", "admin_pass")

        credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_pass)
        params = pika.ConnectionParameters(
            host=rabbitmq_host,
            port=rabbitmq_port,
            credentials=credentials
        )
        self.connection = pika.BlockingConnection(params)
        self.channel = self.connection.channel()

    def get_channel(self):
        return self.channel

    def get_connection(self):
        return self.connection

