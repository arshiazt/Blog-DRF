from rest_framework import serializers
from user.models import Profile, Link

class LinkSerializer(serializers.ModelSerializer):

    class Meta:
        model = Link
        fields = ['id', 'title', 'url']
        read_only_fields = ['id']