from django.contrib import admin
from .models import Flight

# Register your models here.

@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = ['flight_number', 'departure_city', 'arrival_city', 'departure_time', 'arrival_time', 'price', 'available_seats', 'seat_rows', 'seats_per_row', 'status_verbose']
    search_fields = ['flight_number', 'departure_city', 'arrival_city', 'aircraft_type']
    list_filter = ['status', 'departure_city', 'arrival_city']
    
    @admin.display(description='航班状态')
    def status_verbose(self, obj):
        return obj.get_status_display()
