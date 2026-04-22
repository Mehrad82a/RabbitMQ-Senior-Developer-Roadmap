import pika, sys, os , json , time
from part1_rabbitmq_fundamentals.p01_basic_queue.api.rabbitmq_connection import RabbitMQConnection



rabbitmq = RabbitMQConnection()
channel = rabbitmq.get_channel()

def main():
    connection = None
    while not connection:
        try:
            print('Connecting to RabbitMQ...')
            connection = rabbitmq.get_connection()
            print('Connected to RabbitMQ successfully.')
        except pika.exceptions.AMQPConnectionError:
            print('Failed to connect to RabbitMQ. Retrying in 5 seconds...')
            time.sleep(3)

    queue_name = 'tasks'
    channel.queue_declare(queu=queue_name, durable=True)

    def callback(ch, method, properties, body):
        data = json.loads(body)

        print(f'Worker received: {data}')
        time.sleep(3)   # For work simulation
        print(f'Worker task completed')

        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=queue_name, on_message_callback=callback)

    print('waiting for message...')
    channel.start_consuming()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        sys.exit(0)

