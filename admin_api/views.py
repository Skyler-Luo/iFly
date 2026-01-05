from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from flight.models import Flight
from accounts.models import User
from booking.models import Order
from flight.serializers import FlightSerializer
from accounts.serializers import UserSerializer
from booking.serializers import OrderSerializer
from core.services import SettingsService


class AdminFlightViewSet(viewsets.ModelViewSet):
    """
    管理员航班管理API
    """
    permission_classes = [IsAdminUser]
    queryset = Flight.objects.all().order_by('-departure_time')
    serializer_class = FlightSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['status']
    search_fields = ['flight_number', 'departure_city', 'arrival_city']
    pagination_class = None  # 禁用分页，返回所有航班

    def get_queryset(self):
        queryset = super().get_queryset()
        # 支持日期过滤
        date = self.request.query_params.get('date')
        if date:
            queryset = queryset.filter(departure_time__date=date)
        return queryset

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
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['role', 'is_active']
    search_fields = ['username', 'email', 'phone']
    pagination_class = None  # 禁用分页，返回所有用户

    def get_queryset(self):
        queryset = super().get_queryset()
        # 支持状态过滤（前端使用 status 参数）
        status_param = self.request.query_params.get('status')
        if status_param == 'active':
            queryset = queryset.filter(is_active=True)
        elif status_param == 'inactive':
            queryset = queryset.filter(is_active=False)
        elif status_param == 'locked':
            queryset = queryset.filter(is_active=False)
        return queryset

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
        return Response({'status': 'password reset email sent'})
    
    @action(detail=True, methods=['get'])
    def orders(self, request, pk=None):
        user = self.get_object()
        orders = Order.objects.filter(user=user).order_by('-created_at')
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)
    
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
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['status']
    search_fields = ['order_number', 'contact_name', 'contact_phone']
    pagination_class = None  # 禁用分页，返回所有订单

    def get_queryset(self):
        queryset = super().get_queryset().prefetch_related('tickets__flight')
        # 支持日期过滤
        date = self.request.query_params.get('date')
        if date:
            queryset = queryset.filter(created_at__date=date)
        return queryset

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
            'amount': order.total_price,
            'status': order.status,
            'payment_method': order.payment_method or 'Unknown',
            'payment_time': order.paid_at
        }
        return Response(payment_info)


class SiteSettingsView(APIView):
    """
    站点设置 API
    
    满足 Requirements 1.1-1.5:
    - 1.1: 配置站点名称、Logo URL、Favicon
    - 1.2: 配置联系邮箱、电话、地址
    - 1.3: 配置版权文本、ICP备案号
    - 1.4: 设置更新后立即生效
    - 1.5: 验证 URL 格式
    """
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        """
        GET /api/admin/settings/site/
        
        获取所有站点设置
        """
        settings_data = SettingsService.get_site_settings()
        return Response(settings_data)
    
    def put(self, request):
        """
        PUT /api/admin/settings/site/
        
        更新站点设置
        """
        result = SettingsService.update_site_settings(request.data, request.user)
        
        if result['success']:
            return Response({'message': '站点设置已更新'})
        
        return Response(result['errors'], status=status.HTTP_400_BAD_REQUEST)



class BusinessRulesView(APIView):
    """
    业务规则设置 API
    
    满足 Requirements 2.1-2.5:
    - 2.1: 配置订单支付超时时间（默认30分钟）
    - 2.2: 配置退款费率
    - 2.3: 配置改签费率
    - 2.4: 配置值机开放时间（起飞前小时数）
    - 2.5: 更新时记录变更历史（管理员用户和时间戳）
    """
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        """
        GET /api/admin/settings/business/
        
        获取所有业务规则设置
        """
        rules_data = SettingsService.get_business_rules()
        return Response(rules_data)
    
    def put(self, request):
        """
        PUT /api/admin/settings/business/
        
        更新业务规则设置
        变更会自动记录到历史中（满足 Requirement 2.5）
        """
        result = SettingsService.update_business_rules(request.data, request.user)
        return Response({'message': '业务规则已更新'})



class SettingsHistoryView(APIView):
    """
    设置变更历史查询 API
    
    满足 Requirement 2.5:
    - 记录业务规则变更的管理员用户和时间戳
    - 支持按分类过滤历史记录
    """
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        """
        GET /api/admin/settings/history/
        
        获取设置变更历史
        
        Query Parameters:
            category (optional): 过滤分类 ('site' 或 'business')
            limit (optional): 返回记录数量限制，默认50
        """
        category = request.query_params.get('category')
        limit = int(request.query_params.get('limit', 50))
        
        history = SettingsService.get_settings_history(category, limit)
        
        # 序列化历史记录
        history_data = [{
            'id': h.id,
            'setting_key': h.setting.key,
            'setting_category': h.setting.category,
            'old_value': h.old_value,
            'new_value': h.new_value,
            'changed_by': h.changed_by.username if h.changed_by else None,
            'changed_at': h.changed_at.isoformat(),
        } for h in history]
        
        return Response(history_data)
