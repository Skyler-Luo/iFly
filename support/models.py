from django.db import models
from django.conf import settings

class SupportTicket(models.Model):
    STATUS_CHOICES = [
        ('open', '打开'),
        ('in_progress', '处理中'),
        ('closed', '已关闭'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='用户')
    subject = models.CharField(max_length=200, verbose_name='主题')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open', verbose_name='状态')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '支持工单'
        verbose_name_plural = '支持工单'

    def __str__(self):
        return f"{self.id} - {self.subject}"

class SupportMessage(models.Model):
    ticket = models.ForeignKey(SupportTicket, on_delete=models.CASCADE, related_name='messages', verbose_name='工单')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='发送者')
    message = models.TextField(verbose_name='消息内容')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='发送时间')

    class Meta:
        verbose_name = '工单消息'
        verbose_name_plural = '工单消息'

    def __str__(self):
        return f"{self.ticket.id} - {self.sender}" 