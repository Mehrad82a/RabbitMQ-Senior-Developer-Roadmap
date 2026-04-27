import os, pika, time

class RabbitMQConnection:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            # Initializes configuration only, not the connection
            cls._instance._initialized = False
        return cls._instance


    def __init__(self):
        if self._initialized: return
        self.rabbitmq_host = os.getenv("RABBITMQ_HOST", "rabbitmq")
        self.rabbitmq_port = int(os.getenv("RABBITMQ_PORT", 5672))
        self.rabbitmq_user = os.getenv("RABBITMQ_USER", "admin_user")
        self.rabbitmq_pass = os.getenv("RABBITMQ_PASS", "admin_pass")

        self.connection = None
        self.channel = None
        self._initialized = True


    def connect(self):
        credentials = pika.PlainCredentials(self.rabbitmq_user, self.rabbitmq_pass)
        params = pika.ConnectionParameters(
            host=self.rabbitmq_host,
            port=self.rabbitmq_port,
            credentials=credentials
        )

        while not self.connection or self.connection.is_closed:
            try:
                print('Connecting to RabbitMQ...')
                self.connection = pika.BlockingConnection(params)
                self.channel = self.connection.channel()
                print('Connected successfully.')

            except pika.exceptions.AMQPConnectionError:
                print('Failed to connect to RabbitMQ. Retrying in 5 seconds...')
                time.sleep(5)

        return self.channel


