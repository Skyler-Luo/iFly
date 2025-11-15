from django.contrib import admin
from .models import SupportTicket, SupportMessage

@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ['id', 'subject', 'user', 'status', 'created_at']
    list_filter = ['status']
    search_fields = ['subject', 'user__username']

@admin.register(SupportMessage)
class SupportMessageAdmin(admin.ModelAdmin):
    list_display = ['ticket', 'sender', 'created_at']
    search_fields = ['ticket__subject', 'sender__username'] 