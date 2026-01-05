import logging

from django.db import transaction
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from core.utils import mask_id_number
from flight.serializers import FlightSerializer
from notifications.services import create_order_notification, create_refund_notification
from .filters import OrderFilter, TicketFilter
from .models import Order, Ticket
from .serializers import OrderCreateSerializer, OrderSerializer, TicketSerializer
from .services import ReschedulingService, TimeoutService, InventoryService


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = OrderFilter
    search_fields = ['order_number', 'contact_name']
    ordering_fields = ['created_at', 'total_price']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        return OrderSerializer

    def get_queryset(self):
        user = self.request.user
        # 确保用户已认证，未认证返回空查询集
        if not user.is_authenticated:
            return Order.objects.none()
            
        # 使用select_related和prefetch_related优化查询
        queryset = Order.objects.select_related('user').prefetch_related(
            'tickets__flight'
        )
        
        if hasattr(user, 'role') and user.role == 'admin':
            return queryset
        return queryset.filter(user=user)

    def get_object(self):
        """
        允许通过order_number或ID查询订单
        """
        # 获取URL中的参数(pk)
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        pk = self.kwargs.get(lookup_url_kwarg)
        
        # 尝试通过order_number查询订单
        if isinstance(pk, str) and pk.startswith('ORD'):
            try:
                obj = self.get_queryset().get(order_number=pk)
                self.check_object_permissions(self.request, obj)
                return obj
            except Order.DoesNotExist:
                pass
        
        # 如果通过order_number无法找到，回退到默认行为（通过ID查询）
        return super().get_object()
        
    def list(self, request, *args, **kwargs):
        """
        获取订单列表，添加详细的日志
        """
        logger = logging.getLogger(__name__)
        logger.info(f"用户 {request.user.username} 请求订单列表")
        queryset = self.filter_queryset(self.get_queryset())
        logger.info(f"找到 {queryset.count()} 个订单")
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['patch', 'put'], permission_classes=[permissions.IsAuthenticated])
    def status(self, request, pk=None):
        """
        更新订单状态
        """
        order = self.get_object()
        status_data = request.data.get('status')
        
        if not status_data:
            return Response({'detail': '状态字段必须提供'}, status=status.HTTP_400_BAD_REQUEST)
            
        # 检查状态值是否有效
        valid_statuses = [choice[0] for choice in Order.ORDER_STATUS_CHOICES]
        if status_data not in valid_statuses:
            return Response({'detail': f'无效的状态值。有效值为: {", ".join(valid_statuses)}'}, 
                            status=status.HTTP_400_BAD_REQUEST)
        
        # 根据状态更新相关时间字段
        if status_data == 'paid' and order.status == 'pending':
            order.paid_at = timezone.now()
        
        # 更新订单状态
        order.status = status_data
        order.save()
        
        # 创建通知
        create_order_notification(order.user, order, status_data)
        
        # 返回更新后的订单数据
        serializer = self.get_serializer(order)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def pay(self, request, pk=None):
        order = self.get_object()
        if order.status != 'pending':
            return Response({'detail': '订单状态不允许支付'}, status=status.HTTP_400_BAD_REQUEST)
        order.status = 'paid'
        order.paid_at = timezone.now()
        order.save()
        
        # 创建支付成功通知
        create_order_notification(order.user, order, 'paid')
        
        return Response(self.get_serializer(order).data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def cancel(self, request, pk=None):
        order = self.get_object()
        if order.status not in ['pending', 'paid']:
            return Response({'detail': '订单状态不允许取消'}, status=status.HTTP_400_BAD_REQUEST)
        
        with transaction.atomic():
            order.status = 'canceled'
            order.save()
            
            # 退票并使用 InventoryService 释放座位
            tickets = order.tickets.filter(status='valid')
            
            # 按航班分组统计需要释放的座位数
            flight_seat_counts = {}
            for ticket in tickets:
                flight_id = ticket.flight_id
                if flight_id not in flight_seat_counts:
                    flight_seat_counts[flight_id] = 0
                flight_seat_counts[flight_id] += 1
                ticket.status = 'refunded'
                ticket.save()
            
            # 使用 InventoryService 释放座位（原子性操作）
            from flight.models import Flight
            for flight_id, count in flight_seat_counts.items():
                flight = Flight.objects.get(pk=flight_id)
                InventoryService.release_seats(flight, count)
            
        # 创建订单取消通知
        create_order_notification(order.user, order, 'canceled')
        
        return Response(self.get_serializer(order).data)

    @action(detail=True, methods=['get'], url_path='remaining-time', permission_classes=[permissions.IsAuthenticated])
    def remaining_time(self, request, pk=None):
        """
        获取订单剩余支付时间。
        
        GET /api/bookings/orders/{id}/remaining-time/
        
        返回订单的剩余支付时间（秒），仅对待支付状态的订单有效。
        
        Requirements: 3.7
        """
        order = self.get_object()
        
        remaining_seconds = TimeoutService.get_remaining_time(order)
        
        # 计算分钟和秒
        remaining_minutes = remaining_seconds // 60
        remaining_secs = remaining_seconds % 60
        
        return Response({
            'order_id': order.id,
            'order_number': order.order_number,
            'status': order.status,
            'expires_at': order.expires_at,
            'remaining_time': {
                'total_seconds': remaining_seconds,
                'minutes': remaining_minutes,
                'seconds': remaining_secs,
                'formatted': f'{remaining_minutes:02d}:{remaining_secs:02d}',
            },
            'is_expired': remaining_seconds == 0 and order.status == 'pending',
        })

class TicketViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = TicketFilter
    search_fields = ['passenger_name', 'ticket_number']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        # 使用select_related优化查询
        queryset = Ticket.objects.select_related('order__user', 'flight')
        
        if hasattr(user, 'role') and user.role == 'admin':
            return queryset
        return queryset.filter(order__user=user)

    @action(detail=False, methods=['post'], url_path='search-for-checkin',
            permission_classes=[permissions.AllowAny])
    def search_for_checkin(self, request):
        """
        通过票号和证件号搜索机票（用于值机）。
        
        POST /api/bookings/tickets/search-for-checkin/
        
        请求体:
        {
            "ticket_number": "8881234567890",
            "id_number": "110101199001011234",
            "passenger_name": "张三",  // 可选
            "flight_number": "CA1234"  // 可选
        }
        
        返回机票ID，用于后续值机操作。
        """
        ticket_number = request.data.get('ticket_number')
        id_number = request.data.get('id_number')
        passenger_name = request.data.get('passenger_name')
        flight_number = request.data.get('flight_number')
        
        # 验证必填字段
        if not ticket_number:
            return Response(
                {'detail': '请输入票号'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if not id_number:
            return Response(
                {'detail': '请输入证件号'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 搜索机票
        queryset = Ticket.objects.select_related('flight', 'order')
        
        try:
            ticket = queryset.get(
                ticket_number=ticket_number,
                passenger_id_number=id_number
            )
        except Ticket.DoesNotExist:
            return Response(
                {'detail': '未找到匹配的机票，请检查票号和证件号是否正确'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # 可选：验证乘客姓名
        if passenger_name and ticket.passenger_name != passenger_name:
            return Response(
                {'detail': '乘客姓名不匹配'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 可选：验证航班号
        if flight_number and ticket.flight.flight_number != flight_number:
            return Response(
                {'detail': '航班号不匹配'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 检查机票状态
        if ticket.status != 'valid':
            status_labels = {
                'refunded': '已退票',
                'used': '已使用',
                'rescheduled': '已改签',
                'canceled': '已取消'
            }
            return Response(
                {'detail': f'机票{status_labels.get(ticket.status, "状态异常")}，无法办理值机'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 检查订单状态
        if ticket.order.status != 'paid':
            return Response(
                {'detail': '订单未支付，无法办理值机'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        flight = ticket.flight
        
        return Response({
            'ticket_id': ticket.id,
            'ticket_number': ticket.ticket_number,
            'passenger_name': ticket.passenger_name,
            'flight_number': flight.flight_number,
            'departure_city': flight.departure_city,
            'arrival_city': flight.arrival_city,
            'departure_time': flight.departure_time,
            'checked_in': ticket.checked_in,
            'message': '已找到机票' if not ticket.checked_in else '该机票已完成值机'
        })

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def refund(self, request, pk=None):
        ticket = self.get_object()
        if ticket.status != 'valid':
            return Response({'detail': '机票不可退票'}, status=status.HTTP_400_BAD_REQUEST)
        
        with transaction.atomic():
            # 更新机票状态
            ticket.status = 'refunded'
            ticket.save()
            
            # 使用 InventoryService 释放座位（原子性操作）
            flight = ticket.flight
            InventoryService.release_seats(flight, 1)
            
        # 创建退票通知
        user = ticket.order.user
        order = ticket.order
        create_refund_notification(user, order, 'processing')
        
        return Response(self.get_serializer(ticket).data)

    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def checkin_info(self, request, pk=None):
        """获取值机信息"""
        ticket = self.get_object()
        flight = ticket.flight
        
        # 检查机票状态
        if ticket.status != 'valid':
            return Response(
                {'detail': '机票状态不允许值机', 'status': ticket.status},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 检查是否已值机
        if ticket.checked_in:
            return Response(
                {'detail': '该机票已完成值机', 'checked_in': True},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 计算值机时间窗口（仅用于显示，不做强制限制）
        import datetime
        now = timezone.now()
        checkin_open_time = flight.departure_time - datetime.timedelta(hours=24)
        checkin_close_time = flight.departure_time - datetime.timedelta(hours=1)
        
        # 计算登机口和登机时间
        import random
        gate = f"{random.choice(['A', 'B', 'C', 'D'])}{random.randint(1, 30)}"
        boarding_time = flight.departure_time - datetime.timedelta(minutes=30)
        
        # 获取机场信息
        from core.config.airport_data import get_airport_info
        departure_airport_info = get_airport_info(flight.departure_city)
        arrival_airport_info = get_airport_info(flight.arrival_city)
        
        # 证件号码脱敏：保留前4位和后4位，中间用星号替代，长度保持不变
        masked_id_number = mask_id_number(ticket.passenger_id_number)
        
        return Response({
            'ticket_id': ticket.id,
            'ticket_number': ticket.ticket_number,
            'passenger_name': ticket.passenger_name,
            'passenger_id_number': masked_id_number,
            'flight_id': flight.id,
            'flight_number': flight.flight_number,
            'airline_name': flight.airline_name,
            'departure_city': flight.departure_city,
            'arrival_city': flight.arrival_city,
            'departure_time': flight.departure_time,
            'arrival_time': flight.arrival_time,
            'departure_airport': f"{flight.departure_city}{departure_airport_info['name']}",
            'arrival_airport': f"{flight.arrival_city}{arrival_airport_info['name']}",
            'current_seat': ticket.seat_number,
            'cabin_class': ticket.cabin_class,
            'gate': gate,
            'boarding_time': boarding_time,
            'checked_in': ticket.checked_in,
            'can_change_seat': True,
            'checkin_open_time': checkin_open_time,
            'checkin_close_time': checkin_close_time
        })

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def checkin(self, request, pk=None):
        """办理值机"""
        import datetime
        import random
        import uuid
        
        from core.config.airport_data import get_airport_info
        
        ticket = self.get_object()
        flight = ticket.flight
        
        # 检查机票状态
        if ticket.status != 'valid':
            return Response(
                {'detail': '机票状态不允许值机'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 检查是否已值机
        if ticket.checked_in:
            return Response(
                {'detail': '该机票已完成值机'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 获取新座位号（可选）
        new_seat = request.data.get('seat_number')
        if new_seat:
            # 检查座位是否可用
            existing = Ticket.objects.filter(
                flight=flight,
                seat_number=new_seat,
                status='valid'
            ).exclude(id=ticket.id).exists()
            
            if existing:
                return Response(
                    {'detail': f'座位 {new_seat} 已被占用'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            ticket.seat_number = new_seat
        
        # 生成登机牌编号和登机口
        boarding_pass_number = f"BP{uuid.uuid4().hex[:8].upper()}"
        gate = f"{random.choice(['A', 'B', 'C', 'D'])}{random.randint(1, 30)}"
        boarding_time = flight.departure_time - datetime.timedelta(minutes=30)
        
        # 标记为已值机并保存登机牌信息到数据库
        ticket.checked_in = True
        ticket.checked_in_at = timezone.now()
        ticket.boarding_pass_number = boarding_pass_number
        ticket.gate = gate
        ticket.save()
        
        # 获取机场信息
        departure_airport_info = get_airport_info(flight.departure_city)
        arrival_airport_info = get_airport_info(flight.arrival_city)
        
        # 舱位等级显示名称
        cabin_class_display = ticket.get_cabin_class_display()
        
        return Response({
            'success': True,
            'message': '值机成功',
            'boarding_pass': {
                'boarding_pass_number': boarding_pass_number,
                'ticket_number': ticket.ticket_number,
                'passenger_name': ticket.passenger_name,
                'flight_number': flight.flight_number,
                'airline_name': flight.airline_name,
                'departure_city': flight.departure_city,
                'arrival_city': flight.arrival_city,
                'departure_city_code': departure_airport_info['code'],
                'arrival_city_code': arrival_airport_info['code'],
                'departure_airport': f"{flight.departure_city}{departure_airport_info['name']}",
                'arrival_airport': f"{flight.arrival_city}{arrival_airport_info['name']}",
                'departure_time': flight.departure_time,
                'arrival_time': flight.arrival_time,
                'flight_date': flight.departure_time.strftime('%Y-%m-%d'),
                'seat_number': ticket.seat_number,
                'cabin_class': cabin_class_display,
                'gate': gate,
                'boarding_time': boarding_time,
                'checked_in_at': ticket.checked_in_at
            }
        })

    @action(detail=True, methods=['get'], url_path='boarding-pass', permission_classes=[permissions.IsAuthenticated])
    def boarding_pass(self, request, pk=None):
        """获取已值机机票的登机牌信息"""
        import datetime
        
        from core.config.airport_data import get_airport_info
        
        ticket = self.get_object()
        flight = ticket.flight
        
        # 检查是否已值机
        if not ticket.checked_in:
            return Response(
                {'detail': '该机票尚未办理值机'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 获取机场信息
        departure_airport_info = get_airport_info(flight.departure_city)
        arrival_airport_info = get_airport_info(flight.arrival_city)
        
        # 舱位等级显示名称
        cabin_class_display = ticket.get_cabin_class_display()
        
        # 计算登机时间
        boarding_time = flight.departure_time - datetime.timedelta(minutes=30)
        
        return Response({
            'boarding_pass': {
                'boarding_pass_number': ticket.boarding_pass_number,
                'ticket_number': ticket.ticket_number,
                'passenger_name': ticket.passenger_name,
                'flight_number': flight.flight_number,
                'airline_name': flight.airline_name,
                'departure_city': flight.departure_city,
                'arrival_city': flight.arrival_city,
                'departure_city_code': departure_airport_info['code'],
                'arrival_city_code': arrival_airport_info['code'],
                'departure_airport': f"{flight.departure_city}{departure_airport_info['name']}",
                'arrival_airport': f"{flight.arrival_city}{arrival_airport_info['name']}",
                'departure_time': flight.departure_time,
                'arrival_time': flight.arrival_time,
                'flight_date': flight.departure_time.strftime('%Y-%m-%d'),
                'seat_number': ticket.seat_number,
                'cabin_class': cabin_class_display,
                'gate': ticket.gate,
                'boarding_time': boarding_time,
                'checked_in_at': ticket.checked_in_at
            }
        })

    @action(detail=True, methods=['get'], url_path='available-flights', permission_classes=[permissions.IsAuthenticated])
    def available_flights(self, request, pk=None):
        """
        获取可改签的航班列表。
        
        GET /api/bookings/tickets/{id}/available-flights/
        
        返回与原航班相同航线、尚未起飞且有可用座位的航班列表。
        
        Requirements: 1.1
        """
        ticket = self.get_object()
        
        try:
            available_flights = ReschedulingService.get_available_flights(ticket)
            serializer = FlightSerializer(available_flights, many=True)
            return Response({
                'ticket_id': ticket.id,
                'ticket_number': ticket.ticket_number,
                'original_flight': {
                    'id': ticket.flight.id,
                    'flight_number': ticket.flight.flight_number,
                    'departure_city': ticket.flight.departure_city,
                    'arrival_city': ticket.flight.arrival_city,
                    'departure_time': ticket.flight.departure_time,
                    'arrival_time': ticket.flight.arrival_time,
                },
                'available_flights': serializer.data,
                'count': len(serializer.data)
            })
        except ValidationError as e:
            return Response(
                {'detail': e.detail.get('message', str(e)), 'code': e.detail.get('code', 'VALIDATION_ERROR')},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'], url_path='reschedule/preview', permission_classes=[permissions.IsAuthenticated])
    def reschedule_preview(self, request, pk=None):
        """
        获取改签预览（差价计算）。
        
        POST /api/bookings/tickets/{id}/reschedule/preview/
        
        请求体:
        {
            "target_flight_id": int,       # 目标航班 ID（必填）
            "target_cabin_class": string   # 目标舱位（可选，默认与原机票相同）
        }
        
        返回改签差价信息，包括原票价、新票价、差价、手续费、需支付金额或可退金额。
        
        Requirements: 1.2, 1.3, 1.4
        """
        from flight.models import Flight
        
        ticket = self.get_object()
        
        # 获取请求参数
        target_flight_id = request.data.get('target_flight_id')
        target_cabin_class = request.data.get('target_cabin_class')
        
        # 验证目标航班 ID
        if not target_flight_id:
            return Response(
                {'detail': '目标航班 ID 必须提供', 'code': 'MISSING_TARGET_FLIGHT'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 获取目标航班
        try:
            target_flight = Flight.objects.get(pk=target_flight_id)
        except Flight.DoesNotExist:
            return Response(
                {'detail': '目标航班不存在', 'code': 'TARGET_FLIGHT_NOT_FOUND'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # 验证舱位等级
        valid_cabin_classes = ['economy', 'business', 'first']
        if target_cabin_class and target_cabin_class not in valid_cabin_classes:
            return Response(
                {'detail': f'无效的舱位等级，有效值为: {", ".join(valid_cabin_classes)}', 'code': 'INVALID_CABIN_CLASS'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # 先验证机票是否可改签
            ReschedulingService.get_available_flights(ticket)
            
            # 计算改签费用
            fee_info = ReschedulingService.calculate_reschedule_fee(
                ticket, target_flight, target_cabin_class
            )
            
            # 舱位显示名称映射
            cabin_class_display = {
                'economy': '经济舱',
                'business': '商务舱',
                'first': '头等舱'
            }
            
            return Response({
                'ticket_id': ticket.id,
                'ticket_number': ticket.ticket_number,
                'original_flight': {
                    'id': ticket.flight.id,
                    'flight_number': ticket.flight.flight_number,
                    'departure_city': ticket.flight.departure_city,
                    'arrival_city': ticket.flight.arrival_city,
                    'departure_time': ticket.flight.departure_time,
                    'arrival_time': ticket.flight.arrival_time,
                },
                'target_flight': {
                    'id': target_flight.id,
                    'flight_number': target_flight.flight_number,
                    'departure_city': target_flight.departure_city,
                    'arrival_city': target_flight.arrival_city,
                    'departure_time': target_flight.departure_time,
                    'arrival_time': target_flight.arrival_time,
                    'available_seats': target_flight.available_seats,
                },
                'original_cabin_class': ticket.cabin_class,
                'original_cabin_class_display': cabin_class_display.get(ticket.cabin_class, ticket.cabin_class),
                'target_cabin_class': target_cabin_class or ticket.cabin_class,
                'target_cabin_class_display': cabin_class_display.get(target_cabin_class or ticket.cabin_class, target_cabin_class or ticket.cabin_class),
                'fee_info': {
                    'original_price': str(fee_info['original_price']),
                    'new_price': str(fee_info['new_price']),
                    'price_difference': str(fee_info['price_difference']),
                    'reschedule_fee': str(fee_info['reschedule_fee']),
                    'total_to_pay': str(fee_info['total_to_pay']),
                    'refund_amount': str(fee_info['refund_amount']),
                }
            })
        except ValidationError as e:
            return Response(
                {'detail': e.detail.get('message', str(e)), 'code': e.detail.get('code', 'VALIDATION_ERROR')},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'], url_path='reschedule', permission_classes=[permissions.IsAuthenticated])
    def reschedule(self, request, pk=None):
        """
        执行改签操作。
        
        POST /api/bookings/tickets/{id}/reschedule/
        
        请求体:
        {
            "target_flight_id": int,       # 目标航班 ID（必填）
            "target_seat": string,         # 目标座位号（必填）
            "target_cabin_class": string   # 目标舱位（可选，默认与原机票相同）
        }
        
        执行改签操作，将原机票改签到目标航班的指定座位。
        
        Requirements: 1.5, 1.6, 1.7, 1.8, 1.9
        """
        from flight.models import Flight
        from .serializers import RescheduleLogSerializer
        from .models import RescheduleLog
        
        ticket = self.get_object()
        
        # 获取请求参数
        target_flight_id = request.data.get('target_flight_id')
        target_seat = request.data.get('target_seat')
        target_cabin_class = request.data.get('target_cabin_class')
        
        # 验证目标航班 ID
        if not target_flight_id:
            return Response(
                {'detail': '目标航班 ID 必须提供', 'code': 'MISSING_TARGET_FLIGHT'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 验证目标座位号
        if not target_seat:
            return Response(
                {'detail': '目标座位号必须提供', 'code': 'MISSING_TARGET_SEAT'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 获取目标航班
        try:
            target_flight = Flight.objects.get(pk=target_flight_id)
        except Flight.DoesNotExist:
            return Response(
                {'detail': '目标航班不存在', 'code': 'TARGET_FLIGHT_NOT_FOUND'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # 验证舱位等级
        valid_cabin_classes = ['economy', 'business', 'first']
        if target_cabin_class and target_cabin_class not in valid_cabin_classes:
            return Response(
                {'detail': f'无效的舱位等级，有效值为: {", ".join(valid_cabin_classes)}', 'code': 'INVALID_CABIN_CLASS'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # 执行改签
            new_ticket = ReschedulingService.execute_reschedule(
                ticket, target_flight, target_seat, target_cabin_class
            )
            
            # 获取改签记录
            reschedule_log = RescheduleLog.objects.filter(
                original_ticket=ticket,
                new_ticket=new_ticket
            ).first()
            
            # 舱位显示名称映射
            cabin_class_display = {
                'economy': '经济舱',
                'business': '商务舱',
                'first': '头等舱'
            }
            
            # 发送改签通知
            try:
                from notifications.services import create_reschedule_notification
                create_reschedule_notification(
                    ticket.order.user,
                    ticket.order,
                    ticket,
                    new_ticket
                )
            except Exception:
                # 通知发送失败不影响改签结果
                pass
            
            return Response({
                'success': True,
                'message': '改签成功',
                'original_ticket': {
                    'id': ticket.id,
                    'ticket_number': ticket.ticket_number,
                    'status': ticket.status,
                    'flight_number': ticket.flight.flight_number,
                    'seat_number': ticket.seat_number,
                },
                'new_ticket': {
                    'id': new_ticket.id,
                    'ticket_number': new_ticket.ticket_number,
                    'status': new_ticket.status,
                    'flight_number': new_ticket.flight.flight_number,
                    'departure_city': new_ticket.flight.departure_city,
                    'arrival_city': new_ticket.flight.arrival_city,
                    'departure_time': new_ticket.flight.departure_time,
                    'arrival_time': new_ticket.flight.arrival_time,
                    'seat_number': new_ticket.seat_number,
                    'cabin_class': new_ticket.cabin_class,
                    'cabin_class_display': cabin_class_display.get(new_ticket.cabin_class, new_ticket.cabin_class),
                    'price': str(new_ticket.price),
                    'passenger_name': new_ticket.passenger_name,
                },
                'reschedule_log': RescheduleLogSerializer(reschedule_log).data if reschedule_log else None
            }, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response(
                {'detail': e.detail.get('message', str(e)), 'code': e.detail.get('code', 'VALIDATION_ERROR')},
                status=status.HTTP_400_BAD_REQUEST
            )