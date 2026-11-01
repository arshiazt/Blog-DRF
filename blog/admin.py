from django.contrib import admin
from .models import (
    Category,
    Tag,
    Post,
    PostImage,
    Comment,
    Like,
    Bookmark
)

# Register your models here.

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug', 'created_date', 'updated_date')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('name',)

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug', 'created_date', 'updated_date')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('name',)

class PostImageInline(admin.TabularInline):
    model = PostImage
    extra = 1

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'title',
        'author',
        'status',
        'views_count',
        'published_date',
        'created_date'
    )

    list_filter = ('status', 'categories', 'tags', 'created_date')
    search_fields = ('title', 'content', 'author__phone')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('categories', 'tags')
    readonly_fields = ('views_count', 'created_date', 'updated_date')
    inlines = (PostImageInline,)
    ordering = ('-created_date',)

@admin.register(PostImage)
class PostImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'post', 'is_main', 'created_date')
    list_filter = ('is_main', 'created_date')
    search_fields = ('post__title',)
    readonly_fields = ('created_date', 'updated_date')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'post',
        'user',
        'parent',
        'is_active',
        'created_date'
    )

    list_filter = ('is_active', 'created_date')
    search_fields = ('content', 'user__phone', 'post__title')
    readonly_fields = ('created_date',)
    ordering = ('-created_date',)

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'post', 'user', 'created_date')
    search_fields = ('post__title', 'user__phone')
    readonly_fields = ('created_date',)
    ordering = ('-created_date',)

@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ('id', 'post', 'user', 'created_date')
    search_fields = ('post__title', 'user__phone')
    readonly_fields = ('created_date',)
    ordering = ('-created_date',)