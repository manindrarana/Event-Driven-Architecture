import pika
import json
import os
from dotenv import load_dotenv
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

# Load environment variables from .env file
load_dotenv(dotenv_path='/app/.env')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'notification.settings')
import django
django.setup()

from django.core.mail import send_mail
from notification_service.serializers import NotificationSerializer

def send_welcome_email(user_id):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    try:
        user = User.objects.get(id=user_id)
        email = user.email
        send_mail(
            'Welcome to Our Service',
            'Thank you for signing up!',
            'from@manindra.com',
            [email],
            fail_silently=False,
        )
        logging.info(f"Sent welcome email to {email}")
    except User.DoesNotExist:
        logging.error(f"User with id {user_id} does not exist")

def callback(ch, method, properties, body):
    data = json.loads(body)
    user_id = data.get('user_id')
    if user_id:
        send_welcome_email(user_id)
        serializer = NotificationSerializer(data={
            'user_id': user_id,
            'message_type': 'welcome',
            'message': 'Welcome to Our Service'
        })
        if serializer.is_valid():
            serializer.save()
            logging.info(f"Saved notification for user_id {user_id}")
        else:
            logging.error(serializer.errors)

# RabbitMQ connection parameters
rabbitmq_host = os.getenv('RABBITMQ_HOST', 'rabbitmq')
rabbitmq_user = os.getenv('RABBITMQ_DEFAULT_USER', 'rabbitmq')
rabbitmq_pass = os.getenv('RABBITMQ_DEFAULT_PASS', 'password')

credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_pass)
parameters = pika.ConnectionParameters(host=rabbitmq_host, credentials=credentials)

connection = pika.BlockingConnection(parameters)
channel = connection.channel()

channel.queue_declare(queue='welcome_email')

channel.basic_consume(queue='welcome_email', on_message_callback=callback, auto_ack=True)

logging.info('Waiting for messages. To exit press CTRL+C')
channel.start_consuming()