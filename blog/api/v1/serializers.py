from ...models import (Category, Tag)
from rest_framework import serializers

class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'slug',
                  'created_date', 'updated_date']
        read_only_fields = ['id', 'created_date', 'updated_date']

class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug',
                  'created_date', 'updated_date']
        read_only_fields = ['id', 'created_date', 'updated_date']