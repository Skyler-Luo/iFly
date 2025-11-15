from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Payment
from .serializers import PaymentSerializer
from booking.models import Order
from django.shortcuts import get_object_or_404
from notifications.services import create_payment_notification, create_refund_notification

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Payment.objects.all()
        return Payment.objects.filter(order__user=user)

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def initiate(self, request):
        order_id = request.data.get('order')
        method = request.data.get('method')
        order = get_object_or_404(Order, id=order_id, user=request.user)
        if order.status != 'pending':
            return Response({'detail': '订单状态不可支付'}, status=status.HTTP_400_BAD_REQUEST)
        payment, created = Payment.objects.get_or_create(order=order, defaults={
            'method': method, 'amount': order.total_amount
        })
        # TODO: 对接第三方 SDK 生成支付请求参数
        return Response({'payment_id': payment.id, 'order_number': order.order_number})

    @action(detail=True, methods=['post'], permission_classes=[permissions.AllowAny])
    def callback(self, request, pk=None):
        payment = self.get_object()
        status_str = request.data.get('status')
        tx_id = request.data.get('transaction_id')
        if status_str == 'success':
            payment.status = 'success'
            payment.transaction_id = tx_id
            payment.save()
            order = payment.order
            order.status = 'paid'
            order.paid_at = payment.updated_at
            order.save()
            
            # 创建支付成功通知
            create_payment_notification(order.user, order, 'success')
            
        return Response({'detail': 'callback processed'})

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def refund(self, request, pk=None):
        payment = self.get_object()
        if payment.status != 'success':
            return Response({'detail': '支付未成功，无法退款'}, status=status.HTTP_400_BAD_REQUEST)
        # TODO: 对接退款接口
        payment.status = 'refunded'
        payment.save()
        order = payment.order
        order.status = 'canceled'
        order.save()
        
        # 创建退款成功通知
        refund_amount = payment.amount
        create_refund_notification(order.user, order, 'completed', refund_amount)
        
        return Response({'detail': 'refund done'}) 