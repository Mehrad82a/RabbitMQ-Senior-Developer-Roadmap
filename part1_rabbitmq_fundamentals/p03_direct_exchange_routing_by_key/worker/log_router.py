import sys, json, time
from api.rabbitmq_connection import RabbitMQConnection


def process_log(data):
    level = data.get('level')
    body = data.get('body')

    if level == 'error':
        print(f'[ROUTER] Sending alert for error: {body}')
    elif level == 'warning':
        print(f'[ROUTER] Logging warning: {body}')
    elif level == 'info':
        print(f'[ROUTER] Storing info: {body}')


def main():
    rabbitmq = RabbitMQConnection()
    channel = rabbitmq.connect()

    channel.exchange_declare(exchange='direct_logs', exchange_type='direct')

    queue_name = 'router_logs'

    channel.queue_declare(queue=queue_name, durable=True)

    for key in ['info', 'warning', 'error']:
        channel.queue_bind(exchange='direct_logs', queue=queue_name, routing_key=key)

    print('[ROUTER] Listening to all log levels...')

    def callback(ch, method, properties, body):
        data = json.loads(body)

        print(f'[ROUTER] Received message: {data}')
        process_log(data)
        time.sleep(3)  # For work simulation
        print(f'[ROUTER] Done')

        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(queue=queue_name, on_message_callback=callback)
    channel.start_consuming()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        sys.exit(0)
