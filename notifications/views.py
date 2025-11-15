from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Notification
from .serializers import NotificationSerializer

class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Notification.objects.filter(user=user).order_by('-created_at')
        
        # 如果指定了类型过滤
        notif_type = self.request.query_params.get('type')
        if notif_type:
            queryset = queryset.filter(notif_type=notif_type)
            
        return queryset

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def mark_read(self, request, pk=None):
        notif = self.get_object()
        notif.is_read = True
        notif.save()
        return Response(self.get_serializer(notif).data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def mark_unread(self, request, pk=None):
        notif = self.get_object()
        notif.is_read = False
        notif.save()
        return Response(self.get_serializer(notif).data)
        
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def read_all(self, request):
        """标记所有通知为已读"""
        notifications = self.get_queryset()
        notifications.update(is_read=True)
        return Response({'status': 'success'})
        
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def delete_multiple(self, request):
        """批量删除通知"""
        message_ids = request.data.get('message_ids', [])
        if not message_ids:
            return Response({'detail': '未提供要删除的通知ID'}, status=status.HTTP_400_BAD_REQUEST)
            
        self.get_queryset().filter(id__in=message_ids).delete()
        return Response({'status': 'success'})
        
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def unread_count(self, request):
        """获取未读通知数量"""
        count = self.get_queryset().filter(is_read=False).count()
        return Response({'count': count}) 