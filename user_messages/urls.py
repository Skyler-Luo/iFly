"""
用户消息模块 URL 配置。

定义消息相关的 API 路由。
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import MessageViewSet

router = DefaultRouter()
router.register(r'', MessageViewSet, basename='messages')

urlpatterns = [
    path('', include(router.urls)),
]
