from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Order, Ticket
from .serializers import OrderSerializer, TicketSerializer, OrderCreateSerializer
from notifications.services import create_order_notification, create_refund_notification

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        return OrderSerializer

    def get_queryset(self):
        user = self.request.user
        # 确保用户已认证，未认证返回空查询集
        if not user.is_authenticated:
            return Order.objects.none()
            
        if hasattr(user, 'role') and user.role == 'admin':
            return Order.objects.all()
        return Order.objects.filter(user=user)

    def get_object(self):
        """
        允许通过order_number或ID查询订单
        """
        # 获取URL中的参数(pk)
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        pk = self.kwargs.get(lookup_url_kwarg)
        
        # 尝试通过order_number查询订单
        if isinstance(pk, str) and pk.startswith('ORD'):
            try:
                obj = self.get_queryset().get(order_number=pk)
                self.check_object_permissions(self.request, obj)
                return obj
            except Order.DoesNotExist:
                pass
        
        # 如果通过order_number无法找到，回退到默认行为（通过ID查询）
        return super().get_object()
        
    def list(self, request, *args, **kwargs):
        """
        获取订单列表，添加详细的日志
        """
        print(f"用户 {request.user.username} 请求订单列表")
        queryset = self.filter_queryset(self.get_queryset())
        print(f"找到 {queryset.count()} 个订单")
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['patch', 'put'], permission_classes=[permissions.IsAuthenticated])
    def status(self, request, pk=None):
        """
        更新订单状态
        """
        order = self.get_object()
        status_data = request.data.get('status')
        
        if not status_data:
            return Response({'detail': '状态字段必须提供'}, status=status.HTTP_400_BAD_REQUEST)
            
        # 检查状态值是否有效
        valid_statuses = [choice[0] for choice in Order.ORDER_STATUS_CHOICES]
        if status_data not in valid_statuses:
            return Response({'detail': f'无效的状态值。有效值为: {", ".join(valid_statuses)}'}, 
                            status=status.HTTP_400_BAD_REQUEST)
        
        # 根据状态更新相关时间字段
        if status_data == 'paid' and order.status == 'pending':
            order.paid_at = timezone.now()
        
        # 更新订单状态
        order.status = status_data
        order.save()
        
        # 创建通知
        create_order_notification(order.user, order, status_data)
        
        # 返回更新后的订单数据
        serializer = self.get_serializer(order)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def pay(self, request, pk=None):
        order = self.get_object()
        if order.status != 'pending':
            return Response({'detail': '订单状态不允许支付'}, status=status.HTTP_400_BAD_REQUEST)
        order.status = 'paid'
        order.paid_at = timezone.now()
        order.save()
        
        # 创建支付成功通知
        create_order_notification(order.user, order, 'paid')
        
        return Response(self.get_serializer(order).data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def cancel(self, request, pk=None):
        order = self.get_object()
        if order.status != 'paid':
            return Response({'detail': '订单状态不允许取消'}, status=status.HTTP_400_BAD_REQUEST)
        order.status = 'canceled'
        order.save()
        # 退票并补充座位
        for ticket in order.tickets.filter(status='valid'):
            ticket.status = 'refunded'
            ticket.save()
            flight = ticket.flight
            flight.available_seats = min(flight.available_seats + 1, flight.capacity)
            if flight.status == 'full' and flight.available_seats > 0:
                flight.status = 'scheduled'
            flight.save()
            
        # 创建订单取消通知
        create_order_notification(order.user, order, 'canceled')
        
        return Response(self.get_serializer(order).data)

class TicketViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Ticket.objects.all()
        return Ticket.objects.filter(order__user=user)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def refund(self, request, pk=None):
        ticket = self.get_object()
        if ticket.status != 'valid':
            return Response({'detail': '机票不可退票'}, status=status.HTTP_400_BAD_REQUEST)
        ticket.status = 'refunded'
        ticket.save()
        flight = ticket.flight
        flight.available_seats = min(flight.available_seats + 1, flight.capacity)
        if flight.status == 'full' and flight.available_seats > 0:
            flight.status = 'scheduled'
        flight.save()
        
        # 创建退票通知
        user = ticket.order.user
        order = ticket.order
        create_refund_notification(user, order, 'processing')
        
        return Response(self.get_serializer(ticket).data) 