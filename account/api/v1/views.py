from rest_framework import generics
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import *
from .permissions import IsAnonymous

class RegisterCreateApiView(generics.CreateAPIView):
    serializer_class = RegistrationSerializer
    permission_classes = [IsAnonymous]

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [IsAnonymous]