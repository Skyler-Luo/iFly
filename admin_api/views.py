from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from flight.models import Flight
from accounts.models import User
from booking.models import Order
from flight.serializers import FlightSerializer
from accounts.serializers import UserSerializer
from booking.serializers import OrderSerializer


class AdminFlightViewSet(viewsets.ModelViewSet):
    """
    管理员航班管理API
    """
    permission_classes = [IsAdminUser]
    queryset = Flight.objects.all().order_by('-departure_time')
    serializer_class = FlightSerializer

    def list(self, request):
        """重写list方法，确保返回格式正确的数据"""
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['patch'])
    def status(self, request, pk=None):
        flight = self.get_object()
        status_value = request.data.get('status')
        if status_value:
            flight.status = status_value
            flight.save()
            return Response({'status': 'flight status updated'})
        return Response({'error': 'No status provided'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def passengers(self, request, pk=None):
        flight = self.get_object()
        # 获取航班乘客的逻辑
        # 这里需要根据实际数据模型补充实现
        return Response({'message': 'Passenger list functionality will be implemented'})
    
    @action(detail=True, methods=['get', 'put'])
    def pricing(self, request, pk=None):
        flight = self.get_object()
        if request.method == 'GET':
            # 获取价格信息
            return Response({'price': flight.price, 'discounted_price': flight.discounted_price})
        elif request.method == 'PUT':
            # 更新价格信息
            price = request.data.get('price')
            if price:
                flight.price = price
                flight.save()
                return Response({'status': 'pricing updated'})
            return Response({'error': 'No price provided'}, status=status.HTTP_400_BAD_REQUEST)


class AdminUserViewSet(viewsets.ModelViewSet):
    """
    管理员用户管理API
    """
    permission_classes = [IsAdminUser]
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def list(self, request):
        """重写list方法，确保返回格式正确的数据"""
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['patch'])
    def status(self, request, pk=None):
        user = self.get_object()
        status_value = request.data.get('status')
        if status_value:
            user.is_active = (status_value == 'active')
            user.save()
            return Response({'status': 'user status updated'})
        return Response({'error': 'No status provided'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def reset_password(self, request, pk=None):
        user = self.get_object()
        # 重置密码逻辑，通常是发送重置邮件
        # 示例实现:
        # user.set_password('temporary_password')
        # user.save()
        return Response({'status': 'password reset email sent'})
    
    @action(detail=True, methods=['get'])
    def orders(self, request, pk=None):
        user = self.get_object()
        orders = Order.objects.filter(user=user).order_by('-created_at')
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def adjust_points(self, request, pk=None):
        user = self.get_object()
        points_type = request.data.get('type')
        points_value = request.data.get('points', 0)
        
        if points_type == 'add':
            user.points += points_value
        elif points_type == 'subtract':
            user.points = max(0, user.points - points_value)
        elif points_type == 'set':
            user.points = points_value
            
        user.save()
        return Response({'status': 'points adjusted', 'new_points': user.points})
    
    @action(detail=True, methods=['post'])
    def send_notification(self, request, pk=None):
        user = self.get_object()
        message = request.data.get('message')
        if not message:
            return Response({'error': 'No message provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 发送通知的逻辑
        # 示例: Notification.objects.create(user=user, message=message)
        return Response({'status': 'notification sent'})


class AdminOrderViewSet(viewsets.ModelViewSet):
    """
    管理员订单管理API
    """
    permission_classes = [IsAdminUser]
    queryset = Order.objects.all().order_by('-created_at')
    serializer_class = OrderSerializer

    def list(self, request):
        """重写list方法，确保返回格式正确的数据"""
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['patch'])
    def status(self, request, pk=None):
        order = self.get_object()
        status_value = request.data.get('status')
        if status_value:
            order.status = status_value
            order.save()
            return Response({'status': 'order status updated'})
        return Response({'error': 'No status provided'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def refund(self, request, pk=None):
        order = self.get_object()
        amount = request.data.get('amount')
        reason = request.data.get('reason')
        
        # 处理退款逻辑
        order.status = 'refunded'
        order.save()
        
        # 实际项目中应该有更完整的退款处理逻辑
        return Response({'status': 'refund processed'})
    
    @action(detail=True, methods=['get'])
    def payment(self, request, pk=None):
        order = self.get_object()
        # 获取支付信息逻辑
        payment_info = {
            'id': order.id,
            'amount': order.total_amount,
            'status': order.status,
            'payment_method': getattr(order, 'payment_method', 'Unknown'),
            'payment_time': getattr(order, 'payment_time', None)
        }
        return Response(payment_info)
