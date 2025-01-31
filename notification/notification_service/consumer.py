import pika
import json
from django.core.mail import send_mail
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'notification.settings')
django.setup()

def send_welcome_email(email):
    send_mail(
        'Welcome to Our Service',
        'Thank you for signing up!',
        'from@example.com',
        [email],
        fail_silently=False,
    )

def callback(ch, method, properties, body):
    data = json.loads(body)
    email = data.get('email')
    if email:
        send_welcome_email(email)

connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
channel = connection.channel()

channel.queue_declare(queue='welcome_email')

channel.basic_consume(queue='welcome_email', on_message_callback=callback, auto_ack=True)

print('Waiting for messages. To exit press CTRL+C')
channel.start_consuming()