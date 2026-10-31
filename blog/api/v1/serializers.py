from ...models import (Category, Tag, Post, 
                       PostImage)
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

class PostSerializer(serializers.ModelSerializer):

    categories = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), many=True
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )

    class Meta:
        model = Post
        fields = ['id', 'author', 'title', 'content',
                  'slug', 'views_count', 'status',
                  'categories', 'tags', 'published_date',
                  'created_date' ,'updated_date']
        read_only_fields = ['id', 'author', 'views_count',
                            'created_date', 'updated_date']
        
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['categories'] = CategorySerializer(
            instance.categories.all(), many=True
        ).data
        data['tags'] = TagSerializer(
            instance.tags.all(), many=True
        ).data

        return data
    
class PostImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = PostImage
        fields = ['id', 'post', 'image', 'is_main',
                  'created_date', 'updated_date']
        read_only_fields = ['id', 'post',
                            'created_date', 'updated_date']