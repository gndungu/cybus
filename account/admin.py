from django.apps import apps
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from account.models import CustomUser
from conf.models import *

from conf.baseModelAdmin import register_all_models, BaseModelAdmin, BaseTabularInLine


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = (
        "email",
        "full_name",
        "phone_number",
        "account_type",
        "role",
        "department_head",
        "is_active",
        "is_staff",
        "date_joined",
    )
    list_filter = (
        "account_type",
        "role",
        "is_active",
        "is_staff",
        "department_head",
    )
    search_fields = (
        "email",
        "full_name",
        "phone_number",
    )
    ordering = ("email",)
    readonly_fields = ("date_joined",)

    # Group fields logically in the admin form
    fieldsets = (
        (None, {"fields": ("email", "full_name", "phone_number", "password")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Account Details", {"fields": ("account_type", "role", "department_head", "use_two_factor_authentication")}),
        ("Signature", {"fields": ("signature",)}),
        ("Important Dates", {"fields": ("last_login", "date_joined")}),
    )

    # For add form (superuser creation)
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "email",
                "full_name",
                "phone_number",
                "password1",
                "password2",
                "account_type",
                "role",
                "is_active",
                "is_staff",
            ),
        }),
    )