from django.contrib import admin
from .models import Order, Ticket

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user', 'total_price', 'status', 'payment_method', 'created_at', 'paid_at']
    search_fields = ['order_number', 'user__username', 'contact_name', 'contact_phone', 'contact_email']
    list_filter = ['status', 'payment_method']

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ['ticket_number', 'order', 'flight', 'passenger_name', 'seat_number', 'cabin_class', 'price', 'status']
    search_fields = ['ticket_number', 'flight__flight_number', 'passenger_name', 'passenger_id_number']
    list_filter = ['status', 'cabin_class'] 