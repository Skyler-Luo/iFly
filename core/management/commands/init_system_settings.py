"""
初始化系统设置管理命令

满足 Requirements 1.1-1.3, 2.1-2.4
"""
from django.core.management.base import BaseCommand
from django.db import transaction

from core.models import SystemSettings


class Command(BaseCommand):
    help = '初始化默认系统设置'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='强制重置所有设置为默认值',
        )

    def handle(self, *args, **options):
        force = options.get('force', False)
        
        self.stdout.write('开始初始化系统设置...')
        
        try:
            with transaction.atomic():
                # 初始化站点设置 - 满足 Requirements 1.1-1.3
                site_settings_created = self.init_site_settings(force)
                
                # 初始化业务规则 - 满足 Requirements 2.1-2.4
                business_settings_created = self.init_business_rules(force)
                
            total_created = site_settings_created + business_settings_created
            
            if total_created > 0:
                self.stdout.write(
                    self.style.SUCCESS(f'成功初始化 {total_created} 项系统设置!')
                )
            else:
                self.stdout.write(
                    self.style.WARNING('所有设置已存在，未创建新设置。使用 --force 强制重置。')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'初始化系统设置失败: {str(e)}')
            )
            raise

    def init_site_settings(self, force: bool) -> int:
        """
        初始化站点设置
        
        满足 Requirements 1.1-1.3:
        - 1.1: 站点名称、Logo URL、Favicon
        - 1.2: 联系邮箱、电话、地址
        - 1.3: 版权信息、ICP备案号
        """
        site_defaults = [
            # Requirement 1.1 - 站点基本信息
            {
                'key': 'site_name',
                'value': 'iFly 飞机订票系统',
                'description': '站点名称'
            },
            {
                'key': 'logo_url',
                'value': '/static/images/logo.png',
                'description': 'Logo 图片 URL'
            },
            {
                'key': 'favicon_url',
                'value': '/favicon.ico',
                'description': 'Favicon 图标 URL'
            },
            # Requirement 1.2 - 联系方式
            {
                'key': 'contact_email',
                'value': 'support@ifly.example.com',
                'description': '联系邮箱'
            },
            {
                'key': 'contact_phone',
                'value': '400-888-8888',
                'description': '联系电话'
            },
            {
                'key': 'contact_address',
                'value': '北京市朝阳区xxx大厦',
                'description': '联系地址'
            },
            # Requirement 1.3 - 版权信息
            {
                'key': 'copyright_text',
                'value': '© 2024 iFly. All rights reserved.',
                'description': '版权声明文本'
            },
            {
                'key': 'icp_number',
                'value': '京ICP备xxxxxxxx号',
                'description': 'ICP备案号'
            },
        ]
        
        created_count = 0
        for setting_data in site_defaults:
            created = self._create_or_update_setting(
                category='site',
                key=setting_data['key'],
                value=setting_data['value'],
                description=setting_data['description'],
                force=force
            )
            if created:
                created_count += 1
                self.stdout.write(f"  ✓ 站点设置: {setting_data['key']}")
        
        return created_count

    def init_business_rules(self, force: bool) -> int:
        """
        初始化业务规则设置
        
        满足 Requirements 2.1-2.4:
        - 2.1: 订单支付超时时间（默认30分钟）
        - 2.2: 退款费率
        - 2.3: 改签费率
        - 2.4: 值机开放时间
        """
        business_defaults = [
            # Requirement 2.1 - 支付超时
            {
                'key': 'payment_timeout',
                'value': '30',
                'description': '订单支付超时时间（分钟）'
            },
            # Requirement 2.2 - 退款费率
            {
                'key': 'refund_fee_rate',
                'value': '0.05',
                'description': '退款手续费率（0-1之间的小数）'
            },
            # Requirement 2.3 - 改签费率
            {
                'key': 'reschedule_fee_rate',
                'value': '0.1',
                'description': '改签手续费率（0-1之间的小数）'
            },
            # Requirement 2.4 - 值机开放时间
            {
                'key': 'checkin_hours',
                'value': '24',
                'description': '值机开放时间（起飞前小时数）'
            },
            # 额外业务规则
            {
                'key': 'max_passengers_per_order',
                'value': '9',
                'description': '单笔订单最大乘客数'
            },
            {
                'key': 'booking_advance_days',
                'value': '90',
                'description': '可提前预订天数'
            },
        ]
        
        created_count = 0
        for setting_data in business_defaults:
            created = self._create_or_update_setting(
                category='business',
                key=setting_data['key'],
                value=setting_data['value'],
                description=setting_data['description'],
                force=force
            )
            if created:
                created_count += 1
                self.stdout.write(f"  ✓ 业务规则: {setting_data['key']}")
        
        return created_count

    def _create_or_update_setting(
        self, 
        category: str, 
        key: str, 
        value: str, 
        description: str,
        force: bool
    ) -> bool:
        """
        创建或更新单个设置项
        
        Args:
            category: 设置分类
            key: 设置键
            value: 设置值
            description: 设置描述
            force: 是否强制更新
            
        Returns:
            bool: 是否创建/更新了设置
        """
        existing = SystemSettings.objects.filter(
            category=category, 
            key=key
        ).first()
        
        if existing and not force:
            # 设置已存在且不强制更新
            return False
        
        if existing and force:
            # 强制更新现有设置
            existing.value = value
            existing.description = description
            existing.save()
            return True
        
        # 创建新设置
        SystemSettings.objects.create(
            category=category,
            key=key,
            value=value,
            description=description
        )
        return True
