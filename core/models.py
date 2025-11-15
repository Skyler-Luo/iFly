from django.db import models
from django.conf import settings


class SystemLog(models.Model):
    """系统操作日志"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name='用户')
    action = models.CharField(max_length=50, verbose_name='操作类型')
    detail = models.TextField(verbose_name='操作详情')
    ip_address = models.CharField(max_length=50, verbose_name='IP地址')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '系统日志'
        verbose_name_plural = '系统日志'

    def __str__(self):
        return f"{self.user} {self.action} {self.created_at}"

class City(models.Model):
    """城市信息"""
    name = models.CharField(max_length=100, verbose_name='城市名称')
    code = models.CharField(max_length=20, blank=True, null=True, verbose_name='城市代码')
    country = models.CharField(max_length=100, default='中国', verbose_name='国家')
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True, verbose_name='经度')
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True, verbose_name='纬度')
    
    class Meta:
        verbose_name = '城市'
        verbose_name_plural = '城市'
        
    def __str__(self):
        return self.name

class PopularRoute(models.Model):
    """热门航线"""
    from_city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='routes_from', verbose_name='出发城市')
    to_city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='routes_to', verbose_name='到达城市')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='基础价格')
    discount = models.DecimalField(max_digits=3, decimal_places=2, default=1.0, verbose_name='折扣率')
    popularity = models.IntegerField(default=0, verbose_name='受欢迎程度')
    
    class Meta:
        verbose_name = '热门航线'
        verbose_name_plural = '热门航线'
        unique_together = ('from_city', 'to_city')
        
    def __str__(self):
        return f"{self.from_city} → {self.to_city}"

class WeatherCache(models.Model):
    """城市天气缓存数据"""
    city = models.ForeignKey(City, on_delete=models.CASCADE, verbose_name='城市')
    temperature = models.IntegerField(verbose_name='温度(°C)')
    description = models.CharField(max_length=100, verbose_name='天气描述')
    humidity = models.IntegerField(verbose_name='湿度(%)')
    wind_speed = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='风速(m/s)')
    icon = models.CharField(max_length=100, verbose_name='图标代码')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '天气缓存'
        verbose_name_plural = '天气缓存'
        
    def __str__(self):
        return f"{self.city.name} - {self.temperature}°C - {self.description}" 