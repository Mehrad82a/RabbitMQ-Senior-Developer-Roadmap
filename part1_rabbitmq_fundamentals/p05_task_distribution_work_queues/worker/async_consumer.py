import sys, json, asyncio
from api.rabbitmq_connection import RabbitMQConnection



async def process_task(task):
    print(f'[Async Worker] Processing task {task}')
    await asyncio.sleep(3)   # For work simulation
    print(f'[Async Worker] Done')


def main():
    rabbitmq = RabbitMQConnection()
    channel = rabbitmq.connect()


    channel.queue_declare(queue='work_queue', durable=True)
    channel.basic_qos(prefetch_count=1)   # Fair dispatch


    print('[Async Worker] Waiting for tasks...')


    async def handle_task(ch, method, properties, body):
        task = json.loads(body)

        print(f'[Async Worker] Received task: {task}')

        try:
            await process_task(task)
            print(f'[Async Worker] Done processing')
            ch.basic_ack(delivery_tag=method.delivery_tag)

        except Exception as e:
            print(f'[Async Worker] Error processing task: {e}')
            ch.basic_ack(delivery_tag=method.delivery_tag, requeue=False)


    def callback(ch, method, properties, body):
        asyncio.run(handle_task(ch, method, properties, body))

    channel.basic_consume(queue='work_queue', on_message_callback=callback)
    channel.start_consuming()



if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        sys.exit(0)


