from rest_framework import serializers
from account.models import User, PasswordResetOTPCode
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from datetime import timedelta
from django.utils import timezone

class RegistrationSerializer(serializers.ModelSerializer):
    password_confirm = serializers.CharField(max_length=255, write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['phone','user_name','first_name','last_name',
                  'password','password_confirm']
    
    def validate(self, attrs):
        if attrs.get('password') != attrs.get('password_confirm'):
            raise serializers.ValidationError({"detail": "passswords doesnt match"})
        return super().validate(attrs)
    
    def validate_password(self, value):
        try:
            validate_password(value)
        except exceptions.ValidationError as e:
            raise serializers.ValidationError({"password": list(e.messages)})
        
        return value
    
    def validate_phone(self, value):
        if len(value) != 11:
            raise serializers.ValidationError({'phone':'Phone must be exactly 11 digits.'})
        
        if not value.isdigit():
            raise serializers.ValidationError({'phone':'Phone must contain only digits.'})
        
        return value
    
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
    new_password = serializers.CharField(write_only=True)
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
        
    def validate_new_password(self, value):
        try:
            validate_password(value)
        except exceptions.ValidationError as e:
            raise serializers.ValidationError({"new_password": list(e.messages)})
        
        return value
    
    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data["new_password"])
        user.save()

        return user
    
class ForgotPasswordSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=11,write_only=True)

    def validate_phone(self,value):
        if len(value) != 11:
            raise serializers.ValidationError(
                'Phone must be exactly 11 digits.'
            )
        
        if not value.isdigit():
            raise serializers.ValidationError(
                'Phone must contain only digits.'
            )
        
        return value
    
    def validate(self, attrs):
        phone = attrs.get('phone')
        user_exists  = User.objects.filter(phone=phone).exists()
        
        if not user_exists :
            raise serializers.ValidationError(
                {"phone": "User with this phone number does not exist."}
            )
        
        return attrs
    
class VerifyOTPSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=11,write_only=True)
    otp_code = serializers.CharField(max_length=6,write_only=True)

    def validate_phone(self,value):
        if len(value) != 11:
            raise serializers.ValidationError(
                'Phone must be exactly 11 digits.'
            )
        
        if not value.isdigit():
            raise serializers.ValidationError(
                'Phone must contain only digits.'
            )
        
        return value
    
    def validate_otp_code(self,value):
        if len(value)  != 6:
            raise serializers.ValidationError(
                "OTP must be exactly 6 digits."
            )

        if not value.isdigit():
            raise serializers.ValidationError(
                "OTP must contain only digits."
            )
        
        return value
    
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