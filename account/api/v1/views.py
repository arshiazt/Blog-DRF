from rest_framework import generics
from .serializers import *

class RegisterCreateApiView(generics.CreateAPIView):
    serializer_class = RegistrationSerializer
