"""
通知模块数据模型。

定义系统通知相关的数据模型，包括用户通知消息。
"""
from django.conf import settings
from django.db import models


class Notification(models.Model):
    """
    系统通知模型。

    存储发送给用户的各类通知消息，包括系统通知、订单更新、
    航班变动、支付通知等。
    """

    NOTIF_TYPE_CHOICES = [
        ('system', '系统通知'),
        ('order', '订单更新'),
        ('flight', '航班变动'),
        ('payment', '支付通知'),
        ('refund', '退款通知'),
        ('info', '信息'),
        ('warning', '警告'),
        ('alert', '警报'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='用户'
    )
    title = models.CharField(max_length=100, verbose_name='标题')
    message = models.TextField(verbose_name='消息内容')
    notif_type = models.CharField(
        max_length=20,
        choices=NOTIF_TYPE_CHOICES,
        default='system',
        verbose_name='消息类型'
    )
    is_read = models.BooleanField(default=False, verbose_name='已读')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '消息通知'
        verbose_name_plural = '消息通知'

    def __str__(self):
        return f"{self.user} - {self.title}"
