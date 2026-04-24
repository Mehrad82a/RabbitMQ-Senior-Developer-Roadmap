import sys, time, json
from api.rabbitmq_connection import RabbitMQConnection




def main():
    rabbitmq = RabbitMQConnection()
    channel = rabbitmq.connect()

    channel.exchange_declare(exchange='direct_logs', exchange_type='direct')

    queue_name = 'error_logs'

    # Each worker connects to its direct queue
    channel.queue_declare(queue=queue_name, durable=True)

    # Bind queue to exchange
    channel.queue_bind(exchange='direct_logs', queue=queue_name, routing_key='error')

    print(f"[ERROR Service] Waiting for error messages on queue: '{queue_name}'...")

    def callback(ch, method, properties, body):
        data = json.loads(body)

        print(f'[ERROR Service] Received error; sending message for: {data}')
        time.sleep(3)   # For work simulation
        print(f'[ERROR Service] Done')

        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(queue=queue_name, on_message_callback=callback)
    channel.start_consuming()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        sys.exit(0)

