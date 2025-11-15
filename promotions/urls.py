from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PromotionViewSet, ApplyPromotionView

router = DefaultRouter()
router.register(r'', PromotionViewSet, basename='promotion')

urlpatterns = [
    path('apply/', ApplyPromotionView.as_view(), name='apply-promotion'),
    path('', include(router.urls)),
] 