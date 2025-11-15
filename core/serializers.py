from rest_framework import serializers
from .models import City, PopularRoute, WeatherCache

class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['id', 'name', 'code', 'country', 'longitude', 'latitude']


class PopularRouteSerializer(serializers.ModelSerializer):
    from_city_name = serializers.CharField(source='from_city.name', read_only=True)
    to_city_name = serializers.CharField(source='to_city.name', read_only=True)
    
    class Meta:
        model = PopularRoute
        fields = ['id', 'from_city', 'from_city_name', 'to_city', 'to_city_name', 
                 'price', 'discount', 'popularity']


class WeatherCacheSerializer(serializers.ModelSerializer):
    city_name = serializers.CharField(source='city.name', read_only=True)
    
    class Meta:
        model = WeatherCache
        fields = ['id', 'city', 'city_name', 'temperature', 'description', 
                 'humidity', 'wind_speed', 'icon', 'updated_at']

        
# 简化的数据结构，与前端模拟数据保持一致
class SimplePopularRouteSerializer(serializers.ModelSerializer):
    from_name = serializers.CharField(source='from_city.name', read_only=True)
    to_name = serializers.CharField(source='to_city.name', read_only=True)
    
    class Meta:
        model = PopularRoute
        fields = ['id', 'from_name', 'to_name', 'price', 'discount']
        
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        # 重命名键以与前端保持一致
        rep['from'] = rep.pop('from_name')
        rep['to'] = rep.pop('to_name')
        return rep


class SimpleWeatherSerializer(serializers.ModelSerializer):
    city_name = serializers.CharField(source='city.name', read_only=True)
    
    class Meta:
        model = WeatherCache
        fields = ['city_name', 'temperature', 'description', 'humidity', 
                 'wind_speed', 'icon', 'updated_at']
        
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        # 重命名键以与前端保持一致
        rep['city'] = rep.pop('city_name')
        rep['temp'] = rep.pop('temperature')
        rep['feels_like'] = rep['temp'] - 2  # 添加体感温度，通常比实际温度低2度
        rep['wind'] = {'speed': float(rep.pop('wind_speed')), 'deg': 0}  # 添加风向
        rep['clouds'] = min(int(rep['humidity'] / 2), 100)  # 根据湿度估计云量
        rep['timestamp'] = int(instance.updated_at.timestamp())
        return rep 