from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from notifications.models import Notification
from notifications.services import (
    create_notification,
    create_order_notification,
    create_payment_notification,
    create_refund_notification,
    create_flight_notification
)
from django.utils import timezone
import random

User = get_user_model()

class Command(BaseCommand):
    help = '生成测试通知数据'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=5,
            help='每种通知类型的数量'
        )
        parser.add_argument(
            '--user-id',
            type=int,
            default=None,
            help='指定用户ID，不提供则为所有用户生成通知'
        )

    def handle(self, *args, **options):
        count = options['count']
        user_id = options['user_id']
        
        # 获取用户
        if user_id:
            users = User.objects.filter(id=user_id)
            if not users.exists():
                self.stdout.write(self.style.ERROR(f'用户ID {user_id} 不存在'))
                return
        else:
            users = User.objects.all()
            if not users.exists():
                self.stdout.write(self.style.ERROR('系统中没有用户'))
                return
        
        total_notifications = 0
        
        # 为每个用户生成通知
        for user in users:
            self.stdout.write(f'为用户 {user.username} 生成通知...')
            
            # 1. 生成系统通知
            for i in range(count):
                create_notification(
                    user=user,
                    title=f'系统维护通知 #{i+1}',
                    message=f'亲爱的用户，我们将于{timezone.now().date()} 22:00-23:00进行系统维护，请提前安排行程。',
                    notif_type='system'
                )
            total_notifications += count
            
            # 2. 生成订单通知
            for i in range(count):
                order_num = f'ORD{random.randint(10000, 99999)}'
                statuses = ['paid', 'ticketed', 'refunded', 'canceled']
                status = random.choice(statuses)
                mock_order = type('MockOrder', (), {'order_number': order_num})
                create_order_notification(
                    user=user,
                    order=mock_order,
                    status=status
                )
            total_notifications += count
            
            # 3. 生成支付通知
            for i in range(count):
                order_num = f'ORD{random.randint(10000, 99999)}'
                price = random.randint(500, 2000)
                mock_order = type('MockOrder', (), {
                    'order_number': order_num,
                    'total_price': price
                })
                create_payment_notification(
                    user=user,
                    order=mock_order,
                    payment_status='success'
                )
            total_notifications += count
            
            # 4. 生成退款通知
            for i in range(count):
                order_num = f'ORD{random.randint(10000, 99999)}'
                price = random.randint(500, 2000)
                mock_order = type('MockOrder', (), {
                    'order_number': order_num
                })
                status = random.choice(['processing', 'completed'])
                create_refund_notification(
                    user=user,
                    order=mock_order,
                    refund_status=status,
                    refund_amount=price if status == 'completed' else None
                )
            total_notifications += count
            
            # 5. 生成航班通知
            for i in range(count):
                flight_num = f'{random.choice(["CA", "MU", "CZ"])}{random.randint(1000, 9999)}'
                cities = ['北京', '上海', '广州', '深圳', '成都', '杭州', '西安']
                departure = random.choice(cities)
                arrival = random.choice([c for c in cities if c != departure])
                status = random.choice(['准时起飞', '延误', '登机中', '已取消', '改变登机口'])
                mock_flight = type('MockFlight', (), {
                    'flight_number': flight_num,
                    'departure_city': departure,
                    'arrival_city': arrival
                })
                create_flight_notification(
                    user=user,
                    flight=mock_flight,
                    status_change=status
                )
            total_notifications += count
            
        self.stdout.write(self.style.SUCCESS(f'成功为{users.count()}个用户生成了{total_notifications}条通知')) 