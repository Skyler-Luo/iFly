"""订单和机票模块测试"""
from datetime import timedelta
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from accounts.models import User
from flight.models import Flight
from .models import Order, Ticket


class OrderModelTest(TestCase):
    """订单模型测试"""
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )
        self.order = Order.objects.create(
            user=self.user,
            total_price=Decimal('500.00'),
            status='pending'
        )

    def test_order_creation(self):
        """测试订单创建"""
        self.assertIsNotNone(self.order.order_number)
        self.assertTrue(self.order.order_number.startswith('ORD'))
        self.assertEqual(self.order.status, 'pending')
        self.assertEqual(self.order.total_price, Decimal('500.00'))


class OrderAPITest(APITestCase):
    """订单API测试"""
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )
        self.flight = Flight.objects.create(
            flight_number='CA1234',
            departure_city='北京',
            arrival_city='上海',
            departure_time=timezone.now() + timedelta(days=7),
            arrival_time=timezone.now() + timedelta(days=7, hours=2),
            price=Decimal('800.00'),
            discount=Decimal('0.9'),
            capacity=100,
            available_seats=100,
            status='scheduled',
            aircraft_type='Boeing 737',
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_create_order(self):
        """测试创建订单"""
        url = reverse('order-list')
        data = {
            'flight_id': self.flight.id,
            'cabin_class': 'economy',
            'seat_numbers': ['1A'],
            'passengers': [{
                'name': '张三',
                'id_type': '身份证',
                'id_number': '110101199001011234'
            }],
            'contact_info': {
                'name': '张三',
                'phone': '13800138000',
                'email': 'zhangsan@example.com'
            },
            'total_price': '720.00'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('order_number', response.data)

        # 验证航班座位减少
        self.flight.refresh_from_db()
        self.assertEqual(self.flight.available_seats, 99)

    def test_list_orders(self):
        """测试获取订单列表"""
        # 创建一个订单
        Order.objects.create(
            user=self.user,
            total_price=Decimal('500.00'),
            status='pending'
        )

        url = reverse('order-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)

    def test_pay_order(self):
        """测试支付订单"""
        order = Order.objects.create(
            user=self.user,
            total_price=Decimal('500.00'),
            status='pending'
        )

        url = reverse('order-pay', args=[order.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        order.refresh_from_db()
        self.assertEqual(order.status, 'paid')
        self.assertIsNotNone(order.paid_at)

    def test_cancel_order(self):
        """测试取消订单"""
        # 创建已支付订单
        order = Order.objects.create(
            user=self.user,
            total_price=Decimal('500.00'),
            status='paid'
        )
        # 创建关联机票
        ticket = Ticket.objects.create(
            order=order,
            flight=self.flight,
            passenger_name='张三',
            passenger_id_number='110101199001011234',
            seat_number='1A',
            cabin_class='economy',
            price=Decimal('500.00'),
            status='valid'
        )
        # 减少航班座位
        self.flight.available_seats -= 1
        self.flight.save()

        url = reverse('order-cancel', args=[order.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        order.refresh_from_db()
        self.assertEqual(order.status, 'canceled')

        ticket.refresh_from_db()
        self.assertEqual(ticket.status, 'refunded')

        # 验证航班座位恢复
        self.flight.refresh_from_db()
        self.assertEqual(self.flight.available_seats, 100)


class TicketAPITest(APITestCase):
    """机票API测试"""
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )
        self.flight = Flight.objects.create(
            flight_number='CA1234',
            departure_city='北京',
            arrival_city='上海',
            departure_time=timezone.now() + timedelta(days=7),
            arrival_time=timezone.now() + timedelta(days=7, hours=2),
            price=Decimal('800.00'),
            discount=Decimal('0.9'),
            capacity=100,
            available_seats=99,
            status='scheduled',
            aircraft_type='Boeing 737',
        )
        self.order = Order.objects.create(
            user=self.user,
            total_price=Decimal('720.00'),
            status='paid'
        )
        self.ticket = Ticket.objects.create(
            order=self.order,
            flight=self.flight,
            passenger_name='张三',
            passenger_id_number='110101199001011234',
            seat_number='1A',
            cabin_class='economy',
            price=Decimal('720.00'),
            status='valid'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_list_tickets(self):
        """测试获取机票列表"""
        url = reverse('ticket-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)

    def test_refund_ticket(self):
        """测试退票"""
        url = reverse('ticket-refund', args=[self.ticket.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.status, 'refunded')

        # 验证航班座位恢复
        self.flight.refresh_from_db()
        self.assertEqual(self.flight.available_seats, 100)

    def test_filter_tickets_by_status(self):
        """测试按状态筛选机票 (Requirements 4.2)"""
        url = reverse('ticket-list')

        # 筛选未使用的机票
        response = self.client.get(url, {'status': 'UNUSED'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 筛选已退票的机票
        response = self.client.get(url, {'status': 'REFUNDED'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_ticket_detail(self):
        """测试获取机票详情"""
        url = reverse('ticket-detail', args=[self.ticket.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['passenger_name'], '张三')
        self.assertEqual(response.data['seat_number'], '1A')
