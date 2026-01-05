"""
Core 模块数据模型。

包含系统日志、城市、机场、航空公司和热门航线等核心数据模型。
"""
from django.db import models
from django.conf import settings


class SystemLog(models.Model):
    """系统操作日志"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='用户'
    )
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

class Airport(models.Model):
    """机场信息"""
    name = models.CharField(max_length=100, verbose_name='机场名称')
    code = models.CharField(max_length=10, unique=True, verbose_name='机场代码')
    city = models.ForeignKey(City, on_delete=models.CASCADE, verbose_name='所属城市')
    terminal = models.CharField(max_length=10, default='T1', verbose_name='航站楼')
    
    class Meta:
        verbose_name = '机场'
        verbose_name_plural = '机场'
        
    def __str__(self):
        return f"{self.name}({self.code})"

class Airline(models.Model):
    """航空公司信息"""
    name = models.CharField(max_length=100, verbose_name='航空公司名称')
    code = models.CharField(max_length=10, unique=True, verbose_name='航空公司代码')
    logo_url = models.URLField(blank=True, null=True, verbose_name='Logo URL')
    
    class Meta:
        verbose_name = '航空公司'
        verbose_name_plural = '航空公司'
        
    def __str__(self):
        return f"{self.name}({self.code})"

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


class SystemSettings(models.Model):
    """
    系统设置模型 - 键值对存储
    
    满足 Requirements 1.1-1.5, 2.1-2.5
    """
    CATEGORY_CHOICES = [
        ('site', '站点信息'),
        ('business', '业务规则'),
    ]
    
    category = models.CharField(
        max_length=20, 
        choices=CATEGORY_CHOICES, 
        verbose_name='分类'
    )
    key = models.CharField(max_length=100, verbose_name='配置键')
    value = models.TextField(verbose_name='配置值')
    description = models.CharField(max_length=200, blank=True, verbose_name='描述')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL,
        null=True, 
        blank=True,
        verbose_name='更新人'
    )
    
    class Meta:
        unique_together = ('category', 'key')
        verbose_name = '系统设置'
        verbose_name_plural = '系统设置'
    
    def __str__(self):
        return f"[{self.category}] {self.key}"
    
    @classmethod
    def get_value(cls, category: str, key: str, default=None):
        """获取配置值"""
        try:
            setting = cls.objects.get(category=category, key=key)
            return setting.value
        except cls.DoesNotExist:
            return default
    
    @classmethod
    def set_value(cls, category: str, key: str, value: str, user=None):
        """
        设置配置值，同时记录变更历史
        
        满足 Requirement 2.5 - 记录变更历史
        """
        # 获取旧值（如果存在）
        try:
            old_setting = cls.objects.get(category=category, key=key)
            old_value = old_setting.value
        except cls.DoesNotExist:
            old_value = None
        
        # 创建或更新设置
        setting, created = cls.objects.update_or_create(
            category=category, 
            key=key,
            defaults={'value': str(value), 'updated_by': user}
        )
        
        # 记录变更历史（仅当值发生变化时）
        if old_value is not None and old_value != str(value):
            SettingsHistory.objects.create(
                setting=setting,
                old_value=old_value,
                new_value=str(value),
                changed_by=user
            )
        
        return setting
    
    @classmethod
    def get_category_settings(cls, category: str) -> dict:
        """获取某分类的所有设置"""
        settings_qs = cls.objects.filter(category=category)
        return {s.key: s.value for s in settings_qs}



class SettingsHistory(models.Model):
    """
    设置变更历史模型
    
    满足 Requirement 2.5 - 记录业务规则变更历史
    """
    setting = models.ForeignKey(
        SystemSettings, 
        on_delete=models.CASCADE,
        related_name='history', 
        verbose_name='设置项'
    )
    old_value = models.TextField(verbose_name='旧值')
    new_value = models.TextField(verbose_name='新值')
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL,
        null=True, 
        blank=True,
        verbose_name='修改人'
    )
    changed_at = models.DateTimeField(auto_now_add=True, verbose_name='修改时间')
    
    class Meta:
        verbose_name = '设置变更历史'
        verbose_name_plural = '设置变更历史'
        ordering = ['-changed_at']
    
    def __str__(self):
        return f"{self.setting.key}: {self.old_value} → {self.new_value}"
