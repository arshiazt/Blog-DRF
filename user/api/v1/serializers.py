from rest_framework import serializers
from user.models import Profile, Link
from django.db import transaction

class LinkSerializer(serializers.ModelSerializer):

    class Meta:
        model = Link
        fields = ['id', 'title', 'url']
        read_only_fields = ['id']

class ProfileSerializer(serializers.ModelSerializer):

    phone = serializers.CharField(source='user.phone',read_only=True)
    user_name = serializers.CharField(source='user.user_name',required=False)
    first_name = serializers.CharField(source='user.first_name',required=False)
    last_name = serializers.CharField(source='user.last_name',required=False)
    links = LinkSerializer(many=True,read_only=True)

    class Meta:
        model = Profile
        fields = ['user_name','first_name','last_name','phone','avatar',
                  'bio','email','location','job_title','links']
    
    @transaction.atomic
    def update(self, instance, validated_data):
        user_data = validated_data.pop('user',{})
        user = instance.user

        for attr, value in user_data.items():
            setattr(user, attr, value)

        if user_data:
            user.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        return instance
