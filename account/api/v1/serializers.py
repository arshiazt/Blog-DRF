from rest_framework import serializers
from account.models import User
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

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