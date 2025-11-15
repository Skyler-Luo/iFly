import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'iFly.settings')
django.setup()

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import User, Passenger


class UserModelTest(TestCase):
    """测试用户模型"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123',
            phone='13800138000',
            role='user'
        )
    
    def test_user_creation(self):
        """测试用户创建"""
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertEqual(self.user.phone, '13800138000')
        self.assertEqual(self.user.role, 'user')
        self.assertTrue(self.user.is_active)
        self.assertFalse(self.user.is_staff)


class PassengerModelTest(TestCase):
    """测试乘客模型"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )
        self.passenger = Passenger.objects.create(
            user=self.user,
            name='测试乘客',
            id_card='110101199001011234',
            gender='male',
            birth_date='1990-01-01'
        )
    
    def test_passenger_creation(self):
        """测试乘客创建"""
        self.assertEqual(self.passenger.name, '测试乘客')
        self.assertEqual(self.passenger.id_card, '110101199001011234')
        self.assertEqual(self.passenger.gender, 'male')
        self.assertEqual(str(self.passenger.birth_date), '1990-01-01')
        self.assertEqual(self.passenger.user, self.user)


class UserAPITest(APITestCase):
    """测试用户相关API"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123',
            phone='13800138000'
        )
        self.client = APIClient()
    
    def test_user_registration(self):
        """测试用户注册"""
        url = reverse('register')
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'newpassword123',
            'password2': 'newpassword123',
            'phone': '13900139000'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(User.objects.get(username='newuser').email, 'new@example.com')
    
    def test_user_login(self):
        """测试用户登录"""
        url = reverse('login')
        data = {
            'username': 'testuser',
            'password': 'testpassword123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertEqual(response.data['username'], 'testuser')


class PassengerAPITest(APITestCase):
    """测试乘客API及相关功能"""
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='password123',
            role='user'
        )
        self.admin = User.objects.create_user(
            username='adminuser',
            email='admin@example.com',
            password='adminpass',
            role='admin'
        )
        self.passenger = Passenger.objects.create(
            user=self.user,
            name='张三',
            id_card='110101199001011234',
            gender='male',
            birth_date='1990-01-01'
        )
        self.client = APIClient()

    def test_list_passengers(self):
        # 普通用户只能查看自己的乘客信息
        self.client.force_authenticate(user=self.user)
        url = reverse('passenger-list')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data['results']), 1)

    def test_filter_by_birth_date_range(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('passenger-list')
        resp = self.client.get(url, {'birth_date_after': '1990-01-01', 'birth_date_before': '1991-01-01'})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(any(p['id_card'] == self.passenger.id_card for p in resp.data['results']))

    def test_export_and_import_csv(self):
        # 管理员导出与导入CSV
        self.client.force_authenticate(user=self.admin)
        export_url = reverse('passenger-export-csv')
        resp_export = self.client.get(export_url)
        self.assertEqual(resp_export.status_code, status.HTTP_200_OK)
        self.assertEqual(resp_export['Content-Type'], 'text/csv')

        import io, csv
        f = io.StringIO()
        writer = csv.writer(f)
        writer.writerow(['id','user','name','id_card','passport_number','gender','birth_date','created_at','updated_at'])
        writer.writerow(['', self.user.id, '李四', '110101199001011235', '', 'female', '1995-05-05', '', ''])
        content = f.getvalue().encode('utf-8')
        from django.core.files.uploadedfile import SimpleUploadedFile
        file = SimpleUploadedFile('passengers.csv', content, content_type='text/csv')
        import_url = reverse('passenger-import-csv')
        resp_import = self.client.post(import_url, {'file': file}, format='multipart')
        self.assertEqual(resp_import.status_code, status.HTTP_200_OK)
        self.assertIn('created', resp_import.data)
