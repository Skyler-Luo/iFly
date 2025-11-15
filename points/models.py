from django.db import models
from django.utils.timezone import now
from accounts.models import User

class PointsAccount(models.Model):
    """用户积分账户"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='points_account')
    points_balance = models.IntegerField(default=0)  # 积分余额
    lifetime_points = models.IntegerField(default=0)  # 累计积分
    member_level = models.CharField(
        max_length=20,
        choices=[
            ('regular', '普通会员'),
            ('silver', '银卡会员'),
            ('gold', '金卡会员'),
            ('platinum', '白金会员')
        ],
        default='regular'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}的积分账户 - 余额:{self.points_balance}"

class PointsTransaction(models.Model):
    """积分交易记录"""
    account = models.ForeignKey(PointsAccount, on_delete=models.CASCADE, related_name='transactions')
    points = models.IntegerField()  # 正数为获得积分，负数为消费积分
    transaction_type = models.CharField(
        max_length=50,
        choices=[
            ('flight_purchase', '航班购买'),
            ('check_in', '签到'),
            ('exchange', '积分兑换'),
            ('expire', '积分过期'),
            ('adjustment', '人工调整'),
            ('task_completion', '任务完成'),
            ('refund', '退款返还')
        ]
    )
    description = models.TextField()
    reference_id = models.CharField(max_length=100, blank=True, null=True)  # 外部引用ID，如订单ID
    created_at = models.DateTimeField(default=now)
    
    def __str__(self):
        return f"{self.account.user.username} - {'获得' if self.points > 0 else '消费'}{abs(self.points)}积分"

class ExchangeItem(models.Model):
    """积分兑换商品"""
    name = models.CharField(max_length=100)
    description = models.TextField()
    points_required = models.IntegerField()
    image_url = models.URLField(blank=True)
    total_stock = models.IntegerField(default=0)
    available_stock = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.points_required}积分"

class ExchangeRecord(models.Model):
    """积分兑换记录"""
    account = models.ForeignKey(PointsAccount, on_delete=models.CASCADE, related_name='exchanges')
    item = models.ForeignKey(ExchangeItem, on_delete=models.CASCADE, related_name='exchanges')
    quantity = models.IntegerField(default=1)
    total_points = models.IntegerField()
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', '处理中'),
            ('completed', '已完成'),
            ('cancelled', '已取消')
        ],
        default='pending'
    )
    created_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.account.user.username} 兑换 {self.item.name} x{self.quantity}"

class PointsTask(models.Model):
    """积分任务"""
    title = models.CharField(max_length=100)
    description = models.TextField()
    points_reward = models.IntegerField()
    task_type = models.CharField(
        max_length=50,
        choices=[
            ('daily', '每日任务'),
            ('weekly', '每周任务'),
            ('onetime', '一次性任务'),
            ('special', '特别任务')
        ]
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} - {self.points_reward}积分"

class TaskCompletion(models.Model):
    """任务完成记录"""
    account = models.ForeignKey(PointsAccount, on_delete=models.CASCADE, related_name='completed_tasks')
    task = models.ForeignKey(PointsTask, on_delete=models.CASCADE, related_name='completions')
    completed_at = models.DateTimeField(default=now)
    
    class Meta:
        unique_together = ('account', 'task', 'completed_at')  # 防止同一天重复完成任务
        
    def __str__(self):
        return f"{self.account.user.username} 完成 {self.task.title}" 