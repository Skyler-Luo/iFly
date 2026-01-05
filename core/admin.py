from django.contrib import admin
from .models import SystemLog, City, PopularRoute


@admin.register(SystemLog)
class SystemLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'ip_address', 'created_at']
    search_fields = ['user__username', 'action', 'ip_address']
    list_filter = ['action', 'ip_address']
    readonly_fields = ['user', 'action', 'detail', 'ip_address', 'created_at']

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'country')
    search_fields = ('name', 'code')
    
@admin.register(PopularRoute)
class PopularRouteAdmin(admin.ModelAdmin):
    list_display = ('from_city', 'to_city', 'price', 'discount', 'popularity')
    list_filter = ('from_city', 'to_city')