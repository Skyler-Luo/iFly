"""
航班座位图 API 属性测试

使用 Hypothesis 进行属性测试，验证座位图 API 的正确性。
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
from flight.models import Flight


class SeatMapAPIPropertyTest(HypothesisTestCase):
    """
    座位图 API 属性测试
    
    Property 7: 舱位座位范围
    Validates: Requirements 3.6
    """
    
    # 定义舱位对应的行范围
    CABIN_ROW_RANGES = {
        'first': (1, 3),      # 头等舱 1-3 排
        'business': (4, 9),   # 商务舱 4-9 排
        'economy': (10, 30),  # 经济舱 10-30 排
    }
    
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
    
    def create_flight(self, seat_rows=30, seats_per_row=6):
        """创建测试航班"""
        departure_time = timezone.now() + datetime.timedelta(hours=12)
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
            capacity=seat_rows * seats_per_row,
            available_seats=seat_rows * seats_per_row,
            status='scheduled',
            aircraft_type='Boeing 737',
            seat_rows=seat_rows,
            seats_per_row=seats_per_row,
        )
    
    @given(cabin_class=st.sampled_from(['first', 'business', 'economy']))
    @settings(max_examples=100)
    def test_property_7_cabin_seat_range(self, cabin_class):
        """
        Property 7: 舱位座位范围
        
        *For any* 舱位等级，座位图应只显示该舱位对应的行范围：
        头等舱 1-3 排，商务舱 4-9 排，经济舱 10-30 排。
        
        **Feature: online-checkin, Property 7: 舱位座位范围**
        **Validates: Requirements 3.6**
        """
        user = self.get_or_create_user()
        client = APIClient()
        client.force_authenticate(user=user)
        
        flight = self.create_flight(seat_rows=30, seats_per_row=6)
        
        # 调用座位图 API
        response = client.get(
            f'/api/flights/{flight.id}/seats/',
            {'cabin_class': cabin_class}
        )
        
        # 应该成功返回
        self.assertEqual(response.status_code, 200)
        
        # 获取预期的行范围
        expected_start, expected_end = self.CABIN_ROW_RANGES[cabin_class]
        
        # 验证返回的舱位类型正确
        self.assertEqual(response.data['cabin_class'], cabin_class)
        
        # 验证返回的行范围正确
        self.assertEqual(response.data['start_row'], expected_start)
        self.assertEqual(response.data['end_row'], expected_end)
        
        # 验证返回的行数正确
        expected_rows = expected_end - expected_start + 1
        self.assertEqual(response.data['rows'], expected_rows)
        
        # 验证座位图中的行数正确
        seat_map = response.data['seat_map']
        self.assertEqual(len(seat_map), expected_rows)
        
        # 验证座位图中每个座位的行号在正确范围内
        for row_idx, row in enumerate(seat_map):
            actual_row_num = expected_start + row_idx
            for seat_info in row:
                seat_number = seat_info['seat']
                # 从座位号中提取行号
                seat_row = int(''.join(filter(str.isdigit, seat_number)))
                self.assertEqual(seat_row, actual_row_num,
                    f"座位 {seat_number} 的行号 {seat_row} 不在预期范围 {expected_start}-{expected_end} 内")
                self.assertGreaterEqual(seat_row, expected_start)
                self.assertLessEqual(seat_row, expected_end)
    
    @given(
        cabin_class=st.sampled_from(['first', 'business', 'economy']),
        occupied_row=st.integers(min_value=1, max_value=30),
        occupied_col=st.sampled_from(['A', 'B', 'C', 'D', 'E', 'F'])
    )
    @settings(max_examples=100)
    def test_property_7_occupied_seats_filtered_by_cabin(self, cabin_class, occupied_row, occupied_col):
        """
        Property 7: 舱位座位范围 - 已占用座位过滤
        
        *For any* 舱位等级，返回的已占用座位列表应只包含该舱位范围内的座位。
        
        **Feature: online-checkin, Property 7: 舱位座位范围**
        **Validates: Requirements 3.6**
        """
        user = self.get_or_create_user()
        client = APIClient()
        client.force_authenticate(user=user)
        
        flight = self.create_flight(seat_rows=30, seats_per_row=6)
        
        # 创建一个占用指定座位的机票
        occupied_seat = f'{occupied_row}{occupied_col}'
        order = Order.objects.create(
            user=user,
            total_price=Decimal('720.00'),
            status='paid'
        )
        Ticket.objects.create(
            order=order,
            flight=flight,
            passenger_name='测试乘客',
            passenger_id_number='110101199001011234',
            seat_number=occupied_seat,
            cabin_class='economy',
            price=Decimal('720.00'),
            status='valid',
            checked_in=False
        )
        
        # 调用座位图 API
        response = client.get(
            f'/api/flights/{flight.id}/seats/',
            {'cabin_class': cabin_class}
        )
        
        # 应该成功返回
        self.assertEqual(response.status_code, 200)
        
        # 获取预期的行范围
        expected_start, expected_end = self.CABIN_ROW_RANGES[cabin_class]
        
        # 验证已占用座位列表中的座位都在当前舱位范围内
        occupied_seats = response.data['occupied_seats']
        for seat in occupied_seats:
            seat_row = int(''.join(filter(str.isdigit, seat)))
            self.assertGreaterEqual(seat_row, expected_start,
                f"已占用座位 {seat} 的行号 {seat_row} 小于舱位起始行 {expected_start}")
            self.assertLessEqual(seat_row, expected_end,
                f"已占用座位 {seat} 的行号 {seat_row} 大于舱位结束行 {expected_end}")
        
        # 如果占用的座位在当前舱位范围内，应该出现在列表中
        if expected_start <= occupied_row <= expected_end:
            self.assertIn(occupied_seat, occupied_seats,
                f"座位 {occupied_seat} 应该在舱位 {cabin_class} 的已占用列表中")
        else:
            # 如果占用的座位不在当前舱位范围内，不应该出现在列表中
            self.assertNotIn(occupied_seat, occupied_seats,
                f"座位 {occupied_seat} 不应该在舱位 {cabin_class} 的已占用列表中")
