from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, status, filters as drf_filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils.timezone import now
from booking.models import Order

from .models import Promotion, PromotionUse
from .serializers import (
    PromotionSerializer,
    PromotionUseSerializer,
    PromoValidateSerializer,
    PromoApplySerializer
)

class PromotionViewSet(viewsets.ModelViewSet):
    """促销活动视图集"""
    queryset = Promotion.objects.all()
    serializer_class = PromotionSerializer
    filter_backends = [drf_filters.SearchFilter, drf_filters.OrderingFilter]
    search_fields = ['title', 'description', 'promo_code']
    ordering_fields = ['start_date', 'end_date', 'created_at']
    
    def get_permissions(self):
        """根据操作设置权限"""
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """根据用户角色过滤查询结果"""
        queryset = super().get_queryset()
        user = self.request.user
        
        # 普通用户只能看到有效的促销活动
        if not user.is_authenticated or not hasattr(user, 'role') or user.role != 'admin':
            current_time = now()
            queryset = queryset.filter(
                is_active=True,
                start_date__lte=current_time,
                end_date__gte=current_time
            )
            
            # 过滤掉用量已满的促销
            queryset = [promo for promo in queryset if promo.is_valid]
        
        return queryset
    
    @action(detail=True, methods=['get'])
    def usage(self, request, pk=None):
        """获取促销活动使用记录"""
        promotion = self.get_object()
        usages = PromotionUse.objects.filter(promotion=promotion)
        
        # 分页
        page = self.paginate_queryset(usages)
        if page is not None:
            serializer = PromotionUseSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = PromotionUseSerializer(usages, many=True)
        return Response(serializer.data)
        
    @action(detail=False, methods=['get'])
    def active(self, request):
        """获取当前有效的促销活动"""
        current_time = now()
        promotions = Promotion.objects.filter(
            is_active=True,
            start_date__lte=current_time,
            end_date__gte=current_time
        )
        
        # 过滤掉用量已满的促销
        valid_promotions = [promo for promo in promotions if promo.is_valid]
        
        serializer = self.get_serializer(valid_promotions, many=True)
        return Response(serializer.data)
        
    @action(detail=False, methods=['post'])
    def validate(self, request):
        """验证促销码是否有效"""
        serializer = PromoValidateSerializer(data=request.data)
        if serializer.is_valid():
            promo_code = serializer.validated_data['promo_code']
            try:
                promotion = Promotion.objects.get(promo_code=promo_code)
                return Response({
                    'valid': True,
                    'promotion': PromotionSerializer(promotion).data
                })
            except Promotion.DoesNotExist:
                return Response({
                    'valid': False,
                    'message': '优惠码不存在'
                }, status=status.HTTP_404_NOT_FOUND)
        return Response({
            'valid': False,
            'message': serializer.errors.get('promo_code', ['验证失败'])[0]
        }, status=status.HTTP_400_BAD_REQUEST)

class ApplyPromotionView(APIView):
    """应用促销码"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = PromoApplySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        user = request.user
        promotion = serializer.validated_data['promotion']
        order_id = serializer.validated_data['order_id']
        
        # 获取订单
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({"detail": "订单不存在"}, status=status.HTTP_404_NOT_FOUND)
            
        # 检查订单是否属于当前用户或用户是管理员
        if order.user != user and not hasattr(user, 'role') or user.role != 'admin':
            return Response({"detail": "无权操作此订单"}, status=status.HTTP_403_FORBIDDEN)
            
        # 检查订单状态是否允许使用优惠码
        if order.status != 'pending':
            return Response({"detail": "只有待支付订单可以应用优惠码"}, status=status.HTTP_400_BAD_REQUEST)
            
        # 检查订单金额是否满足最低消费要求
        if order.total_amount < float(promotion.min_purchase):
            return Response({
                "detail": f"订单金额不满足最低消费要求: {promotion.min_purchase}"
            }, status=status.HTTP_400_BAD_REQUEST)
            
        # 计算折扣金额
        discount_amount = 0
        
        if promotion.discount_type == 'percentage':
            # 百分比折扣
            discount_amount = order.total_amount * float(promotion.discount_value) / 100
        elif promotion.discount_type == 'fixed':
            # 固定金额
            discount_amount = min(float(promotion.discount_value), order.total_amount)
        
        # 创建使用记录
        PromotionUse.objects.create(
            promotion=promotion,
            user=user,
            order_id=order_id,
            discount_amount=discount_amount
        )
        
        # 更新促销活动使用计数
        promotion.used_count += 1
        promotion.save()
        
        # 更新订单金额
        order.discount_amount = discount_amount
        order.save()
        
        return Response({
            "success": True,
            "discount_amount": discount_amount,
            "new_total": order.total_amount - discount_amount,
            "message": "优惠码应用成功"
        }) 