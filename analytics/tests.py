"""管理后台分析模块测试 (Requirements 7.1, 7.2)"""
from datetime import timedelta
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from accounts.models import User
from flight.models import Flight
from booking.models import Order


class AnalyticsAPITest(APITestCase):
    """分析API测试"""
    def setUp(self):
        # 创建管理员用户
        self.admin = User.objects.create_user(
            username='adminuser',
            email='admin@example.com',
            password='adminpassword123',
            role='admin'
        )
        # 创建普通用户
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123',
            role='user'
        )
        # 创建测试航班
        self.flight = Flight.objects.create(
            flight_number='CA1234',
            departure_city='北京',
            arrival_city='上海',
            departure_time=timezone.now() + timedelta(days=7),
            arrival_time=timezone.now() + timedelta(days=7, hours=2),
            price=Decimal('800.00'),
            discount=Decimal('0.9'),
            capacity=100,
            available_seats=80,
            status='scheduled',
            aircraft_type='Boeing 737',
        )
        # 创建测试订单
        self.order = Order.objects.create(
            user=self.user,
            total_price=Decimal('720.00'),
            status='paid',
            paid_at=timezone.now()
        )
        self.client = APIClient()

    def test_analytics_overview_admin(self):
        """测试管理员访问分析概览 (Requirements 7.1)"""
        self.client.force_authenticate(user=self.admin)
        url = reverse('analytics-overview')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('stats', response.data)
        self.assertIn('revenueData', response.data)

    def test_analytics_overview_non_admin(self):
        """测试非管理员无法访问分析概览"""
        self.client.force_authenticate(user=self.user)
        url = reverse('analytics-overview')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_flight_analytics_admin(self):
        """测试管理员访问航班分析 (Requirements 7.2)"""
        self.client.force_authenticate(user=self.admin)
        url = reverse('flight-analytics')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('popular_routes', response.data)
        self.assertIn('avg_occupancy_rate', response.data)

    def test_revenue_analytics_admin(self):
        """测试管理员访问收入分析 (Requirements 7.1)"""
        self.client.force_authenticate(user=self.admin)
        url = reverse('revenue-analytics')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_revenue', response.data)
        self.assertIn('monthly_trend', response.data)

    def test_business_intelligence_admin(self):
        """测试管理员访问商业智能分析"""
        self.client.force_authenticate(user=self.admin)
        url = reverse('business-intelligence')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('user_stats', response.data)

    def test_data_visualization_admin(self):
        """测试管理员访问数据可视化"""
        self.client.force_authenticate(user=self.admin)
        url = reverse('data-visualization')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('city_data', response.data)

    def test_system_logs_admin(self):
        """测试管理员访问系统日志"""
        self.client.force_authenticate(user=self.admin)
        url = reverse('system-logs')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('logs', response.data)
