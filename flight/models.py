"""
航班管理模块的数据模型。

本模块定义了航班相关的数据模型，包括航班信息、座位布局、状态管理等。
"""
from django.db import models


class Flight(models.Model):
    """
    航班信息模型。

    存储航班的基本信息，包括航班号、出发/到达城市、时间、票价、座位等。
    支持航班状态管理和座位布局配置。
    """
    FLIGHT_STATUS_CHOICES = [
        ('scheduled', '已计划'),
        ('full', '已满'),
        ('departed', '已起飞'),
        ('canceled', '已取消'),
    ]
    flight_number = models.CharField(max_length=10, unique=True, verbose_name='航班号')
    airline_name = models.CharField(max_length=50, verbose_name='航空公司', default='')
    departure_city = models.CharField(max_length=50, verbose_name='出发城市')
    arrival_city = models.CharField(max_length=50, verbose_name='到达城市')
    departure_time = models.DateTimeField(verbose_name='起飞时间')
    arrival_time = models.DateTimeField(verbose_name='到达时间')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='票价')
    discount = models.DecimalField(
        max_digits=3, decimal_places=2, default=1.0, verbose_name='折扣率'
    )
    capacity = models.IntegerField(verbose_name='总座位数')
    available_seats = models.IntegerField(verbose_name='剩余座位数')
    status = models.CharField(
        max_length=20,
        choices=FLIGHT_STATUS_CHOICES,
        default='scheduled',
        verbose_name='航班状态'
    )
    aircraft_type = models.CharField(max_length=50, verbose_name='飞机型号')
    # 座位布局设置：排数和每排座位数
    seat_rows = models.IntegerField(default=0, verbose_name='座位排数')
    seats_per_row = models.IntegerField(default=0, verbose_name='每排座位数')
    is_international = models.BooleanField(default=False, verbose_name='是否国际航班')
    meal_service = models.BooleanField(default=True, verbose_name='提供餐食')
    baggage_allowance = models.IntegerField(default=20, verbose_name='行李额度(kg)')
    wifi = models.BooleanField(default=False, verbose_name='提供WiFi')
    power_outlet = models.BooleanField(default=False, verbose_name='提供电源插座')
    entertainment = models.BooleanField(default=False, verbose_name='提供娱乐系统')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    def __str__(self):
        return f"{self.flight_number}: {self.departure_city} -> {self.arrival_city}"

    class Meta:
        verbose_name = '航班'
        verbose_name_plural = '航班'
        indexes = [
            models.Index(fields=['departure_city', 'arrival_city', 'departure_time']),
            models.Index(fields=['status', 'departure_time']),
            models.Index(fields=['departure_time']),
            models.Index(fields=['price']),
        ]
