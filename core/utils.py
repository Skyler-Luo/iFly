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

