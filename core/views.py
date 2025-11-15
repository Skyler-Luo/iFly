from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.shortcuts import render
from django.db.models import Count, Avg, F, Sum
import logging

from core.models import City, PopularRoute, WeatherCache
from core.serializers import CitySerializer
from core.serializers import PopularRouteSerializer
from core.serializers import SimplePopularRouteSerializer
from core.serializers import WeatherCacheSerializer
from core.serializers import SimpleWeatherSerializer
from core import weather_api

logger = logging.getLogger(__name__)

# 获取天气缓存过期时间
WEATHER_CACHE_EXPIRY = getattr(settings, 'WEATHER_CACHE_EXPIRY', 60)  # 默认60分钟

class CityListView(generics.ListAPIView):
    """获取所有城市列表"""
    queryset = City.objects.all()
    serializer_class = CitySerializer


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


@method_decorator(cache_page(60), name='dispatch')
class WeatherDetailView(APIView):
    """获取指定城市的天气信息"""
    def get(self, request, city_name):
        try:
            # 先查找城市
            city = City.objects.get(name=city_name)
            
            # 查找该城市的天气缓存
            weather = WeatherCache.objects.filter(city=city).first()
            
            # 判断天气缓存是否过期（根据设置的过期时间）或不存在
            weather_expired = False
            if not weather:
                weather_expired = True
            elif weather.updated_at < timezone.now() - timedelta(minutes=WEATHER_CACHE_EXPIRY):
                weather_expired = True
            
            # 如果天气数据过期或不存在，获取新的天气数据
            if weather_expired:
                # 调用天气API获取最新数据
                weather_data = weather_api.get_weather_data(city_name)
                
                if weather_data:
                    # 如果已经有缓存记录，更新它
                    if weather:
                        weather.temperature = weather_data['temperature']
                        weather.description = weather_data['description']
                        weather.humidity = weather_data['humidity']
                        weather.wind_speed = weather_data['wind_speed']
                        weather.icon = weather_data['icon']
                        # 更新时间由model自动更新
                        weather.save()
                    # 否则创建新记录
                    else:
                        weather = WeatherCache.objects.create(
                            city=city,
                            temperature=weather_data['temperature'],
                            description=weather_data['description'],
                            humidity=weather_data['humidity'],
                            wind_speed=weather_data['wind_speed'],
                            icon=weather_data['icon']
                            # 更新时间由model自动设置
                        )
                else:
                    # 如果获取新数据失败，但有旧数据，则继续使用旧数据
                    if not weather:
                        return Response(
                            {"error": f"无法获取城市 {city_name} 的天气数据"},
                            status=status.HTTP_404_NOT_FOUND
                        )
            
            # 根据查询参数选择序列化器
            if request.query_params.get('simple') == 'true':
                serializer = SimpleWeatherSerializer(weather)
            else:
                serializer = WeatherCacheSerializer(weather)
                
            return Response(serializer.data)
            
        except City.DoesNotExist:
            return Response(
                {"error": f"城市 {city_name} 不存在"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": f"获取天气数据失败: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@method_decorator(cache_page(60), name='dispatch')
@api_view(['GET'])
def get_weather(request, city):
    """
    获取指定城市的天气信息
    """
    # 检查是否有缓存
    cache_key = f'weather:{city}'
    weather_data = cache.get(cache_key)
    
    if not weather_data:
        # 从API获取天气数据
        try:
            weather_data = weather_api.get_weather_data(city)
            
            if weather_data:
                # 设置缓存，过期时间由设置决定
                cache_timeout = getattr(settings, 'WEATHER_CACHE_TIMEOUT', 30) * 60  # 转为秒
                cache.set(cache_key, weather_data, cache_timeout)
            else:
                return Response({"error": "无法获取天气数据"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(f"获取天气数据时出错: {e}")
            return Response({"error": f"获取天气数据时出错: {str(e)}"}, 
                          status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # 获取天气预报数据
    forecast_cache_key = f'forecast:{city}'
    forecast_data = cache.get(forecast_cache_key)
    
    if not forecast_data:
        try:
            forecast_data = weather_api.get_forecast_data(city)
            
            if forecast_data:
                # 设置缓存
                cache_timeout = getattr(settings, 'WEATHER_CACHE_TIMEOUT', 30) * 60  # 转为秒
                cache.set(forecast_cache_key, forecast_data, cache_timeout)
        except Exception as e:
            logger.error(f"获取天气预报时出错: {e}")
            # 预报数据出错不影响当前天气返回
            forecast_data = None
    
    # 组合数据
    result = {
        'city': city,
        'current': weather_data,
        'forecast': forecast_data.get('forecast', []) if forecast_data else []
    }
    
    return Response(result) 