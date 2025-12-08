from rest_framework import serializers
from .models import ChatBotMessage


class ChatBotMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatBotMessage
        fields = ["id", "user", "user_input", "ai_response", "created_at"]
        read_only_fields = ["id", "ai_response", "created_at", "user"]


        