"""
系统设置模块属性测试

使用 Hypothesis 进行属性测试，验证系统设置功能的正确性。
Feature: system-enhancements
"""
import uuid

from django.test import TransactionTestCase
from hypothesis import given, settings, strategies as st
from hypothesis.extra.django import TestCase as HypothesisTestCase

from accounts.models import User
from core.models import SystemSettings, SettingsHistory
from core.services import SettingsService


class SettingsRoundTripPropertyTest(HypothesisTestCase):
    """
    设置存取一致性属性测试
    
    Property 1: 设置存取一致性（Round-trip）
    Validates: Requirements 1.1-1.4, 2.1-2.4
    """
    
    def get_or_create_user(self):
        """获取或创建测试用户"""
        unique_id = uuid.uuid4().hex[:8]
        user, _ = User.objects.get_or_create(
            username=f'testuser_{unique_id}',
            defaults={
                'email': f'test_{unique_id}@example.com',
                'password': 'testpassword123'
            }
        )
        return user
    
    @given(
        category=st.sampled_from(['site', 'business']),
        key=st.text(
            min_size=1, 
            max_size=50, 
            alphabet=st.characters(
                whitelist_categories=('L', 'N'),
                whitelist_characters='_'
            )
        ).filter(lambda x: len(x.strip()) > 0),
        value=st.text(min_size=0, max_size=200)
    )
    @settings(max_examples=100)
    def test_property_1_setting_round_trip(self, category, key, value):
        """
        Property 1: 设置存取一致性（Round-trip）
        
        *For any* valid setting key-value pair, storing the value and then 
        retrieving it should return the same value.
        
        **Feature: system-enhancements, Property 1: 设置存取一致性**
        **Validates: Requirements 1.1, 1.2, 1.3, 1.4, 2.1, 2.2, 2.3, 2.4**
        """
        user = self.get_or_create_user()
        
        # 存储设置
        SystemSettings.set_value(category, key, value, user)
        
        # 读取设置
        retrieved = SystemSettings.get_value(category, key)
        
        # 验证一致性：存储后读取应返回相同的值
        self.assertEqual(
            retrieved, 
            value,
            f"Round-trip 失败: 存储 '{value}' 后读取得到 '{retrieved}'"
        )
    
    @given(
        category=st.sampled_from(['site', 'business']),
        key=st.text(
            min_size=1, 
            max_size=50, 
            alphabet=st.characters(
                whitelist_categories=('L', 'N'),
                whitelist_characters='_'
            )
        ).filter(lambda x: len(x.strip()) > 0),
        value1=st.text(min_size=0, max_size=100),
        value2=st.text(min_size=0, max_size=100)
    )
    @settings(max_examples=100)
    def test_property_1_setting_update_round_trip(self, category, key, value1, value2):
        """
        Property 1: 设置存取一致性（Round-trip）- 更新场景
        
        *For any* setting that is updated multiple times, the retrieved value 
        should always equal the most recently stored value.
        
        **Feature: system-enhancements, Property 1: 设置存取一致性**
        **Validates: Requirements 1.4, 2.1, 2.2, 2.3, 2.4**
        """
        user = self.get_or_create_user()
        
        # 第一次存储
        SystemSettings.set_value(category, key, value1, user)
        retrieved1 = SystemSettings.get_value(category, key)
        self.assertEqual(retrieved1, value1)
        
        # 第二次存储（更新）
        SystemSettings.set_value(category, key, value2, user)
        retrieved2 = SystemSettings.get_value(category, key)
        
        # 验证读取的是最新值
        self.assertEqual(
            retrieved2, 
            value2,
            f"更新后 Round-trip 失败: 存储 '{value2}' 后读取得到 '{retrieved2}'"
        )
    
    @given(
        key=st.text(
            min_size=1, 
            max_size=50, 
            alphabet=st.characters(
                whitelist_categories=('L', 'N'),
                whitelist_characters='_'
            )
        ).filter(lambda x: len(x.strip()) > 0),
        default_value=st.text(min_size=1, max_size=50)
    )
    @settings(max_examples=100)
    def test_property_1_get_value_with_default(self, key, default_value):
        """
        Property 1: 设置存取一致性 - 默认值场景
        
        *For any* non-existent setting key, get_value should return the 
        specified default value.
        
        **Feature: system-enhancements, Property 1: 设置存取一致性**
        **Validates: Requirements 1.1, 1.2, 1.3, 2.1, 2.2, 2.3, 2.4**
        """
        # 使用唯一的 key 确保不存在
        unique_key = f"nonexistent_{uuid.uuid4().hex[:8]}_{key}"
        
        # 读取不存在的设置，应返回默认值
        retrieved = SystemSettings.get_value('site', unique_key, default_value)
        
        self.assertEqual(
            retrieved, 
            default_value,
            f"默认值返回失败: 期望 '{default_value}' 但得到 '{retrieved}'"
        )
    
    def test_property_1_site_settings_service_round_trip(self):
        """
        Property 1: 设置存取一致性 - SettingsService 站点设置
        
        验证通过 SettingsService 更新站点设置后，读取应返回相同的值。
        
        **Feature: system-enhancements, Property 1: 设置存取一致性**
        **Validates: Requirements 1.1, 1.2, 1.3, 1.4**
        """
        user = self.get_or_create_user()
        
        # 准备测试数据
        test_data = {
            'site_name': f'TestSite_{uuid.uuid4().hex[:6]}',
            'contact_email': f'test_{uuid.uuid4().hex[:6]}@example.com',
            'contact_phone': '400-123-4567',
            'contact_address': '北京市朝阳区测试路123号',
            'copyright_text': '© 2026 iFly 版权所有',
            'icp_number': '京ICP备12345678号',
        }
        
        # 更新站点设置
        result = SettingsService.update_site_settings(test_data, user)
        self.assertTrue(result['success'])
        
        # 读取站点设置
        retrieved = SettingsService.get_site_settings()
        
        # 验证每个字段的一致性
        for key, expected_value in test_data.items():
            self.assertEqual(
                retrieved.get(key), 
                expected_value,
                f"站点设置 '{key}' Round-trip 失败"
            )
    
    def test_property_1_business_rules_service_round_trip(self):
        """
        Property 1: 设置存取一致性 - SettingsService 业务规则
        
        验证通过 SettingsService 更新业务规则后，读取应返回相同的值。
        
        **Feature: system-enhancements, Property 1: 设置存取一致性**
        **Validates: Requirements 2.1, 2.2, 2.3, 2.4**
        """
        user = self.get_or_create_user()
        
        # 准备测试数据
        test_data = {
            'payment_timeout_minutes': 45,
            'refund_fee_rate': 0.08,
            'reschedule_fee_rate': 0.15,
            'checkin_hours_before': 48,
        }
        
        # 更新业务规则
        result = SettingsService.update_business_rules(test_data, user)
        self.assertTrue(result['success'])
        
        # 读取业务规则
        retrieved = SettingsService.get_business_rules()
        
        # 验证每个字段的一致性
        self.assertEqual(
            retrieved['payment_timeout_minutes'], 
            test_data['payment_timeout_minutes']
        )
        self.assertAlmostEqual(
            retrieved['refund_fee_rate'], 
            test_data['refund_fee_rate'],
            places=2
        )
        self.assertAlmostEqual(
            retrieved['reschedule_fee_rate'], 
            test_data['reschedule_fee_rate'],
            places=2
        )
        self.assertEqual(
            retrieved['checkin_hours_before'], 
            test_data['checkin_hours_before']
        )
    
    @given(
        payment_timeout=st.integers(min_value=1, max_value=120),
        refund_rate=st.floats(min_value=0.0, max_value=1.0, allow_nan=False),
        reschedule_rate=st.floats(min_value=0.0, max_value=1.0, allow_nan=False),
        checkin_hours=st.integers(min_value=1, max_value=72)
    )
    @settings(max_examples=100)
    def test_property_1_business_rules_numeric_round_trip(
        self, payment_timeout, refund_rate, reschedule_rate, checkin_hours
    ):
        """
        Property 1: 设置存取一致性 - 业务规则数值类型
        
        *For any* valid business rule numeric values, storing and retrieving 
        should preserve the values (within floating point precision).
        
        **Feature: system-enhancements, Property 1: 设置存取一致性**
        **Validates: Requirements 2.1, 2.2, 2.3, 2.4**
        """
        user = self.get_or_create_user()
        
        # 准备测试数据
        test_data = {
            'payment_timeout_minutes': payment_timeout,
            'refund_fee_rate': round(refund_rate, 2),
            'reschedule_fee_rate': round(reschedule_rate, 2),
            'checkin_hours_before': checkin_hours,
        }
        
        # 更新业务规则
        result = SettingsService.update_business_rules(test_data, user)
        self.assertTrue(result['success'])
        
        # 读取业务规则
        retrieved = SettingsService.get_business_rules()
        
        # 验证整数字段
        self.assertEqual(
            retrieved['payment_timeout_minutes'], 
            payment_timeout,
            f"payment_timeout Round-trip 失败"
        )
        self.assertEqual(
            retrieved['checkin_hours_before'], 
            checkin_hours,
            f"checkin_hours Round-trip 失败"
        )
        
        # 验证浮点数字段（考虑精度）
        self.assertAlmostEqual(
            retrieved['refund_fee_rate'], 
            round(refund_rate, 2),
            places=2,
            msg=f"refund_fee_rate Round-trip 失败"
        )
        self.assertAlmostEqual(
            retrieved['reschedule_fee_rate'], 
            round(reschedule_rate, 2),
            places=2,
            msg=f"reschedule_fee_rate Round-trip 失败"
        )


class URLValidationPropertyTest(HypothesisTestCase):
    """
    URL 验证正确性属性测试
    
    Property 2: URL 验证正确性
    Validates: Requirements 1.5
    
    *For any* string, the URL validator should return True only if the string 
    starts with 'http://', 'https://', or '/', and return False otherwise.
    """
    
    @given(url=st.text(max_size=200))
    @settings(max_examples=100)
    def test_property_2_url_validation_arbitrary_strings(self, url):
        """
        Property 2: URL 验证正确性 - 任意字符串
        
        *For any* arbitrary string, validate_url should return True only if:
        - The string is empty, OR
        - The string starts with 'http://', 'https://', or '/'
        
        **Feature: system-enhancements, Property 2: URL 验证正确性**
        **Validates: Requirements 1.5**
        """
        result = SettingsService.validate_url(url)
        
        # 空字符串应该返回 True（允许清空 URL）
        if not url:
            self.assertTrue(
                result,
                f"空字符串应该返回 True，但返回了 {result}"
            )
        # 以有效前缀开头的 URL 应该返回 True
        elif url.startswith(('http://', 'https://', '/')):
            # 检查是否包含空白字符（正则表达式不允许空白）
            if ' ' in url or '\t' in url or '\n' in url or '\r' in url:
                self.assertFalse(
                    result,
                    f"包含空白字符的 URL '{url}' 应该返回 False，但返回了 {result}"
                )
            else:
                self.assertTrue(
                    result,
                    f"有效 URL '{url}' 应该返回 True，但返回了 {result}"
                )
        # 其他字符串应该返回 False
        else:
            self.assertFalse(
                result,
                f"无效 URL '{url}' 应该返回 False，但返回了 {result}"
            )
    
    @given(
        protocol=st.sampled_from(['http://', 'https://']),
        domain=st.text(
            min_size=1, 
            max_size=50,
            alphabet=st.characters(
                whitelist_categories=('L', 'N'),
                whitelist_characters='.-_'
            )
        ).filter(lambda x: len(x.strip()) > 0 and ' ' not in x),
        path=st.text(
            min_size=0, 
            max_size=50,
            alphabet=st.characters(
                whitelist_categories=('L', 'N'),
                whitelist_characters='/-_.~'
            )
        ).filter(lambda x: ' ' not in x)
    )
    @settings(max_examples=100)
    def test_property_2_valid_absolute_urls(self, protocol, domain, path):
        """
        Property 2: URL 验证正确性 - 有效绝对 URL
        
        *For any* well-formed absolute URL (http:// or https://), 
        validate_url should return True.
        
        **Feature: system-enhancements, Property 2: URL 验证正确性**
        **Validates: Requirements 1.5**
        """
        url = f"{protocol}{domain}{path}"
        result = SettingsService.validate_url(url)
        
        self.assertTrue(
            result,
            f"有效绝对 URL '{url}' 应该返回 True，但返回了 {result}"
        )
    
    @given(
        path=st.text(
            min_size=1, 
            max_size=100,
            alphabet=st.characters(
                whitelist_categories=('L', 'N'),
                whitelist_characters='/-_.~'
            )
        ).filter(lambda x: len(x.strip()) > 0 and ' ' not in x)
    )
    @settings(max_examples=100)
    def test_property_2_valid_relative_urls(self, path):
        """
        Property 2: URL 验证正确性 - 有效相对路径
        
        *For any* path starting with '/', validate_url should return True.
        
        **Feature: system-enhancements, Property 2: URL 验证正确性**
        **Validates: Requirements 1.5**
        """
        url = f"/{path}"
        result = SettingsService.validate_url(url)
        
        self.assertTrue(
            result,
            f"有效相对路径 '{url}' 应该返回 True，但返回了 {result}"
        )
    
    @given(
        invalid_prefix=st.text(
            min_size=1, 
            max_size=20,
            alphabet=st.characters(
                whitelist_categories=('L', 'N'),
                whitelist_characters='.-_:'
            )
        ).filter(
            lambda x: not x.startswith(('http://', 'https://', '/')) 
            and len(x.strip()) > 0
        )
    )
    @settings(max_examples=100)
    def test_property_2_invalid_urls(self, invalid_prefix):
        """
        Property 2: URL 验证正确性 - 无效 URL
        
        *For any* non-empty string that doesn't start with 'http://', 
        'https://', or '/', validate_url should return False.
        
        **Feature: system-enhancements, Property 2: URL 验证正确性**
        **Validates: Requirements 1.5**
        """
        result = SettingsService.validate_url(invalid_prefix)
        
        self.assertFalse(
            result,
            f"无效 URL '{invalid_prefix}' 应该返回 False，但返回了 {result}"
        )
    
    def test_property_2_empty_string(self):
        """
        Property 2: URL 验证正确性 - 空字符串
        
        空字符串应该返回 True（允许清空 URL 字段）。
        
        **Feature: system-enhancements, Property 2: URL 验证正确性**
        **Validates: Requirements 1.5**
        """
        result = SettingsService.validate_url('')
        self.assertTrue(result, "空字符串应该返回 True")
        
        result_none = SettingsService.validate_url(None)
        self.assertTrue(result_none, "None 应该返回 True")
    
    def test_property_2_common_valid_urls(self):
        """
        Property 2: URL 验证正确性 - 常见有效 URL 示例
        
        验证常见的有效 URL 格式。
        
        **Feature: system-enhancements, Property 2: URL 验证正确性**
        **Validates: Requirements 1.5**
        """
        valid_urls = [
            'http://example.com',
            'https://example.com',
            'http://example.com/path/to/resource',
            'https://example.com/path/to/resource.png',
            'https://cdn.example.com/images/logo.png',
            '/static/images/logo.png',
            '/favicon.ico',
            '/assets/css/style.css',
        ]
        
        for url in valid_urls:
            result = SettingsService.validate_url(url)
            self.assertTrue(
                result,
                f"有效 URL '{url}' 应该返回 True，但返回了 {result}"
            )
    
    def test_property_2_common_invalid_urls(self):
        """
        Property 2: URL 验证正确性 - 常见无效 URL 示例
        
        验证常见的无效 URL 格式。
        
        **Feature: system-enhancements, Property 2: URL 验证正确性**
        **Validates: Requirements 1.5**
        """
        invalid_urls = [
            'ftp://example.com',
            'example.com',
            'www.example.com',
            'javascript:alert(1)',
            'data:image/png;base64,xxx',
            'file:///etc/passwd',
            'mailto:test@example.com',
        ]
        
        for url in invalid_urls:
            result = SettingsService.validate_url(url)
            self.assertFalse(
                result,
                f"无效 URL '{url}' 应该返回 False，但返回了 {result}"
            )


class SettingsHistoryPropertyTest(HypothesisTestCase):
    """
    设置变更历史完整性属性测试
    
    Property 3: 设置变更历史完整性
    Validates: Requirements 2.5
    
    *For any* setting update where the value changes, a history record should 
    be created with the correct old value, new value, and user information.
    """
    
    def get_or_create_user(self):
        """获取或创建测试用户"""
        unique_id = uuid.uuid4().hex[:8]
        user, _ = User.objects.get_or_create(
            username=f'testuser_{unique_id}',
            defaults={
                'email': f'test_{unique_id}@example.com',
                'password': 'testpassword123'
            }
        )
        return user
    
    @given(
        category=st.sampled_from(['site', 'business']),
        key=st.text(
            min_size=1, 
            max_size=50, 
            alphabet=st.characters(
                whitelist_categories=('L', 'N'),
                whitelist_characters='_'
            )
        ).filter(lambda x: len(x.strip()) > 0),
        old_value=st.text(min_size=1, max_size=100),
        new_value=st.text(min_size=1, max_size=100)
    )
    @settings(max_examples=100)
    def test_property_3_history_created_on_value_change(
        self, category, key, old_value, new_value
    ):
        """
        Property 3: 设置变更历史完整性 - 值变更时创建历史记录
        
        *For any* setting update where the value changes, a history record 
        should be created.
        
        **Feature: system-enhancements, Property 3: 设置变更历史完整性**
        **Validates: Requirements 2.5**
        """
        # 跳过相同值的情况（不应创建历史记录）
        if old_value == new_value:
            return
        
        user = self.get_or_create_user()
        
        # 使用唯一的 key 避免测试间干扰
        unique_key = f"{key}_{uuid.uuid4().hex[:8]}"
        
        # 首先设置初始值
        SystemSettings.set_value(category, unique_key, old_value, user)
        
        # 记录更新前的历史数量
        setting = SystemSettings.objects.get(category=category, key=unique_key)
        history_count_before = SettingsHistory.objects.filter(setting=setting).count()
        
        # 更新为新值
        SystemSettings.set_value(category, unique_key, new_value, user)
        
        # 验证历史记录数量增加了 1
        history_count_after = SettingsHistory.objects.filter(setting=setting).count()
        self.assertEqual(
            history_count_after,
            history_count_before + 1,
            f"历史记录数量应该增加 1，但从 {history_count_before} 变为 {history_count_after}"
        )
    
    @given(
        category=st.sampled_from(['site', 'business']),
        key=st.text(
            min_size=1, 
            max_size=50, 
            alphabet=st.characters(
                whitelist_categories=('L', 'N'),
                whitelist_characters='_'
            )
        ).filter(lambda x: len(x.strip()) > 0),
        old_value=st.text(min_size=1, max_size=100),
        new_value=st.text(min_size=1, max_size=100)
    )
    @settings(max_examples=100)
    def test_property_3_history_contains_correct_old_value(
        self, category, key, old_value, new_value
    ):
        """
        Property 3: 设置变更历史完整性 - 历史记录包含正确的旧值
        
        *For any* setting update where the value changes, the history record 
        should contain the correct old value.
        
        **Feature: system-enhancements, Property 3: 设置变更历史完整性**
        **Validates: Requirements 2.5**
        """
        # 跳过相同值的情况
        if old_value == new_value:
            return
        
        user = self.get_or_create_user()
        unique_key = f"{key}_{uuid.uuid4().hex[:8]}"
        
        # 设置初始值
        SystemSettings.set_value(category, unique_key, old_value, user)
        
        # 更新为新值
        SystemSettings.set_value(category, unique_key, new_value, user)
        
        # 获取最新的历史记录
        setting = SystemSettings.objects.get(category=category, key=unique_key)
        latest_history = SettingsHistory.objects.filter(setting=setting).first()
        
        self.assertIsNotNone(latest_history, "应该创建历史记录")
        self.assertEqual(
            latest_history.old_value,
            old_value,
            f"历史记录的旧值应该是 '{old_value}'，但得到 '{latest_history.old_value}'"
        )
    
    @given(
        category=st.sampled_from(['site', 'business']),
        key=st.text(
            min_size=1, 
            max_size=50, 
            alphabet=st.characters(
                whitelist_categories=('L', 'N'),
                whitelist_characters='_'
            )
        ).filter(lambda x: len(x.strip()) > 0),
        old_value=st.text(min_size=1, max_size=100),
        new_value=st.text(min_size=1, max_size=100)
    )
    @settings(max_examples=100)
    def test_property_3_history_contains_correct_new_value(
        self, category, key, old_value, new_value
    ):
        """
        Property 3: 设置变更历史完整性 - 历史记录包含正确的新值
        
        *For any* setting update where the value changes, the history record 
        should contain the correct new value.
        
        **Feature: system-enhancements, Property 3: 设置变更历史完整性**
        **Validates: Requirements 2.5**
        """
        # 跳过相同值的情况
        if old_value == new_value:
            return
        
        user = self.get_or_create_user()
        unique_key = f"{key}_{uuid.uuid4().hex[:8]}"
        
        # 设置初始值
        SystemSettings.set_value(category, unique_key, old_value, user)
        
        # 更新为新值
        SystemSettings.set_value(category, unique_key, new_value, user)
        
        # 获取最新的历史记录
        setting = SystemSettings.objects.get(category=category, key=unique_key)
        latest_history = SettingsHistory.objects.filter(setting=setting).first()
        
        self.assertIsNotNone(latest_history, "应该创建历史记录")
        self.assertEqual(
            latest_history.new_value,
            new_value,
            f"历史记录的新值应该是 '{new_value}'，但得到 '{latest_history.new_value}'"
        )
    
    @given(
        category=st.sampled_from(['site', 'business']),
        key=st.text(
            min_size=1, 
            max_size=50, 
            alphabet=st.characters(
                whitelist_categories=('L', 'N'),
                whitelist_characters='_'
            )
        ).filter(lambda x: len(x.strip()) > 0),
        old_value=st.text(min_size=1, max_size=100),
        new_value=st.text(min_size=1, max_size=100)
    )
    @settings(max_examples=100)
    def test_property_3_history_contains_correct_user(
        self, category, key, old_value, new_value
    ):
        """
        Property 3: 设置变更历史完整性 - 历史记录包含正确的用户信息
        
        *For any* setting update where the value changes, the history record 
        should contain the correct user who made the change.
        
        **Feature: system-enhancements, Property 3: 设置变更历史完整性**
        **Validates: Requirements 2.5**
        """
        # 跳过相同值的情况
        if old_value == new_value:
            return
        
        user = self.get_or_create_user()
        unique_key = f"{key}_{uuid.uuid4().hex[:8]}"
        
        # 设置初始值
        SystemSettings.set_value(category, unique_key, old_value, user)
        
        # 更新为新值
        SystemSettings.set_value(category, unique_key, new_value, user)
        
        # 获取最新的历史记录
        setting = SystemSettings.objects.get(category=category, key=unique_key)
        latest_history = SettingsHistory.objects.filter(setting=setting).first()
        
        self.assertIsNotNone(latest_history, "应该创建历史记录")
        self.assertEqual(
            latest_history.changed_by,
            user,
            f"历史记录的修改人应该是 '{user.username}'，但得到 '{latest_history.changed_by}'"
        )
    
    @given(
        category=st.sampled_from(['site', 'business']),
        key=st.text(
            min_size=1, 
            max_size=50, 
            alphabet=st.characters(
                whitelist_categories=('L', 'N'),
                whitelist_characters='_'
            )
        ).filter(lambda x: len(x.strip()) > 0),
        value=st.text(min_size=1, max_size=100)
    )
    @settings(max_examples=100)
    def test_property_3_no_history_when_value_unchanged(self, category, key, value):
        """
        Property 3: 设置变更历史完整性 - 值未变更时不创建历史记录
        
        *For any* setting update where the value remains the same, no history 
        record should be created.
        
        **Feature: system-enhancements, Property 3: 设置变更历史完整性**
        **Validates: Requirements 2.5**
        """
        user = self.get_or_create_user()
        unique_key = f"{key}_{uuid.uuid4().hex[:8]}"
        
        # 设置初始值
        SystemSettings.set_value(category, unique_key, value, user)
        
        # 记录历史数量
        setting = SystemSettings.objects.get(category=category, key=unique_key)
        history_count_before = SettingsHistory.objects.filter(setting=setting).count()
        
        # 再次设置相同的值
        SystemSettings.set_value(category, unique_key, value, user)
        
        # 验证历史记录数量没有变化
        history_count_after = SettingsHistory.objects.filter(setting=setting).count()
        self.assertEqual(
            history_count_after,
            history_count_before,
            f"值未变更时不应创建历史记录，但历史数量从 {history_count_before} 变为 {history_count_after}"
        )
    
    @given(
        category=st.sampled_from(['site', 'business']),
        key=st.text(
            min_size=1, 
            max_size=50, 
            alphabet=st.characters(
                whitelist_categories=('L', 'N'),
                whitelist_characters='_'
            )
        ).filter(lambda x: len(x.strip()) > 0),
        values=st.lists(
            st.text(min_size=1, max_size=50),
            min_size=3,
            max_size=5,
            unique=True
        )
    )
    @settings(max_examples=100)
    def test_property_3_multiple_updates_create_multiple_history_records(
        self, category, key, values
    ):
        """
        Property 3: 设置变更历史完整性 - 多次更新创建多条历史记录
        
        *For any* sequence of distinct value updates, the number of history 
        records should equal the number of value changes (n-1 for n distinct values).
        
        **Feature: system-enhancements, Property 3: 设置变更历史完整性**
        **Validates: Requirements 2.5**
        """
        user = self.get_or_create_user()
        unique_key = f"{key}_{uuid.uuid4().hex[:8]}"
        
        # 设置初始值
        SystemSettings.set_value(category, unique_key, values[0], user)
        
        # 依次更新为后续的值
        for value in values[1:]:
            SystemSettings.set_value(category, unique_key, value, user)
        
        # 验证历史记录数量
        setting = SystemSettings.objects.get(category=category, key=unique_key)
        history_count = SettingsHistory.objects.filter(setting=setting).count()
        
        # 应该有 len(values) - 1 条历史记录（每次值变更创建一条）
        expected_count = len(values) - 1
        self.assertEqual(
            history_count,
            expected_count,
            f"应该有 {expected_count} 条历史记录，但得到 {history_count} 条"
        )
    
    def test_property_3_history_ordering(self):
        """
        Property 3: 设置变更历史完整性 - 历史记录按时间倒序排列
        
        验证历史记录按 changed_at 倒序排列（最新的在前）。
        
        **Feature: system-enhancements, Property 3: 设置变更历史完整性**
        **Validates: Requirements 2.5**
        """
        user = self.get_or_create_user()
        unique_key = f"test_ordering_{uuid.uuid4().hex[:8]}"
        
        # 创建多条历史记录
        values = ['value1', 'value2', 'value3', 'value4']
        SystemSettings.set_value('site', unique_key, values[0], user)
        for value in values[1:]:
            SystemSettings.set_value('site', unique_key, value, user)
        
        # 获取历史记录
        setting = SystemSettings.objects.get(category='site', key=unique_key)
        history_records = list(SettingsHistory.objects.filter(setting=setting))
        
        # 验证按时间倒序排列
        for i in range(len(history_records) - 1):
            self.assertGreaterEqual(
                history_records[i].changed_at,
                history_records[i + 1].changed_at,
                "历史记录应该按时间倒序排列"
            )
    
    def test_property_3_service_update_creates_history(self):
        """
        Property 3: 设置变更历史完整性 - 通过 SettingsService 更新也创建历史
        
        验证通过 SettingsService 更新业务规则时也会创建历史记录。
        
        **Feature: system-enhancements, Property 3: 设置变更历史完整性**
        **Validates: Requirements 2.5**
        """
        user = self.get_or_create_user()
        
        # 首先设置初始业务规则
        initial_data = {
            'payment_timeout_minutes': 30,
            'refund_fee_rate': 0.05,
        }
        SettingsService.update_business_rules(initial_data, user)
        
        # 记录历史数量
        initial_history_count = SettingsHistory.objects.filter(
            setting__category='business'
        ).count()
        
        # 更新业务规则
        updated_data = {
            'payment_timeout_minutes': 45,
            'refund_fee_rate': 0.08,
        }
        SettingsService.update_business_rules(updated_data, user)
        
        # 验证历史记录增加
        final_history_count = SettingsHistory.objects.filter(
            setting__category='business'
        ).count()
        
        self.assertGreater(
            final_history_count,
            initial_history_count,
            "通过 SettingsService 更新业务规则应该创建历史记录"
        )
