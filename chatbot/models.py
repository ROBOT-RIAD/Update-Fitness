
from django.db import models
from accounts.models import User

# Create your models here.


class ChatBotMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="chatbot_messages")
    user_input = models.TextField()
    ai_response = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username}: {self.user_input[:50]}"