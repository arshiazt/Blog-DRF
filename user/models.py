from django.db import models
from django.conf import settings

# Create your models here.

class Profile(models.Model):

    user = models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='profile')
    avatar = models.ImageField(upload_to='profile/',blank=True,null=True)
    bio = models.TextField(blank=True,null=True)
    email = models.EmailField(blank=True,null=True)
    location = models.CharField(max_length=100,blank=True,null=True)
    job_title = models.CharField(max_length=100,blank=True,null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.user.phone