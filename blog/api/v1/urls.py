from django.urls import path
from . import views

app_name = 'api-v1'

urlpatterns = [
    # Category urls
    path('categories/',views.CategoryListApiView.as_view(),name='category-list'),
    path('categories/<int:pk>/',views.CategoryRetrieveAPIView.as_view(),name='category-detail'),

    # Tag urls
    path('tags/',views.TagListAPIView.as_view(),name='tag-list'),
    path('tags/<int:pk>/',views.TagRetrieveAPIView.as_view(),name='tag-detail'),

    # Post urls
    path('post/',views.PostListApiView.as_view(),name='post-list'),
    path('post/<int:pk>/',views.PostDetailApiView.as_view(),name='post-detail'),
    path('my-post/',views.PostListCreateAPIView.as_view(),name='my-post'),
    path('my-post/<int:pk>/',views.PostRetrieveUpdateDestroyAPIView.as_view(),name='my-post-detail'),
]