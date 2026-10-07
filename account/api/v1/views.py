from rest_framework import generics, views, status
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import *
from .permissions import IsAnonymous
from ...tasks import send_otp_code_task

class RegisterCreateApiView(generics.CreateAPIView):
    serializer_class = RegistrationSerializer
    permission_classes = [IsAnonymous]

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [IsAnonymous]

class LogoutApiView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response(
                {"detail": "Refresh token is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {"detail": "Successfully logged out."},
                status=status.HTTP_204_NO_CONTENT
            )
        except Exception:
            return Response(
                {"detail": "Invalid refresh token."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
class PasswordChangeApiView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PasswordChangeSerializer(
            data=request.data,
            context={'request':request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"detail": "Password changed successfully."},
            status=status.HTTP_200_OK
        )
    
class ForgotPasswordApiView(generics.GenericAPIView):
    serializer_class = ForgotPasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data['phone']
        user = User.objects.get(phone=phone)
        otp_code = PasswordResetOTPCode.generate_otp(user)

        send_otp_code_task.delay(phone,otp_code)

        return Response(
            {"detail": "OTP has been sent successfully."},
            status=status.HTTP_200_OK
        )