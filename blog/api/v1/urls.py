from django.urls import path
from . import views

app_name = 'api-v1'

urlpatterns = [
    path('categories/',views.CategoryListApiView.as_view(),name='category-list'),
    path('categories/<int:pk>/',views.CategoryRetrieveAPIView.as_view(),name='category-detail'),
]