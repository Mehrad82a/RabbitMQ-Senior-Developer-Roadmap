import sys, time, json
from api.rabbitmq_connection import RabbitMQConnection



def main():
    rabbitmq = RabbitMQConnection()
    channel = rabbitmq.connect()

    channel.queue_declare(queue='work_queue', durable=True)
    channel.basic_qos(prefetch_count=1)   # Fair dispatch

    print('[Worker] Waiting for tasks...')


    def callback(ch, method, properties, body):
        task = json.loads(body)

        print(f'[Worker] received task: {task}')
        time.sleep(3)   # For work simulation
        print('[Worker] Done')

        ch.basic_ack(delivery_tag=method.delivery_tag)


    channel.basic_consume(queue='work_queue', on_message_callback=callback)
    channel.start_consuming()



if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        sys.exit(0)
