from django_filters import rest_framework as filters
from .models import Flight

class FlightFilter(filters.FilterSet):
    departure_time = filters.DateTimeFromToRangeFilter(field_name='departure_time')
    arrival_time = filters.DateTimeFromToRangeFilter(field_name='arrival_time')
    price = filters.RangeFilter(field_name='price')
    discount = filters.RangeFilter(field_name='discount')
    capacity = filters.RangeFilter(field_name='capacity')
    available_seats = filters.RangeFilter(field_name='available_seats')

    class Meta:
        model = Flight
        fields = ['flight_number', 'departure_city', 'arrival_city', 'status', 'departure_time', 'arrival_time'] 