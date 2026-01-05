from django_filters import rest_framework as filters
from .models import Passenger

class PassengerFilter(filters.FilterSet):
    """乘客信息过滤器，支持出生日期和创建时间范围筛选"""
    birth_date = filters.DateFromToRangeFilter(field_name='birth_date')
    created_at = filters.DateTimeFromToRangeFilter(field_name='created_at')

    class Meta:
        model = Passenger
        fields = ['name', 'id_card', 'passport_number', 'gender', 'birth_date', 'created_at'] 