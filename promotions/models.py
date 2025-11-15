from django.db import models
from django.utils.timezone import now
from accounts.models import User

class Promotion(models.Model):
    """促销活动"""
    title = models.CharField(max_length=100)
    description = models.TextField()
    promo_code = models.CharField(max_length=20, unique=True)
    discount_type = models.CharField(
        max_length=20,
        choices=[
            ('percentage', '百分比折扣'),
            ('fixed', '固定金额折扣'),
            ('free_shipping', '免运费'),
            ('points_bonus', '额外积分')
        ]
    )
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    min_purchase = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # 最低消费要求
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    usage_limit = models.IntegerField(default=0)  # 0表示不限制
    used_count = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} ({self.promo_code})"
        
    @property
    def is_valid(self):
        """检查促销活动是否有效"""
        current_time = now()
        usage_valid = self.usage_limit == 0 or self.used_count < self.usage_limit
        time_valid = self.start_date <= current_time <= self.end_date
        return self.is_active and usage_valid and time_valid

class PromotionUse(models.Model):
    """促销活动使用记录"""
    promotion = models.ForeignKey(Promotion, on_delete=models.CASCADE, related_name='usages')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='used_promotions')
    order_id = models.CharField(max_length=100)  # 关联的订单ID
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
    used_at = models.DateTimeField(default=now)
    
    def __str__(self):
        return f"{self.user.username} 使用 {self.promotion.promo_code} 优惠券"
        
    class Meta:
        unique_together = ('promotion', 'order_id')  # 一个订单不能重复使用同一个优惠码 