from rest_framework import generics, views, status
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from .serializers import *
from .permissions import IsAnonymous
from .tokens import PasswordResetToken
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
    
class VerifyOTPApiView(generics.GenericAPIView):
    serializer_class = VerifyOTPSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        reset_token = PasswordResetToken.for_user(user)

        return Response(
            {"detail": "OTP verified successfully.",
             "reset_token":str(reset_token)},
            status=status.HTTP_200_OK
        )
    
class ResetPasswordApiView(generics.GenericAPIView):
    serializer_class = ResetPasswordSerializer
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        token = request.headers.get("Authorization")

        if not token:
            return Response(
                {"detail": "Reset token is required."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        try:
            token = token.split(" ")[1]
            reset_token = PasswordResetToken(token)

        except (IndexError, TokenError):
            return Response(
                {"detail": "Invalid or expired reset token."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if reset_token.get("token_type") != "password_reset":
            return Response(
                {"detail": "Invalid reset token."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        user_id = reset_token.get("user_id")
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {"detail": "User does not exist."},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = self.get_serializer(data=request.data,context={"user": user})
        serializer.is_valid(raise_exception=True)
        serializer.save(user=user)

        return Response(
            {"detail": "Password reset successfully."},
            status=status.HTTP_200_OK
        )
    
class PhoneChangeApiView(generics.GenericAPIView):
    serializer_class = PhoneChangeSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_phone = serializer.validated_data['new_phone']
        otp_code = PhoneResetOTP.generate_otp(request.user,new_phone=new_phone)
        send_otp_code_task.delay(new_phone,otp_code)

        return Response({
            "detail": "OTP code sent successfully.",
        },
        status=status.HTTP_200_OK)