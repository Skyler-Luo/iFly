from django.utils import timezone
from django.db.models import Sum, Count
from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from datetime import datetime, timedelta

from .models import (
    PointsAccount,
    PointsTransaction,
    ExchangeItem,
    ExchangeRecord,
    PointsTask,
    TaskCompletion
)
from .serializers import (
    PointsAccountSerializer,
    PointsTransactionSerializer,
    ExchangeItemSerializer,
    ExchangeRecordSerializer,
    ExchangeRequestSerializer,
    PointsTaskSerializer,
    TaskCompletionSerializer,
    MemberLevelProgressSerializer
)

# 定义会员等级所需积分
LEVEL_THRESHOLDS = {
    'regular': 0,
    'silver': 5000,
    'gold': 20000,
    'platinum': 50000
}

# 等级顺序
LEVEL_ORDER = ['regular', 'silver', 'gold', 'platinum']

class UserPointsView(APIView):
    """获取用户积分信息"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        # 获取或创建积分账户
        account, created = PointsAccount.objects.get_or_create(
            user=user,
            defaults={
                'points_balance': 0,
                'lifetime_points': 0,
                'member_level': 'regular'
            }
        )
        
        serializer = PointsAccountSerializer(account)
        return Response(serializer.data)

class PointsHistoryView(APIView):
    """获取用户积分明细"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        try:
            account = PointsAccount.objects.get(user=user)
        except PointsAccount.DoesNotExist:
            return Response({"detail": "积分账户不存在"}, status=status.HTTP_404_NOT_FOUND)
            
        # 获取查询参数
        transaction_type = request.query_params.get('type')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        # 筛选事务
        transactions = PointsTransaction.objects.filter(account=account)
        
        if transaction_type:
            transactions = transactions.filter(transaction_type=transaction_type)
        if start_date:
            transactions = transactions.filter(created_at__gte=start_date)
        if end_date:
            transactions = transactions.filter(created_at__lte=end_date)
            
        # 按时间倒序排列
        transactions = transactions.order_by('-created_at')
        
        serializer = PointsTransactionSerializer(transactions, many=True)
        return Response(serializer.data)

class PointsOverviewView(APIView):
    """获取积分摘要"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        try:
            account = PointsAccount.objects.get(user=user)
        except PointsAccount.DoesNotExist:
            return Response({"detail": "积分账户不存在"}, status=status.HTTP_404_NOT_FOUND)
            
        # 获取积分收支统计
        now = timezone.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # 本月收入
        month_earned = PointsTransaction.objects.filter(
            account=account,
            points__gt=0,
            created_at__gte=month_start
        ).aggregate(total=Sum('points'))['total'] or 0
        
        # 本月支出
        month_spent = PointsTransaction.objects.filter(
            account=account,
            points__lt=0,
            created_at__gte=month_start
        ).aggregate(total=Sum('points'))['total'] or 0
        
        # 即将过期积分（假设90天后过期）
        expiring_soon = 0  # 实际应该从即将过期的积分记录中计算
        
        # 各类交易统计
        transaction_stats = PointsTransaction.objects.filter(
            account=account
        ).values('transaction_type').annotate(
            count=Count('id'),
            total=Sum('points')
        )
        
        return Response({
            'current_balance': account.points_balance,
            'lifetime_points': account.lifetime_points,
            'member_level': account.member_level,
            'month_earned': month_earned,
            'month_spent': abs(month_spent),  # 转为正数显示
            'expiring_soon': expiring_soon,
            'transaction_stats': transaction_stats
        })

class ExchangeItemViewSet(viewsets.ReadOnlyModelViewSet):
    """积分商品查询"""
    queryset = ExchangeItem.objects.filter(is_active=True)
    serializer_class = ExchangeItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # 按分类筛选
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)
            
        # 按价格区间筛选
        min_points = self.request.query_params.get('min_points')
        max_points = self.request.query_params.get('max_points')
        
        if min_points:
            queryset = queryset.filter(points_required__gte=min_points)
        if max_points:
            queryset = queryset.filter(points_required__lte=max_points)
            
        # 只显示有库存的
        in_stock = self.request.query_params.get('in_stock')
        if in_stock and in_stock.lower() == 'true':
            queryset = queryset.filter(available_stock__gt=0)
            
        # 默认按积分要求排序
        return queryset.order_by('points_required')

class ExchangeView(APIView):
    """积分兑换"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        user = request.user
        
        try:
            account = PointsAccount.objects.get(user=user)
        except PointsAccount.DoesNotExist:
            return Response({"detail": "积分账户不存在"}, status=status.HTTP_404_NOT_FOUND)
            
        serializer = ExchangeRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        # 获取验证后的数据
        item = serializer.validated_data['item']
        quantity = serializer.validated_data['quantity']
        points_required = serializer.validated_data['points_required']
        
        # 检查积分是否足够
        if account.points_balance < points_required:
            return Response({"detail": "积分不足"}, status=status.HTTP_400_BAD_REQUEST)
            
        # 创建兑换记录
        exchange_record = ExchangeRecord.objects.create(
            account=account,
            item=item,
            quantity=quantity,
            total_points=points_required,
            status='completed'  # 默认为已完成，实际可能需要审核或发货
        )
        
        # 扣减积分
        account.points_balance -= points_required
        account.save()
        
        # 记录积分交易
        PointsTransaction.objects.create(
            account=account,
            points=-points_required,
            transaction_type='exchange',
            description=f'兑换: {item.name} x{quantity}',
            reference_id=str(exchange_record.id)
        )
        
        # 减少商品库存
        item.available_stock -= quantity
        item.save()
        
        # 返回兑换结果
        exchange_serializer = ExchangeRecordSerializer(exchange_record)
        return Response(exchange_serializer.data)

class PointsTaskViewSet(viewsets.ReadOnlyModelViewSet):
    """积分任务"""
    queryset = PointsTask.objects.filter(is_active=True)
    serializer_class = PointsTaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        try:
            account = PointsAccount.objects.get(user=user)
        except PointsAccount.DoesNotExist:
            return PointsTask.objects.none()
            
        queryset = super().get_queryset()
        
        # 获取任务类型过滤
        task_type = self.request.query_params.get('type')
        if task_type:
            queryset = queryset.filter(task_type=task_type)
            
        # 标记任务是否已完成
        for task in queryset:
            if task.task_type == 'daily':
                # 检查今天是否已完成
                today = timezone.now().date()
                task.is_completed = TaskCompletion.objects.filter(
                    account=account,
                    task=task,
                    completed_at__date=today
                ).exists()
            elif task.task_type == 'weekly':
                # 检查本周是否已完成
                today = timezone.now().date()
                week_start = today - timedelta(days=today.weekday())
                task.is_completed = TaskCompletion.objects.filter(
                    account=account,
                    task=task,
                    completed_at__date__gte=week_start
                ).exists()
            else:
                # 一次性任务检查是否有完成记录
                task.is_completed = TaskCompletion.objects.filter(
                    account=account,
                    task=task
                ).exists()
                
        return queryset

class CompleteTaskView(APIView):
    """完成积分任务"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, task_id):
        user = request.user
        
        try:
            account = PointsAccount.objects.get(user=user)
            task = PointsTask.objects.get(id=task_id, is_active=True)
        except PointsAccount.DoesNotExist:
            return Response({"detail": "积分账户不存在"}, status=status.HTTP_404_NOT_FOUND)
        except PointsTask.DoesNotExist:
            return Response({"detail": "任务不存在"}, status=status.HTTP_404_NOT_FOUND)
            
        # 检查任务是否已完成
        today = timezone.now().date()
        
        if task.task_type == 'daily':
            # 检查今天是否已完成
            if TaskCompletion.objects.filter(
                account=account,
                task=task,
                completed_at__date=today
            ).exists():
                return Response({"detail": "今天已完成此任务"}, status=status.HTTP_400_BAD_REQUEST)
        elif task.task_type == 'weekly':
            # 检查本周是否已完成
            week_start = today - timedelta(days=today.weekday())
            if TaskCompletion.objects.filter(
                account=account,
                task=task,
                completed_at__date__gte=week_start
            ).exists():
                return Response({"detail": "本周已完成此任务"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            # 一次性任务检查是否有完成记录
            if TaskCompletion.objects.filter(
                account=account,
                task=task
            ).exists():
                return Response({"detail": "已完成此任务"}, status=status.HTTP_400_BAD_REQUEST)
                
        # 创建任务完成记录
        completion = TaskCompletion.objects.create(
            account=account,
            task=task
        )
        
        # 增加积分
        account.points_balance += task.points_reward
        account.lifetime_points += task.points_reward
        
        # 更新会员等级
        self._update_member_level(account)
        account.save()
        
        # 记录积分交易
        PointsTransaction.objects.create(
            account=account,
            points=task.points_reward,
            transaction_type='task_completion',
            description=f'完成任务: {task.title}',
            reference_id=str(completion.id)
        )
        
        # 返回完成结果
        return Response({
            "task_title": task.title,
            "points_earned": task.points_reward,
            "current_balance": account.points_balance,
            "completed_at": completion.completed_at
        })
        
    def _update_member_level(self, account):
        """根据累计积分更新会员等级"""
        lifetime_points = account.lifetime_points
        
        for level, threshold in sorted(LEVEL_THRESHOLDS.items(), key=lambda x: x[1], reverse=True):
            if lifetime_points >= threshold:
                account.member_level = level
                break

class MemberLevelView(APIView):
    """会员等级信息"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        # 返回所有会员等级及其特权信息
        levels = []
        
        for level in LEVEL_ORDER:
            level_info = {
                'level': level,
                'name': self._get_level_name(level),
                'threshold': LEVEL_THRESHOLDS[level],
                'benefits': self._get_level_benefits(level)
            }
            levels.append(level_info)
            
        return Response({
            'levels': levels
        })
        
    def _get_level_name(self, level):
        """获取等级显示名称"""
        names = {
            'regular': '普通会员',
            'silver': '银卡会员',
            'gold': '金卡会员',
            'platinum': '白金会员'
        }
        return names.get(level, level)
        
    def _get_level_benefits(self, level):
        """获取等级特权列表"""
        benefits = {
            'regular': [
                '基础积分权益',
                '正常积分累计'
            ],
            'silver': [
                '基础积分权益',
                '积分累计1.2倍',
                '生日双倍积分',
                '优先值机'
            ],
            'gold': [
                '基础积分权益',
                '积分累计1.5倍',
                '生日双倍积分',
                '优先值机',
                '贵宾休息室2次/年',
                '超重行李5kg'
            ],
            'platinum': [
                '基础积分权益',
                '积分累计2倍',
                '生日三倍积分',
                '优先值机',
                '贵宾休息室不限次',
                '超重行李10kg',
                '免费升舱1次/年'
            ]
        }
        return benefits.get(level, [])

class LevelProgressView(APIView):
    """会员等级进度"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        try:
            account = PointsAccount.objects.get(user=user)
        except PointsAccount.DoesNotExist:
            return Response({"detail": "积分账户不存在"}, status=status.HTTP_404_NOT_FOUND)
            
        current_level = account.member_level
        lifetime_points = account.lifetime_points
        
        # 获取当前等级和下一等级信息
        current_idx = LEVEL_ORDER.index(current_level)
        next_level = LEVEL_ORDER[current_idx + 1] if current_idx < len(LEVEL_ORDER) - 1 else None
        
        # 计算进度
        current_threshold = LEVEL_THRESHOLDS[current_level]
        if next_level:
            next_threshold = LEVEL_THRESHOLDS[next_level]
            points_needed = next_threshold - current_threshold
            points_earned = lifetime_points - current_threshold
            progress = min(100, (points_earned / points_needed) * 100) if points_needed > 0 else 100
        else:
            # 已是最高等级
            points_needed = 0
            progress = 100
            
        serializer = MemberLevelProgressSerializer(data={
            'current_level': current_level,
            'next_level': next_level,
            'current_points': lifetime_points,
            'points_needed': points_needed if next_level else 0,
            'progress_percentage': progress
        })
        
        serializer.is_valid()  # 这里无需验证，数据由我们构造
        return Response(serializer.data)

class CheckInView(APIView):
    """每日签到获取积分"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        user = request.user
        
        try:
            account = PointsAccount.objects.get(user=user)
        except PointsAccount.DoesNotExist:
            # 创建积分账户
            account = PointsAccount.objects.create(
                user=user,
                points_balance=0,
                lifetime_points=0,
                member_level='regular'
            )
            
        # 检查今天是否已经签到
        today = timezone.now().date()
        has_checked_in = PointsTransaction.objects.filter(
            account=account,
            transaction_type='check_in',
            created_at__date=today
        ).exists()
        
        if has_checked_in:
            return Response({"detail": "今天已经签到"}, status=status.HTTP_400_BAD_REQUEST)
            
        # 计算签到积分奖励
        points_reward = 10  # 基础签到奖励
        
        # 检查连续签到（实际逻辑应该更复杂，这里简化处理）
        yesterday = today - timedelta(days=1)
        continuous_days = 1
        
        # 检查昨天是否签到
        if PointsTransaction.objects.filter(
            account=account,
            transaction_type='check_in',
            created_at__date=yesterday
        ).exists():
            # 简单处理，实际应该递归检查之前所有的连续签到
            continuous_days = 2
            points_reward += 5  # 连续签到额外奖励
            
        # 记录签到及奖励积分
        account.points_balance += points_reward
        account.lifetime_points += points_reward
        account.save()
        
        transaction = PointsTransaction.objects.create(
            account=account,
            points=points_reward,
            transaction_type='check_in',
            description=f'每日签到奖励 (连续{continuous_days}天)'
        )
        
        return Response({
            "success": True,
            "points_earned": points_reward,
            "continuous_days": continuous_days,
            "current_balance": account.points_balance,
            "checked_in_at": transaction.created_at
        })

class ExpiringPointsView(APIView):
    """即将过期的积分"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        try:
            account = PointsAccount.objects.get(user=user)
        except PointsAccount.DoesNotExist:
            return Response({"detail": "积分账户不存在"}, status=status.HTTP_404_NOT_FOUND)
            
        # 实际应该从积分有效期记录中查询
        # 这里模拟返回数据
        today = timezone.now().date()
        expiring_points = [
            {
                'expiry_date': (today + timedelta(days=30)).isoformat(),
                'points': 500,
                'source': '航班购买'
            },
            {
                'expiry_date': (today + timedelta(days=60)).isoformat(),
                'points': 200,
                'source': '促销活动'
            }
        ]
        
        # 汇总
        total_expiring = sum(item['points'] for item in expiring_points)
        
        return Response({
            'expiring_points': expiring_points,
            'total_expiring': total_expiring
        }) 