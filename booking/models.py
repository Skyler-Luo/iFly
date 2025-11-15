from django.db import models
from django.utils import timezone
from django.conf import settings
import uuid

class Order(models.Model):
    ORDER_STATUS_CHOICES = [
        ('pending', '待支付'),
        ('paid', '已支付'),
        ('completed', '已完成'),
        ('canceled', '已取消'),
    ]
    order_number = models.CharField(max_length=20, unique=True, verbose_name='订单编号')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders', verbose_name='用户')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='总金额')
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='pending', verbose_name='订单状态')
    payment_method = models.CharField(max_length=20, blank=True, null=True, verbose_name='支付方式')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    paid_at = models.DateTimeField(blank=True, null=True, verbose_name='支付时间')
    contact_name = models.CharField(max_length=100, blank=True, null=True, verbose_name='联系人姓名')
    contact_phone = models.CharField(max_length=20, blank=True, null=True, verbose_name='联系人电话')
    contact_email = models.EmailField(blank=True, null=True, verbose_name='联系人邮箱')

    def __str__(self):
        return self.order_number

    class Meta:
        verbose_name = '订单'
        verbose_name_plural = '订单'

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f"ORD{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

class Ticket(models.Model):
    TICKET_STATUS_CHOICES = [
        ('valid', '有效'),
        ('refunded', '已退票'),
        ('used', '已使用'),
    ]
    CABIN_CLASS_CHOICES = [
        ('economy', '经济舱'),
        ('business', '商务舱'),
        ('first', '头等舱'),
    ]
    ticket_number = models.CharField(max_length=15, unique=True, blank=True, null=True, verbose_name='机票编号')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='tickets', verbose_name='订单')
    flight = models.ForeignKey('flight.Flight', on_delete=models.CASCADE, verbose_name='航班')
    passenger_name = models.CharField(max_length=100, verbose_name='乘客姓名')
    passenger_id_type = models.CharField(max_length=20, default='身份证', verbose_name='证件类型')
    passenger_id_number = models.CharField(max_length=30, verbose_name='证件号码')
    seat_number = models.CharField(max_length=10, verbose_name='座位号')
    cabin_class = models.CharField(max_length=20, choices=CABIN_CLASS_CHOICES, default='economy', verbose_name='舱位等级')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='机票价格')
    status = models.CharField(max_length=20, choices=TICKET_STATUS_CHOICES, default='valid', verbose_name='票务状态')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    def __str__(self):
        return self.ticket_number or f"{self.passenger_name} - {self.flight.flight_number} - {self.seat_number}"

    class Meta:
        verbose_name = '机票'
        verbose_name_plural = '机票'
        
    def save(self, *args, **kwargs):
        if not self.ticket_number:
            self.ticket_number = f"TK{uuid.uuid4().hex[:10].upper()}"
        super().save(*args, **kwargs) 