from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserPointsView,
    PointsHistoryView,
    PointsOverviewView,
    ExchangeItemViewSet,
    ExchangeView,
    PointsTaskViewSet,
    CompleteTaskView,
    MemberLevelView,
    LevelProgressView,
    CheckInView,
    ExpiringPointsView
)

router = DefaultRouter()
router.register(r'exchange-items', ExchangeItemViewSet, basename='exchange-item')
router.register(r'tasks', PointsTaskViewSet, basename='points-task')

urlpatterns = [
    path('user/', UserPointsView.as_view(), name='user-points'),
    path('history/', PointsHistoryView.as_view(), name='points-history'),
    path('overview/', PointsOverviewView.as_view(), name='points-overview'),
    path('exchange/', ExchangeView.as_view(), name='points-exchange'),
    path('tasks/<int:task_id>/complete/', CompleteTaskView.as_view(), name='complete-task'),
    path('member-level/', MemberLevelView.as_view(), name='member-level'),
    path('level-progress/', LevelProgressView.as_view(), name='level-progress'),
    path('check-in/', CheckInView.as_view(), name='check-in'),
    path('expiring/', ExpiringPointsView.as_view(), name='expiring-points'),
    path('', include(router.urls)),
] 