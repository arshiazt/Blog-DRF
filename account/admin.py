from django.contrib import admin
from .models import User
from django.contrib.auth.admin import UserAdmin

# Register your models here.

class CustomUserAdmin(UserAdmin):

    models = User
    list_display = ('phone','user_name','is_active','is_staff','is_superuser')
    list_filter = ('is_superuser',)
    search_fields = ('phone','user_name')
    ordering = ('-created_date',)
    fieldsets = (
        ('Authentication',{
            'fields':(
                'phone','user_name','first_name','last_name','password'
            )
        }),
        ('Permissions',{
            'fields':(
                'is_active','is_staff','is_superuser',
            )
        }),
        ('Group Permissions',{
            'fields':(
                'groups','user_permissions'
            )
        }),
        ('Importants Dates',{
            'fields':(
                'last_login',
            )
        })
    )
    add_fieldsets = (
        (None,{
            'classes':('wide',),
            'fields':('phone','user_name','first_name','last_name','password1','password2','is_active','is_staff','is_superuser')
        }),
    )


admin.site.register(User,CustomUserAdmin)