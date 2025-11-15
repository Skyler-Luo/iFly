from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# 创建路由器
router = DefaultRouter()
router.register(r'passengers', views.PassengerViewSet, basename='passenger')
router.register(r'management', views.UserManagementViewSet, basename='user-management')

# URL模式
urlpatterns = [
    # 用户认证相关
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', views.UserLogoutView.as_view(), name='logout'),
    
    # 用户个人信息管理
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('profile/update/', views.UserProfileUpdateView.as_view(), name='profile-update'),
    path('profile/change-password/', views.ChangePasswordView.as_view(), name='change-password'),
    
    # 视图集路由
    path('', include(router.urls)),
] 