from django.contrib import admin
from .models import ChatBotMessage

# Register your models here.




@admin.register(ChatBotMessage)
class ChatBotMessageAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "short_input", "created_at")
    search_fields = ("user__username", "user_input")
    list_filter = ("created_at",)
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)

    def short_input(self, obj):
        return obj.user_input[:50]
    short_input.short_description = "User Input"
