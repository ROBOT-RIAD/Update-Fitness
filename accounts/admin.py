from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Profile

# Register your models here.


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom admin for User model"""

    list_display = ("id", "email", "username", "role", "is_active", "is_staff")
    list_filter = ("role", "is_active", "is_staff", "is_superuser")
    search_fields = ("email", "username")
    ordering = ("id",)

    fieldsets = (
        (None, {"fields": ("email", "username", "password", "role")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "username", "role", "password1", "password2"),
            },
        ),
    )






@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """Admin for Profile model"""

    list_display = (
        "id",
        "user",
        "fullname",
        "gender",
        "date_of_birth",
        "weight",
        "height",
        "abdominal",
        "sacroiliac",
        "subscapularis",
        "triceps",
        "trainer",
        "train_duration",
        "fitness_goals",
        "injuries_discomfort",
        "dietary_preferences",
        "allergies",
        "medical_conditions",
        "gender_spanish",
        "trainer_spanish",
        "fitness_goals_spanish",
        "injuries_discomfort_spanish",
        "dietary_preferences_spanish",
        "allergies_spanish",
        "medical_conditions_spanish",
    )

    search_fields = (
        "fullname",
        "user__email",
        "user__username",
        "fitness_goals",
        "medical_conditions",
        "fitness_goals_spanish",
        "medical_conditions_spanish",
    )

    list_filter = ("gender", "gender_spanish")



    