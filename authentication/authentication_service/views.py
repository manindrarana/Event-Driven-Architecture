from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
import pika
import json

User = get_user_model()

@api_view(['POST'])
def signup(request):
    username = request.data.get('username')
    password = request.data.get('password')
    role = request.data.get('role')
    email = request.data.get('email')
    if username is None or password is None or role is None or email is None:
        return Response({'error': 'Please provide username, password, role, and email'}, status=status.HTTP_400_BAD_REQUEST)
    if User.objects.filter(username=username).exists():
        return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)
    user = User.objects.create_user(username=username, password=password, role=role, email=email)
    refresh = RefreshToken.for_user(user)

    # message to RabbitMQ
    connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
    channel = connection.channel()
    channel.queue_declare(queue='welcome_email')
    message = json.dumps({'email': email, 'user_id': user.id})
    channel.basic_publish(exchange='', routing_key='welcome_email', body=message)
    connection.close()

    return Response({
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }, status=status.HTTP_201_CREATED)

class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        try:
            user = User.objects.get(username=request.data.get('username'))
            response.data['role'] = user.role
        except User.DoesNotExist:
            return Response({'detail': 'No active account found with the given credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        return response