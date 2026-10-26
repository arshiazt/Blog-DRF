from django.db import models

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