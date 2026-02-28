from django.shortcuts import render

# Create your views here.
from rest_framework import generics
from rest_framework.response import Response
from django.contrib.auth import authenticate
from .serializers import UserSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from django.contrib.auth.models import User

class RegisterView(generics.CreateAPIView):
    serializer_class = UserSerializer

class LoginView(generics.GenericAPIView):
    serializer_class = UserSerializer

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            return Response({"message": "Login successful"})
        return Response({"error": "Invalid credentials"}, status=400)
    

@api_view(['GET'])
@permission_classes([IsAdminUser])
def all_users(request):
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)

from django.shortcuts import redirect
from rest_framework.decorators import api_view
from rest_framework.response import Response
from social_django.utils import psa

@api_view(['POST'])
@psa('social:complete')
def google_login(request, backend):
    token = request.data.get('token')
    user = request.backend.do_auth(token)
    if user:
        return Response({"username": user.username, "email": user.email})
    return Response({"error": "Google authentication failed"}, status=400)