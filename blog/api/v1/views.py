from .serializers import (CategorySerializer,TagSerializer)
from rest_framework import permissions, generics
from ...models import (Category,Tag)

class CategoryListApiView(generics.ListAPIView):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()

class CategoryRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()

class TagListAPIView(generics.ListAPIView):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()