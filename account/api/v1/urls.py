from django.urls import path
from rest_framework_simplejwt.views import TokenVerifyView, TokenRefreshView
from . import views

app_name = 'api-v1'

urlpatterns = [
    path('register/',views.RegisterCreateApiView.as_view(),name='register'),
    path('login/',views.CustomTokenObtainPairView.as_view(),name='login'),
    path('logout/', views.LogoutApiView.as_view(),name='logout'),

    path("jwt/refresh/", TokenRefreshView.as_view(), name="jwt-refresh"),
    path("jwt/verify/", TokenVerifyView.as_view(), name="jwt-verify"),
    
    path('change-password/',views.PasswordChangeApiView.as_view(),name='change-password'),
    path('forgot-password/',views.ForgotPasswordApiView.as_view(),name='forgot-password'),
    path('verify-otp/',views.VerifyOTPApiView.as_view(),name='verify'),
    path('reset-password/',views.ResetPasswordApiView.as_view(),name='reset-password'),

    path('change-phone/',views.PhoneChangeApiView.as_view(),name='phone-change'),
    path('verify-phone/',views.VerifyPhoneChangeOTPApiView.as_view(),name='phone-verify'),

    path('deactivate/',views.DeactivateAccountApiView.as_view(),name='deactivate'),
]