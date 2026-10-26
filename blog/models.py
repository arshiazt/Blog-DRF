from django.db import models
from django.conf import settings

# Create your models here.

class Category(models.Model):

    name = models.CharField(max_length=255,unique=True)
    description = models.TextField(blank=True,null=True)
    slug = models.SlugField(max_length=128,unique=True)
    
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
class Tag(models.Model):

    name = models.CharField(max_length=255,unique=True)
    slug = models.SlugField(max_length=128,unique=True) 

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
class Post(models.Model):

    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        PUBLISHED = 'published', 'Published'

    author = models.ForeignKey(settings.AUTH_USER_MODEL,
                               on_delete=models.CASCADE,
                               related_name='posts')
    title = models.CharField(max_length=255)
    content = models.TextField()
    slug = models.SlugField(max_length=255, unique=True)
    views_count = models.PositiveBigIntegerField(default=0)

    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.DRAFT
    )

    category = models.ManyToManyField(Category,related_name='posts',
                                      null=True, blank=True)
    tag = models.ManyToManyField(Tag,related_name='posts',
                                      null=True, blank=True)

    published_date = models.DateTimeField(null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)