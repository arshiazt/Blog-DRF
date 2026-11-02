from .serializers import (CategorySerializer, TagSerializer, PostSerializer)
from rest_framework import permissions, generics, filters
from rest_framework.response import Response
from ...models import (Category, Tag, Post)
from django.utils import timezone
from django.db.models import F
from django_filters.rest_framework import DjangoFilterBackend

class CategoryListApiView(generics.ListAPIView):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()

class CategoryRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()

class TagListAPIView(generics.ListAPIView):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()

class TagRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()

class PostListApiView(generics.ListAPIView):
    serializer_class = PostSerializer
    queryset = Post.objects.filter(status=Post.Status.PUBLISHED)

    filter_backends = [filters.SearchFilter,
                       filters.OrderingFilter,
                       DjangoFilterBackend]

    search_fields = ['title', 'content']
    filterset_fields = ['categories', 'tags']
    ordering_fields = ['published_date', 'views_count']

class PostDetailApiView(generics.RetrieveAPIView):
    serializer_class = PostSerializer
    queryset = Post.objects.filter(status=Post.Status.PUBLISHED)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        Post.objects.filter(pk=instance.pk).update(
            views_count=F('views_count')  + 1
        )
        instance.refresh_from_db()
        serializer = self.get_serializer(instance)

        return Response(serializer.data)

class PostListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Post.objects.filter(author=self.request.user)
     
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class PostRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Post.objects.filter(author=self.request.user)
    
class PostPublishApiView(generics.UpdateAPIView):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Post.objects.filter(author=self.request.user)
    
    def perform_update(self, serializer):
        serializer.save(status=Post.Status.PUBLISHED,
                        published_date=timezone.now())