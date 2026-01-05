"""
在线值机功能集成测试

测试完整值机流程：验证 → 选座 → 确认 → 登机牌
Feature: online-checkin
Requirements: 1.1-1.6, 3.1-3.7, 4.1-4.6, 5.1-5.7, 6.1-6.5
"""
import datetime
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status

from accounts.models import User
from booking.models import Order, Ticket
from flight.models import Flight


class CheckinEndToEndTest(TestCase):
    """
    端到端值机流程测试
    
    测试完整值机流程：验证 → 选座 → 确认 → 登机牌
    Requirements: 1.1-1.6, 3.1-3.7, 4.1-4.6, 5.1-5.7
    """
    
    def setUp(self):
        """设置测试数据"""
        # 创建测试用户
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )
        
        # 创建航班（在值机窗口期内：起飞前12小时）
        departure_time = timezone.now() + datetime.timedelta(hours=12)
        self.flight = Flight.objects.create(
            flight_number='CA1234',
            airline_name='中国国航',
            departure_city='北京',
            arrival_city='上海',
            departure_time=departure_time,
            arrival_time=departure_time + datetime.timedelta(hours=2),
            price=Decimal('800.00'),
            discount=Decimal('0.9'),
            capacity=180,
            available_seats=180,
            status='scheduled',
            aircraft_type='Boeing 737',
            seat_rows=30,
            seats_per_row=6,
        )
        
        # 创建订单
        self.order = Order.objects.create(
            user=self.user,
            total_price=Decimal('720.00'),
            status='paid'
        )
        
        # 创建机票
        self.ticket = Ticket.objects.create(
            order=self.order,
            flight=self.flight,
            passenger_name='张三',
            passenger_id_number='110101199001011234',
            seat_number='10A',
            cabin_class='economy',
            price=Decimal('720.00'),
            status='valid'
        )
        
        # 设置 API 客户端
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_complete_checkin_flow(self):
        """
        测试完整值机流程
        
        步骤：
        1. 获取值机信息（验证机票资格）
        2. 获取座位图（选座）
        3. 办理值机（确认）
        4. 验证登机牌信息
        
        Requirements: 1.1-1.6, 3.1-3.7, 4.1-4.6, 5.1-5.7
        """
        # 步骤 1: 获取值机信息
        response = self.client.get(f'/api/bookings/tickets/{self.ticket.id}/checkin_info/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 验证值机信息完整性 (Requirements 2.1-2.5)
        checkin_info = response.data
        self.assertEqual(checkin_info['ticket_id'], self.ticket.id)
        self.assertEqual(checkin_info['passenger_name'], '张三')
        self.assertEqual(checkin_info['flight_number'], 'CA1234')
        self.assertEqual(checkin_info['departure_city'], '北京')
        self.assertEqual(checkin_info['arrival_city'], '上海')
        self.assertEqual(checkin_info['current_seat'], '10A')
        self.assertEqual(checkin_info['cabin_class'], 'economy')
        self.assertFalse(checkin_info['checked_in'])
        self.assertTrue(checkin_info['can_change_seat'])
        
        # 验证证件号码已脱敏 (Requirements 2.5)
        self.assertIn('*', checkin_info['passenger_id_number'])
        self.assertEqual(checkin_info['passenger_id_number'][:4], '1101')
        self.assertEqual(checkin_info['passenger_id_number'][-4:], '1234')
        
        # 步骤 2: 获取座位图
        flight_id = checkin_info['flight_id']
        response = self.client.get(f'/api/flights/{flight_id}/seats/', {'cabin_class': 'economy'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 验证座位图信息 (Requirements 3.1, 3.6)
        seat_data = response.data
        self.assertEqual(seat_data['flight_id'], flight_id)
        self.assertEqual(seat_data['cabin_class'], 'economy')
        self.assertEqual(seat_data['start_row'], 10)
        self.assertEqual(seat_data['end_row'], 30)
        self.assertIn('seat_map', seat_data)
        self.assertIn('occupied_seats', seat_data)
        
        # 步骤 3: 选择新座位并办理值机
        new_seat = '15C'
        response = self.client.post(
            f'/api/bookings/tickets/{self.ticket.id}/checkin/',
            {'seat_number': new_seat},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 验证值机成功 (Requirements 4.3-4.6)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['message'], '值机成功')
        
        # 步骤 4: 验证登机牌信息 (Requirements 5.1-5.5)
        boarding_pass = response.data['boarding_pass']
        
        # 验证登机牌必要字段
        self.assertIn('boarding_pass_number', boarding_pass)
        self.assertTrue(boarding_pass['boarding_pass_number'].startswith('BP'))
        self.assertEqual(boarding_pass['passenger_name'], '张三')
        self.assertEqual(boarding_pass['flight_number'], 'CA1234')
        self.assertEqual(boarding_pass['airline_name'], '中国国航')
        self.assertEqual(boarding_pass['departure_city'], '北京')
        self.assertEqual(boarding_pass['arrival_city'], '上海')
        self.assertEqual(boarding_pass['seat_number'], new_seat)
        self.assertIn('gate', boarding_pass)
        self.assertIn('boarding_time', boarding_pass)
        self.assertIn('checked_in_at', boarding_pass)
        
        # 验证数据库状态更新
        self.ticket.refresh_from_db()
        self.assertTrue(self.ticket.checked_in)
        self.assertIsNotNone(self.ticket.checked_in_at)
        self.assertEqual(self.ticket.seat_number, new_seat)
        self.assertIsNotNone(self.ticket.boarding_pass_number)
        self.assertIsNotNone(self.ticket.gate)
    
    def test_checkin_without_seat_change(self):
        """
        测试不更换座位的值机流程
        
        Requirements: 4.3-4.6, 5.1-5.5
        """
        # 直接办理值机，不更换座位
        response = self.client.post(
            f'/api/bookings/tickets/{self.ticket.id}/checkin/',
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 验证值机成功
        self.assertTrue(response.data['success'])
        
        # 验证座位保持不变
        boarding_pass = response.data['boarding_pass']
        self.assertEqual(boarding_pass['seat_number'], '10A')
        
        # 验证数据库状态
        self.ticket.refresh_from_db()
        self.assertTrue(self.ticket.checked_in)
        self.assertEqual(self.ticket.seat_number, '10A')
    
    def test_checkin_flow_with_multiple_passengers(self):
        """
        测试多乘客值机流程
        
        Requirements: 1.1-1.6, 4.1-4.6
        """
        # 创建第二张机票
        ticket2 = Ticket.objects.create(
            order=self.order,
            flight=self.flight,
            passenger_name='李四',
            passenger_id_number='110101199002022345',
            seat_number='10B',
            cabin_class='economy',
            price=Decimal('720.00'),
            status='valid'
        )
        
        # 第一位乘客值机
        response1 = self.client.post(
            f'/api/bookings/tickets/{self.ticket.id}/checkin/',
            {'seat_number': '15A'},
            format='json'
        )
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        
        # 第二位乘客值机
        response2 = self.client.post(
            f'/api/bookings/tickets/{ticket2.id}/checkin/',
            {'seat_number': '15B'},
            format='json'
        )
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        
        # 验证两位乘客都已值机
        self.ticket.refresh_from_db()
        ticket2.refresh_from_db()
        
        self.assertTrue(self.ticket.checked_in)
        self.assertTrue(ticket2.checked_in)
        self.assertEqual(self.ticket.seat_number, '15A')
        self.assertEqual(ticket2.seat_number, '15B')


class CheckinErrorScenariosTest(TestCase):
    """
    值机错误场景测试
    
    测试各种错误情况的处理
    Requirements: 6.1-6.5
    """
    
    def setUp(self):
        """设置测试数据"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )
        
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpassword123'
        )
        
        # 创建航班（在值机窗口期内）
        departure_time = timezone.now() + datetime.timedelta(hours=12)
        self.flight = Flight.objects.create(
            flight_number='CA1234',
            airline_name='中国国航',
            departure_city='北京',
            arrival_city='上海',
            departure_time=departure_time,
            arrival_time=departure_time + datetime.timedelta(hours=2),
            price=Decimal('800.00'),
            discount=Decimal('0.9'),
            capacity=180,
            available_seats=180,
            status='scheduled',
            aircraft_type='Boeing 737',
            seat_rows=30,
            seats_per_row=6,
        )
        
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_checkin_invalid_ticket_id(self):
        """
        测试无效机票 ID
        
        Requirements: 6.2
        """
        response = self.client.get('/api/bookings/tickets/99999/checkin_info/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_checkin_refunded_ticket(self):
        """
        测试已退票的机票
        
        Requirements: 1.2
        """
        order = Order.objects.create(
            user=self.user,
            total_price=Decimal('720.00'),
            status='paid'
        )
        ticket = Ticket.objects.create(
            order=order,
            flight=self.flight,
            passenger_name='张三',
            passenger_id_number='110101199001011234',
            seat_number='10A',
            cabin_class='economy',
            price=Decimal('720.00'),
            status='refunded'
        )
        
        response = self.client.get(f'/api/bookings/tickets/{ticket.id}/checkin_info/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('detail', response.data)
        self.assertEqual(response.data['status'], 'refunded')
    
    def test_checkin_used_ticket(self):
        """
        测试已使用的机票
        
        Requirements: 1.2
        """
        order = Order.objects.create(
            user=self.user,
            total_price=Decimal('720.00'),
            status='paid'
        )
        ticket = Ticket.objects.create(
            order=order,
            flight=self.flight,
            passenger_name='张三',
            passenger_id_number='110101199001011234',
            seat_number='10A',
            cabin_class='economy',
            price=Decimal('720.00'),
            status='used'
        )
        
        response = self.client.get(f'/api/bookings/tickets/{ticket.id}/checkin_info/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('detail', response.data)
        self.assertEqual(response.data['status'], 'used')
    
    def test_checkin_already_checked_in(self):
        """
        测试已值机的机票
        
        Requirements: 1.3
        """
        order = Order.objects.create(
            user=self.user,
            total_price=Decimal('720.00'),
            status='paid'
        )
        ticket = Ticket.objects.create(
            order=order,
            flight=self.flight,
            passenger_name='张三',
            passenger_id_number='110101199001011234',
            seat_number='10A',
            cabin_class='economy',
            price=Decimal('720.00'),
            status='valid',
            checked_in=True,
            checked_in_at=timezone.now()
        )
        
        response = self.client.get(f'/api/bookings/tickets/{ticket.id}/checkin_info/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('detail', response.data)
        self.assertTrue(response.data['checked_in'])
    
    def test_checkin_before_window(self):
        """
        测试值机窗口期前
        
        Requirements: 1.4
        """
        # 创建起飞时间在 48 小时后的航班
        future_flight = Flight.objects.create(
            flight_number='CA5678',
            airline_name='中国国航',
            departure_city='北京',
            arrival_city='广州',
            departure_time=timezone.now() + datetime.timedelta(hours=48),
            arrival_time=timezone.now() + datetime.timedelta(hours=51),
            price=Decimal('1200.00'),
            discount=Decimal('0.9'),
            capacity=180,
            available_seats=180,
            status='scheduled',
            aircraft_type='Boeing 737',
        )
        
        order = Order.objects.create(
            user=self.user,
            total_price=Decimal('1080.00'),
            status='paid'
        )
        ticket = Ticket.objects.create(
            order=order,
            flight=future_flight,
            passenger_name='张三',
            passenger_id_number='110101199001011234',
            seat_number='10A',
            cabin_class='economy',
            price=Decimal('1080.00'),
            status='valid'
        )
        
        response = self.client.get(f'/api/bookings/tickets/{ticket.id}/checkin_info/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('值机尚未开放', response.data['detail'])
    
    def test_checkin_after_window(self):
        """
        测试值机窗口期后
        
        Requirements: 1.5
        """
        # 创建起飞时间在 30 分钟后的航班
        soon_flight = Flight.objects.create(
            flight_number='CA9999',
            airline_name='中国国航',
            departure_city='北京',
            arrival_city='深圳',
            departure_time=timezone.now() + datetime.timedelta(minutes=30),
            arrival_time=timezone.now() + datetime.timedelta(hours=3),
            price=Decimal('1500.00'),
            discount=Decimal('0.9'),
            capacity=180,
            available_seats=180,
            status='scheduled',
            aircraft_type='Boeing 737',
        )
        
        order = Order.objects.create(
            user=self.user,
            total_price=Decimal('1350.00'),
            status='paid'
        )
        ticket = Ticket.objects.create(
            order=order,
            flight=soon_flight,
            passenger_name='张三',
            passenger_id_number='110101199001011234',
            seat_number='10A',
            cabin_class='economy',
            price=Decimal('1350.00'),
            status='valid'
        )
        
        response = self.client.get(f'/api/bookings/tickets/{ticket.id}/checkin_info/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('值机已关闭', response.data['detail'])
    
    def test_checkin_seat_conflict(self):
        """
        测试座位冲突
        
        Requirements: 4.1, 4.2
        """
        # 创建第一个用户的机票并占用座位 15C
        order1 = Order.objects.create(
            user=self.other_user,
            total_price=Decimal('720.00'),
            status='paid'
        )
        Ticket.objects.create(
            order=order1,
            flight=self.flight,
            passenger_name='李四',
            passenger_id_number='110101199002022345',
            seat_number='15C',
            cabin_class='economy',
            price=Decimal('720.00'),
            status='valid'
        )
        
        # 创建当前用户的机票
        order2 = Order.objects.create(
            user=self.user,
            total_price=Decimal('720.00'),
            status='paid'
        )
        ticket = Ticket.objects.create(
            order=order2,
            flight=self.flight,
            passenger_name='张三',
            passenger_id_number='110101199001011234',
            seat_number='10A',
            cabin_class='economy',
            price=Decimal('720.00'),
            status='valid'
        )
        
        # 尝试选择已被占用的座位
        response = self.client.post(
            f'/api/bookings/tickets/{ticket.id}/checkin/',
            {'seat_number': '15C'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('已被占用', response.data['detail'])
    
    def test_checkin_unauthorized_access(self):
        """
        测试无权访问其他用户的机票
        
        Requirements: 6.3
        """
        # 创建其他用户的机票
        order = Order.objects.create(
            user=self.other_user,
            total_price=Decimal('720.00'),
            status='paid'
        )
        ticket = Ticket.objects.create(
            order=order,
            flight=self.flight,
            passenger_name='李四',
            passenger_id_number='110101199002022345',
            seat_number='10B',
            cabin_class='economy',
            price=Decimal('720.00'),
            status='valid'
        )
        
        # 当前用户尝试访问其他用户的机票
        response = self.client.get(f'/api/bookings/tickets/{ticket.id}/checkin_info/')
        # 应该返回 404（因为查询集过滤了其他用户的机票）
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_checkin_unauthenticated(self):
        """
        测试未认证用户访问
        
        Requirements: 6.3
        """
        # 创建未认证的客户端
        unauthenticated_client = APIClient()
        
        order = Order.objects.create(
            user=self.user,
            total_price=Decimal('720.00'),
            status='paid'
        )
        ticket = Ticket.objects.create(
            order=order,
            flight=self.flight,
            passenger_name='张三',
            passenger_id_number='110101199001011234',
            seat_number='10A',
            cabin_class='economy',
            price=Decimal('720.00'),
            status='valid'
        )
        
        response = unauthenticated_client.get(f'/api/bookings/tickets/{ticket.id}/checkin_info/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class SeatMapIntegrationTest(TestCase):
    """
    座位图集成测试
    
    Requirements: 3.1-3.7
    """
    
    def setUp(self):
        """设置测试数据"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )
        
        departure_time = timezone.now() + datetime.timedelta(hours=12)
        self.flight = Flight.objects.create(
            flight_number='CA1234',
            airline_name='中国国航',
            departure_city='北京',
            arrival_city='上海',
            departure_time=departure_time,
            arrival_time=departure_time + datetime.timedelta(hours=2),
            price=Decimal('800.00'),
            discount=Decimal('0.9'),
            capacity=180,
            available_seats=180,
            status='scheduled',
            aircraft_type='Boeing 737',
            seat_rows=30,
            seats_per_row=6,
        )
        
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_seat_map_shows_occupied_seats(self):
        """
        测试座位图显示已占用座位
        
        Requirements: 3.2
        """
        # 创建一些已占用的座位
        order = Order.objects.create(
            user=self.user,
            total_price=Decimal('2160.00'),
            status='paid'
        )
        
        occupied_seats = ['10A', '10B', '15C', '20D']
        for seat in occupied_seats:
            Ticket.objects.create(
                order=order,
                flight=self.flight,
                passenger_name='测试乘客',
                passenger_id_number='110101199001011234',
                seat_number=seat,
                cabin_class='economy',
                price=Decimal('720.00'),
                status='valid'
            )
        
        # 获取座位图
        response = self.client.get(f'/api/flights/{self.flight.id}/seats/', {'cabin_class': 'economy'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 验证已占用座位列表
        returned_occupied = response.data['occupied_seats']
        for seat in occupied_seats:
            self.assertIn(seat, returned_occupied)
    
    def test_seat_map_cabin_class_filtering(self):
        """
        测试座位图舱位过滤
        
        Requirements: 3.6
        """
        # 测试头等舱
        response = self.client.get(f'/api/flights/{self.flight.id}/seats/', {'cabin_class': 'first'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['start_row'], 1)
        self.assertEqual(response.data['end_row'], 3)
        
        # 测试商务舱
        response = self.client.get(f'/api/flights/{self.flight.id}/seats/', {'cabin_class': 'business'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['start_row'], 4)
        self.assertEqual(response.data['end_row'], 9)
        
        # 测试经济舱
        response = self.client.get(f'/api/flights/{self.flight.id}/seats/', {'cabin_class': 'economy'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['start_row'], 10)
        self.assertEqual(response.data['end_row'], 30)
    
    def test_seat_map_structure(self):
        """
        测试座位图结构
        
        Requirements: 3.1, 3.7
        """
        response = self.client.get(f'/api/flights/{self.flight.id}/seats/', {'cabin_class': 'economy'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        seat_map = response.data['seat_map']
        columns = response.data['columns']
        
        # 验证每行有正确数量的座位
        for row in seat_map:
            self.assertEqual(len(row), columns)
        
        # 验证座位信息结构
        for row in seat_map:
            for seat_info in row:
                self.assertIn('seat', seat_info)
                self.assertIn('taken', seat_info)
                self.assertIsInstance(seat_info['taken'], bool)
