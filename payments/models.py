from django.db import models
from django.conf import settings
from booking.models import Order

class Payment(models.Model):
    PAY_METHOD_CHOICES = [
        ('alipay', '支付宝'),
        ('wechat', '微信'),
    ]
    PAY_STATUS_CHOICES = [
        ('pending', '待支付'),
        ('success', '成功'),
        ('failed', '失败'),
        ('refunded', '已退款'),
    ]
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment', verbose_name='订单')
    method = models.CharField(max_length=20, choices=PAY_METHOD_CHOICES, verbose_name='支付方式')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='支付金额')
    status = models.CharField(max_length=20, choices=PAY_STATUS_CHOICES, default='pending', verbose_name='支付状态')
    transaction_id = models.CharField(max_length=100, blank=True, null=True, verbose_name='交易流水号')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '支付记录'
        verbose_name_plural = '支付记录'

    def __str__(self):
        return f"{self.order.order_number} - {self.method} - {self.status}" 