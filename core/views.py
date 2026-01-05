from rest_framework import generics

from core.models import City, PopularRoute
from core.serializers import (
    CitySerializer,
    PopularRouteSerializer,
    SimplePopularRouteSerializer,
)

class CityListView(generics.ListAPIView):
    """获取所有城市列表"""
    queryset = City.objects.all().order_by('name')
    serializer_class = CitySerializer
    pagination_class = None  # 禁用分页，返回完整城市列表


class PopularRouteListView(generics.ListAPIView):
    """获取热门航线列表"""
    queryset = PopularRoute.objects.all().order_by('-popularity')
    
    def get_serializer_class(self):
        # 根据查询参数选择序列化器
        if self.request.query_params.get('simple') == 'true':
            return SimplePopularRouteSerializer
        return PopularRouteSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        # 可选参数：limit - 限制返回的航线数量
        limit = self.request.query_params.get('limit')
        if limit and limit.isdigit():
            queryset = queryset[:int(limit)]
        return queryset