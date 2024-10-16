import time
import requests
import psycopg2
import boto3
from botocore.exceptions import NoCredentialsError, ClientError
from PIL import Image
import io
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

API_URL = "https://api-inference.huggingface.co/models/ZB-Tech/Text-to-Image"
headers = {"Authorization": "Bearer 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"}

postgres_host = "fitz-roy.liara.cloud"
postgres_database = "cloud_practice1"
postgres_user = "root"
postgres_password = "sPp1eeaw0L78YduOFKIKXdbW"

LIARA_ENDPOINT = "https://storage.c2.liara.space"
LIARA_BUCKET_NAME = "cloud-computing-practice1-40031022"
LIARA_ACCESS_KEY = "p1acqtur7hl54lhm"
LIARA_SECRET_KEY = "3d85581f-1434-4f7c-8250-d0c000d7b69b"

def get_postgres_connection():
    return psycopg2.connect(database=postgres_database, host=postgres_host, user=postgres_user, password=postgres_password,port=33746)

def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.content

def upload_image_to_s3(image_bytes, object_key):
    try:
        session = boto3.session.Session()

        s3_client = session.client(
            service_name='s3',
            aws_access_key_id=LIARA_ACCESS_KEY,
            aws_secret_access_key=LIARA_SECRET_KEY,
            endpoint_url=LIARA_ENDPOINT
        
        )
        s3_client.put_object(Bucket=LIARA_BUCKET_NAME, Key=object_key, Body=image_bytes)
        return f"{LIARA_ENDPOINT}/{LIARA_BUCKET_NAME}/{object_key}"
    
    except (NoCredentialsError, ClientError) as e:
        print(f"Error uploading image: {e}")
        return None

def send_email(to_address, subject, message):
    from_address = "serajyali72@gmail.com"
    password = "jdec ycpq ejmn okla"
    msg = MIMEMultipart()
    msg["From"] = from_address
    msg["To"] = to_address
    msg["Subject"] = subject
    msg.attach(MIMEText(message, "plain"))
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(from_address, password)  
        text = msg.as_string()
        server.sendmail(from_address, to_address, text)
        print(f"Email successfully sent to {to_address}")
    except Exception as e:
        print(f"Failed to send email: {e}")

    finally:
        server.quit()

def check_ready_requests():
    while True:
        try:
            connection = get_postgres_connection()
            cursor = connection.cursor()

            cursor.execute("SELECT \"ID\", caption, email FROM cloud_app_request_data WHERE status = 'ready';")
            ready_requests = cursor.fetchall()

            for request_id, caption, email in ready_requests:
                print(f"Processing request ID: {request_id} with caption: {caption}")

                image_bytes = query({"inputs": caption})


                object_key = f"generated_images/{request_id}.png"  
                image_url = upload_image_to_s3(image_bytes, object_key)

                if image_url:
                    
                    cursor.execute("UPDATE cloud_app_request_data SET new_url = %s WHERE \"ID\" = %s;", (image_url, request_id))
                    connection.commit()
                    print(f"Image URL stored in database: {image_url}")

                    cursor.execute("UPDATE cloud_app_request_data SET status = 'done' WHERE \"ID\" = %s;", (request_id,))
                    
                    connection.commit()
                    subject = "Your Generated Image"
                    message = f"Your image has been generated and is available at the following URL: {image_url}"
                    send_email(email, subject, message)

            cursor.close()
            connection.close()
        except Exception as e:
            print(f"An error occurred: {e}")
        time.sleep(60)

if __name__ == "__main__":
    check_ready_requests()
