"""
用户消息模块 Admin 配置。

定义消息模型在 Django Admin 后台的展示和管理方式。
"""
from django.contrib import admin

from .models import Message


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """消息模型的 Admin 配置类。"""

    list_display = ('id', 'user', 'type', 'title', 'is_read', 'created_at')
    list_filter = ('type', 'is_read', 'created_at')
    search_fields = ('title', 'content', 'user__username')
    date_hierarchy = 'created_at'
    list_per_page = 20
