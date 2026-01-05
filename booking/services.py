"""
订单与机票模块服务层。

本模块包含订单增强功能的核心业务逻辑服务，包括座位库存管理、订单超时处理和改签服务。
"""
from datetime import timedelta
from decimal import Decimal
from typing import Dict, Any

from django.db import transaction
from django.db.models import F, QuerySet
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from flight.models import Flight
from booking.models import Order, Ticket, RescheduleLog


class InventoryService:
    """
    座位库存服务类。
    
    确保座位库存的一致性，防止并发超售问题。
    使用数据库事务和行级锁定来保证原子性操作。
    """
    
    @staticmethod
    @transaction.atomic
    def reserve_seats(flight: Flight, count: int = 1) -> bool:
        """
        预留座位（使用 select_for_update 锁定防止并发超售）。
        
        Args:
            flight: 航班对象
            count: 预留座位数，默认为 1
            
        Returns:
            是否预留成功
            
        Raises:
            ValueError: 当 count 小于等于 0 时
        """
        if count <= 0:
            raise ValueError("预留座位数必须大于 0")
        
        # 使用 select_for_update 锁定航班记录，防止并发修改
        locked_flight = Flight.objects.select_for_update().get(pk=flight.pk)
        
        # 检查是否有足够的可用座位
        if locked_flight.available_seats < count:
            return False
        
        # 扣减可用座位数
        locked_flight.available_seats = F('available_seats') - count
        locked_flight.save(update_fields=['available_seats', 'updated_at'])
        
        # 刷新对象以获取更新后的值
        locked_flight.refresh_from_db()
        
        # 更新航班状态
        InventoryService._update_flight_status(locked_flight)
        
        return True
    
    @staticmethod
    @transaction.atomic
    def release_seats(flight: Flight, count: int = 1) -> bool:
        """
        释放座位。
        
        Args:
            flight: 航班对象
            count: 释放座位数，默认为 1
            
        Returns:
            是否释放成功
            
        Raises:
            ValueError: 当 count 小于等于 0 时
        """
        if count <= 0:
            raise ValueError("释放座位数必须大于 0")
        
        # 使用 select_for_update 锁定航班记录
        locked_flight = Flight.objects.select_for_update().get(pk=flight.pk)
        
        # 计算释放后的座位数，确保不超过总容量
        new_available = min(locked_flight.available_seats + count, locked_flight.capacity)
        
        # 更新可用座位数
        locked_flight.available_seats = new_available
        locked_flight.save(update_fields=['available_seats', 'updated_at'])
        
        # 更新航班状态
        InventoryService._update_flight_status(locked_flight)
        
        return True
    
    @staticmethod
    def check_seat_availability(flight: Flight, seat_number: str) -> bool:
        """
        检查特定座位是否可用。
        
        Args:
            flight: 航班对象
            seat_number: 座位号
            
        Returns:
            座位是否可用
        """
        # 检查航班是否有可用座位
        if flight.available_seats <= 0:
            return False
        
        # 检查该座位是否已被有效机票占用
        is_occupied = Ticket.objects.filter(
            flight=flight,
            seat_number=seat_number,
            status__in=['valid', 'used']
        ).exists()
        
        return not is_occupied
    
    @staticmethod
    def _update_flight_status(flight: Flight) -> None:
        """
        根据可用座位数更新航班状态。
        
        当可用座位数为 0 时，状态更新为 'full'；
        当可用座位数大于 0 且当前状态为 'full' 时，状态恢复为 'scheduled'。
        
        Args:
            flight: 航班对象
        """
        if flight.available_seats <= 0 and flight.status != 'full':
            flight.status = 'full'
            flight.save(update_fields=['status', 'updated_at'])
        elif flight.available_seats > 0 and flight.status == 'full':
            flight.status = 'scheduled'
            flight.save(update_fields=['status', 'updated_at'])


class TimeoutService:
    """
    订单超时服务类。
    
    处理订单超时取消逻辑，包括获取超时订单、取消超时订单、
    处理所有超时订单以及计算剩余支付时间。
    """
    
    ORDER_TIMEOUT_MINUTES = 30
    
    @staticmethod
    def get_expired_orders():
        """
        获取已超时的待支付订单。
        
        Returns:
            超时订单的 QuerySet
        """
        now = timezone.now()
        return Order.objects.filter(
            status='pending',
            expires_at__isnull=False,
            expires_at__lt=now
        )
    
    @staticmethod
    @transaction.atomic
    def cancel_expired_order(order: Order) -> bool:
        """
        取消超时订单。
        
        将订单状态更新为已取消，将关联机票状态更新为已取消，
        并释放被占用的座位。
        
        Args:
            order: 订单对象
            
        Returns:
            是否取消成功
        """
        # 检查订单状态是否为待支付
        if order.status != 'pending':
            return False
        
        # 检查订单是否已超时
        if order.expires_at and order.expires_at > timezone.now():
            return False
        
        # 使用 select_for_update 锁定订单记录
        locked_order = Order.objects.select_for_update().get(pk=order.pk)
        
        # 再次检查状态（防止并发）
        if locked_order.status != 'pending':
            return False
        
        # 获取订单关联的所有有效机票
        tickets = Ticket.objects.filter(order=locked_order, status='valid')
        
        # 按航班分组统计需要释放的座位数
        flight_seat_counts = {}
        for ticket in tickets:
            flight_id = ticket.flight_id
            if flight_id not in flight_seat_counts:
                flight_seat_counts[flight_id] = 0
            flight_seat_counts[flight_id] += 1
        
        # 释放座位
        for flight_id, count in flight_seat_counts.items():
            flight = Flight.objects.get(pk=flight_id)
            InventoryService.release_seats(flight, count)
        
        # 更新机票状态为已取消
        tickets.update(status='canceled')
        
        # 更新订单状态为已取消
        locked_order.status = 'canceled'
        locked_order.save(update_fields=['status'])
        
        return True
    
    @staticmethod
    def process_all_expired_orders() -> dict:
        """
        处理所有超时订单。
        
        Returns:
            {
                'processed': int,  # 成功处理的订单数
                'failed': int,     # 处理失败的订单数
                'errors': list     # 错误信息列表
            }
        """
        result = {
            'processed': 0,
            'failed': 0,
            'errors': []
        }
        
        expired_orders = TimeoutService.get_expired_orders()
        
        for order in expired_orders:
            try:
                success = TimeoutService.cancel_expired_order(order)
                if success:
                    result['processed'] += 1
                else:
                    result['failed'] += 1
                    result['errors'].append(
                        f"订单 {order.order_number} 取消失败：状态不允许"
                    )
            except Exception as e:
                result['failed'] += 1
                result['errors'].append(
                    f"订单 {order.order_number} 取消失败：{str(e)}"
                )
        
        return result
    
    @staticmethod
    def get_remaining_time(order: Order) -> int:
        """
        获取订单剩余支付时间（秒）。
        
        Args:
            order: 订单对象
            
        Returns:
            剩余秒数，已超时返回 0
        """
        # 如果订单不是待支付状态，返回 0
        if order.status != 'pending':
            return 0
        
        # 如果没有设置超时时间，返回 0
        if not order.expires_at:
            return 0
        
        now = timezone.now()
        
        # 如果已超时，返回 0
        if order.expires_at <= now:
            return 0
        
        # 计算剩余时间（秒）
        remaining = (order.expires_at - now).total_seconds()
        return max(0, int(remaining))


class ReschedulingService:
    """
    改签服务类。
    
    处理机票改签的核心业务逻辑，包括获取可改签航班、计算改签费用和执行改签操作。
    """
    
    # 改签手续费率（原票价的百分比）
    RESCHEDULE_FEE_RATE = Decimal('0.05')
    # 起飞前最少改签时间（小时）
    MIN_HOURS_BEFORE_DEPARTURE = 2
    
    @staticmethod
    def get_available_flights(ticket: Ticket) -> QuerySet:
        """
        获取可改签的航班列表。
        
        返回与原航班相同航线、尚未起飞且有可用座位的航班。
        
        Args:
            ticket: 原机票对象
            
        Returns:
            可改签航班的 QuerySet
            
        Raises:
            ValidationError: 当机票状态不允许改签时
        """
        # 检查机票状态是否允许改签
        if ticket.status != 'valid':
            raise ValidationError({
                'code': 'RESCHEDULE_INVALID_STATUS',
                'message': '机票状态不允许改签'
            })
        
        original_flight = ticket.flight
        now = timezone.now()
        
        # 检查原航班是否已起飞
        if original_flight.departure_time <= now:
            raise ValidationError({
                'code': 'RESCHEDULE_FLIGHT_DEPARTED',
                'message': '原航班已起飞，无法改签'
            })
        
        # 检查是否在起飞前 2 小时内
        min_departure_time = now + timedelta(
            hours=ReschedulingService.MIN_HOURS_BEFORE_DEPARTURE
        )
        if original_flight.departure_time <= min_departure_time:
            raise ValidationError({
                'code': 'RESCHEDULE_TIME_LIMIT',
                'message': '起飞前2小时内不可改签'
            })
        
        # 查询可改签航班：相同航线、未起飞、有座位、非原航班
        available_flights = Flight.objects.filter(
            departure_city=original_flight.departure_city,
            arrival_city=original_flight.arrival_city,
            departure_time__gt=min_departure_time,
            status__in=['scheduled'],
            available_seats__gt=0
        ).exclude(
            pk=original_flight.pk
        ).order_by('departure_time')
        
        return available_flights
    
    @staticmethod
    def calculate_reschedule_fee(
        ticket: Ticket,
        target_flight: Flight,
        target_cabin_class: str = None
    ) -> Dict[str, Any]:
        """
        计算改签费用。
        
        Args:
            ticket: 原机票
            target_flight: 目标航班
            target_cabin_class: 目标舱位，默认与原机票相同
            
        Returns:
            {
                'original_price': Decimal,      # 原票价
                'new_price': Decimal,           # 新票价
                'price_difference': Decimal,    # 差价（正数需补，负数可退）
                'reschedule_fee': Decimal,      # 改签手续费
                'total_to_pay': Decimal,        # 需支付总额（差价为正时）
                'refund_amount': Decimal        # 可退金额（差价为负时）
            }
        """
        if target_cabin_class is None:
            target_cabin_class = ticket.cabin_class
        
        # 原票价
        original_price = ticket.price
        
        # 计算新票价（根据舱位等级）
        price_multiplier = Decimal('1.0')
        if target_cabin_class == 'business':
            price_multiplier = Decimal('2.5')
        elif target_cabin_class == 'first':
            price_multiplier = Decimal('4.0')
        
        # 确保 discount 是 Decimal 类型
        discount = Decimal(str(target_flight.discount))
        new_price = target_flight.price * price_multiplier * discount
        
        # 计算差价
        price_difference = new_price - original_price
        
        # 计算改签手续费（基于原票价）
        reschedule_fee = original_price * ReschedulingService.RESCHEDULE_FEE_RATE
        reschedule_fee = reschedule_fee.quantize(Decimal('0.01'))
        
        # 计算需支付金额或可退金额
        if price_difference >= 0:
            # 需补差价
            total_to_pay = price_difference + reschedule_fee
            refund_amount = Decimal('0.00')
        else:
            # 可退差价（扣除手续费）
            total_to_pay = reschedule_fee
            refund_amount = abs(price_difference) - reschedule_fee
            if refund_amount < 0:
                refund_amount = Decimal('0.00')
                total_to_pay = reschedule_fee + price_difference  # 手续费减去可退差价
                if total_to_pay < 0:
                    total_to_pay = Decimal('0.00')
        
        return {
            'original_price': original_price,
            'new_price': new_price.quantize(Decimal('0.01')),
            'price_difference': price_difference.quantize(Decimal('0.01')),
            'reschedule_fee': reschedule_fee,
            'total_to_pay': total_to_pay.quantize(Decimal('0.01')),
            'refund_amount': refund_amount.quantize(Decimal('0.01'))
        }
    
    @staticmethod
    @transaction.atomic
    def execute_reschedule(
        ticket: Ticket,
        target_flight: Flight,
        target_seat: str,
        target_cabin_class: str = None
    ) -> Ticket:
        """
        执行改签操作。
        
        Args:
            ticket: 原机票
            target_flight: 目标航班
            target_seat: 目标座位号
            target_cabin_class: 目标舱位，默认与原机票相同
            
        Returns:
            新机票对象
            
        Raises:
            ValidationError: 改签条件不满足时
        """
        if target_cabin_class is None:
            target_cabin_class = ticket.cabin_class
        
        # 1. 验证原机票状态
        if ticket.status != 'valid':
            raise ValidationError({
                'code': 'RESCHEDULE_INVALID_STATUS',
                'message': '机票状态不允许改签'
            })
        
        original_flight = ticket.flight
        now = timezone.now()
        
        # 2. 检查原航班是否已起飞
        if original_flight.departure_time <= now:
            raise ValidationError({
                'code': 'RESCHEDULE_FLIGHT_DEPARTED',
                'message': '原航班已起飞，无法改签'
            })
        
        # 3. 检查是否在起飞前 2 小时内
        min_departure_time = now + timedelta(
            hours=ReschedulingService.MIN_HOURS_BEFORE_DEPARTURE
        )
        if original_flight.departure_time <= min_departure_time:
            raise ValidationError({
                'code': 'RESCHEDULE_TIME_LIMIT',
                'message': '起飞前2小时内不可改签'
            })
        
        # 4. 检查目标航班是否已起飞
        if target_flight.departure_time <= now:
            raise ValidationError({
                'code': 'RESCHEDULE_FLIGHT_DEPARTED',
                'message': '目标航班已起飞'
            })
        
        # 5. 检查目标航班座位可用性
        if not InventoryService.check_seat_availability(target_flight, target_seat):
            raise ValidationError({
                'code': 'RESCHEDULE_SEAT_TAKEN',
                'message': '目标座位已被占用'
            })
        
        # 6. 检查目标航班是否有可用座位
        if target_flight.available_seats <= 0:
            raise ValidationError({
                'code': 'RESCHEDULE_NO_SEATS',
                'message': '目标航班座位不足'
            })
        
        # 7. 计算改签费用
        fee_info = ReschedulingService.calculate_reschedule_fee(
            ticket, target_flight, target_cabin_class
        )
        
        # 8. 锁定原机票记录
        locked_ticket = Ticket.objects.select_for_update().get(pk=ticket.pk)
        
        # 再次检查状态（防止并发）
        if locked_ticket.status != 'valid':
            raise ValidationError({
                'code': 'RESCHEDULE_INVALID_STATUS',
                'message': '机票状态已变更，请刷新后重试'
            })
        
        # 9. 释放原航班座位
        InventoryService.release_seats(original_flight, 1)
        
        # 10. 预留目标航班座位
        if not InventoryService.reserve_seats(target_flight, 1):
            # 回滚原航班座位释放
            InventoryService.reserve_seats(original_flight, 1)
            raise ValidationError({
                'code': 'RESCHEDULE_NO_SEATS',
                'message': '目标航班座位不足'
            })
        
        # 11. 更新原机票状态为已改签
        locked_ticket.status = 'rescheduled'
        locked_ticket.save(update_fields=['status', 'updated_at'])
        
        # 12. 创建新机票
        new_ticket = Ticket.objects.create(
            order=locked_ticket.order,
            flight=target_flight,
            passenger_name=locked_ticket.passenger_name,
            passenger_id_type=locked_ticket.passenger_id_type,
            passenger_id_number=locked_ticket.passenger_id_number,
            seat_number=target_seat,
            cabin_class=target_cabin_class,
            price=fee_info['new_price'],
            status='valid'
        )
        
        # 13. 创建改签记录
        RescheduleLog.objects.create(
            original_ticket=locked_ticket,
            new_ticket=new_ticket,
            original_flight=original_flight,
            new_flight=target_flight,
            price_difference=fee_info['price_difference'],
            reschedule_fee=fee_info['reschedule_fee']
        )
        
        return new_ticket
