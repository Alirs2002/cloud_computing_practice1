import pika 
import psycopg2
import boto3
from botocore.exceptions import NoCredentialsError, ClientError
import requests
from io import BytesIO
from PIL import Image
from urllib.parse import quote

import requests

import requests

API_URL = "https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-large"
headers = {"Authorization": "Bearer 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"}

def query(filename):
    
    response = requests.post(API_URL, headers=headers, data=filename)
    return response.json()

output = query("cats.jpg")


cloud_rabbit_url = "amqps://flqnvhuf:NhsiXNWrN1JoeFpopD01vT47hg2NPMM3@prawn.rmq.cloudamqp.com/flqnvhuf"

postgres_host = "fitz-roy.liara.cloud"
postgres_database = "cloud_practice1"
postgres_user = "root"
postgres_password = "sPp1eeaw0L78YduOFKIKXdbW"






LIARA_ENDPOINT = "https://storage.c2.liara.space"
LIARA_BUCKET_NAME = "cloud-computing-practice1-40031022"
LIARA_ACCESS_KEY = "p1acqtur7hl54lhm"
LIARA_SECRET_KEY = "3d85581f-1434-4f7c-8250-d0c000d7b69b"

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
def get_postgres_connection():
    connection_db = psycopg2.connect(database=postgres_database,host=postgres_host,user=postgres_user,password=postgres_password,port=33746)
    return connection_db





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

def download_image_from_s3(url):
    try:
        session = boto3.session.Session()
        s3_client = session.client(
            service_name='s3',
            aws_access_key_id=LIARA_ACCESS_KEY,
            aws_secret_access_key=LIARA_SECRET_KEY,
            endpoint_url=LIARA_ENDPOINT
        )

     
        object_key = url.split(f"{LIARA_ENDPOINT}/{LIARA_BUCKET_NAME}/")[-1]
        object_key = quote(object_key) 

        print(f"Attempting to download image with object key: {object_key}")

        response = s3_client.get_object(Bucket=LIARA_BUCKET_NAME, Key=object_key)
        image_data = response['Body'].read()

        image = Image.open(BytesIO(image_data))
        image.show() 
        return image

    except (NoCredentialsError, ClientError) as e:
        print(f"Error downloading image: {e}")
        return None
    
def consume_id():
    connection = get_connection()
    channel = connection.channel()

    channel.queue_declare(queue="request_queue")

    def callback(ch, method, properties, body):
        request_id = properties.headers.get('request_id', 'No request ID')
        print(f"Received message: {body.decode()}")
        print(f"Request ID: {request_id}")
        try:
            postgres_connection = get_postgres_connection()
            cursor = postgres_connection.cursor()

            cursor.execute("SELECT prev_url FROM cloud_app_request_data WHERE \"ID\" = %s;", (int(request_id),))
            result = cursor.fetchone() 

            if result:
                prev_url = result[0] 
                print(f"Previous URL: {prev_url}")
                url_image = "https://cloud-computing-practice1-40031022.storage.c2.liara.space/"+prev_url
                img = download_image_from_s3(prev_url)
                img_byte_arr = BytesIO()
                img.save(img_byte_arr, format='PNG')  
                img_byte_arr.seek(0) 

                caption = query(img_byte_arr)[0]["generated_text"]
                cursor.execute(
                    "UPDATE cloud_app_request_data SET caption = %s WHERE \"ID\" = %s;",
                    (caption, int(request_id))
                )
                postgres_connection.commit() 


                cursor.execute(
                            "UPDATE cloud_app_request_data SET caption = %s, status = %s WHERE \"ID\" = %s;",
                            (caption, 'ready', int(request_id))
                        )
                postgres_connection.commit() 
                print(f"Caption stored: {caption}")
            
            else:
                print("No row found with the given request ID.")

            cursor.close()
            postgres_connection.close()
        except Exception as e:
            print(f"An error occurred while querying the database: {e}")

        

    channel.basic_consume(queue="request_queue", on_message_callback=callback, auto_ack=True)

    print('Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()



if __name__ == "__main__":
    store_id_rabbit('12')
    postgres_connection = get_connection()

    consume_id()
