"""
航班状态自动更新命令。

用法:
    python manage.py update_flight_status          # 执行一次更新
    python manage.py update_flight_status --daemon # 后台持续运行
    python manage.py update_flight_status --interval 300  # 自定义间隔(秒)
"""
import time
import signal
import sys
from django.core.management.base import BaseCommand
from flight.services import FlightStatusService


class Command(BaseCommand):
    help = '自动更新航班状态（已起飞、已满等）'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.running = True

    def add_arguments(self, parser):
        parser.add_argument(
            '--daemon',
            action='store_true',
            help='以守护进程模式运行，持续更新状态'
        )
        parser.add_argument(
            '--interval',
            type=int,
            default=60,
            help='守护进程模式下的更新间隔（秒），默认60秒'
        )
        parser.add_argument(
            '--summary',
            action='store_true',
            help='显示航班状态统计摘要'
        )

    def handle(self, *args, **options):
        if options['summary']:
            self.show_summary()
            return

        if options['daemon']:
            self.run_daemon(options['interval'])
        else:
            self.run_once()

    def run_once(self):
        """执行一次状态更新"""
        results = FlightStatusService.run_all_updates()
        
        total = sum(results.values())
        if total > 0:
            self.stdout.write(self.style.SUCCESS(
                f"状态更新完成: 已起飞 {results['departed']}, "
                f"已满 {results['full']}, 恢复正常 {results['restored']}"
            ))
        else:
            self.stdout.write("没有需要更新的航班")

    def run_daemon(self, interval):
        """守护进程模式"""
        self.stdout.write(self.style.SUCCESS(
            f"航班状态更新服务已启动，更新间隔: {interval}秒"
        ))
        self.stdout.write("按 Ctrl+C 停止服务")

        # 注册信号处理
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

        while self.running:
            try:
                results = FlightStatusService.run_all_updates()
                total = sum(results.values())
                
                if total > 0:
                    self.stdout.write(
                        f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] "
                        f"更新: 已起飞 {results['departed']}, "
                        f"已满 {results['full']}, 恢复 {results['restored']}"
                    )
                
                time.sleep(interval)
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"更新出错: {e}"))
                time.sleep(interval)

        self.stdout.write(self.style.SUCCESS("服务已停止"))

    def signal_handler(self, signum, frame):
        """处理停止信号"""
        self.stdout.write("\n正在停止服务...")
        self.running = False

    def show_summary(self):
        """显示状态统计"""
        summary = FlightStatusService.get_status_summary()
        
        self.stdout.write("\n航班状态统计:")
        self.stdout.write("-" * 30)
        
        status_labels = {
            'scheduled': '已计划',
            'full': '已满',
            'departed': '已起飞',
            'canceled': '已取消'
        }
        
        total = 0
        for status, label in status_labels.items():
            count = summary.get(status, 0)
            total += count
            self.stdout.write(f"  {label}: {count}")
        
        self.stdout.write("-" * 30)
        self.stdout.write(f"  总计: {total}")
