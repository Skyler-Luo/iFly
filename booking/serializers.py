from datetime import timedelta
from decimal import Decimal

from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from accounts.models import Passenger  # 导入乘客模型
from flight.models import Flight  # 导入航班模型
from .models import Order, Ticket
from .services import TimeoutService, InventoryService

class TicketSerializer(serializers.ModelSerializer):
    flight_number = serializers.SerializerMethodField()
    departure_city = serializers.SerializerMethodField()
    arrival_city = serializers.SerializerMethodField()
    departure_time = serializers.SerializerMethodField()
    arrival_time = serializers.SerializerMethodField()
    # 添加更多航班相关字段
    airline_name = serializers.SerializerMethodField()
    airline_logo = serializers.SerializerMethodField()
    departure_airport = serializers.SerializerMethodField()
    arrival_airport = serializers.SerializerMethodField()
    duration = serializers.SerializerMethodField()
    flight_status = serializers.SerializerMethodField()
    # 添加前端需要的嵌套字段
    order_number = serializers.SerializerMethodField()
    order_id = serializers.SerializerMethodField()
    flight_info = serializers.SerializerMethodField()
    seat_info = serializers.SerializerMethodField()
    passenger_info = serializers.SerializerMethodField()
    # 前端状态映射
    frontend_status = serializers.SerializerMethodField()

    class Meta:
        model = Ticket
        fields = '__all__'

    def get_flight_number(self, obj):
        return obj.flight.flight_number if obj.flight else None

    def get_departure_city(self, obj):
        return obj.flight.departure_city if obj.flight else None

    def get_arrival_city(self, obj):
        return obj.flight.arrival_city if obj.flight else None

    def get_departure_time(self, obj):
        return obj.flight.departure_time if obj.flight else None

    def get_arrival_time(self, obj):
        return obj.flight.arrival_time if obj.flight else None

    # 添加获取新字段的方法
    def get_airline_name(self, obj):
        return obj.flight.airline_name if obj.flight else "未知航空"

    def get_airline_logo(self, obj):
        # 返回默认LOGO或航空公司LOGO
        return getattr(obj.flight, 'airline_logo', None) or "https://picsum.photos/id/24/40/40"

    def get_departure_airport(self, obj):
        if not obj.flight:
            return None
        # 尝试获取更详细的机场信息
        try:
            return f"{obj.flight.departure_city}机场"
        except:
            return None

    def get_arrival_airport(self, obj):
        if not obj.flight:
            return None
        # 尝试获取更详细的机场信息
        try:
            return f"{obj.flight.arrival_city}机场"
        except:
            return None

    def get_duration(self, obj):
        """计算飞行持续时间（分钟）"""
        if not obj.flight or not obj.flight.departure_time or not obj.flight.arrival_time:
            return 0

        try:
            from datetime import datetime
            departure = obj.flight.departure_time
            arrival = obj.flight.arrival_time
            # 确保处理的是datetime对象
            if isinstance(departure, str):
                departure = datetime.fromisoformat(departure.replace('Z', '+00:00'))
            if isinstance(arrival, str):
                arrival = datetime.fromisoformat(arrival.replace('Z', '+00:00'))

            duration = (arrival - departure).total_seconds() / 60
            return int(duration)
        except Exception as e:
            return 120  # 默认2小时

    def get_flight_status(self, obj):
        """获取航班状态"""
        if not obj.flight:
            return "scheduled"
        return getattr(obj.flight, 'status', 'scheduled')

    def get_order_number(self, obj):
        """获取订单编号"""
        return obj.order.order_number if obj.order else None

    def get_order_id(self, obj):
        """获取订单ID"""
        return obj.order.id if obj.order else None

    def get_flight_info(self, obj):
        """获取航班信息（前端嵌套格式）"""
        if not obj.flight:
            return None
        return {
            'airline': obj.flight.airline_name or '未知航空',
            'flight_number': obj.flight.flight_number,
            'departure_city': obj.flight.departure_city,
            'departure_airport': f"{obj.flight.departure_city}机场",
            'departure_time': obj.flight.departure_time.isoformat() if obj.flight.departure_time else None,
            'arrival_city': obj.flight.arrival_city,
            'arrival_airport': f"{obj.flight.arrival_city}机场",
            'arrival_time': obj.flight.arrival_time.isoformat() if obj.flight.arrival_time else None,
        }

    def get_seat_info(self, obj):
        """获取座位信息（前端嵌套格式）"""
        cabin_class_map = {
            'economy': '经济舱',
            'business': '商务舱',
            'first': '头等舱',
        }
        return {
            'cabin_class': cabin_class_map.get(obj.cabin_class, obj.cabin_class),
            'seat_number': obj.seat_number,
        }

    def get_passenger_info(self, obj):
        """获取乘客信息（前端嵌套格式）"""
        # 对证件号码进行脱敏处理
        id_card = obj.passenger_id_number
        if id_card and len(id_card) > 8:
            id_card = id_card[:4] + '*' * (len(id_card) - 8) + id_card[-4:]
        return {
            'name': obj.passenger_name,
            'id_card': id_card,
        }

    def get_frontend_status(self, obj):
        """获取前端状态"""
        from django.utils import timezone

        # 后端状态到前端状态的映射
        if obj.status == 'refunded':
            return 'REFUNDED'
        elif obj.status == 'used':
            return 'USED'
        elif obj.status == 'valid':
            # 检查是否已过期（航班已起飞）
            if obj.flight and obj.flight.departure_time:
                if obj.flight.departure_time < timezone.now():
                    return 'EXPIRED'
            return 'UNUSED'
        return 'UNUSED'

class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=True)
    # 添加前端期望的字段
    total_amount = serializers.SerializerMethodField(read_only=True)
    order_number = serializers.CharField(read_only=True)
    status = serializers.CharField(read_only=True)
    # 添加剩余支付时间字段
    remaining_time = serializers.SerializerMethodField(read_only=True)
    # 添加乘客列表字段（从机票中提取）
    passengers = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Order
        fields = '__all__'

    def get_total_amount(self, obj):
        # 为了兼容前端，将total_price映射为total_amount
        return obj.total_price
    
    def get_remaining_time(self, obj):
        """
        获取订单剩余支付时间（秒）。
        
        仅对待支付状态的订单返回剩余时间，其他状态返回 0。
        """
        return TimeoutService.get_remaining_time(obj)
    
    def get_passengers(self, obj):
        """
        从订单关联的机票中提取乘客信息列表。
        
        返回去重后的乘客列表，包含姓名、证件类型、证件号码等信息。
        """
        passengers = []
        seen_ids = set()
        
        for ticket in obj.tickets.all():
            # 使用证件号码作为唯一标识去重
            if ticket.passenger_id_number not in seen_ids:
                seen_ids.add(ticket.passenger_id_number)
                # 证件号码脱敏处理
                id_number = ticket.passenger_id_number
                if id_number and len(id_number) > 8:
                    id_number = id_number[:4] + '*' * (len(id_number) - 8) + id_number[-4:]
                
                passengers.append({
                    'id': ticket.id,
                    'name': ticket.passenger_name,
                    'id_type': ticket.passenger_id_type,
                    'id_number': id_number,
                    'phone': None  # 机票模型中没有存储乘客电话
                })
        
        return passengers

class PassengerInfoSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    gender = serializers.CharField(max_length=10, required=False)
    id_type = serializers.CharField(max_length=20, default='身份证')
    id_number = serializers.CharField(max_length=30)
    birth_date = serializers.DateField(required=False, allow_null=True)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    seat_number = serializers.CharField(max_length=10, required=False)  # 前端可能会传递此字段
    
    def validate_id_type(self, value):
        """将前端的 id_type 值转换为后端存储格式"""
        id_type_mapping = {
            'idcard': '身份证',
            'passport': '护照',
            'other': '其他',
            '身份证': '身份证',
            '护照': '护照',
            '其他': '其他',
        }
        return id_type_mapping.get(value, '身份证')

class ContactInfoSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    phone = serializers.CharField(max_length=20)
    email = serializers.EmailField()

class OrderCreateSerializer(serializers.ModelSerializer):
    flight_id = serializers.IntegerField(write_only=True)
    cabin_class = serializers.ChoiceField(choices=['economy', 'business', 'first'], write_only=True)
    seat_numbers = serializers.ListField(
        child=serializers.CharField(max_length=10), 
        write_only=True, 
        required=False,  # 座位号现在是可选的，将在值机时分配
        default=list
    )
    passengers = serializers.ListField(child=PassengerInfoSerializer(), write_only=True)
    contact_info = ContactInfoSerializer(write_only=True)
    payment_method = serializers.CharField(max_length=20, required=False, allow_blank=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2)

    # 添加一个输出字段，返回订单编号
    order_number = serializers.CharField(read_only=True)

    class Meta:
        model = Order
        fields = ['flight_id', 'cabin_class', 'seat_numbers', 'passengers', 'contact_info',
                 'payment_method', 'total_price', 'order_number']

    def create(self, validated_data):
        flight_id = validated_data.pop('flight_id')
        cabin_class = validated_data.pop('cabin_class')
        seat_numbers = validated_data.pop('seat_numbers', [])  # 座位号可选
        passengers_data = validated_data.pop('passengers')
        contact_info = validated_data.pop('contact_info')
        total_price = validated_data.pop('total_price')
        payment_method = validated_data.pop('payment_method', None)
        # 将空字符串转换为 None
        if payment_method == '':
            payment_method = None

        user = self.context['request'].user

        # 检查航班存在
        try:
            flight = Flight.objects.get(id=flight_id)
        except Flight.DoesNotExist:
            raise serializers.ValidationError('航班不存在')

        # 检查航班是否已起飞或已取消
        if flight.status in ['departed', 'canceled']:
            raise serializers.ValidationError('该航班已起飞或已取消，无法预订')
        
        # 检查航班起飞时间是否已过
        if flight.departure_time <= timezone.now():
            raise serializers.ValidationError('该航班已过起飞时间，无法预订')

        # 如果提供了座位号，校验座位数量与乘客数量一致
        if seat_numbers and len(seat_numbers) != len(passengers_data):
            raise serializers.ValidationError('座位数量必须与乘客数量一致')

        with transaction.atomic():
            # 如果提供了座位号，检查每个座位是否可用
            if seat_numbers:
                for seat_number in seat_numbers:
                    if not InventoryService.check_seat_availability(flight, seat_number):
                        raise serializers.ValidationError(f'座位{seat_number}已被占用')
            
            # 使用 InventoryService 预留座位（原子性操作，防止并发超售）
            seat_count = len(passengers_data)
            if not InventoryService.reserve_seats(flight, seat_count):
                raise serializers.ValidationError('航班座位不足')
            
            # 计算支付截止时间（默认 30 分钟）
            expires_at = timezone.now() + timedelta(
                minutes=TimeoutService.ORDER_TIMEOUT_MINUTES
            )
            
            # 创建订单
            order = Order.objects.create(
                user=user,
                total_price=total_price,
                status='pending',
                payment_method=payment_method,
                contact_name=contact_info.get('name'),
                contact_phone=contact_info.get('phone'),
                contact_email=contact_info.get('email'),
                expires_at=expires_at
            )

            # 生成舱位价格
            price_multiplier = Decimal('1.0')
            if cabin_class == 'business':
                price_multiplier = Decimal('2.5')
            elif cabin_class == 'first':
                price_multiplier = Decimal('4.0')

            # 确保flight.discount也是Decimal类型
            discount = Decimal(str(flight.discount))
            base_price = flight.price * price_multiplier * discount

            # 创建机票（座位号可选，将在值机时分配）
            for i, passenger_data in enumerate(passengers_data):
                # 如果提供了座位号则使用，否则留空（值机时分配）
                seat_number = seat_numbers[i] if seat_numbers and i < len(seat_numbers) else None

                Ticket.objects.create(
                    order=order,
                    flight=flight,
                    passenger_name=passenger_data['name'],
                    passenger_id_type=passenger_data['id_type'],
                    passenger_id_number=passenger_data['id_number'],
                    seat_number=seat_number,  # 可以为空
                    cabin_class=cabin_class,
                    price=base_price,
                    status='valid'
                )

        return order


class RescheduleLogSerializer(serializers.ModelSerializer):
    """
    改签记录序列化器。
    
    用于序列化改签记录，包含原机票、新机票、原航班、新航班、差价和手续费等信息。
    """
    
    # 原机票信息
    original_ticket_number = serializers.SerializerMethodField()
    original_passenger_name = serializers.SerializerMethodField()
    
    # 新机票信息
    new_ticket_number = serializers.SerializerMethodField()
    new_seat_number = serializers.SerializerMethodField()
    
    # 原航班信息
    original_flight_number = serializers.SerializerMethodField()
    original_departure_city = serializers.SerializerMethodField()
    original_arrival_city = serializers.SerializerMethodField()
    original_departure_time = serializers.SerializerMethodField()
    
    # 新航班信息
    new_flight_number = serializers.SerializerMethodField()
    new_departure_city = serializers.SerializerMethodField()
    new_arrival_city = serializers.SerializerMethodField()
    new_departure_time = serializers.SerializerMethodField()
    
    class Meta:
        from .models import RescheduleLog
        model = RescheduleLog
        fields = [
            'id',
            'original_ticket', 'original_ticket_number', 'original_passenger_name',
            'new_ticket', 'new_ticket_number', 'new_seat_number',
            'original_flight', 'original_flight_number', 
            'original_departure_city', 'original_arrival_city', 'original_departure_time',
            'new_flight', 'new_flight_number',
            'new_departure_city', 'new_arrival_city', 'new_departure_time',
            'price_difference', 'reschedule_fee', 'created_at'
        ]
        read_only_fields = fields
    
    def get_original_ticket_number(self, obj):
        """获取原机票编号"""
        return obj.original_ticket.ticket_number if obj.original_ticket else None
    
    def get_original_passenger_name(self, obj):
        """获取原机票乘客姓名"""
        return obj.original_ticket.passenger_name if obj.original_ticket else None
    
    def get_new_ticket_number(self, obj):
        """获取新机票编号"""
        return obj.new_ticket.ticket_number if obj.new_ticket else None
    
    def get_new_seat_number(self, obj):
        """获取新机票座位号"""
        return obj.new_ticket.seat_number if obj.new_ticket else None
    
    def get_original_flight_number(self, obj):
        """获取原航班号"""
        return obj.original_flight.flight_number if obj.original_flight else None
    
    def get_original_departure_city(self, obj):
        """获取原航班出发城市"""
        return obj.original_flight.departure_city if obj.original_flight else None
    
    def get_original_arrival_city(self, obj):
        """获取原航班到达城市"""
        return obj.original_flight.arrival_city if obj.original_flight else None
    
    def get_original_departure_time(self, obj):
        """获取原航班起飞时间"""
        return obj.original_flight.departure_time if obj.original_flight else None
    
    def get_new_flight_number(self, obj):
        """获取新航班号"""
        return obj.new_flight.flight_number if obj.new_flight else None
    
    def get_new_departure_city(self, obj):
        """获取新航班出发城市"""
        return obj.new_flight.departure_city if obj.new_flight else None
    
    def get_new_arrival_city(self, obj):
        """获取新航班到达城市"""
        return obj.new_flight.arrival_city if obj.new_flight else None
    
    def get_new_departure_time(self, obj):
        """获取新航班起飞时间"""
        return obj.new_flight.departure_time if obj.new_flight else None
