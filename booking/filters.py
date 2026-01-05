"""
订单与机票模块过滤器定义。
"""
import django_filters
from .models import Order, Ticket


class OrderFilter(django_filters.FilterSet):
    """订单过滤器"""
    
    status = django_filters.CharFilter(method='filter_status')
    order_number = django_filters.CharFilter(lookup_expr='icontains')
    created_at_after = django_filters.DateTimeFilter(
        field_name='created_at', lookup_expr='gte'
    )
    created_at_before = django_filters.DateTimeFilter(
        field_name='created_at', lookup_expr='lte'
    )
    min_price = django_filters.NumberFilter(
        field_name='total_price', lookup_expr='gte'
    )
    max_price = django_filters.NumberFilter(
        field_name='total_price', lookup_expr='lte'
    )
    
    class Meta:
        model = Order
        fields = ['status', 'order_number']
    
    def filter_status(self, queryset, name, value):
        """
        状态过滤，支持前端大写状态映射到后端小写状态
        """
        if not value:
            return queryset
        
        # 前端状态到后端状态的映射
        status_map = {
            'PENDING': 'pending',
            'PAID': 'paid',
            'COMPLETED': 'completed',
            'CANCELLED': 'canceled',
            'CANCELED': 'canceled',
        }
        
        backend_status = status_map.get(value.upper(), value.lower())
        return queryset.filter(status=backend_status)


class TicketFilter(django_filters.FilterSet):
    """机票过滤器"""
    
    status = django_filters.CharFilter(method='filter_status')
    flight = django_filters.NumberFilter(field_name='flight_id')
    passenger_name = django_filters.CharFilter(lookup_expr='icontains')
    
    class Meta:
        model = Ticket
        fields = ['status', 'flight', 'passenger_name']
    
    def filter_status(self, queryset, name, value):
        """状态过滤"""
        if not value:
            return queryset
        
        status_map = {
            'VALID': 'valid',
            'UNUSED': 'valid',
            'USED': 'used',
            'REFUNDED': 'refunded',
        }
        
        backend_status = status_map.get(value.upper(), value.lower())
        return queryset.filter(status=backend_status)
