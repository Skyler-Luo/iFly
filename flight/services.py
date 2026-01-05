"""
航班服务模块。

提供航班状态自动更新、通知发送等业务逻辑。
"""
import logging
from datetime import timedelta
from django.utils import timezone
from django.db import transaction
from django.db.models import Q

from .models import Flight

logger = logging.getLogger(__name__)


class FlightStatusService:
    """航班状态管理服务"""
    
    @classmethod
    def update_departed_flights(cls) -> int:
        """
        将已过起飞时间的航班标记为已起飞。
        
        Returns:
            更新的航班数量
        """
        now = timezone.now()
        flights = Flight.objects.filter(
            departure_time__lte=now,
            status='scheduled'
        )
        count = flights.update(status='departed')
        
        if count > 0:
            logger.info(f"已将 {count} 个航班状态更新为已起飞")
        
        return count
    
    @classmethod
    def update_full_flights(cls) -> int:
        """
        将座位售罄的航班标记为已满。
        
        Returns:
            更新的航班数量
        """
        flights = Flight.objects.filter(
            available_seats=0,
            status='scheduled'
        )
        count = flights.update(status='full')
        
        if count > 0:
            logger.info(f"已将 {count} 个航班状态更新为已满")
        
        return count
    
    @classmethod
    def restore_available_flights(cls) -> int:
        """
        将有空位但状态为已满的航班恢复为正常。
        
        Returns:
            更新的航班数量
        """
        flights = Flight.objects.filter(
            available_seats__gt=0,
            status='full'
        )
        count = flights.update(status='scheduled')
        
        if count > 0:
            logger.info(f"已将 {count} 个航班状态恢复为正常")
        
        return count
    
    @classmethod
    def run_all_updates(cls) -> dict:
        """
        执行所有状态更新任务。
        
        Returns:
            各任务更新数量的字典
        """
        results = {
            'departed': cls.update_departed_flights(),
            'full': cls.update_full_flights(),
            'restored': cls.restore_available_flights(),
        }
        
        total = sum(results.values())
        if total > 0:
            logger.info(f"航班状态更新完成: {results}")
        
        return results
    
    @classmethod
    def get_status_summary(cls) -> dict:
        """
        获取航班状态统计摘要。
        
        Returns:
            各状态航班数量
        """
        from django.db.models import Count
        
        stats = Flight.objects.values('status').annotate(count=Count('id'))
        return {item['status']: item['count'] for item in stats}
