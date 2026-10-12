from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions

def validate_user_password(value):
        
    try:
        validate_password(value)
    except exceptions.ValidationError as e:
        raise serializers.ValidationError({"password": list(e.messages)})
    
    return value

def validate_phone(value):

    if len(value) != 11:
        raise serializers.ValidationError(
            "Phone must be exactly 11 digits.")

    if not value.isdigit():
        raise serializers.ValidationError(
            "Phone must contain only digits.")

    return value

def validate_otp_code(value):
        
        if len(value)  != 6:
            raise serializers.ValidationError(
                "OTP must be exactly 6 digits.")

        if not value.isdigit():
            raise serializers.ValidationError(
                "OTP must contain only digits.")
        
        return value