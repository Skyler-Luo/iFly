"""
用户消息模块模型定义。

定义站内消息相关的数据模型。
"""
from django.conf import settings
from django.db import models


class Message(models.Model):
    """用户消息模型，用于存储系统通知、订单更新、航班变动等消息。"""

    MESSAGE_TYPES = (
        ('system', '系统通知'),
        ('order', '订单更新'),
        ('flight', '航班变动'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name='用户'
    )
    type = models.CharField(max_length=20, choices=MESSAGE_TYPES, default='system', verbose_name='消息类型')
    title = models.CharField(max_length=200, verbose_name='标题')
    content = models.TextField(verbose_name='内容')
    is_read = models.BooleanField(default=False, verbose_name='是否已读')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '用户消息'
        verbose_name_plural = '用户消息列表'
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.get_type_display()}: {self.title} - {self.user.username}"
