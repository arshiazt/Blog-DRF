from ...models import (Category,)
from rest_framework import serializers

class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'slug',
                  'created_date', 'updated_date']
        read_only_fields = ['id', 'created_date', 'updated_date']