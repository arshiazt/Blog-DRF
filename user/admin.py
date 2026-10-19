
from django.contrib import admin
from .models import Profile, Link


class LinkInline(admin.TabularInline):
    model = Link
    extra = 1
    fields = ("title", "url")
    show_change_link = True


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    inlines = [LinkInline]

    list_display = (
        "user_phone",
        "email",
        "location",
        "job_title",
        "created_at",
    )

    search_fields = (
        "user__phone",
        "email",
        "location",
        "job_title",
    )

    list_filter = ("created_at",)
    ordering = ("-created_at",)

    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("User Information", {
            "fields": ("user",)
        }),
        ("Profile Information", {
            "fields": (
                "avatar",
                "bio",
                "email",
                "location",
                "job_title",
            )
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )

    def user_phone(self, obj):
        return obj.user.phone

    user_phone.short_description = "Phone Number"

    def get_readonly_fields(self, request, obj=None):
        readonly = list(super().get_readonly_fields(request, obj))

        if obj is not None:
            readonly.append("user")

        return readonly


@admin.register(Link)
class LinkAdmin(admin.ModelAdmin):
    list_display = ("title", "profile", "url")
    search_fields = ("title", "url", "profile__user__phone")
    list_select_related = ("profile", "profile__user")
