from .serializers import (CategorySerializer,)
from rest_framework import permissions, generics
from ...models import (Category,)

class CategoryListApiView(generics.ListAPIView):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()

class CategoryRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()