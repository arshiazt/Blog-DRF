from rest_framework import generics
from .serializers import *
from rest_framework_simplejwt.views import TokenObtainPairView

class RegisterCreateApiView(generics.CreateAPIView):
    serializer_class = RegistrationSerializer

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer