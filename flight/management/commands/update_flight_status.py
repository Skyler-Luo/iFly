from django.core.management.base import BaseCommand
from django.utils import timezone
from flight.models import Flight

class Command(BaseCommand):
    help = '自动更新航班状态，将已过起飞时间且状态为 scheduled 的航班标记为 departed'

    def handle(self, *args, **options):
        now = timezone.now()
        flights = Flight.objects.filter(departure_time__lte=now, status='scheduled')
        count = flights.update(status='departed')
        self.stdout.write(self.style.SUCCESS(f"成功更新 {count} 个航班状态为已起飞"))        