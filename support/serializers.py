from rest_framework import serializers
from .models import SupportTicket, SupportMessage

class SupportMessageSerializer(serializers.ModelSerializer):
    sender_username = serializers.ReadOnlyField(source='sender.username')
    class Meta:
        model = SupportMessage
        fields = ['id', 'sender', 'sender_username', 'message', 'created_at']

class SupportTicketSerializer(serializers.ModelSerializer):
    messages = SupportMessageSerializer(many=True, read_only=True)
    class Meta:
        model = SupportTicket
        fields = ['id', 'user', 'subject', 'status', 'messages', 'created_at', 'updated_at']
        read_only_fields = ['user'] 