from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions

def validate_password(value):
        
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