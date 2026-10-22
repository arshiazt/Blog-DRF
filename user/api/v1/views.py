from rest_framework.generics import (RetrieveUpdateAPIView, ListCreateAPIView, 
                                     RetrieveUpdateDestroyAPIView, RetrieveAPIView)
from rest_framework.permissions import IsAuthenticated,AllowAny
from .serializers import ProfileSerializer,LinkSerializer
from user.models import Profile

class ProfileRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.profile
    
class LinkListCreateAPIView(ListCreateAPIView):
    serializer_class = LinkSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.profile.links.all()
    
    def perform_create(self, serializer):
        serializer.save(profile=self.request.user.profile)

class LinkRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = LinkSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.profile.links.all()
    
class ProfileRetrieveAPIView(RetrieveAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        return Profile.objects.select_related('user')
    
    def get_object(self):
        return self.get_queryset().get(
            user__user_name=self.kwargs['user_name']
        )