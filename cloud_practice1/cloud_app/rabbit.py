import pika
import pika.connection

cloud_rabbit_url = "amqps://flqnvhuf:NhsiXNWrN1JoeFpopD01vT47hg2NPMM3@prawn.rmq.cloudamqp.com/flqnvhuf"

def get_connection():
    url_parts = cloud_rabbit_url.split('@')
    credentials = url_parts[0].replace('amqps://', '').split(':')
    host_vhost = url_parts[1].split('/')
    
    username = credentials[0]
    password = credentials[1]
    host = host_vhost[0]
    vhost = host_vhost[1]

    parameters = pika.ConnectionParameters(
        host=host,
        virtual_host=vhost,
        credentials=pika.PlainCredentials(username, password),
        port=5672  
    )
    return pika.BlockingConnection(parameters=parameters)

def store_id_rabbit(request_id):
    connection = get_connection()
    channel = connection.channel()

    channel.queue_declare(queue="request_queue")
    channel.basic_publish(
        exchange='',
        routing_key='request_queue',
        body='Your message body',
        properties=pika.BasicProperties(
            headers={'request_id': request_id}
        )
    )
    print(f"The request_id '{request_id}' has been stored.")
    connection.close()






def consume_id():
    try:
        connection = get_connection()
        channel = connection.channel()

        channel.queue_declare(queue="request_queue")

        def callback(ch, method, properties, body):
            print(f"Received ID: {body.decode()}")

        channel.basic_consume(queue="request_queue", auto_ack=True, on_message_callback=callback)
        print("Waiting for messages...")
        channel.start_consuming()
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        if connection:
            connection.close()