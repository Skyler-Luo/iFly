"""
Core 模块服务层。

包含系统设置服务，提供站点信息和业务规则的管理功能。
满足 Requirements 1.1-1.5, 2.1-2.5
"""
import re
from typing import Optional
from .models import SystemSettings, SettingsHistory


class SettingsService:
    """
    系统设置服务类
    
    提供站点设置和业务规则的读取、更新功能。
    满足 Requirements 1, 2
    """
    
    @staticmethod
    def get_site_settings() -> dict:
        """
        获取站点设置
        
        满足 Requirements 1.1-1.3:
        - 1.1: 站点名称、Logo URL、Favicon
        - 1.2: 联系邮箱、电话、地址
        - 1.3: 版权文本、ICP备案号
        
        Returns:
            dict: 包含所有站点设置的字典
        """
        return {
            'site_name': SystemSettings.get_value('site', 'site_name', 'iFly'),
            'logo_url': SystemSettings.get_value('site', 'logo_url', ''),
            'favicon_url': SystemSettings.get_value('site', 'favicon_url', ''),
            'contact_email': SystemSettings.get_value('site', 'contact_email', ''),
            'contact_phone': SystemSettings.get_value('site', 'contact_phone', ''),
            'contact_address': SystemSettings.get_value('site', 'contact_address', ''),
            'copyright_text': SystemSettings.get_value('site', 'copyright_text', ''),
            'icp_number': SystemSettings.get_value('site', 'icp_number', ''),
        }
    
    @staticmethod
    def get_business_rules() -> dict:
        """
        获取业务规则设置
        
        满足 Requirements 2.1-2.4:
        - 2.1: 订单支付超时时间（默认30分钟）
        - 2.2: 退款费率
        - 2.3: 改签费率
        - 2.4: 值机开放时间（起飞前小时数）
        
        Returns:
            dict: 包含所有业务规则的字典
        """
        return {
            'payment_timeout_minutes': int(
                SystemSettings.get_value('business', 'payment_timeout', '30')
            ),
            'refund_fee_rate': float(
                SystemSettings.get_value('business', 'refund_fee_rate', '0.05')
            ),
            'reschedule_fee_rate': float(
                SystemSettings.get_value('business', 'reschedule_fee_rate', '0.1')
            ),
            'checkin_hours_before': int(
                SystemSettings.get_value('business', 'checkin_hours', '24')
            ),
        }

    
    @staticmethod
    def update_site_settings(data: dict, user=None) -> dict:
        """
        更新站点设置
        
        满足 Requirements 1.4, 1.5:
        - 1.4: 设置更新后立即生效，无需重启
        - 1.5: 验证 Logo 和 Favicon 的 URL 格式
        
        Args:
            data: 要更新的设置数据字典
            user: 执行更新的用户对象
            
        Returns:
            dict: 包含 success 状态和可能的 errors 信息
        """
        errors = {}
        
        # URL 格式验证 - 满足 Requirement 1.5
        url_fields = ['logo_url', 'favicon_url']
        for url_field in url_fields:
            if url_field in data and data[url_field]:
                if not SettingsService.validate_url(data[url_field]):
                    errors[url_field] = 'Invalid URL format'
        
        if errors:
            return {'success': False, 'errors': errors}
        
        # 更新设置 - 满足 Requirement 1.4 (立即生效)
        for key, value in data.items():
            SystemSettings.set_value('site', key, str(value), user)
        
        return {'success': True}
    
    @staticmethod
    def update_business_rules(data: dict, user=None) -> dict:
        """
        更新业务规则设置
        
        满足 Requirement 2.5:
        - 更新时自动记录变更历史（通过 SystemSettings.set_value 实现）
        
        Args:
            data: 要更新的业务规则数据字典
            user: 执行更新的用户对象
            
        Returns:
            dict: 包含 success 状态
        """
        # 字段映射：前端字段名 -> 数据库键名
        field_mapping = {
            'payment_timeout_minutes': 'payment_timeout',
            'refund_fee_rate': 'refund_fee_rate',
            'reschedule_fee_rate': 'reschedule_fee_rate',
            'checkin_hours_before': 'checkin_hours',
        }
        
        for field, db_key in field_mapping.items():
            if field in data:
                # set_value 会自动记录变更历史 - 满足 Requirement 2.5
                SystemSettings.set_value('business', db_key, str(data[field]), user)
        
        return {'success': True}
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """
        验证 URL 格式
        
        满足 Requirement 1.5:
        - 支持 http://, https:// 协议
        - 支持相对路径 (以 / 开头)
        - 空字符串视为有效（允许清空 URL）
        
        Args:
            url: 要验证的 URL 字符串
            
        Returns:
            bool: URL 格式是否有效
        """
        if not url:
            return True
        
        # 支持 http://, https://, 或相对路径 /
        pattern = r'^(https?://|/)[^\s]*$'
        return bool(re.match(pattern, url))
    
    @staticmethod
    def get_settings_history(
        category: Optional[str] = None, 
        limit: int = 50
    ) -> list:
        """
        获取设置变更历史
        
        满足 Requirement 2.5:
        - 记录变更的管理员用户和时间戳
        
        Args:
            category: 可选的分类过滤（'site' 或 'business'）
            limit: 返回记录数量限制
            
        Returns:
            list: 变更历史记录列表
        """
        queryset = SettingsHistory.objects.select_related('setting', 'changed_by')
        
        if category:
            queryset = queryset.filter(setting__category=category)
        
        return list(queryset[:limit])
