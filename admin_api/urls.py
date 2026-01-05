from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AdminFlightViewSet, 
    AdminUserViewSet, 
    AdminOrderViewSet,
    SiteSettingsView,
    BusinessRulesView,
    SettingsHistoryView,
)

# 创建路由器并注册视图集
router = DefaultRouter()
router.register(r'flights', AdminFlightViewSet, basename='admin-flight')
router.register(r'users', AdminUserViewSet, basename='admin-user')
router.register(r'orders', AdminOrderViewSet, basename='admin-order')

urlpatterns = [
    path('', include(router.urls)),
    # 系统设置 API - 满足 Requirements 1, 2
    path('settings/site/', SiteSettingsView.as_view(), name='admin-site-settings'),
    path('settings/business/', BusinessRulesView.as_view(), name='admin-business-rules'),
    path('settings/history/', SettingsHistoryView.as_view(), name='admin-settings-history'),
]