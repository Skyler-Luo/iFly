from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AdminFlightViewSet, AdminUserViewSet, AdminOrderViewSet

# 创建路由器并注册视图集
router = DefaultRouter()
router.register(r'flights', AdminFlightViewSet, basename='admin-flight')
router.register(r'users', AdminUserViewSet, basename='admin-user')
router.register(r'orders', AdminOrderViewSet, basename='admin-order')

urlpatterns = [
    path('', include(router.urls)),
] 