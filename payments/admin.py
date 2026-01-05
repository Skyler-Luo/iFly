from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['order', 'method', 'amount', 'status', 'transaction_id', 'created_at']
    list_filter = ['method', 'status']
    search_fields = ['order__order_number', 'transaction_id']
    readonly_fields = ['transaction_id', 'created_at', 'updated_at'] 