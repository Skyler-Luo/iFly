from rest_framework import serializers
from .models import Message

class MessageSerializer(serializers.ModelSerializer):
    """消息序列化器"""
    class Meta:
        model = Message
        fields = ['id', 'type', 'title', 'content', 'is_read', 'created_at']
        read_only_fields = ['created_at'] 