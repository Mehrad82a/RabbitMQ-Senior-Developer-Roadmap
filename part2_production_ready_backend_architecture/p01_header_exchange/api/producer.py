import pika, os, json

from api.rabbitmq_connection import RabbitMQConnection



def publish(job: dict):
    rabbitmq = RabbitMQConnection()
    channel = rabbitmq.connect()

    channel.exchange_declare(
        exchange='department_exchange',
        exchange_type='headers',
        durable=True
    )

    message = json.dumps(job)

    priority = job.get('headers', {}).get('priority', '')

    channel.basic_publish(
        exchange='department_exchange',
        routing_key='',
        body=message,
        properties=pika.BasicProperties(
            headers={
                'department': 'finance',
                'priority': priority
            },
            delivery_mode=2,
        )
    )

    print('Message published')


