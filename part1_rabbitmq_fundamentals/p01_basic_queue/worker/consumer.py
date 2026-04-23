import sys, json , time
from api.rabbitmq_connection import RabbitMQConnection

def main():
    rabbitmq = RabbitMQConnection()
    channel = rabbitmq.connect()

    queue_name = 'tasks'
    channel.queue_declare(queue=queue_name, durable=True)

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

