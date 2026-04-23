import pika, sys, time, json
from part1_rabbitmq_fundamentals.p02_pubsub_pattern_fanout_exchange.api.rabbitmq_connection import RabbitMQConnection



rabbitmq = RabbitMQConnection()
channel = rabbitmq.get_channel()

def main():
    connection = None
    while not connection:
        try:
            print('[EMAIL Service] Connecting to RabbitMQ...')
            connection = rabbitmq.get_connection()
            print('[EMAIL Service] Connected to RabbitMQ successfully.')
        except pika.exceptions.AMQPConnectionError:
            print('[EMAIL Service] failed to connect to RabbitMQ. Retrying in 3 seconds...')
            time.sleep(3)

    channel.exchange_declare(exchange='logs', exchange_type='fanout')

    # Each subscriber gets a unique queue (by exclusive=True)
    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue

    # Bind queue to exchange
    channel.queue_bind(exchange='logs', queue=queue_name)
    print(f"[EMAIL Service] Waiting for events on queue: '{queue_name}'...")

    def callback(ch, method, properties, body):
        data = json.loads(body)

        print(f'[EMAIL Service] Received event; sending email for: {data}')
        time.sleep(3)   # For work simulation
        print(f'[EMAIL Service] Done')

        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(queue=queue_name, on_message_callback=callback)
    channel.start_consuming()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        sys.exit(0)
