import pika, json

from api.rabbitmq_connection import RabbitMQConnection


def publish(job: dict):
    rabbitmq = RabbitMQConnection()
    channel = rabbitmq.connect()

    channel.exchange_declare(
        exchange='jobs_exchange',
        exchange_type='direct',
        durable=True
    )

    routing_key = f"{job['job_type']}.job"

    message = json.dumps(job)

    channel.basic_publish(
        exchange='jobs_exchange',
        routing_key=routing_key,
        body=message,
        properties=pika.BasicProperties(
            delivery_mode=2,
        )
    )

    print(f'Published: {routing_key}')


