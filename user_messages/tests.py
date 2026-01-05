"""消息中心模块测试"""
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from accounts.models import User
from user_messages.models import Message


class MessageModelTest(TestCase):
    """消息模型测试"""
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )
        self.message = Message.objects.create(
            user=self.user,
            type='system',
            title='测试消息',
            content='这是一条测试消息'
        )

    def test_message_creation(self):
        """测试消息创建"""
        self.assertEqual(self.message.title, '测试消息')
        self.assertEqual(self.message.type, 'system')
        self.assertFalse(self.message.is_read)


class MessageAPITest(APITestCase):
    """消息API测试 (Requirements 3.1)"""
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )
        # 创建多条测试消息
        self.message1 = Message.objects.create(
            user=self.user,
            type='system',
            title='系统消息1',
            content='系统消息内容1'
        )
        self.message2 = Message.objects.create(
            user=self.user,
            type='order',
            title='订单消息1',
            content='订单消息内容1'
        )
        self.message3 = Message.objects.create(
            user=self.user,
            type='flight',
            title='航班消息1',
            content='航班消息内容1',
            is_read=True
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_list_messages(self):
        """测试获取消息列表"""
        url = reverse('messages-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)

    def test_filter_messages_by_type(self):
        """测试按类型筛选消息 (Requirements 3.2)"""
        url = reverse('messages-list')
        
        # 筛选系统消息
        response = self.client.get(url, {'type': 'system'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['type'], 'system')
        
        # 筛选订单消息
        response = self.client.get(url, {'type': 'order'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['type'], 'order')

    def test_mark_message_as_read(self):
        """测试标记消息为已读 (Requirements 3.3)"""
        url = reverse('messages-read', args=[self.message1.id])
        response = self.client.post(url, {'is_read': True})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.message1.refresh_from_db()
        self.assertTrue(self.message1.is_read)

    def test_mark_all_as_read(self):
        """测试全部标记为已读 (Requirements 3.4)"""
        url = reverse('messages-read-all')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 验证所有消息都已读
        unread_count = Message.objects.filter(user=self.user, is_read=False).count()
        self.assertEqual(unread_count, 0)

    def test_get_unread_count(self):
        """测试获取未读消息数量"""
        url = reverse('messages-unread-count')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)  # message1 和 message2 未读

    def test_delete_multiple_messages(self):
        """测试批量删除消息 (Requirements 3.5)"""
        url = reverse('messages-delete-multiple')
        response = self.client.post(url, {
            'message_ids': [self.message1.id, self.message2.id]
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        
        # 验证消息已删除
        remaining = Message.objects.filter(user=self.user).count()
        self.assertEqual(remaining, 1)
