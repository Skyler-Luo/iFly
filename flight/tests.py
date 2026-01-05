from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from accounts.models import User
from .models import Flight


class FlightModelTest(TestCase):
    """航班模型测试"""
    def setUp(self):
        self.flight = Flight.objects.create(
            flight_number='F100',
            departure_city='CityA',
            arrival_city='CityB',
            departure_time=timezone.now() + timedelta(days=1),
            arrival_time=timezone.now() + timedelta(days=1, hours=2),
            price=100.00,
            discount=0.8,
            capacity=100,
            available_seats=100,
            status='scheduled',
            aircraft_type='A320',
        )

    def test_str(self):
        """测试航班字符串表示"""
        self.assertEqual(str(self.flight), 'F100: CityA -> CityB')


class FlightAPITest(APITestCase):
    """航班API测试"""
    def setUp(self):
        # 创建普通用户
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )
        # 创建管理员用户
        self.admin = User.objects.create_superuser(
            username='adminuser',
            email='admin@example.com',
            password='adminpassword123'
        )
        self.flight = Flight.objects.create(
            flight_number='F200',
            departure_city='CityX',
            arrival_city='CityY',
            departure_time=timezone.now() + timedelta(days=2),
            arrival_time=timezone.now() + timedelta(days=2, hours=3),
            price=200.00,
            discount=0.9,
            capacity=50,
            available_seats=50,
            status='scheduled',
            aircraft_type='B737',
        )
        self.client = APIClient()

    def test_list_flights(self):
        url = reverse('flight-list')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['results'][0]['flight_number'], self.flight.flight_number)

    def test_filter_by_date_range(self):
        start = timezone.now()
        end = timezone.now() + timedelta(days=3)
        url = reverse('flight-list')
        resp = self.client.get(url, {'departure_time_after': start.isoformat(), 'departure_time_before': end.isoformat()})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(any(f['flight_number'] == self.flight.flight_number for f in resp.data['results']))

    def test_booking_and_cancel_seat(self):
        """测试预订和取消座位（需要认证）"""
        # 使用普通用户认证
        self.client.force_authenticate(user=self.user)
        
        book_url = reverse('flight-book', args=[self.flight.id])
        resp_book = self.client.post(book_url)
        self.assertEqual(resp_book.status_code, status.HTTP_200_OK)
        self.flight.refresh_from_db()
        self.assertEqual(self.flight.available_seats, 49)

        cancel_url = reverse('flight-cancel-seat', args=[self.flight.id])
        resp_cancel = self.client.post(cancel_url)
        self.assertEqual(resp_cancel.status_code, status.HTTP_200_OK)
        self.flight.refresh_from_db()
        self.assertEqual(self.flight.available_seats, 50)

    def test_depart_and_cancel_flight(self):
        """测试航班起飞和取消（需要管理员权限）"""
        # 使用管理员用户认证
        self.client.force_authenticate(user=self.admin)
        
        depart_url = reverse('flight-depart', args=[self.flight.id])
        resp_depart = self.client.post(depart_url)
        self.assertEqual(resp_depart.status_code, status.HTTP_200_OK)
        self.flight.refresh_from_db()
        self.assertEqual(self.flight.status, 'departed')

        cancel_url = reverse('flight-cancel-flight', args=[self.flight.id])
        resp_cancel = self.client.post(cancel_url)
        self.assertEqual(resp_cancel.status_code, status.HTTP_200_OK)
        self.flight.refresh_from_db()
        self.assertEqual(self.flight.status, 'canceled')

    def test_export_and_import_csv(self):
        """测试导出和导入CSV（需要管理员权限）"""
        import io
        import csv
        
        # 使用管理员用户认证
        self.client.force_authenticate(user=self.admin)
        
        export_url = reverse('flight-export-csv')
        resp_export = self.client.get(export_url)
        self.assertEqual(resp_export.status_code, status.HTTP_200_OK)
        self.assertEqual(resp_export['Content-Type'], 'text/csv')

        # Prepare import CSV file
        f = io.StringIO()
        writer = csv.writer(f)
        writer.writerow([
            'flight_number', 'departure_city', 'arrival_city', 
            'departure_time', 'arrival_time', 'price', 'discount', 
            'capacity', 'available_seats', 'status', 'aircraft_type'
        ])
        writer.writerow([
            self.flight.flight_number, 'A', 'B', 
            (timezone.now() + timedelta(days=1)).isoformat(), 
            (timezone.now() + timedelta(days=1)).isoformat(), 
            '300', '1.0', '20', '20', 'scheduled', 'B747'
        ])
        content = f.getvalue().encode('utf-8')
        file = SimpleUploadedFile('flights.csv', content, content_type='text/csv')
        import_url = reverse('flight-import-csv')
        resp_import = self.client.post(import_url, {'file': file}, format='multipart')
        self.assertEqual(resp_import.status_code, status.HTTP_200_OK)
        data = resp_import.data
        self.assertIn('updated', data)
