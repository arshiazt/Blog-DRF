from rest_framework import serializers
from account.models import User, PasswordResetOTPCode, PhoneResetOTP
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from datetime import timedelta
from django.utils import timezone
from .validators import validate_phone, validate_user_password, validate_otp_code

class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=255, write_only=True, min_length=8, validators=[validate_user_password])
    password_confirm = serializers.CharField(max_length=255, write_only=True, min_length=8)
    phone = serializers.CharField(max_length=11,validators=[validate_phone])

    class Meta:
        model = User
        fields = ['phone','user_name','first_name','last_name',
                  'password','password_confirm']
    
    def validate(self, attrs):
        if attrs.get('password') != attrs.get('password_confirm'):
            raise serializers.ValidationError({"detail": "passswords doesnt match"})
        return super().validate(attrs)
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)

        return user
    
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['id'] = user.id
        token['phone'] = user.phone
        token['user_name'] = user.user_name
        token['is_staff'] = user.is_staff

        return token
    
    def validate(self, attrs):
        data =  super().validate(attrs)
        user = self.user

        data['user'] = {
            'id':user.id,
            'phone':user.phone,
            'user_name':user.user_name,
            'is_staff':user.is_staff,
        }

        return data
    
class PasswordChangeSerializer(serializers.Serializer):

    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True,validators=[validate_user_password])
    new_password_confirm = serializers.CharField(write_only=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError(
                "Old password is incorrect."
            )
        return value
    
    def validate(self, attrs):
        if attrs.get('new_password') != attrs.get('new_password_confirm'):
            raise serializers.ValidationError({
                "new_password_confirm": "Passwords do not match."
            })
        return attrs
    
    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data["new_password"])
        user.save()

        return user
    
class ForgotPasswordSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=11,write_only=True,validators=[validate_phone])
    
    def validate(self, attrs):
        phone = attrs.get('phone')
        user_exists  = User.objects.filter(phone=phone).exists()
        
        if not user_exists :
            raise serializers.ValidationError(
                {"phone": "User with this phone number does not exist."}
            )
        
        return attrs
    
class VerifyOTPSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=11,write_only=True,validators=[validate_phone])
    otp_code = serializers.CharField(max_length=6,write_only=True,validators=[validate_otp_code])
    
    def validate(self, attrs):
        phone = attrs.get('phone')
        otp_code = attrs.get('otp_code')

        user = User.objects.filter(phone=phone).first()
        if not user:
            raise serializers.ValidationError(
                {"phone": "User with this phone number does not exist."}
            )

        otp = PasswordResetOTPCode.objects.filter(
            user=user,
            otp_code=otp_code,
            is_used=False
        ).order_by('-created_date').first()

        if not otp:
            raise serializers.ValidationError(
                {"otp_code": "Invalid OTP code."}
            )
        
        expiration_time = otp.created_date + timedelta(minutes=2)

        if timezone.now() > expiration_time:
            raise serializers.ValidationError(
                {"otp_code": "OTP has expired."}
            )

        otp.is_used = True
        otp.save(update_fields=["is_used"])
        attrs["user"] = user

        return attrs
    
class ResetPasswordSerializer(serializers.Serializer):
    
    new_password = serializers.CharField(write_only=True,min_length=8,validators=[validate_user_password])
    new_password_confirm = serializers.CharField(write_only=True,min_length=8)

    def validate(self, attrs):
        if attrs.get('new_password') != attrs.get('new_password_confirm'):
            raise serializers.ValidationError({
                "new_password_confirm": "Passwords do not match."
            })
        return attrs
    
    def save(self, **kwargs):
        user = self.context['user']
        user.set_password(self.validated_data["new_password"])
        user.save()

        return user
    
class PhoneChangeSerializer(serializers.Serializer):
    new_phone = serializers.CharField(max_length=11,write_only=True,validators=[validate_phone])

    def validate_new_phone(self, value):
        user = self.context['request'].user

        if value == user.phone:
            raise serializers.ValidationError(
                "New phone number must be different from the current phone number."
            )

        if User.objects.filter(phone=value).exists():
            raise serializers.ValidationError(
                "This phone number is already in use."
            )

        return value
    
class VerifyPhoneChangeOTPSerializer(serializers.Serializer):
    new_phone = serializers.CharField(max_length=11,write_only=True,validators=[validate_phone])
    otp_code = serializers.CharField(max_length=6,write_only=True,validators=[validate_otp_code])
    refresh = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = self.context['request'].user
        new_phone = attrs['new_phone']
        otp_code = attrs['otp_code']

        otp = PhoneResetOTP.objects.filter(
            user=user,
            new_phone=new_phone,
            otp_code=otp_code,
            is_used=False
        ).order_by('-created_date').first()

        if not otp:
            raise serializers.ValidationError({
                "otp_code": "Invalid OTP code."
            })
        expiration_time = otp.created_date + timedelta(minutes=2)

        if timezone.now() > expiration_time:
            raise serializers.ValidationError({
                "otp_code": "OTP has expired."
            })
        attrs['otp'] = otp

        return attrs
    
class DeactivateAccountSerializer(serializers.Serializer):
    refresh = serializers.CharField(write_only=True)