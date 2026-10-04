from django.urls import path
from . import views

app_name = 'api-v1'

urlpatterns = [
    path('register',views.RegisterCreateApiView.as_view(),name='register'),
    path('login',views.CustomTokenObtainPairView.as_view(),name='login'),
]