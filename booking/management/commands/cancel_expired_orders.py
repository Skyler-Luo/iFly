"""
超时订单取消管理命令。

用于手动触发超时订单检查和取消操作。
可通过 cron 或 celery beat 定期执行。

Usage:
    python manage.py cancel_expired_orders
    python manage.py cancel_expired_orders --dry-run
"""
from django.core.management.base import BaseCommand

from booking.services import TimeoutService


class Command(BaseCommand):
    """取消超时订单的管理命令。"""
    
    help = '检查并取消所有超时的待支付订单'
    
    def add_arguments(self, parser):
        """添加命令行参数。"""
        parser.add_argument(
            '--dry-run',
            action='store_true',
            dest='dry_run',
            help='仅显示将要取消的订单，不执行实际取消操作',
        )
    
    def handle(self, *args, **options):
        """执行命令。"""
        dry_run = options.get('dry_run', False)
        
        if dry_run:
            self.stdout.write(self.style.WARNING('=== 试运行模式 ==='))
            expired_orders = TimeoutService.get_expired_orders()
            count = expired_orders.count()
            
            if count == 0:
                self.stdout.write(self.style.SUCCESS('没有超时的待支付订单'))
                return
            
            self.stdout.write(f'发现 {count} 个超时订单:')
            for order in expired_orders:
                ticket_count = order.tickets.filter(status='valid').count()
                self.stdout.write(
                    f'  - 订单 {order.order_number}: '
                    f'创建于 {order.created_at}, '
                    f'超时于 {order.expires_at}, '
                    f'包含 {ticket_count} 张机票'
                )
            return
        
        self.stdout.write('开始处理超时订单...')
        
        result = TimeoutService.process_all_expired_orders()
        
        processed = result['processed']
        failed = result['failed']
        errors = result['errors']
        
        if processed > 0:
            self.stdout.write(
                self.style.SUCCESS(f'成功取消 {processed} 个超时订单')
            )
        
        if failed > 0:
            self.stdout.write(
                self.style.ERROR(f'取消失败 {failed} 个订单')
            )
            for error in errors:
                self.stdout.write(self.style.ERROR(f'  - {error}'))
        
        if processed == 0 and failed == 0:
            self.stdout.write(self.style.SUCCESS('没有超时的待支付订单'))
