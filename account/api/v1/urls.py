from django.urls import path
from rest_framework_simplejwt.views import TokenVerifyView, TokenRefreshView
from . import views

app_name = 'api-v1'

urlpatterns = [
    path('register',views.RegisterCreateApiView.as_view(),name='register'),
    path('login',views.CustomTokenObtainPairView.as_view(),name='login'),
    path("jwt/refresh/", TokenRefreshView.as_view(), name="jwt-refresh"),
    path("jwt/verify/", TokenVerifyView.as_view(), name="jwt-verify"),
]