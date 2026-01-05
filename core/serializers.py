from rest_framework import serializers

from .models import City, PopularRoute


class CommonSerializerMixin:
    """
    通用序列化器混入类，提供常用的只读字段
    """
    
    @staticmethod
    def get_username_field(source_path='user.username'):
        """获取用户名只读字段"""
        return serializers.ReadOnlyField(source=source_path)
    
    @staticmethod
    def get_user_id_field(source_path='user.id'):
        """获取用户ID只读字段"""
        return serializers.ReadOnlyField(source=source_path)
    
    @staticmethod
    def get_created_at_field():
        """获取创建时间只读字段"""
        return serializers.DateTimeField(read_only=True)
    
    @staticmethod
    def get_updated_at_field():
        """获取更新时间只读字段"""
        return serializers.DateTimeField(read_only=True)


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['id', 'name', 'code', 'country', 'longitude', 'latitude']


class PopularRouteSerializer(serializers.ModelSerializer):
    from_city_name = serializers.CharField(source='from_city.name', read_only=True)
    to_city_name = serializers.CharField(source='to_city.name', read_only=True)
    
    class Meta:
        model = PopularRoute
        fields = [
            'id', 'from_city', 'from_city_name', 'to_city', 'to_city_name',
            'price', 'discount', 'popularity'
        ]


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