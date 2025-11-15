from rest_framework import serializers
from .models import (
    PointsAccount,
    PointsTransaction,
    ExchangeItem,
    ExchangeRecord,
    PointsTask,
    TaskCompletion
)

class PointsAccountSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')
    
    class Meta:
        model = PointsAccount
        fields = ['id', 'username', 'points_balance', 'lifetime_points', 
                 'member_level', 'created_at', 'updated_at']
        read_only_fields = ['id', 'username', 'created_at', 'updated_at']

class PointsTransactionSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='account.user.username')
    
    class Meta:
        model = PointsTransaction
        fields = ['id', 'username', 'points', 'transaction_type', 
                 'description', 'reference_id', 'created_at']
        read_only_fields = ['id', 'created_at']

class ExchangeItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExchangeItem
        fields = ['id', 'name', 'description', 'points_required', 
                 'image_url', 'available_stock', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']

class ExchangeRecordSerializer(serializers.ModelSerializer):
    item_name = serializers.ReadOnlyField(source='item.name')
    username = serializers.ReadOnlyField(source='account.user.username')
    
    class Meta:
        model = ExchangeRecord
        fields = ['id', 'username', 'item_name', 'quantity', 'total_points',
                 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class ExchangeRequestSerializer(serializers.Serializer):
    item_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)
    
    def validate(self, data):
        try:
            item = ExchangeItem.objects.get(id=data['item_id'])
        except ExchangeItem.DoesNotExist:
            raise serializers.ValidationError("商品不存在")
            
        if not item.is_active:
            raise serializers.ValidationError("商品已下架")
            
        if item.available_stock < data['quantity']:
            raise serializers.ValidationError("商品库存不足")
            
        data['item'] = item
        data['points_required'] = item.points_required * data['quantity']
        return data

class PointsTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = PointsTask
        fields = ['id', 'title', 'description', 'points_reward', 
                 'task_type', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']

class TaskCompletionSerializer(serializers.ModelSerializer):
    task_title = serializers.ReadOnlyField(source='task.title')
    task_points = serializers.ReadOnlyField(source='task.points_reward')
    username = serializers.ReadOnlyField(source='account.user.username')
    
    class Meta:
        model = TaskCompletion
        fields = ['id', 'username', 'task_title', 'task_points', 'completed_at']
        read_only_fields = ['id', 'completed_at']

class MemberLevelProgressSerializer(serializers.Serializer):
    current_level = serializers.CharField()
    next_level = serializers.CharField(allow_null=True)
    current_points = serializers.IntegerField()
    points_needed = serializers.IntegerField()
    progress_percentage = serializers.FloatField() 