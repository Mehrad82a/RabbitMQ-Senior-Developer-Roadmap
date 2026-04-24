import pika, sys, time, json
from api.rabbitmq_connection import RabbitMQConnection





def main():
    rabbitmq = RabbitMQConnection()
    channel = rabbitmq.connect()

    channel.exchange_declare(exchange='logs', exchange_type='fanout')

    # Each subscriber gets a unique queue (by exclusive=True)
    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue

    # Bind queue to exchange
    channel.queue_bind(exchange='logs', queue=queue_name)
    print(f"[SMS Service] Waiting for events on queue: '{queue_name}'...")

    def callback(ch, method, properties, body):
        data = json.loads(body)

        print(f'[SMS Service] Received event; sending email for: {data}')
        time.sleep(3)  # For work simulation
        print(f'[SMS Service] Done')

        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(queue=queue_name, on_message_callback=callback)
    channel.start_consuming()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        sys.exit(0)