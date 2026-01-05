"""
用户消息模块序列化器定义。

提供消息模型的序列化和反序列化功能。
"""
from rest_framework import serializers

from .models import Message


class MessageSerializer(serializers.ModelSerializer):
    """消息序列化器，用于消息数据的序列化和反序列化。"""

    class Meta:
        model = Message
        fields = ['id', 'type', 'title', 'content', 'is_read', 'created_at']
        read_only_fields = ['created_at']
