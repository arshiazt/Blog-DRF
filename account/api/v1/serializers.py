from rest_framework import serializers
from account.models import User
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions

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