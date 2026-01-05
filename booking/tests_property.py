"""
在线值机功能属性测试

使用 Hypothesis 进行属性测试，验证值机 API 的正确性。
Feature: online-checkin
"""
import datetime
import uuid
from decimal import Decimal

from django.utils import timezone
from hypothesis import given, settings, strategies as st
from hypothesis.extra.django import TestCase as HypothesisTestCase
from rest_framework.test import APIClient

from accounts.models import User
from booking.models import Order, Ticket
from booking.views import mask_id_number
from flight.models import Flight


class CheckinInfoPropertyTest(HypothesisTestCase):
    """
    checkin_info API 属性测试
    
    Property 2: 机票状态验证
    Property 3: 值机信息完整性
    Validates: Requirements 1.1, 1.2, 1.3, 2.1-2.4
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
    
    def create_flight(self, departure_offset_hours=12):
        """创建测试航班，默认在值机窗口期内"""
        departure_time = timezone.now() + datetime.timedelta(hours=departure_offset_hours)
        unique_id = uuid.uuid4().hex[:6]
        return Flight.objects.create(
            flight_number=f'CA{unique_id}',
            airline_name='中国国航',
            departure_city='北京',
            arrival_city='上海',
            departure_time=departure_time,
            arrival_time=departure_time + datetime.timedelta(hours=2),
            price=Decimal('800.00'),
            discount=Decimal('0.9'),
            capacity=100,
            available_seats=100,
            status='scheduled',
            aircraft_type='Boeing 737',
        )
    
    def create_ticket(self, user, flight, ticket_status='valid', checked_in=False, 
                      passenger_id_number='110101199001011234'):
        """创建测试机票"""
        order = Order.objects.create(
            user=user,
            total_price=Decimal('720.00'),
            status='paid'
        )
        return Ticket.objects.create(
            order=order,
            flight=flight,
            passenger_name='张三',
            passenger_id_number=passenger_id_number,
            seat_number='1A',
            cabin_class='economy',
            price=Decimal('720.00'),
            status=ticket_status,
            checked_in=checked_in
        )
    
    @given(ticket_status=st.sampled_from(['refunded', 'used']))
    @settings(max_examples=100)
    def test_property_2_invalid_ticket_status_rejected(self, ticket_status):
        """
        Property 2: 机票状态验证
        
        *For any* 机票，只有状态为 valid 且 checked_in 为 False 的机票才能办理值机；
        其他状态应返回相应错误。
        
        **Feature: online-checkin, Property 2: 机票状态验证**
        **Validates: Requirements 1.1, 1.2**
        """
        user = self.get_or_create_user()
        client = APIClient()
        client.force_authenticate(user=user)
        
        flight = self.create_flight()
        ticket = self.create_ticket(user, flight, ticket_status=ticket_status)
        
        response = client.get(f'/api/bookings/tickets/{ticket.id}/checkin_info/')
        
        # 非 valid 状态的机票应该被拒绝
        self.assertEqual(response.status_code, 400)
        self.assertIn('detail', response.data)
        self.assertEqual(response.data.get('status'), ticket_status)
    
    def test_property_2_already_checked_in_rejected(self):
        """
        Property 2: 机票状态验证 - 已值机机票
        
        *For any* 已值机的机票，应返回已值机状态。
        
        **Feature: online-checkin, Property 2: 机票状态验证**
        **Validates: Requirements 1.3**
        """
        user = self.get_or_create_user()
        client = APIClient()
        client.force_authenticate(user=user)
        
        flight = self.create_flight()
        ticket = self.create_ticket(user, flight, checked_in=True)
        
        response = client.get(f'/api/bookings/tickets/{ticket.id}/checkin_info/')
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('detail', response.data)
        self.assertTrue(response.data.get('checked_in'))

    
    @given(
        passenger_name=st.text(min_size=1, max_size=50, alphabet=st.characters(
            whitelist_categories=('L',), whitelist_characters='·'
        )).filter(lambda x: len(x.strip()) > 0),
        passenger_id_number=st.text(
            min_size=9, max_size=18, 
            alphabet=st.characters(whitelist_categories=('Nd', 'Lu'))
        )
    )
    @settings(max_examples=100)
    def test_property_3_checkin_info_completeness(self, passenger_name, passenger_id_number):
        """
        Property 3: 值机信息完整性
        
        *For any* 通过值机资格验证的机票，返回的值机信息应包含：
        乘客姓名、脱敏证件号、机票编号、航班号、航空公司、出发/到达城市、
        起飞/到达时间、舱位等级、当前座位、登机口。
        
        **Feature: online-checkin, Property 3: 值机信息完整性**
        **Validates: Requirements 2.1, 2.2, 2.3, 2.4**
        """
        user = self.get_or_create_user()
        client = APIClient()
        client.force_authenticate(user=user)
        
        flight = self.create_flight()
        ticket = self.create_ticket(
            user, flight, 
            passenger_id_number=passenger_id_number
        )
        # 更新乘客姓名
        ticket.passenger_name = passenger_name
        ticket.save()
        
        response = client.get(f'/api/bookings/tickets/{ticket.id}/checkin_info/')
        
        # 应该成功返回
        self.assertEqual(response.status_code, 200)
        
        # 验证必要字段存在
        required_fields = [
            'ticket_id', 'ticket_number', 'passenger_name', 'passenger_id_number',
            'flight_id', 'flight_number', 'airline_name',
            'departure_city', 'arrival_city', 'departure_airport', 'arrival_airport',
            'departure_time', 'arrival_time',
            'current_seat', 'cabin_class', 'gate', 'boarding_time',
            'checked_in', 'can_change_seat',
            'checkin_open_time', 'checkin_close_time'
        ]
        
        for field in required_fields:
            self.assertIn(field, response.data, f"缺少必要字段: {field}")
        
        # 验证乘客姓名正确
        self.assertEqual(response.data['passenger_name'], passenger_name)
        
        # 验证证件号码已脱敏
        masked_id = response.data['passenger_id_number']
        if len(passenger_id_number) > 8:
            self.assertEqual(masked_id[:4], passenger_id_number[:4])
            self.assertEqual(masked_id[-4:], passenger_id_number[-4:])
            self.assertIn('*', masked_id)
            self.assertEqual(len(masked_id), len(passenger_id_number))
        
        # 验证航班信息正确
        self.assertEqual(response.data['flight_id'], flight.id)
        self.assertEqual(response.data['flight_number'], flight.flight_number)
        self.assertEqual(response.data['airline_name'], flight.airline_name)
        self.assertEqual(response.data['departure_city'], flight.departure_city)
        self.assertEqual(response.data['arrival_city'], flight.arrival_city)


class MaskIdNumberPropertyTest(HypothesisTestCase):
    """
    证件号码脱敏函数属性测试
    
    Property 4: 证件号码脱敏
    Validates: Requirements 2.5
    """
    
    @given(id_number=st.text(
        min_size=9, max_size=18, 
        alphabet=st.characters(whitelist_categories=('Nd', 'Lu'))
    ))
    @settings(max_examples=100)
    def test_property_4_id_masking_preserves_length(self, id_number):
        """
        Property 4: 证件号码脱敏
        
        *For any* 长度大于 8 的证件号码，脱敏后应仅显示前 4 位和后 4 位，
        中间用星号替代；脱敏后长度应与原长度相同。
        
        **Feature: online-checkin, Property 4: 证件号码脱敏**
        **Validates: Requirements 2.5**
        """
        masked = mask_id_number(id_number)
        
        # 脱敏后长度应与原长度相同
        self.assertEqual(len(masked), len(id_number))
        
        # 前4位应保持不变
        self.assertEqual(masked[:4], id_number[:4])
        
        # 后4位应保持不变
        self.assertEqual(masked[-4:], id_number[-4:])
        
        # 中间应包含星号
        if len(id_number) > 8:
            middle = masked[4:-4]
            self.assertTrue(all(c == '*' for c in middle))
    
    @given(id_number=st.text(min_size=1, max_size=8))
    @settings(max_examples=100)
    def test_property_4_short_id_all_masked(self, id_number):
        """
        Property 4: 证件号码脱敏 - 短证件号
        
        *For any* 长度小于等于 8 的证件号码，应全部用星号替代。
        
        **Feature: online-checkin, Property 4: 证件号码脱敏**
        **Validates: Requirements 2.5**
        """
        if len(id_number) == 0:
            return  # 空字符串跳过
            
        masked = mask_id_number(id_number)
        
        # 脱敏后长度应与原长度相同
        self.assertEqual(len(masked), len(id_number))
        
        # 全部应为星号
        self.assertTrue(all(c == '*' for c in masked))



class CheckinAPIPropertyTest(HypothesisTestCase):
    """
    checkin API 属性测试
    
    Property 9: 座位冲突检测
    Property 10: 值机状态更新
    Property 11: 登机牌数据完整性
    Validates: Requirements 4.1-4.6, 5.1-5.5
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
    
    def create_flight(self, departure_offset_hours=12):
        """创建测试航班，默认在值机窗口期内"""
        departure_time = timezone.now() + datetime.timedelta(hours=departure_offset_hours)
        unique_id = uuid.uuid4().hex[:6]
        return Flight.objects.create(
            flight_number=f'CA{unique_id}',
            airline_name='中国国航',
            departure_city='北京',
            arrival_city='上海',
            departure_time=departure_time,
            arrival_time=departure_time + datetime.timedelta(hours=2),
            price=Decimal('800.00'),
            discount=Decimal('0.9'),
            capacity=100,
            available_seats=100,
            status='scheduled',
            aircraft_type='Boeing 737',
        )
    
    def create_ticket(self, user, flight, seat_number='1A', ticket_status='valid', checked_in=False):
        """创建测试机票"""
        order = Order.objects.create(
            user=user,
            total_price=Decimal('720.00'),
            status='paid'
        )
        return Ticket.objects.create(
            order=order,
            flight=flight,
            passenger_name='张三',
            passenger_id_number='110101199001011234',
            seat_number=seat_number,
            cabin_class='economy',
            price=Decimal('720.00'),
            status=ticket_status,
            checked_in=checked_in
        )
    
    @given(
        seat_row=st.integers(min_value=1, max_value=30),
        seat_col=st.sampled_from(['A', 'B', 'C', 'D', 'E', 'F'])
    )
    @settings(max_examples=100)
    def test_property_9_seat_conflict_detection(self, seat_row, seat_col):
        """
        Property 9: 座位冲突检测
        
        *For any* 值机请求中的新座位，如果该座位已被其他有效机票占用，
        应返回座位冲突错误。
        
        **Feature: online-checkin, Property 9: 座位冲突检测**
        **Validates: Requirements 4.1, 4.2**
        """
        user = self.get_or_create_user()
        client = APIClient()
        client.force_authenticate(user=user)
        
        flight = self.create_flight()
        target_seat = f'{seat_row}{seat_col}'
        
        # 创建一个已占用目标座位的机票
        other_user = self.get_or_create_user()
        self.create_ticket(other_user, flight, seat_number=target_seat)
        
        # 创建当前用户的机票（不同座位）
        current_seat = f'{(seat_row % 30) + 1}{"ABCDEF"[(ord(seat_col) - ord("A") + 1) % 6]}'
        ticket = self.create_ticket(user, flight, seat_number=current_seat)
        
        # 尝试值机并选择已占用的座位
        response = client.post(
            f'/api/bookings/tickets/{ticket.id}/checkin/',
            {'seat_number': target_seat},
            format='json'
        )
        
        # 应该返回座位冲突错误
        self.assertEqual(response.status_code, 400)
        self.assertIn('已被占用', response.data.get('detail', ''))
    
    @given(
        seat_row=st.integers(min_value=1, max_value=30),
        seat_col=st.sampled_from(['A', 'B', 'C', 'D', 'E', 'F'])
    )
    @settings(max_examples=100)
    def test_property_10_checkin_status_update(self, seat_row, seat_col):
        """
        Property 10: 值机状态更新
        
        *For any* 成功的值机操作，机票的 checked_in 应为 True，
        checked_in_at 应不为空，boarding_pass_number 应被生成，
        座位号应更新为选择的座位。
        
        **Feature: online-checkin, Property 10: 值机状态更新**
        **Validates: Requirements 4.3, 4.4, 4.5, 4.6**
        """
        user = self.get_or_create_user()
        client = APIClient()
        client.force_authenticate(user=user)
        
        flight = self.create_flight()
        new_seat = f'{seat_row}{seat_col}'
        
        # 创建机票（使用不同的初始座位）
        initial_seat = f'{(seat_row % 30) + 1}{"ABCDEF"[(ord(seat_col) - ord("A") + 1) % 6]}'
        ticket = self.create_ticket(user, flight, seat_number=initial_seat)
        
        # 执行值机
        response = client.post(
            f'/api/bookings/tickets/{ticket.id}/checkin/',
            {'seat_number': new_seat},
            format='json'
        )
        
        # 应该成功
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data.get('success'))
        
        # 验证数据库中的状态更新
        ticket.refresh_from_db()
        self.assertTrue(ticket.checked_in)
        self.assertIsNotNone(ticket.checked_in_at)
        self.assertIsNotNone(ticket.boarding_pass_number)
        self.assertTrue(ticket.boarding_pass_number.startswith('BP'))
        self.assertEqual(ticket.seat_number, new_seat)
        self.assertIsNotNone(ticket.gate)

    
    @given(
        passenger_name=st.text(min_size=1, max_size=20, alphabet=st.characters(
            whitelist_categories=('L',)
        )).filter(lambda x: len(x.strip()) > 0)
    )
    @settings(max_examples=100)
    def test_property_11_boarding_pass_completeness(self, passenger_name):
        """
        Property 11: 登机牌数据完整性
        
        *For any* 成功的值机操作，返回的登机牌应包含：
        登机牌编号、乘客姓名、航班号、日期、舱位、出发/到达城市代码、
        起飞/到达时间、座位号、登机口。
        
        **Feature: online-checkin, Property 11: 登机牌数据完整性**
        **Validates: Requirements 5.1, 5.2, 5.3, 5.5**
        """
        user = self.get_or_create_user()
        client = APIClient()
        client.force_authenticate(user=user)
        
        flight = self.create_flight()
        ticket = self.create_ticket(user, flight)
        ticket.passenger_name = passenger_name
        ticket.save()
        
        # 执行值机
        response = client.post(
            f'/api/bookings/tickets/{ticket.id}/checkin/',
            format='json'
        )
        
        # 应该成功
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data.get('success'))
        
        # 验证登机牌包含所有必要字段
        boarding_pass = response.data.get('boarding_pass', {})
        required_fields = [
            'boarding_pass_number', 'ticket_number', 'passenger_name',
            'flight_number', 'airline_name',
            'departure_city', 'arrival_city',
            'departure_city_code', 'arrival_city_code',
            'departure_airport', 'arrival_airport',
            'departure_time', 'arrival_time', 'flight_date',
            'seat_number', 'cabin_class', 'gate', 'boarding_time',
            'checked_in_at'
        ]
        
        for field in required_fields:
            self.assertIn(field, boarding_pass, f"登机牌缺少必要字段: {field}")
        
        # 验证乘客姓名正确
        self.assertEqual(boarding_pass['passenger_name'], passenger_name)
        
        # 验证登机牌编号格式
        self.assertTrue(boarding_pass['boarding_pass_number'].startswith('BP'))
        
        # 验证航班信息
        self.assertEqual(boarding_pass['flight_number'], flight.flight_number)
        self.assertEqual(boarding_pass['airline_name'], flight.airline_name)
        self.assertEqual(boarding_pass['departure_city'], flight.departure_city)
        self.assertEqual(boarding_pass['arrival_city'], flight.arrival_city)


class BoardingTimePropertyTest(HypothesisTestCase):
    """
    登机时间计算函数属性测试
    
    Property 12: 登机时间计算
    Validates: Requirements 5.4
    """
    
    @given(
        year=st.integers(min_value=2024, max_value=2030),
        month=st.integers(min_value=1, max_value=12),
        day=st.integers(min_value=1, max_value=28),
        hour=st.integers(min_value=0, max_value=23),
        minute=st.integers(min_value=0, max_value=59)
    )
    @settings(max_examples=100)
    def test_property_12_boarding_time_calculation(self, year, month, day, hour, minute):
        """
        Property 12: 登机时间计算
        
        *For any* 航班，登机时间应等于起飞时间减去 30 分钟。
        
        **Feature: online-checkin, Property 12: 登机时间计算**
        **Validates: Requirements 5.4**
        """
        from core.utils import calculate_boarding_time
        
        # 创建起飞时间
        departure_time = datetime.datetime(year, month, day, hour, minute)
        
        # 计算登机时间
        boarding_time = calculate_boarding_time(departure_time)
        
        # 验证登机时间 = 起飞时间 - 30 分钟
        expected_boarding_time = departure_time - datetime.timedelta(minutes=30)
        self.assertEqual(boarding_time, expected_boarding_time)
        
        # 验证时间差为 30 分钟
        time_diff = departure_time - boarding_time
        self.assertEqual(time_diff.total_seconds(), 30 * 60)
    
    @given(
        hour=st.integers(min_value=0, max_value=23),
        minute=st.integers(min_value=0, max_value=59)
    )
    @settings(max_examples=100)
    def test_property_12_boarding_time_across_midnight(self, hour, minute):
        """
        Property 12: 登机时间计算 - 跨午夜场景
        
        *For any* 凌晨起飞的航班，登机时间应正确计算（可能跨越到前一天）。
        
        **Feature: online-checkin, Property 12: 登机时间计算**
        **Validates: Requirements 5.4**
        """
        from core.utils import calculate_boarding_time
        
        # 创建凌晨起飞时间
        departure_time = datetime.datetime(2026, 1, 15, hour, minute)
        
        # 计算登机时间
        boarding_time = calculate_boarding_time(departure_time)
        
        # 验证时间差始终为 30 分钟
        time_diff = departure_time - boarding_time
        self.assertEqual(time_diff.total_seconds(), 30 * 60)
        
        # 如果起飞时间在 00:00-00:29，登机时间应在前一天
        if hour == 0 and minute < 30:
            self.assertEqual(boarding_time.day, 14)  # 前一天
            self.assertEqual(boarding_time.hour, 23)
            self.assertEqual(boarding_time.minute, minute + 30)
    
    def test_property_12_boarding_time_none_input(self):
        """
        Property 12: 登机时间计算 - 空输入
        
        当输入为 None 时，应返回 None。
        
        **Feature: online-checkin, Property 12: 登机时间计算**
        **Validates: Requirements 5.4**
        """
        from core.utils import calculate_boarding_time
        
        result = calculate_boarding_time(None)
        self.assertIsNone(result)


class CheckinWindowPropertyTest(HypothesisTestCase):
    """
    值机窗口期属性测试
    
    Property 1: 值机窗口期验证
    Validates: Requirements 1.4, 1.5
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
    
    def create_flight(self, departure_offset_hours):
        """创建测试航班，指定起飞时间偏移量"""
        departure_time = timezone.now() + datetime.timedelta(hours=departure_offset_hours)
        unique_id = uuid.uuid4().hex[:6]
        return Flight.objects.create(
            flight_number=f'CA{unique_id}',
            airline_name='中国国航',
            departure_city='北京',
            arrival_city='上海',
            departure_time=departure_time,
            arrival_time=departure_time + datetime.timedelta(hours=2),
            price=Decimal('800.00'),
            discount=Decimal('0.9'),
            capacity=100,
            available_seats=100,
            status='scheduled',
            aircraft_type='Boeing 737',
        )
    
    def create_ticket(self, user, flight):
        """创建测试机票"""
        order = Order.objects.create(
            user=user,
            total_price=Decimal('720.00'),
            status='paid'
        )
        return Ticket.objects.create(
            order=order,
            flight=flight,
            passenger_name='张三',
            passenger_id_number='110101199001011234',
            seat_number='10A',
            cabin_class='economy',
            price=Decimal('720.00'),
            status='valid',
            checked_in=False
        )
    
    @given(hours_before_departure=st.integers(min_value=25, max_value=72))
    @settings(max_examples=100)
    def test_property_1_checkin_before_window_rejected(self, hours_before_departure):
        """
        Property 1: 值机窗口期验证 - 窗口期前
        
        *For any* 机票和当前时间，如果当前时间在起飞前 24 小时之前，
        值机请求应被拒绝并返回"值机尚未开放"的错误信息。
        
        **Feature: online-checkin, Property 1: 值机窗口期验证**
        **Validates: Requirements 1.4**
        """
        user = self.get_or_create_user()
        client = APIClient()
        client.force_authenticate(user=user)
        
        # 创建起飞时间在 hours_before_departure 小时后的航班
        # 由于 hours_before_departure >= 25，当前时间一定在值机窗口期前
        flight = self.create_flight(departure_offset_hours=hours_before_departure)
        ticket = self.create_ticket(user, flight)
        
        # 尝试获取值机信息
        response = client.get(f'/api/bookings/tickets/{ticket.id}/checkin_info/')
        
        # 应该返回 400 错误
        self.assertEqual(response.status_code, 400)
        self.assertIn('detail', response.data)
        self.assertIn('值机尚未开放', response.data['detail'])
        self.assertIn('checkin_open_time', response.data)
    
    @given(minutes_before_departure=st.integers(min_value=0, max_value=59))
    @settings(max_examples=100)
    def test_property_1_checkin_after_window_rejected(self, minutes_before_departure):
        """
        Property 1: 值机窗口期验证 - 窗口期后
        
        *For any* 机票和当前时间，如果当前时间在起飞前 1 小时之后，
        值机请求应被拒绝并返回"值机已关闭"的错误信息。
        
        **Feature: online-checkin, Property 1: 值机窗口期验证**
        **Validates: Requirements 1.5**
        """
        user = self.get_or_create_user()
        client = APIClient()
        client.force_authenticate(user=user)
        
        # 创建起飞时间在 minutes_before_departure 分钟后的航班
        # 由于 minutes_before_departure < 60，当前时间一定在值机窗口期后
        # 将分钟转换为小时（小数）
        hours_offset = minutes_before_departure / 60.0
        
        # 创建航班，起飞时间在 minutes_before_departure 分钟后
        departure_time = timezone.now() + datetime.timedelta(minutes=minutes_before_departure)
        unique_id = uuid.uuid4().hex[:6]
        flight = Flight.objects.create(
            flight_number=f'CA{unique_id}',
            airline_name='中国国航',
            departure_city='北京',
            arrival_city='上海',
            departure_time=departure_time,
            arrival_time=departure_time + datetime.timedelta(hours=2),
            price=Decimal('800.00'),
            discount=Decimal('0.9'),
            capacity=100,
            available_seats=100,
            status='scheduled',
            aircraft_type='Boeing 737',
        )
        ticket = self.create_ticket(user, flight)
        
        # 尝试获取值机信息
        response = client.get(f'/api/bookings/tickets/{ticket.id}/checkin_info/')
        
        # 应该返回 400 错误
        self.assertEqual(response.status_code, 400)
        self.assertIn('detail', response.data)
        self.assertIn('值机已关闭', response.data['detail'])
        self.assertIn('checkin_close_time', response.data)
    
    @given(hours_before_departure=st.integers(min_value=2, max_value=23))
    @settings(max_examples=100)
    def test_property_1_checkin_within_window_accepted(self, hours_before_departure):
        """
        Property 1: 值机窗口期验证 - 窗口期内
        
        *For any* 机票和当前时间，如果当前时间在起飞前 24 小时至 1 小时之间，
        值机请求应被接受并返回值机信息。
        
        **Feature: online-checkin, Property 1: 值机窗口期验证**
        **Validates: Requirements 1.4, 1.5**
        """
        user = self.get_or_create_user()
        client = APIClient()
        client.force_authenticate(user=user)
        
        # 创建起飞时间在 hours_before_departure 小时后的航班
        # 由于 2 <= hours_before_departure <= 23，当前时间一定在值机窗口期内
        flight = self.create_flight(departure_offset_hours=hours_before_departure)
        ticket = self.create_ticket(user, flight)
        
        # 尝试获取值机信息
        response = client.get(f'/api/bookings/tickets/{ticket.id}/checkin_info/')
        
        # 应该成功返回
        self.assertEqual(response.status_code, 200)
        
        # 验证返回了值机信息
        self.assertIn('ticket_id', response.data)
        self.assertIn('flight_number', response.data)
        self.assertIn('checkin_open_time', response.data)
        self.assertIn('checkin_close_time', response.data)
        
        # 验证值机窗口期时间正确
        checkin_open = response.data['checkin_open_time']
        checkin_close = response.data['checkin_close_time']
        
        # checkin_open 应该是起飞前 24 小时
        # checkin_close 应该是起飞前 1 小时
        self.assertIsNotNone(checkin_open)
        self.assertIsNotNone(checkin_close)



class InventoryBoundsPropertyTest(HypothesisTestCase):
    """
    座位库存边界属性测试
    
    Property 4: 座位库存边界不变量
    Validates: Requirements 2.6, 2.7
    """
    
    def create_flight(self, capacity=100, available_seats=None):
        """创建测试航班"""
        if available_seats is None:
            available_seats = capacity
        unique_id = uuid.uuid4().hex[:6]
        departure_time = timezone.now() + datetime.timedelta(hours=24)
        return Flight.objects.create(
            flight_number=f'CA{unique_id}',
            airline_name='中国国航',
            departure_city='北京',
            arrival_city='上海',
            departure_time=departure_time,
            arrival_time=departure_time + datetime.timedelta(hours=2),
            price=Decimal('800.00'),
            discount=Decimal('0.9'),
            capacity=capacity,
            available_seats=available_seats,
            status='scheduled',
            aircraft_type='Boeing 737',
        )
    
    @given(
        capacity=st.integers(min_value=50, max_value=500),
        operations=st.lists(
            st.tuples(
                st.sampled_from(['reserve', 'release']),
                st.integers(min_value=1, max_value=10)
            ),
            min_size=1,
            max_size=50
        )
    )
    @settings(max_examples=100)
    def test_property_4_seat_inventory_bounds(self, capacity, operations):
        """
        Property 4: 座位库存边界不变量
        
        *For any* 航班，在任何操作后，可用座位数应满足：0 ≤ available_seats ≤ capacity。
        
        **Feature: order-enhancement, Property 4: 座位库存边界不变量**
        **Validates: Requirements 2.6, 2.7**
        """
        from booking.services import InventoryService
        
        # 创建航班
        flight = self.create_flight(capacity=capacity, available_seats=capacity)
        
        # 执行一系列操作
        for op_type, count in operations:
            if op_type == 'reserve':
                InventoryService.reserve_seats(flight, count)
            else:
                InventoryService.release_seats(flight, count)
            
            # 刷新航班数据
            flight.refresh_from_db()
            
            # 验证边界不变量：0 ≤ available_seats ≤ capacity
            self.assertGreaterEqual(
                flight.available_seats, 0,
                f"可用座位数不应小于 0，当前值: {flight.available_seats}"
            )
            self.assertLessEqual(
                flight.available_seats, flight.capacity,
                f"可用座位数不应超过总容量，当前值: {flight.available_seats}, 容量: {flight.capacity}"
            )
    
    @given(
        capacity=st.integers(min_value=50, max_value=200),
        reserve_count=st.integers(min_value=1, max_value=100)
    )
    @settings(max_examples=100)
    def test_property_4_reserve_never_goes_negative(self, capacity, reserve_count):
        """
        Property 4: 座位库存边界不变量 - 预留不会导致负数
        
        *For any* 航班和预留数量，预留操作后可用座位数不应小于 0。
        
        **Feature: order-enhancement, Property 4: 座位库存边界不变量**
        **Validates: Requirements 2.7**
        """
        from booking.services import InventoryService
        
        # 创建航班
        flight = self.create_flight(capacity=capacity, available_seats=capacity)
        
        # 尝试预留座位
        InventoryService.reserve_seats(flight, reserve_count)
        
        # 刷新航班数据
        flight.refresh_from_db()
        
        # 验证可用座位数不小于 0
        self.assertGreaterEqual(
            flight.available_seats, 0,
            f"预留后可用座位数不应小于 0，当前值: {flight.available_seats}"
        )
    
    @given(
        capacity=st.integers(min_value=50, max_value=200),
        release_count=st.integers(min_value=1, max_value=100)
    )
    @settings(max_examples=100)
    def test_property_4_release_never_exceeds_capacity(self, capacity, release_count):
        """
        Property 4: 座位库存边界不变量 - 释放不会超过容量
        
        *For any* 航班和释放数量，释放操作后可用座位数不应超过总容量。
        
        **Feature: order-enhancement, Property 4: 座位库存边界不变量**
        **Validates: Requirements 2.6**
        """
        from booking.services import InventoryService
        
        # 创建航班，初始可用座位为容量的一半
        initial_available = capacity // 2
        flight = self.create_flight(capacity=capacity, available_seats=initial_available)
        
        # 释放座位
        InventoryService.release_seats(flight, release_count)
        
        # 刷新航班数据
        flight.refresh_from_db()
        
        # 验证可用座位数不超过容量
        self.assertLessEqual(
            flight.available_seats, flight.capacity,
            f"释放后可用座位数不应超过容量，当前值: {flight.available_seats}, 容量: {flight.capacity}"
        )



class FlightStatusConsistencyPropertyTest(HypothesisTestCase):
    """
    航班状态一致性属性测试
    
    Property 6: 航班状态与座位数一致性
    Validates: Requirements 2.4, 2.5
    """
    
    def create_flight(self, capacity=100, available_seats=None, status='scheduled'):
        """创建测试航班"""
        if available_seats is None:
            available_seats = capacity
        unique_id = uuid.uuid4().hex[:6]
        departure_time = timezone.now() + datetime.timedelta(hours=24)
        return Flight.objects.create(
            flight_number=f'CA{unique_id}',
            airline_name='中国国航',
            departure_city='北京',
            arrival_city='上海',
            departure_time=departure_time,
            arrival_time=departure_time + datetime.timedelta(hours=2),
            price=Decimal('800.00'),
            discount=Decimal('0.9'),
            capacity=capacity,
            available_seats=available_seats,
            status=status,
            aircraft_type='Boeing 737',
        )
    
    @given(
        capacity=st.integers(min_value=10, max_value=200)
    )
    @settings(max_examples=100)
    def test_property_6_status_full_when_no_seats(self, capacity):
        """
        Property 6: 航班状态与座位数一致性 - 座位为零时状态为 full
        
        *For any* 航班，当 available_seats = 0 时状态应为 'full'。
        
        **Feature: order-enhancement, Property 6: 航班状态与座位数一致性**
        **Validates: Requirements 2.4**
        """
        from booking.services import InventoryService
        
        # 创建航班
        flight = self.create_flight(capacity=capacity, available_seats=capacity)
        
        # 预留所有座位
        InventoryService.reserve_seats(flight, capacity)
        
        # 刷新航班数据
        flight.refresh_from_db()
        
        # 验证座位数为 0
        self.assertEqual(flight.available_seats, 0)
        
        # 验证状态为 full
        self.assertEqual(
            flight.status, 'full',
            f"当可用座位数为 0 时，状态应为 'full'，当前状态: {flight.status}"
        )
    
    @given(
        capacity=st.integers(min_value=10, max_value=200),
        release_count=st.integers(min_value=1, max_value=50)
    )
    @settings(max_examples=100)
    def test_property_6_status_scheduled_when_seats_restored(self, capacity, release_count):
        """
        Property 6: 航班状态与座位数一致性 - 恢复座位后状态为 scheduled
        
        *For any* 航班，当 available_seats > 0 且之前为 'full' 时状态应恢复为 'scheduled'。
        
        **Feature: order-enhancement, Property 6: 航班状态与座位数一致性**
        **Validates: Requirements 2.5**
        """
        from booking.services import InventoryService
        
        # 创建已满航班
        flight = self.create_flight(capacity=capacity, available_seats=0, status='full')
        
        # 释放一些座位
        actual_release = min(release_count, capacity)
        InventoryService.release_seats(flight, actual_release)
        
        # 刷新航班数据
        flight.refresh_from_db()
        
        # 验证座位数大于 0
        self.assertGreater(flight.available_seats, 0)
        
        # 验证状态为 scheduled
        self.assertEqual(
            flight.status, 'scheduled',
            f"当可用座位数 > 0 且之前为 'full' 时，状态应恢复为 'scheduled'，当前状态: {flight.status}"
        )
    
    @given(
        capacity=st.integers(min_value=20, max_value=200),
        operations=st.lists(
            st.tuples(
                st.sampled_from(['reserve', 'release']),
                st.integers(min_value=1, max_value=10)
            ),
            min_size=5,
            max_size=30
        )
    )
    @settings(max_examples=100)
    def test_property_6_status_consistency_after_operations(self, capacity, operations):
        """
        Property 6: 航班状态与座位数一致性 - 操作后状态一致性
        
        *For any* 航班和一系列操作，操作后航班状态应与可用座位数保持一致：
        - available_seats = 0 时状态为 'full'
        - available_seats > 0 时状态为 'scheduled'（如果之前是 'full'）
        
        **Feature: order-enhancement, Property 6: 航班状态与座位数一致性**
        **Validates: Requirements 2.4, 2.5**
        """
        from booking.services import InventoryService
        
        # 创建航班
        flight = self.create_flight(capacity=capacity, available_seats=capacity)
        
        # 执行一系列操作
        for op_type, count in operations:
            if op_type == 'reserve':
                InventoryService.reserve_seats(flight, count)
            else:
                InventoryService.release_seats(flight, count)
            
            # 刷新航班数据
            flight.refresh_from_db()
            
            # 验证状态一致性
            if flight.available_seats == 0:
                self.assertEqual(
                    flight.status, 'full',
                    f"当可用座位数为 0 时，状态应为 'full'，当前状态: {flight.status}"
                )
            elif flight.available_seats > 0:
                # 状态应该是 'scheduled' 或保持原状态（如果不是 'full'）
                self.assertIn(
                    flight.status, ['scheduled', 'departed', 'canceled'],
                    f"当可用座位数 > 0 时，状态不应为 'full'，当前状态: {flight.status}"
                )



class RemainingTimePropertyTest(HypothesisTestCase):
    """
    剩余支付时间属性测试
    
    Property 8: 剩余支付时间计算正确性
    Validates: Requirements 3.1, 3.7
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
    
    def create_order(self, user, status='pending', expires_at=None):
        """创建测试订单"""
        return Order.objects.create(
            user=user,
            total_price=Decimal('720.00'),
            status=status,
            expires_at=expires_at
        )
    
    @given(
        minutes_remaining=st.integers(min_value=1, max_value=60)
    )
    @settings(max_examples=100)
    def test_property_8_remaining_time_positive(self, minutes_remaining):
        """
        Property 8: 剩余支付时间计算正确性 - 正数剩余时间
        
        *For any* 待支付订单，当 expires_at > current_time 时，
        剩余支付时间应等于 expires_at - current_time（秒）。
        
        **Feature: order-enhancement, Property 8: 剩余支付时间计算正确性**
        **Validates: Requirements 3.1, 3.7**
        """
        from booking.services import TimeoutService
        
        user = self.get_or_create_user()
        
        # 创建订单，设置超时时间为 minutes_remaining 分钟后
        expires_at = timezone.now() + datetime.timedelta(minutes=minutes_remaining)
        order = self.create_order(user, status='pending', expires_at=expires_at)
        
        # 获取剩余时间
        remaining = TimeoutService.get_remaining_time(order)
        
        # 验证剩余时间大于 0
        self.assertGreater(
            remaining, 0,
            f"当 expires_at > current_time 时，剩余时间应大于 0，当前值: {remaining}"
        )
        
        # 验证剩余时间在合理范围内（允许 2 秒误差）
        expected_seconds = minutes_remaining * 60
        self.assertLessEqual(
            abs(remaining - expected_seconds), 2,
            f"剩余时间应接近 {expected_seconds} 秒，当前值: {remaining}"
        )
    
    @given(
        minutes_expired=st.integers(min_value=1, max_value=60)
    )
    @settings(max_examples=100)
    def test_property_8_remaining_time_zero_when_expired(self, minutes_expired):
        """
        Property 8: 剩余支付时间计算正确性 - 已超时返回 0
        
        *For any* 待支付订单，当 current_time > expires_at 时，
        剩余支付时间应返回 0。
        
        **Feature: order-enhancement, Property 8: 剩余支付时间计算正确性**
        **Validates: Requirements 3.1, 3.7**
        """
        from booking.services import TimeoutService
        
        user = self.get_or_create_user()
        
        # 创建订单，设置超时时间为 minutes_expired 分钟前（已超时）
        expires_at = timezone.now() - datetime.timedelta(minutes=minutes_expired)
        order = self.create_order(user, status='pending', expires_at=expires_at)
        
        # 获取剩余时间
        remaining = TimeoutService.get_remaining_time(order)
        
        # 验证剩余时间为 0
        self.assertEqual(
            remaining, 0,
            f"当 current_time > expires_at 时，剩余时间应为 0，当前值: {remaining}"
        )
    
    @given(
        status=st.sampled_from(['paid', 'completed', 'canceled'])
    )
    @settings(max_examples=100)
    def test_property_8_remaining_time_zero_for_non_pending(self, status):
        """
        Property 8: 剩余支付时间计算正确性 - 非待支付订单返回 0
        
        *For any* 非待支付状态的订单，剩余支付时间应返回 0。
        
        **Feature: order-enhancement, Property 8: 剩余支付时间计算正确性**
        **Validates: Requirements 3.7**
        """
        from booking.services import TimeoutService
        
        user = self.get_or_create_user()
        
        # 创建非待支付状态的订单，设置一个未来的超时时间
        expires_at = timezone.now() + datetime.timedelta(minutes=30)
        order = self.create_order(user, status=status, expires_at=expires_at)
        
        # 获取剩余时间
        remaining = TimeoutService.get_remaining_time(order)
        
        # 验证剩余时间为 0
        self.assertEqual(
            remaining, 0,
            f"非待支付订单的剩余时间应为 0，当前状态: {status}，剩余时间: {remaining}"
        )
    
    @given(
        minutes_remaining=st.integers(min_value=1, max_value=60)
    )
    @settings(max_examples=100)
    def test_property_8_remaining_time_zero_when_no_expires_at(self, minutes_remaining):
        """
        Property 8: 剩余支付时间计算正确性 - 无超时时间返回 0
        
        *For any* 待支付订单，如果没有设置 expires_at，剩余支付时间应返回 0。
        
        **Feature: order-enhancement, Property 8: 剩余支付时间计算正确性**
        **Validates: Requirements 3.7**
        """
        from booking.services import TimeoutService
        
        user = self.get_or_create_user()
        
        # 创建订单，不设置超时时间
        order = self.create_order(user, status='pending', expires_at=None)
        
        # 获取剩余时间
        remaining = TimeoutService.get_remaining_time(order)
        
        # 验证剩余时间为 0
        self.assertEqual(
            remaining, 0,
            f"没有设置 expires_at 时，剩余时间应为 0，当前值: {remaining}"
        )



class TimeoutCancellationPropertyTest(HypothesisTestCase):
    """
    订单超时取消完整性属性测试
    
    Property 7: 订单超时取消完整性
    Validates: Requirements 3.2, 3.3, 3.4
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
    
    def create_flight(self, capacity=100, available_seats=None):
        """创建测试航班"""
        if available_seats is None:
            available_seats = capacity
        unique_id = uuid.uuid4().hex[:6]
        departure_time = timezone.now() + datetime.timedelta(hours=24)
        return Flight.objects.create(
            flight_number=f'CA{unique_id}',
            airline_name='中国国航',
            departure_city='北京',
            arrival_city='上海',
            departure_time=departure_time,
            arrival_time=departure_time + datetime.timedelta(hours=2),
            price=Decimal('800.00'),
            discount=Decimal('0.9'),
            capacity=capacity,
            available_seats=available_seats,
            status='scheduled',
            aircraft_type='Boeing 737',
        )
    
    def create_expired_order_with_tickets(self, user, flight, ticket_count=1):
        """创建已超时的订单及其机票"""
        # 创建已超时的订单
        expires_at = timezone.now() - datetime.timedelta(minutes=5)
        order = Order.objects.create(
            user=user,
            total_price=Decimal('720.00') * ticket_count,
            status='pending',
            expires_at=expires_at
        )
        
        # 创建机票
        tickets = []
        for i in range(ticket_count):
            ticket = Ticket.objects.create(
                order=order,
                flight=flight,
                passenger_name=f'乘客{i+1}',
                passenger_id_number=f'11010119900101{1234+i:04d}',
                seat_number=f'{i+1}A',
                cabin_class='economy',
                price=Decimal('720.00'),
                status='valid',
                checked_in=False
            )
            tickets.append(ticket)
        
        return order, tickets
    
    @given(
        ticket_count=st.integers(min_value=1, max_value=5)
    )
    @settings(max_examples=100)
    def test_property_7_order_status_canceled(self, ticket_count):
        """
        Property 7: 订单超时取消完整性 - 订单状态更新
        
        *For any* 超时的待支付订单，执行超时取消后，订单状态应为"已取消"。
        
        **Feature: order-enhancement, Property 7: 订单超时取消完整性**
        **Validates: Requirements 3.2**
        """
        from booking.services import TimeoutService
        
        user = self.get_or_create_user()
        flight = self.create_flight(capacity=100, available_seats=100)
        
        # 创建已超时的订单
        order, tickets = self.create_expired_order_with_tickets(user, flight, ticket_count)
        
        # 执行超时取消
        success = TimeoutService.cancel_expired_order(order)
        
        # 验证取消成功
        self.assertTrue(success, "超时订单取消应该成功")
        
        # 刷新订单数据
        order.refresh_from_db()
        
        # 验证订单状态为已取消
        self.assertEqual(
            order.status, 'canceled',
            f"超时取消后订单状态应为 'canceled'，当前状态: {order.status}"
        )
    
    @given(
        ticket_count=st.integers(min_value=1, max_value=5)
    )
    @settings(max_examples=100)
    def test_property_7_tickets_status_canceled(self, ticket_count):
        """
        Property 7: 订单超时取消完整性 - 机票状态更新
        
        *For any* 超时的待支付订单，执行超时取消后，所有关联机票状态应为"已取消"。
        
        **Feature: order-enhancement, Property 7: 订单超时取消完整性**
        **Validates: Requirements 3.3**
        """
        from booking.services import TimeoutService
        
        user = self.get_or_create_user()
        flight = self.create_flight(capacity=100, available_seats=100)
        
        # 创建已超时的订单
        order, tickets = self.create_expired_order_with_tickets(user, flight, ticket_count)
        
        # 执行超时取消
        success = TimeoutService.cancel_expired_order(order)
        
        # 验证取消成功
        self.assertTrue(success, "超时订单取消应该成功")
        
        # 验证所有机票状态为已取消
        for ticket in tickets:
            ticket.refresh_from_db()
            self.assertEqual(
                ticket.status, 'canceled',
                f"超时取消后机票状态应为 'canceled'，当前状态: {ticket.status}"
            )
    
    @given(
        ticket_count=st.integers(min_value=1, max_value=5)
    )
    @settings(max_examples=100)
    def test_property_7_seats_released(self, ticket_count):
        """
        Property 7: 订单超时取消完整性 - 座位释放
        
        *For any* 超时的待支付订单，执行超时取消后，航班座位应恢复。
        
        **Feature: order-enhancement, Property 7: 订单超时取消完整性**
        **Validates: Requirements 3.4**
        """
        from booking.services import TimeoutService
        
        user = self.get_or_create_user()
        
        # 创建航班，初始可用座位为 50
        initial_available = 50
        flight = self.create_flight(capacity=100, available_seats=initial_available)
        
        # 创建已超时的订单
        order, tickets = self.create_expired_order_with_tickets(user, flight, ticket_count)
        
        # 执行超时取消
        success = TimeoutService.cancel_expired_order(order)
        
        # 验证取消成功
        self.assertTrue(success, "超时订单取消应该成功")
        
        # 刷新航班数据
        flight.refresh_from_db()
        
        # 验证座位已恢复
        expected_available = initial_available + ticket_count
        self.assertEqual(
            flight.available_seats, expected_available,
            f"超时取消后座位应恢复，期望: {expected_available}，实际: {flight.available_seats}"
        )
    
    @given(
        ticket_count=st.integers(min_value=1, max_value=5)
    )
    @settings(max_examples=100)
    def test_property_7_complete_cancellation(self, ticket_count):
        """
        Property 7: 订单超时取消完整性 - 完整性验证
        
        *For any* 超时的待支付订单，执行超时取消后，订单状态、机票状态和座位数应同时正确更新。
        
        **Feature: order-enhancement, Property 7: 订单超时取消完整性**
        **Validates: Requirements 3.2, 3.3, 3.4**
        """
        from booking.services import TimeoutService
        
        user = self.get_or_create_user()
        
        # 创建航班
        initial_available = 80
        flight = self.create_flight(capacity=100, available_seats=initial_available)
        
        # 创建已超时的订单
        order, tickets = self.create_expired_order_with_tickets(user, flight, ticket_count)
        
        # 执行超时取消
        success = TimeoutService.cancel_expired_order(order)
        
        # 验证取消成功
        self.assertTrue(success, "超时订单取消应该成功")
        
        # 刷新数据
        order.refresh_from_db()
        flight.refresh_from_db()
        
        # 验证订单状态
        self.assertEqual(order.status, 'canceled')
        
        # 验证所有机票状态
        for ticket in tickets:
            ticket.refresh_from_db()
            self.assertEqual(ticket.status, 'canceled')
        
        # 验证座位恢复
        expected_available = initial_available + ticket_count
        self.assertEqual(flight.available_seats, expected_available)
    
    @given(
        status=st.sampled_from(['paid', 'completed', 'canceled'])
    )
    @settings(max_examples=100)
    def test_property_7_non_pending_order_not_canceled(self, status):
        """
        Property 7: 订单超时取消完整性 - 非待支付订单不取消
        
        *For any* 非待支付状态的订单，即使已超时，也不应被取消。
        
        **Feature: order-enhancement, Property 7: 订单超时取消完整性**
        **Validates: Requirements 3.2**
        """
        from booking.services import TimeoutService
        
        user = self.get_or_create_user()
        flight = self.create_flight(capacity=100, available_seats=100)
        
        # 创建非待支付状态的订单
        expires_at = timezone.now() - datetime.timedelta(minutes=5)
        order = Order.objects.create(
            user=user,
            total_price=Decimal('720.00'),
            status=status,
            expires_at=expires_at
        )
        
        # 尝试取消
        success = TimeoutService.cancel_expired_order(order)
        
        # 验证取消失败
        self.assertFalse(success, f"非待支付订单（状态: {status}）不应被取消")
        
        # 验证订单状态未变
        order.refresh_from_db()
        self.assertEqual(order.status, status)



class RescheduleFeeCalculationPropertyTest(HypothesisTestCase):
    """
    改签差价计算属性测试
    
    Property 1: 改签差价计算正确性
    Validates: Requirements 1.2, 1.3, 1.4
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
    
    def create_flight(self, price, capacity=100, available_seats=None, departure_offset_hours=24):
        """创建测试航班"""
        if available_seats is None:
            available_seats = capacity
        unique_id = uuid.uuid4().hex[:6]
        departure_time = timezone.now() + datetime.timedelta(hours=departure_offset_hours)
        return Flight.objects.create(
            flight_number=f'CA{unique_id}',
            airline_name='中国国航',
            departure_city='北京',
            arrival_city='上海',
            departure_time=departure_time,
            arrival_time=departure_time + datetime.timedelta(hours=2),
            price=price,
            discount=Decimal('1.0'),
            capacity=capacity,
            available_seats=available_seats,
            status='scheduled',
            aircraft_type='Boeing 737',
        )
    
    def create_ticket(self, user, flight, price, cabin_class='economy'):
        """创建测试机票"""
        order = Order.objects.create(
            user=user,
            total_price=price,
            status='paid'
        )
        return Ticket.objects.create(
            order=order,
            flight=flight,
            passenger_name='张三',
            passenger_id_number='110101199001011234',
            seat_number='10A',
            cabin_class=cabin_class,
            price=price,
            status='valid',
            checked_in=False
        )
    
    @given(
        original_price=st.decimals(min_value=100, max_value=5000, places=2, allow_nan=False, allow_infinity=False),
        target_price=st.decimals(min_value=100, max_value=5000, places=2, allow_nan=False, allow_infinity=False)
    )
    @settings(max_examples=100)
    def test_property_1_price_difference_calculation(self, original_price, target_price):
        """
        Property 1: 改签差价计算正确性 - 差价等于新票价减原票价
        
        *For any* 原机票和目标航班组合，改签差价应等于目标航班价格减去原机票价格。
        
        **Feature: order-enhancement, Property 1: 改签差价计算正确性**
        **Validates: Requirements 1.2**
        """
        from booking.services import ReschedulingService
        
        user = self.get_or_create_user()
        
        # 创建原航班和机票
        original_flight = self.create_flight(price=original_price, departure_offset_hours=24)
        ticket = self.create_ticket(user, original_flight, price=original_price)
        
        # 创建目标航班
        target_flight = self.create_flight(price=target_price, departure_offset_hours=48)
        
        # 计算改签费用
        fee_info = ReschedulingService.calculate_reschedule_fee(ticket, target_flight)
        
        # 验证差价计算正确
        expected_difference = target_price - original_price
        self.assertEqual(
            fee_info['price_difference'],
            expected_difference.quantize(Decimal('0.01')),
            f"差价应等于新票价减原票价，期望: {expected_difference}，实际: {fee_info['price_difference']}"
        )
    
    @given(
        original_price=st.decimals(min_value=100, max_value=3000, places=2, allow_nan=False, allow_infinity=False),
        price_increase=st.decimals(min_value=1, max_value=2000, places=2, allow_nan=False, allow_infinity=False)
    )
    @settings(max_examples=100)
    def test_property_1_positive_difference_requires_payment(self, original_price, price_increase):
        """
        Property 1: 改签差价计算正确性 - 正差价需补款
        
        *For any* 改签差价为正数（需补差价）时，总支付金额应等于差价加手续费。
        
        **Feature: order-enhancement, Property 1: 改签差价计算正确性**
        **Validates: Requirements 1.3**
        """
        from booking.services import ReschedulingService
        
        user = self.get_or_create_user()
        
        # 创建原航班和机票
        original_flight = self.create_flight(price=original_price, departure_offset_hours=24)
        ticket = self.create_ticket(user, original_flight, price=original_price)
        
        # 创建更贵的目标航班
        target_price = original_price + price_increase
        target_flight = self.create_flight(price=target_price, departure_offset_hours=48)
        
        # 计算改签费用
        fee_info = ReschedulingService.calculate_reschedule_fee(ticket, target_flight)
        
        # 验证差价为正
        self.assertGreater(
            fee_info['price_difference'], 0,
            f"差价应为正数，实际: {fee_info['price_difference']}"
        )
        
        # 验证总支付金额 = 差价 + 手续费
        expected_total = fee_info['price_difference'] + fee_info['reschedule_fee']
        self.assertEqual(
            fee_info['total_to_pay'],
            expected_total.quantize(Decimal('0.01')),
            f"总支付金额应等于差价加手续费，期望: {expected_total}，实际: {fee_info['total_to_pay']}"
        )
        
        # 验证退款金额为 0
        self.assertEqual(
            fee_info['refund_amount'],
            Decimal('0.00'),
            f"正差价时退款金额应为 0，实际: {fee_info['refund_amount']}"
        )
    
    @given(
        original_price=st.decimals(min_value=500, max_value=5000, places=2, allow_nan=False, allow_infinity=False),
        price_decrease=st.decimals(min_value=100, max_value=400, places=2, allow_nan=False, allow_infinity=False)
    )
    @settings(max_examples=100)
    def test_property_1_negative_difference_allows_refund(self, original_price, price_decrease):
        """
        Property 1: 改签差价计算正确性 - 负差价可退款
        
        *For any* 改签差价为负数（可退差价）时，退款金额应等于差价绝对值减手续费（如果结果为正）。
        
        **Feature: order-enhancement, Property 1: 改签差价计算正确性**
        **Validates: Requirements 1.4**
        """
        from booking.services import ReschedulingService
        
        user = self.get_or_create_user()
        
        # 创建原航班和机票
        original_flight = self.create_flight(price=original_price, departure_offset_hours=24)
        ticket = self.create_ticket(user, original_flight, price=original_price)
        
        # 创建更便宜的目标航班
        target_price = original_price - price_decrease
        target_flight = self.create_flight(price=target_price, departure_offset_hours=48)
        
        # 计算改签费用
        fee_info = ReschedulingService.calculate_reschedule_fee(ticket, target_flight)
        
        # 验证差价为负
        self.assertLess(
            fee_info['price_difference'], 0,
            f"差价应为负数，实际: {fee_info['price_difference']}"
        )
        
        # 计算期望的退款金额
        expected_refund = abs(fee_info['price_difference']) - fee_info['reschedule_fee']
        if expected_refund < 0:
            expected_refund = Decimal('0.00')
        
        self.assertEqual(
            fee_info['refund_amount'],
            expected_refund.quantize(Decimal('0.01')),
            f"退款金额计算不正确，期望: {expected_refund}，实际: {fee_info['refund_amount']}"
        )
    
    @given(
        original_price=st.decimals(min_value=100, max_value=5000, places=2, allow_nan=False, allow_infinity=False)
    )
    @settings(max_examples=100)
    def test_property_1_reschedule_fee_based_on_original_price(self, original_price):
        """
        Property 1: 改签差价计算正确性 - 手续费基于原票价
        
        *For any* 改签操作，手续费应等于原票价的 5%。
        
        **Feature: order-enhancement, Property 1: 改签差价计算正确性**
        **Validates: Requirements 1.2**
        """
        from booking.services import ReschedulingService
        
        user = self.get_or_create_user()
        
        # 创建原航班和机票
        original_flight = self.create_flight(price=original_price, departure_offset_hours=24)
        ticket = self.create_ticket(user, original_flight, price=original_price)
        
        # 创建目标航班（价格任意）
        target_flight = self.create_flight(price=Decimal('1000.00'), departure_offset_hours=48)
        
        # 计算改签费用
        fee_info = ReschedulingService.calculate_reschedule_fee(ticket, target_flight)
        
        # 验证手续费 = 原票价 * 5%
        expected_fee = (original_price * Decimal('0.05')).quantize(Decimal('0.01'))
        self.assertEqual(
            fee_info['reschedule_fee'],
            expected_fee,
            f"手续费应等于原票价的 5%，期望: {expected_fee}，实际: {fee_info['reschedule_fee']}"
        )



class RescheduleOperationIntegrityPropertyTest(HypothesisTestCase):
    """
    改签操作完整性属性测试
    
    Property 2: 改签操作完整性
    Validates: Requirements 1.5, 1.6
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
    
    def create_flight(self, price, capacity=100, available_seats=None, departure_offset_hours=24):
        """创建测试航班"""
        if available_seats is None:
            available_seats = capacity
        unique_id = uuid.uuid4().hex[:6]
        departure_time = timezone.now() + datetime.timedelta(hours=departure_offset_hours)
        return Flight.objects.create(
            flight_number=f'CA{unique_id}',
            airline_name='中国国航',
            departure_city='北京',
            arrival_city='上海',
            departure_time=departure_time,
            arrival_time=departure_time + datetime.timedelta(hours=2),
            price=price,
            discount=Decimal('1.0'),
            capacity=capacity,
            available_seats=available_seats,
            status='scheduled',
            aircraft_type='Boeing 737',
        )
    
    def create_ticket(self, user, flight, price, seat_number='10A', cabin_class='economy'):
        """创建测试机票"""
        order = Order.objects.create(
            user=user,
            total_price=price,
            status='paid'
        )
        return Ticket.objects.create(
            order=order,
            flight=flight,
            passenger_name='张三',
            passenger_id_number='110101199001011234',
            seat_number=seat_number,
            cabin_class=cabin_class,
            price=price,
            status='valid',
            checked_in=False
        )
    
    @given(
        original_price=st.decimals(min_value=500, max_value=2000, places=2, allow_nan=False, allow_infinity=False),
        target_price=st.decimals(min_value=500, max_value=2000, places=2, allow_nan=False, allow_infinity=False),
        seat_row=st.integers(min_value=1, max_value=30),
        seat_col=st.sampled_from(['A', 'B', 'C', 'D', 'E', 'F'])
    )
    @settings(max_examples=100)
    def test_property_2_original_ticket_status_rescheduled(self, original_price, target_price, seat_row, seat_col):
        """
        Property 2: 改签操作完整性 - 原机票状态变为已改签
        
        *For any* 成功的改签操作，原机票状态应变为"已改签"。
        
        **Feature: order-enhancement, Property 2: 改签操作完整性**
        **Validates: Requirements 1.5**
        """
        from booking.services import ReschedulingService
        
        user = self.get_or_create_user()
        
        # 创建原航班和机票
        original_flight = self.create_flight(price=original_price, departure_offset_hours=24)
        ticket = self.create_ticket(user, original_flight, price=original_price)
        
        # 创建目标航班
        target_flight = self.create_flight(price=target_price, departure_offset_hours=48)
        target_seat = f'{seat_row}{seat_col}'
        
        # 执行改签
        new_ticket = ReschedulingService.execute_reschedule(
            ticket, target_flight, target_seat
        )
        
        # 刷新原机票数据
        ticket.refresh_from_db()
        
        # 验证原机票状态为已改签
        self.assertEqual(
            ticket.status, 'rescheduled',
            f"改签后原机票状态应为 'rescheduled'，当前状态: {ticket.status}"
        )
    
    @given(
        original_price=st.decimals(min_value=500, max_value=2000, places=2, allow_nan=False, allow_infinity=False),
        target_price=st.decimals(min_value=500, max_value=2000, places=2, allow_nan=False, allow_infinity=False),
        seat_row=st.integers(min_value=1, max_value=30),
        seat_col=st.sampled_from(['A', 'B', 'C', 'D', 'E', 'F'])
    )
    @settings(max_examples=100)
    def test_property_2_new_ticket_created_valid(self, original_price, target_price, seat_row, seat_col):
        """
        Property 2: 改签操作完整性 - 新机票被创建且状态为有效
        
        *For any* 成功的改签操作，新机票应被创建且状态为"有效"。
        
        **Feature: order-enhancement, Property 2: 改签操作完整性**
        **Validates: Requirements 1.5**
        """
        from booking.services import ReschedulingService
        
        user = self.get_or_create_user()
        
        # 创建原航班和机票
        original_flight = self.create_flight(price=original_price, departure_offset_hours=24)
        ticket = self.create_ticket(user, original_flight, price=original_price)
        
        # 创建目标航班
        target_flight = self.create_flight(price=target_price, departure_offset_hours=48)
        target_seat = f'{seat_row}{seat_col}'
        
        # 执行改签
        new_ticket = ReschedulingService.execute_reschedule(
            ticket, target_flight, target_seat
        )
        
        # 验证新机票存在
        self.assertIsNotNone(new_ticket, "改签后应创建新机票")
        self.assertIsNotNone(new_ticket.pk, "新机票应已保存到数据库")
        
        # 验证新机票状态为有效
        self.assertEqual(
            new_ticket.status, 'valid',
            f"新机票状态应为 'valid'，当前状态: {new_ticket.status}"
        )
        
        # 验证新机票关联目标航班
        self.assertEqual(
            new_ticket.flight_id, target_flight.id,
            "新机票应关联目标航班"
        )
        
        # 验证新机票座位号正确
        self.assertEqual(
            new_ticket.seat_number, target_seat,
            f"新机票座位号应为 {target_seat}，当前: {new_ticket.seat_number}"
        )
    
    @given(
        original_price=st.decimals(min_value=500, max_value=2000, places=2, allow_nan=False, allow_infinity=False),
        target_price=st.decimals(min_value=500, max_value=2000, places=2, allow_nan=False, allow_infinity=False),
        seat_row=st.integers(min_value=1, max_value=30),
        seat_col=st.sampled_from(['A', 'B', 'C', 'D', 'E', 'F'])
    )
    @settings(max_examples=100)
    def test_property_2_original_flight_seats_increased(self, original_price, target_price, seat_row, seat_col):
        """
        Property 2: 改签操作完整性 - 原航班座位增加1
        
        *For any* 成功的改签操作，原航班座位应增加1。
        
        **Feature: order-enhancement, Property 2: 改签操作完整性**
        **Validates: Requirements 1.6**
        """
        from booking.services import ReschedulingService
        
        user = self.get_or_create_user()
        
        # 创建原航班和机票
        original_available = 50
        original_flight = self.create_flight(
            price=original_price, 
            departure_offset_hours=24,
            available_seats=original_available
        )
        ticket = self.create_ticket(user, original_flight, price=original_price)
        
        # 创建目标航班
        target_flight = self.create_flight(price=target_price, departure_offset_hours=48)
        target_seat = f'{seat_row}{seat_col}'
        
        # 执行改签
        new_ticket = ReschedulingService.execute_reschedule(
            ticket, target_flight, target_seat
        )
        
        # 刷新原航班数据
        original_flight.refresh_from_db()
        
        # 验证原航班座位增加1
        expected_available = original_available + 1
        self.assertEqual(
            original_flight.available_seats, expected_available,
            f"改签后原航班座位应增加1，期望: {expected_available}，实际: {original_flight.available_seats}"
        )
    
    @given(
        original_price=st.decimals(min_value=500, max_value=2000, places=2, allow_nan=False, allow_infinity=False),
        target_price=st.decimals(min_value=500, max_value=2000, places=2, allow_nan=False, allow_infinity=False),
        seat_row=st.integers(min_value=1, max_value=30),
        seat_col=st.sampled_from(['A', 'B', 'C', 'D', 'E', 'F'])
    )
    @settings(max_examples=100)
    def test_property_2_target_flight_seats_decreased(self, original_price, target_price, seat_row, seat_col):
        """
        Property 2: 改签操作完整性 - 目标航班座位减少1
        
        *For any* 成功的改签操作，目标航班座位应减少1。
        
        **Feature: order-enhancement, Property 2: 改签操作完整性**
        **Validates: Requirements 1.6**
        """
        from booking.services import ReschedulingService
        
        user = self.get_or_create_user()
        
        # 创建原航班和机票
        original_flight = self.create_flight(price=original_price, departure_offset_hours=24)
        ticket = self.create_ticket(user, original_flight, price=original_price)
        
        # 创建目标航班
        target_available = 80
        target_flight = self.create_flight(
            price=target_price, 
            departure_offset_hours=48,
            available_seats=target_available
        )
        target_seat = f'{seat_row}{seat_col}'
        
        # 执行改签
        new_ticket = ReschedulingService.execute_reschedule(
            ticket, target_flight, target_seat
        )
        
        # 刷新目标航班数据
        target_flight.refresh_from_db()
        
        # 验证目标航班座位减少1
        expected_available = target_available - 1
        self.assertEqual(
            target_flight.available_seats, expected_available,
            f"改签后目标航班座位应减少1，期望: {expected_available}，实际: {target_flight.available_seats}"
        )
    
    @given(
        original_price=st.decimals(min_value=500, max_value=2000, places=2, allow_nan=False, allow_infinity=False),
        target_price=st.decimals(min_value=500, max_value=2000, places=2, allow_nan=False, allow_infinity=False),
        seat_row=st.integers(min_value=1, max_value=30),
        seat_col=st.sampled_from(['A', 'B', 'C', 'D', 'E', 'F'])
    )
    @settings(max_examples=100)
    def test_property_2_complete_integrity(self, original_price, target_price, seat_row, seat_col):
        """
        Property 2: 改签操作完整性 - 完整性验证
        
        *For any* 成功的改签操作，原机票状态应变为"已改签"，新机票应被创建且状态为"有效"，
        原航班座位应增加1，目标航班座位应减少1。
        
        **Feature: order-enhancement, Property 2: 改签操作完整性**
        **Validates: Requirements 1.5, 1.6**
        """
        from booking.services import ReschedulingService
        
        user = self.get_or_create_user()
        
        # 创建原航班和机票
        original_available = 60
        original_flight = self.create_flight(
            price=original_price, 
            departure_offset_hours=24,
            available_seats=original_available
        )
        ticket = self.create_ticket(user, original_flight, price=original_price)
        original_ticket_id = ticket.id
        
        # 创建目标航班
        target_available = 70
        target_flight = self.create_flight(
            price=target_price, 
            departure_offset_hours=48,
            available_seats=target_available
        )
        target_seat = f'{seat_row}{seat_col}'
        
        # 执行改签
        new_ticket = ReschedulingService.execute_reschedule(
            ticket, target_flight, target_seat
        )
        
        # 刷新所有数据
        ticket.refresh_from_db()
        original_flight.refresh_from_db()
        target_flight.refresh_from_db()
        
        # 验证原机票状态
        self.assertEqual(ticket.status, 'rescheduled')
        
        # 验证新机票
        self.assertIsNotNone(new_ticket)
        self.assertEqual(new_ticket.status, 'valid')
        self.assertEqual(new_ticket.flight_id, target_flight.id)
        self.assertEqual(new_ticket.seat_number, target_seat)
        
        # 验证原航班座位增加
        self.assertEqual(original_flight.available_seats, original_available + 1)
        
        # 验证目标航班座位减少
        self.assertEqual(target_flight.available_seats, target_available - 1)
        
        # 验证新机票继承乘客信息
        self.assertEqual(new_ticket.passenger_name, ticket.passenger_name)
        self.assertEqual(new_ticket.passenger_id_number, ticket.passenger_id_number)



class RescheduleLogConsistencyPropertyTest(HypothesisTestCase):
    """
    改签记录一致性属性测试
    
    Property 3: 改签记录一致性
    Validates: Requirements 1.9
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
    
    def create_flight(self, price, capacity=100, available_seats=None, departure_offset_hours=24):
        """创建测试航班"""
        if available_seats is None:
            available_seats = capacity
        unique_id = uuid.uuid4().hex[:6]
        departure_time = timezone.now() + datetime.timedelta(hours=departure_offset_hours)
        return Flight.objects.create(
            flight_number=f'CA{unique_id}',
            airline_name='中国国航',
            departure_city='北京',
            arrival_city='上海',
            departure_time=departure_time,
            arrival_time=departure_time + datetime.timedelta(hours=2),
            price=price,
            discount=Decimal('1.0'),
            capacity=capacity,
            available_seats=available_seats,
            status='scheduled',
            aircraft_type='Boeing 737',
        )
    
    def create_ticket(self, user, flight, price, seat_number='10A', cabin_class='economy'):
        """创建测试机票"""
        order = Order.objects.create(
            user=user,
            total_price=price,
            status='paid'
        )
        return Ticket.objects.create(
            order=order,
            flight=flight,
            passenger_name='张三',
            passenger_id_number='110101199001011234',
            seat_number=seat_number,
            cabin_class=cabin_class,
            price=price,
            status='valid',
            checked_in=False
        )
    
    @given(
        original_price=st.decimals(min_value=500, max_value=2000, places=2, allow_nan=False, allow_infinity=False),
        target_price=st.decimals(min_value=500, max_value=2000, places=2, allow_nan=False, allow_infinity=False),
        seat_row=st.integers(min_value=1, max_value=30),
        seat_col=st.sampled_from(['A', 'B', 'C', 'D', 'E', 'F'])
    )
    @settings(max_examples=100)
    def test_property_3_reschedule_log_created(self, original_price, target_price, seat_row, seat_col):
        """
        Property 3: 改签记录一致性 - 改签记录被创建
        
        *For any* 成功的改签操作，应创建一条改签记录。
        
        **Feature: order-enhancement, Property 3: 改签记录一致性**
        **Validates: Requirements 1.9**
        """
        from booking.services import ReschedulingService
        from booking.models import RescheduleLog
        
        user = self.get_or_create_user()
        
        # 记录改签前的记录数
        initial_log_count = RescheduleLog.objects.count()
        
        # 创建原航班和机票
        original_flight = self.create_flight(price=original_price, departure_offset_hours=24)
        ticket = self.create_ticket(user, original_flight, price=original_price)
        
        # 创建目标航班
        target_flight = self.create_flight(price=target_price, departure_offset_hours=48)
        target_seat = f'{seat_row}{seat_col}'
        
        # 执行改签
        new_ticket = ReschedulingService.execute_reschedule(
            ticket, target_flight, target_seat
        )
        
        # 验证改签记录被创建
        final_log_count = RescheduleLog.objects.count()
        self.assertEqual(
            final_log_count, initial_log_count + 1,
            f"改签后应创建一条改签记录，期望: {initial_log_count + 1}，实际: {final_log_count}"
        )
    
    @given(
        original_price=st.decimals(min_value=500, max_value=2000, places=2, allow_nan=False, allow_infinity=False),
        target_price=st.decimals(min_value=500, max_value=2000, places=2, allow_nan=False, allow_infinity=False),
        seat_row=st.integers(min_value=1, max_value=30),
        seat_col=st.sampled_from(['A', 'B', 'C', 'D', 'E', 'F'])
    )
    @settings(max_examples=100)
    def test_property_3_log_original_ticket_correct(self, original_price, target_price, seat_row, seat_col):
        """
        Property 3: 改签记录一致性 - 原机票信息正确
        
        *For any* 成功的改签操作，改签记录中的原机票应与实际原机票一致。
        
        **Feature: order-enhancement, Property 3: 改签记录一致性**
        **Validates: Requirements 1.9**
        """
        from booking.services import ReschedulingService
        from booking.models import RescheduleLog
        
        user = self.get_or_create_user()
        
        # 创建原航班和机票
        original_flight = self.create_flight(price=original_price, departure_offset_hours=24)
        ticket = self.create_ticket(user, original_flight, price=original_price)
        original_ticket_id = ticket.id
        
        # 创建目标航班
        target_flight = self.create_flight(price=target_price, departure_offset_hours=48)
        target_seat = f'{seat_row}{seat_col}'
        
        # 执行改签
        new_ticket = ReschedulingService.execute_reschedule(
            ticket, target_flight, target_seat
        )
        
        # 获取改签记录
        log = RescheduleLog.objects.filter(original_ticket_id=original_ticket_id).first()
        
        # 验证改签记录存在
        self.assertIsNotNone(log, "应存在改签记录")
        
        # 验证原机票信息正确
        self.assertEqual(
            log.original_ticket_id, original_ticket_id,
            f"改签记录中的原机票ID应正确，期望: {original_ticket_id}，实际: {log.original_ticket_id}"
        )
        self.assertEqual(
            log.original_flight_id, original_flight.id,
            f"改签记录中的原航班ID应正确，期望: {original_flight.id}，实际: {log.original_flight_id}"
        )
    
    @given(
        original_price=st.decimals(min_value=500, max_value=2000, places=2, allow_nan=False, allow_infinity=False),
        target_price=st.decimals(min_value=500, max_value=2000, places=2, allow_nan=False, allow_infinity=False),
        seat_row=st.integers(min_value=1, max_value=30),
        seat_col=st.sampled_from(['A', 'B', 'C', 'D', 'E', 'F'])
    )
    @settings(max_examples=100)
    def test_property_3_log_new_ticket_correct(self, original_price, target_price, seat_row, seat_col):
        """
        Property 3: 改签记录一致性 - 新机票信息正确
        
        *For any* 成功的改签操作，改签记录中的新机票应与实际新机票一致。
        
        **Feature: order-enhancement, Property 3: 改签记录一致性**
        **Validates: Requirements 1.9**
        """
        from booking.services import ReschedulingService
        from booking.models import RescheduleLog
        
        user = self.get_or_create_user()
        
        # 创建原航班和机票
        original_flight = self.create_flight(price=original_price, departure_offset_hours=24)
        ticket = self.create_ticket(user, original_flight, price=original_price)
        
        # 创建目标航班
        target_flight = self.create_flight(price=target_price, departure_offset_hours=48)
        target_seat = f'{seat_row}{seat_col}'
        
        # 执行改签
        new_ticket = ReschedulingService.execute_reschedule(
            ticket, target_flight, target_seat
        )
        
        # 获取改签记录
        log = RescheduleLog.objects.filter(new_ticket_id=new_ticket.id).first()
        
        # 验证改签记录存在
        self.assertIsNotNone(log, "应存在改签记录")
        
        # 验证新机票信息正确
        self.assertEqual(
            log.new_ticket_id, new_ticket.id,
            f"改签记录中的新机票ID应正确，期望: {new_ticket.id}，实际: {log.new_ticket_id}"
        )
        self.assertEqual(
            log.new_flight_id, target_flight.id,
            f"改签记录中的新航班ID应正确，期望: {target_flight.id}，实际: {log.new_flight_id}"
        )
    
    @given(
        original_price=st.decimals(min_value=500, max_value=2000, places=2, allow_nan=False, allow_infinity=False),
        target_price=st.decimals(min_value=500, max_value=2000, places=2, allow_nan=False, allow_infinity=False),
        seat_row=st.integers(min_value=1, max_value=30),
        seat_col=st.sampled_from(['A', 'B', 'C', 'D', 'E', 'F'])
    )
    @settings(max_examples=100)
    def test_property_3_log_price_difference_correct(self, original_price, target_price, seat_row, seat_col):
        """
        Property 3: 改签记录一致性 - 差价信息正确
        
        *For any* 成功的改签操作，改签记录中的差价应与实际计算的差价一致。
        
        **Feature: order-enhancement, Property 3: 改签记录一致性**
        **Validates: Requirements 1.9**
        """
        from booking.services import ReschedulingService
        from booking.models import RescheduleLog
        
        user = self.get_or_create_user()
        
        # 创建原航班和机票
        original_flight = self.create_flight(price=original_price, departure_offset_hours=24)
        ticket = self.create_ticket(user, original_flight, price=original_price)
        
        # 创建目标航班
        target_flight = self.create_flight(price=target_price, departure_offset_hours=48)
        target_seat = f'{seat_row}{seat_col}'
        
        # 计算期望的差价
        fee_info = ReschedulingService.calculate_reschedule_fee(ticket, target_flight)
        expected_difference = fee_info['price_difference']
        expected_fee = fee_info['reschedule_fee']
        
        # 执行改签
        new_ticket = ReschedulingService.execute_reschedule(
            ticket, target_flight, target_seat
        )
        
        # 获取改签记录
        log = RescheduleLog.objects.filter(new_ticket_id=new_ticket.id).first()
        
        # 验证改签记录存在
        self.assertIsNotNone(log, "应存在改签记录")
        
        # 验证差价信息正确
        self.assertEqual(
            log.price_difference, expected_difference,
            f"改签记录中的差价应正确，期望: {expected_difference}，实际: {log.price_difference}"
        )
        self.assertEqual(
            log.reschedule_fee, expected_fee,
            f"改签记录中的手续费应正确，期望: {expected_fee}，实际: {log.reschedule_fee}"
        )
    
    @given(
        original_price=st.decimals(min_value=500, max_value=2000, places=2, allow_nan=False, allow_infinity=False),
        target_price=st.decimals(min_value=500, max_value=2000, places=2, allow_nan=False, allow_infinity=False),
        seat_row=st.integers(min_value=1, max_value=30),
        seat_col=st.sampled_from(['A', 'B', 'C', 'D', 'E', 'F'])
    )
    @settings(max_examples=100)
    def test_property_3_complete_log_consistency(self, original_price, target_price, seat_row, seat_col):
        """
        Property 3: 改签记录一致性 - 完整性验证
        
        *For any* 成功的改签操作，应创建一条改签记录，记录中的原机票、新机票、差价信息应与实际操作一致。
        
        **Feature: order-enhancement, Property 3: 改签记录一致性**
        **Validates: Requirements 1.9**
        """
        from booking.services import ReschedulingService
        from booking.models import RescheduleLog
        
        user = self.get_or_create_user()
        
        # 创建原航班和机票
        original_flight = self.create_flight(price=original_price, departure_offset_hours=24)
        ticket = self.create_ticket(user, original_flight, price=original_price)
        original_ticket_id = ticket.id
        
        # 创建目标航班
        target_flight = self.create_flight(price=target_price, departure_offset_hours=48)
        target_seat = f'{seat_row}{seat_col}'
        
        # 计算期望的差价
        fee_info = ReschedulingService.calculate_reschedule_fee(ticket, target_flight)
        
        # 执行改签
        new_ticket = ReschedulingService.execute_reschedule(
            ticket, target_flight, target_seat
        )
        
        # 获取改签记录
        log = RescheduleLog.objects.filter(
            original_ticket_id=original_ticket_id,
            new_ticket_id=new_ticket.id
        ).first()
        
        # 验证改签记录存在
        self.assertIsNotNone(log, "应存在改签记录")
        
        # 验证所有字段
        self.assertEqual(log.original_ticket_id, original_ticket_id)
        self.assertEqual(log.new_ticket_id, new_ticket.id)
        self.assertEqual(log.original_flight_id, original_flight.id)
        self.assertEqual(log.new_flight_id, target_flight.id)
        self.assertEqual(log.price_difference, fee_info['price_difference'])
        self.assertEqual(log.reschedule_fee, fee_info['reschedule_fee'])
        self.assertIsNotNone(log.created_at)


class SeatInventoryAtomicityPropertyTest(HypothesisTestCase):
    """
    座位库存操作原子性属性测试
    
    Property 5: 座位库存操作原子性
    Validates: Requirements 2.1, 2.2, 2.3
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
    
    def create_flight(self, capacity=100, available_seats=None):
        """创建测试航班"""
        if available_seats is None:
            available_seats = capacity
        unique_id = uuid.uuid4().hex[:6]
        departure_time = timezone.now() + datetime.timedelta(hours=24)
        return Flight.objects.create(
            flight_number=f'CA{unique_id}',
            airline_name='中国国航',
            departure_city='北京',
            arrival_city='上海',
            departure_time=departure_time,
            arrival_time=departure_time + datetime.timedelta(hours=2),
            price=Decimal('800.00'),
            discount=Decimal('0.9'),
            capacity=capacity,
            available_seats=available_seats,
            status='scheduled',
            aircraft_type='Boeing 737',
        )
    
    @given(
        capacity=st.integers(min_value=50, max_value=200),
        ticket_count=st.integers(min_value=1, max_value=10)
    )
    @settings(max_examples=100)
    def test_property_5_order_creation_reserves_seats(self, capacity, ticket_count):
        """
        Property 5: 座位库存操作原子性 - 订单创建预留座位
        
        *For any* 订单创建操作，航班座位数的变更应与机票数量一致。
        创建 N 张机票后，航班可用座位应减少 N。
        
        **Feature: order-enhancement, Property 5: 座位库存操作原子性**
        **Validates: Requirements 2.1, 2.2**
        """
        from booking.services import InventoryService
        
        # 创建航班
        flight = self.create_flight(capacity=capacity, available_seats=capacity)
        initial_available = flight.available_seats
        
        # 使用 InventoryService 预留座位
        success = InventoryService.reserve_seats(flight, ticket_count)
        
        # 刷新航班数据
        flight.refresh_from_db()
        
        if success:
            # 验证座位减少量等于机票数量
            expected_available = initial_available - ticket_count
            self.assertEqual(
                flight.available_seats, expected_available,
                f"预留 {ticket_count} 个座位后，可用座位应为 {expected_available}，实际: {flight.available_seats}"
            )
        else:
            # 如果预留失败，座位数应保持不变
            self.assertEqual(
                flight.available_seats, initial_available,
                f"预留失败时座位数应保持不变，期望: {initial_available}，实际: {flight.available_seats}"
            )
    
    @given(
        capacity=st.integers(min_value=50, max_value=200),
        ticket_count=st.integers(min_value=1, max_value=10)
    )
    @settings(max_examples=100)
    def test_property_5_refund_releases_seats(self, capacity, ticket_count):
        """
        Property 5: 座位库存操作原子性 - 退票释放座位
        
        *For any* 退票操作，航班座位数的变更应与机票数量一致。
        退 N 张机票后，航班可用座位应增加 N（不超过容量）。
        
        **Feature: order-enhancement, Property 5: 座位库存操作原子性**
        **Validates: Requirements 2.3**
        """
        from booking.services import InventoryService
        
        # 创建航班，初始可用座位为容量的一半
        initial_available = capacity // 2
        flight = self.create_flight(capacity=capacity, available_seats=initial_available)
        
        # 使用 InventoryService 释放座位
        success = InventoryService.release_seats(flight, ticket_count)
        
        # 刷新航班数据
        flight.refresh_from_db()
        
        # 验证座位增加量等于机票数量（不超过容量）
        expected_available = min(initial_available + ticket_count, capacity)
        self.assertEqual(
            flight.available_seats, expected_available,
            f"释放 {ticket_count} 个座位后，可用座位应为 {expected_available}，实际: {flight.available_seats}"
        )
    
    @given(
        capacity=st.integers(min_value=50, max_value=200),
        reserve_count=st.integers(min_value=1, max_value=20),
        release_count=st.integers(min_value=1, max_value=20)
    )
    @settings(max_examples=100)
    def test_property_5_reserve_then_release_consistency(self, capacity, reserve_count, release_count):
        """
        Property 5: 座位库存操作原子性 - 预留后释放一致性
        
        *For any* 先预留后释放的操作序列，最终座位数应等于初始座位数减去预留数加上释放数
        （在边界范围内）。
        
        **Feature: order-enhancement, Property 5: 座位库存操作原子性**
        **Validates: Requirements 2.1, 2.2, 2.3**
        """
        from booking.services import InventoryService
        
        # 创建航班
        flight = self.create_flight(capacity=capacity, available_seats=capacity)
        initial_available = flight.available_seats
        
        # 预留座位
        reserve_success = InventoryService.reserve_seats(flight, reserve_count)
        flight.refresh_from_db()
        after_reserve = flight.available_seats
        
        # 释放座位
        release_success = InventoryService.release_seats(flight, release_count)
        flight.refresh_from_db()
        final_available = flight.available_seats
        
        # 计算期望的最终座位数
        if reserve_success:
            expected_after_reserve = initial_available - reserve_count
        else:
            expected_after_reserve = initial_available
        
        expected_final = min(expected_after_reserve + release_count, capacity)
        expected_final = max(expected_final, 0)
        
        # 验证最终座位数
        self.assertEqual(
            final_available, expected_final,
            f"预留 {reserve_count} 后释放 {release_count}，期望最终座位: {expected_final}，实际: {final_available}"
        )
    
    @given(
        capacity=st.integers(min_value=20, max_value=100),
        ticket_count=st.integers(min_value=1, max_value=5)
    )
    @settings(max_examples=100)
    def test_property_5_order_cancel_releases_all_tickets(self, capacity, ticket_count):
        """
        Property 5: 座位库存操作原子性 - 订单取消释放所有机票座位
        
        *For any* 订单取消操作，应释放该订单所有机票占用的座位。
        取消包含 N 张机票的订单后，航班可用座位应增加 N。
        
        **Feature: order-enhancement, Property 5: 座位库存操作原子性**
        **Validates: Requirements 2.3**
        """
        from booking.services import InventoryService
        
        user = self.get_or_create_user()
        
        # 创建航班
        initial_available = capacity // 2
        flight = self.create_flight(capacity=capacity, available_seats=initial_available)
        
        # 创建订单和机票
        order = Order.objects.create(
            user=user,
            total_price=Decimal('720.00') * ticket_count,
            status='paid'
        )
        
        tickets = []
        for i in range(ticket_count):
            ticket = Ticket.objects.create(
                order=order,
                flight=flight,
                passenger_name=f'乘客{i+1}',
                passenger_id_number=f'11010119900101{1234+i:04d}',
                seat_number=f'{i+1}A',
                cabin_class='economy',
                price=Decimal('720.00'),
                status='valid',
                checked_in=False
            )
            tickets.append(ticket)
        
        # 模拟订单取消：更新机票状态并释放座位
        for ticket in tickets:
            ticket.status = 'refunded'
            ticket.save()
        
        # 使用 InventoryService 释放座位
        InventoryService.release_seats(flight, ticket_count)
        
        # 刷新航班数据
        flight.refresh_from_db()
        
        # 验证座位已释放
        expected_available = min(initial_available + ticket_count, capacity)
        self.assertEqual(
            flight.available_seats, expected_available,
            f"取消 {ticket_count} 张机票后，可用座位应为 {expected_available}，实际: {flight.available_seats}"
        )
    
    @given(
        capacity=st.integers(min_value=50, max_value=200),
        over_reserve_count=st.integers(min_value=1, max_value=50)
    )
    @settings(max_examples=100)
    def test_property_5_reserve_fails_when_insufficient(self, capacity, over_reserve_count):
        """
        Property 5: 座位库存操作原子性 - 座位不足时预留失败
        
        *For any* 预留数量超过可用座位的操作，应失败且座位数保持不变。
        
        **Feature: order-enhancement, Property 5: 座位库存操作原子性**
        **Validates: Requirements 2.1**
        """
        from booking.services import InventoryService
        
        # 创建航班，可用座位较少
        available = 10
        flight = self.create_flight(capacity=capacity, available_seats=available)
        
        # 尝试预留超过可用座位的数量
        reserve_count = available + over_reserve_count
        success = InventoryService.reserve_seats(flight, reserve_count)
        
        # 刷新航班数据
        flight.refresh_from_db()
        
        # 验证预留失败
        self.assertFalse(
            success,
            f"预留 {reserve_count} 个座位（可用 {available}）应失败"
        )
        
        # 验证座位数保持不变
        self.assertEqual(
            flight.available_seats, available,
            f"预留失败时座位数应保持不变，期望: {available}，实际: {flight.available_seats}"
        )
    
    @given(
        capacity=st.integers(min_value=50, max_value=200),
        operations=st.lists(
            st.tuples(
                st.sampled_from(['reserve', 'release']),
                st.integers(min_value=1, max_value=10)
            ),
            min_size=5,
            max_size=20
        )
    )
    @settings(max_examples=100)
    def test_property_5_multiple_operations_consistency(self, capacity, operations):
        """
        Property 5: 座位库存操作原子性 - 多次操作一致性
        
        *For any* 一系列预留和释放操作，每次操作后座位数应正确反映累计变化，
        且始终保持在 [0, capacity] 范围内。
        
        **Feature: order-enhancement, Property 5: 座位库存操作原子性**
        **Validates: Requirements 2.1, 2.2, 2.3**
        """
        from booking.services import InventoryService
        
        # 创建航班
        flight = self.create_flight(capacity=capacity, available_seats=capacity)
        
        # 执行一系列操作
        for op_type, count in operations:
            before_available = flight.available_seats
            
            if op_type == 'reserve':
                success = InventoryService.reserve_seats(flight, count)
                flight.refresh_from_db()
                
                if success:
                    expected = before_available - count
                else:
                    expected = before_available
            else:
                InventoryService.release_seats(flight, count)
                flight.refresh_from_db()
                expected = min(before_available + count, capacity)
            
            # 验证座位数在有效范围内
            self.assertGreaterEqual(
                flight.available_seats, 0,
                f"操作后座位数不应小于 0，当前: {flight.available_seats}"
            )
            self.assertLessEqual(
                flight.available_seats, capacity,
                f"操作后座位数不应超过容量，当前: {flight.available_seats}, 容量: {capacity}"
            )
