"""
用户消息模块视图定义。

提供消息的 CRUD 操作及标记已读、批量删除等功能。
"""
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Message
from .serializers import MessageSerializer


class StandardResultsSetPagination(PageNumberPagination):
    """标准分页配置，默认每页10条记录。"""

    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class MessageViewSet(viewsets.ModelViewSet):
    """消息API视图集，提供消息的增删改查及批量操作功能。"""
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """只返回当前登录用户的消息"""
        queryset = Message.objects.filter(user=self.request.user)
        
        # 过滤消息类型
        message_type = self.request.query_params.get('type')
        if message_type:
            queryset = queryset.filter(type=message_type)
            
        return queryset
    
    def perform_create(self, serializer):
        """创建消息时自动关联到当前用户"""
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def read(self, request, pk=None):
        """标记消息为已读或未读"""
        message = self.get_object()
        is_read = request.data.get('is_read', True)
        message.is_read = is_read
        message.save()
        serializer = self.get_serializer(message)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def read_all(self, request):
        """标记所有消息为已读"""
        self.get_queryset().update(is_read=True)
        return Response({'status': 'success', 'message': '所有消息已标记为已读'})
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """获取未读消息数量"""
        count = self.get_queryset().filter(is_read=False).count()
        return Response({'count': count})
    
    @action(detail=False, methods=['post'])
    def delete_multiple(self, request):
        """批量删除消息"""
        message_ids = request.data.get('message_ids', [])
        if not message_ids:
            return Response({'error': '未提供消息ID'}, status=status.HTTP_400_BAD_REQUEST)
            
        messages_to_delete = self.get_queryset().filter(id__in=message_ids)
        count = messages_to_delete.count()
        messages_to_delete.delete()
        
        return Response({
            'status': 'success',
            'message': f'成功删除{count}条消息',
            'count': count
        })
