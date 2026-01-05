"""
订单与机票模块模型定义。

本模块包含 iFly 飞机订票系统的订单（Order）和机票（Ticket）数据模型。
"""
import random
import uuid

from django.conf import settings
from django.db import models


class Order(models.Model):
    """
    订单模型。

    存储用户的订单信息，包括订单编号、总金额、支付状态、联系人信息等。
    一个订单可以包含多张机票。
    """

    ORDER_STATUS_CHOICES = [
        ('pending', '待支付'),
        ('paid', '已支付'),
        ('completed', '已完成'),
        ('canceled', '已取消'),
    ]

    order_number = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='订单编号'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name='用户'
    )
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='总金额'
    )
    status = models.CharField(
        max_length=20,
        choices=ORDER_STATUS_CHOICES,
        default='pending',
        verbose_name='订单状态'
    )
    payment_method = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='支付方式'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )
    paid_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='支付时间'
    )
    contact_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='联系人姓名'
    )
    contact_phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='联系人电话'
    )
    contact_email = models.EmailField(
        blank=True,
        null=True,
        verbose_name='联系人邮箱'
    )
    expires_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='支付截止时间'
    )

    class Meta:
        """订单模型元数据配置。"""

        verbose_name = '订单'
        verbose_name_plural = '订单'
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return self.order_number

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f"ORD{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)


class Ticket(models.Model):
    """
    机票模型。

    存储机票信息，包括机票编号、乘客信息、座位号、舱位等级、价格和状态等。
    每张机票关联一个订单和一个航班。
    """

    TICKET_STATUS_CHOICES = [
        ('valid', '有效'),
        ('refunded', '已退票'),
        ('used', '已使用'),
        ('rescheduled', '已改签'),
        ('canceled', '已取消'),
    ]
    CABIN_CLASS_CHOICES = [
        ('economy', '经济舱'),
        ('business', '商务舱'),
        ('first', '头等舱'),
    ]

    ticket_number = models.CharField(
        max_length=15,
        unique=True,
        blank=True,
        null=True,
        verbose_name='机票编号'
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='tickets',
        verbose_name='订单'
    )
    flight = models.ForeignKey(
        'flight.Flight',
        on_delete=models.CASCADE,
        verbose_name='航班'
    )
    passenger_name = models.CharField(
        max_length=100,
        verbose_name='乘客姓名'
    )
    passenger_id_type = models.CharField(
        max_length=20,
        default='身份证',
        verbose_name='证件类型'
    )
    passenger_id_number = models.CharField(
        max_length=30,
        verbose_name='证件号码'
    )
    seat_number = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        verbose_name='座位号（值机时分配）'
    )
    cabin_class = models.CharField(
        max_length=20,
        choices=CABIN_CLASS_CHOICES,
        default='economy',
        verbose_name='舱位等级'
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='机票价格'
    )
    status = models.CharField(
        max_length=20,
        choices=TICKET_STATUS_CHOICES,
        default='valid',
        verbose_name='票务状态'
    )
    checked_in = models.BooleanField(
        default=False,
        verbose_name='是否已值机'
    )
    checked_in_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='值机时间'
    )
    boarding_pass_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='登机牌编号'
    )
    gate = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        verbose_name='登机口'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='更新时间'
    )

    class Meta:
        """机票模型元数据配置。"""

        verbose_name = '机票'
        verbose_name_plural = '机票'
        indexes = [
            models.Index(fields=['flight', 'status']),
            models.Index(fields=['order', 'status']),
            models.Index(fields=['passenger_id_number']),
        ]

    def __str__(self):
        flight_number = getattr(self.flight, 'flight_number', '')
        return (
            self.ticket_number or
            f"{self.passenger_name} - {flight_number} - {self.seat_number}"
        )

    def save(self, *args, **kwargs):
        if not self.ticket_number:
            self.ticket_number = self.generate_ticket_number()
        super().save(*args, **kwargs)

    @staticmethod
    def generate_ticket_number():
        """
        生成13位纯数字票号。
        
        格式：前3位为航空公司代码数字化 + 10位序列号
        示例：8801234567890
        """
        import time
        # 前3位：随机航空公司代码（常见范围 880-999）
        airline_prefix = str(random.randint(880, 999))
        # 后10位：时间戳后6位 + 4位随机数
        timestamp_part = str(int(time.time() * 1000))[-6:]
        random_part = str(random.randint(1000, 9999))
        return airline_prefix + timestamp_part + random_part


class RescheduleLog(models.Model):
    """
    改签记录模型。

    存储机票改签的历史记录，包括原机票、新机票、原航班、新航班、差价和手续费等信息。
    """

    original_ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name='reschedule_from_logs',
        verbose_name='原机票'
    )
    new_ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name='reschedule_to_logs',
        verbose_name='新机票'
    )
    original_flight = models.ForeignKey(
        'flight.Flight',
        on_delete=models.CASCADE,
        related_name='reschedule_from_logs',
        verbose_name='原航班'
    )
    new_flight = models.ForeignKey(
        'flight.Flight',
        on_delete=models.CASCADE,
        related_name='reschedule_to_logs',
        verbose_name='新航班'
    )
    price_difference = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='差价'
    )
    reschedule_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='改签手续费'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='改签时间'
    )

    class Meta:
        """改签记录模型元数据配置。"""

        verbose_name = '改签记录'
        verbose_name_plural = '改签记录'
        indexes = [
            models.Index(fields=['original_ticket']),
            models.Index(fields=['new_ticket']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"改签: {self.original_ticket} -> {self.new_ticket}"
