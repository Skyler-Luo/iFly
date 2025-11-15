from rest_framework import serializers
from .models import Promotion, PromotionUse

class PromotionSerializer(serializers.ModelSerializer):
    """促销活动序列化器"""
    is_valid = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Promotion
        fields = ['id', 'title', 'description', 'promo_code', 'discount_type', 
                 'discount_value', 'min_purchase', 'start_date', 'end_date', 
                 'usage_limit', 'used_count', 'is_active', 'is_valid', 
                 'created_at', 'updated_at']
        read_only_fields = ['id', 'used_count', 'created_at', 'updated_at']
        
    def validate(self, data):
        """验证促销活动数据"""
        if 'start_date' in data and 'end_date' in data:
            if data['start_date'] >= data['end_date']:
                raise serializers.ValidationError("开始时间必须早于结束时间")
        return data

class PromotionUseSerializer(serializers.ModelSerializer):
    """促销活动使用记录序列化器"""
    promotion_title = serializers.ReadOnlyField(source='promotion.title')
    promo_code = serializers.ReadOnlyField(source='promotion.promo_code')
    username = serializers.ReadOnlyField(source='user.username')
    
    class Meta:
        model = PromotionUse
        fields = ['id', 'promotion_title', 'promo_code', 'username', 
                 'order_id', 'discount_amount', 'used_at']
        read_only_fields = ['id', 'used_at']

class PromoValidateSerializer(serializers.Serializer):
    """优惠码验证序列化器"""
    promo_code = serializers.CharField(max_length=20)
    
    def validate_promo_code(self, value):
        """验证优惠码是否有效"""
        try:
            promotion = Promotion.objects.get(promo_code=value)
        except Promotion.DoesNotExist:
            raise serializers.ValidationError("优惠码不存在")
            
        if not promotion.is_valid:
            if not promotion.is_active:
                raise serializers.ValidationError("优惠码已禁用")
            elif promotion.usage_limit > 0 and promotion.used_count >= promotion.usage_limit:
                raise serializers.ValidationError("优惠码已达到使用上限")
            else:
                raise serializers.ValidationError("优惠码不在有效期内")
                
        return value

class PromoApplySerializer(serializers.Serializer):
    """应用优惠码序列化器"""
    promo_code = serializers.CharField(max_length=20)
    order_id = serializers.CharField(max_length=100)
    
    def validate(self, data):
        """验证优惠码和订单"""
        promo_code = data.get('promo_code')
        order_id = data.get('order_id')
        
        # 验证优惠码
        try:
            promotion = Promotion.objects.get(promo_code=promo_code)
        except Promotion.DoesNotExist:
            raise serializers.ValidationError({"promo_code": "优惠码不存在"})
            
        if not promotion.is_valid:
            if not promotion.is_active:
                raise serializers.ValidationError({"promo_code": "优惠码已禁用"})
            elif promotion.usage_limit > 0 and promotion.used_count >= promotion.usage_limit:
                raise serializers.ValidationError({"promo_code": "优惠码已达到使用上限"})
            else:
                raise serializers.ValidationError({"promo_code": "优惠码不在有效期内"})
                
        # 检查订单是否已使用过此优惠码
        if PromotionUse.objects.filter(promotion=promotion, order_id=order_id).exists():
            raise serializers.ValidationError({"order_id": "此订单已使用过该优惠码"})
            
        data['promotion'] = promotion
        return data 