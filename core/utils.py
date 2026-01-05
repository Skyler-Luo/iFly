"""
通用工具函数，用于消除重复代码
"""
from django.utils import timezone
from datetime import timedelta, datetime


def mask_id_number(id_number: str) -> str:
    """
    证件号码脱敏函数。
    
    保留前4位和后4位，中间用星号替代，脱敏后长度与原长度相同。
    如果证件号码长度小于等于8位，则全部用星号替代。
    
    Args:
        id_number: 原始证件号码
        
    Returns:
        脱敏后的证件号码
        
    Examples:
        >>> mask_id_number('110101199001011234')
        '1101**********1234'
        >>> mask_id_number('G12345678')
        'G123*5678'
        >>> mask_id_number('12345678')
        '********'
        >>> mask_id_number('')
        ''
    """
    if not id_number:
        return ''
    
    length = len(id_number)
    if length <= 8:
        return '*' * length
    
    # 保留前4位和后4位，中间用星号替代
    middle_length = length - 8
    return id_number[:4] + '*' * middle_length + id_number[-4:]


def calculate_boarding_time(departure_time: datetime) -> datetime:
    """
    计算登机时间。
    
    登机时间 = 起飞时间 - 30 分钟
    
    Args:
        departure_time: 起飞时间（datetime 对象）
        
    Returns:
        登机时间（datetime 对象）
        
    Examples:
        >>> from datetime import datetime
        >>> departure = datetime(2026, 1, 15, 8, 30)
        >>> calculate_boarding_time(departure)
        datetime.datetime(2026, 1, 15, 8, 0)
    """
    if not departure_time:
        return None
    
    return departure_time - timedelta(minutes=30)


class TimeUtils:
    """时间处理工具类"""
    
    @staticmethod
    def get_month_start():
        """获取当月开始时间"""
        now = timezone.now()
        return now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    @staticmethod
    def get_week_start():
        """获取当周开始时间"""
        today = timezone.now().date()
        return today - timedelta(days=today.weekday())
    
    @staticmethod
    def get_today():
        """获取今天日期"""
        return timezone.now().date()
    
    @staticmethod
    def is_same_day(date1, date2):
        """判断两个日期是否是同一天"""
        return date1.date() == date2.date()
    
    @staticmethod
    def is_same_week(date1, date2):
        """判断两个日期是否在同一周"""
        week_start1 = date1.date() - timedelta(days=date1.weekday())
        week_start2 = date2.date() - timedelta(days=date2.weekday())
        return week_start1 == week_start2


class ValidationUtils:
    """验证工具类"""
    
    @staticmethod
    def validate_promo_code(promotion):
        """验证优惠码是否有效"""
        if not promotion.is_active:
            return False, "优惠码已禁用"
        
        if promotion.usage_limit > 0 and promotion.used_count >= promotion.usage_limit:
            return False, "优惠码已达到使用上限"
        
        current_time = timezone.now()
        if not (promotion.start_date <= current_time <= promotion.end_date):
            return False, "优惠码不在有效期内"
        
        return True, "优惠码有效"
    
    @staticmethod
    def validate_order_status_for_payment(order):
        """验证订单状态是否允许支付"""
        if order.status != 'pending':
            return False, "订单状态不允许支付"
        return True, "订单状态允许支付"
    
    @staticmethod
    def validate_order_status_for_cancel(order):
        """验证订单状态是否允许取消"""
        if order.status not in ['pending', 'paid']:
            return False, "订单状态不允许取消"
        return True, "订单状态允许取消"


class ResponseUtils:
    """响应工具类"""
    
    @staticmethod
    def success_response(data=None, message="操作成功"):
        """成功响应"""
        result = {"success": True, "message": message}
        if data is not None:
            result["data"] = data
        return result
    
    @staticmethod
    def error_response(message="操作失败", code=None):
        """错误响应"""
        result = {"success": False, "message": message}
        if code is not None:
            result["code"] = code
        return result
    
    @staticmethod
    def pagination_response(data, count, page, page_size):
        """分页响应"""
        return {
            "success": True,
            "data": data,
            "pagination": {
                "count": count,
                "page": page,
                "page_size": page_size,
                "total_pages": (count + page_size - 1) // page_size
            }
        }


class QuerySetUtils:
    """查询集工具类"""
    
    @staticmethod
    def get_user_filtered_queryset(queryset, user, user_field='user'):
        """根据用户过滤查询集"""
        if hasattr(user, 'role') and user.role == 'admin':
            return queryset
        
        filter_kwargs = {user_field: user}
        return queryset.filter(**filter_kwargs)
    
    @staticmethod
    def get_date_filtered_queryset(queryset, start_date=None, end_date=None, date_field='created_at'):
        """根据日期范围过滤查询集"""
        if start_date:
            filter_kwargs = {f'{date_field}__gte': start_date}
            queryset = queryset.filter(**filter_kwargs)
        
        if end_date:
            filter_kwargs = {f'{date_field}__lte': end_date}
            queryset = queryset.filter(**filter_kwargs)
        
        return queryset
    
    @staticmethod
    def get_status_filtered_queryset(queryset, status, status_field='status'):
        """根据状态过滤查询集"""
        if status:
            filter_kwargs = {status_field: status}
            return queryset.filter(**filter_kwargs)
        return queryset
