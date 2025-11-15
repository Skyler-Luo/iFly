from rest_framework import serializers
from .models import Order, Ticket
from flight.models import Flight  # 导入航班模型
from accounts.models import Passenger  # 导入乘客模型
from django.db import transaction
import uuid  # 用于生成唯一编号
from decimal import Decimal  # 添加Decimal导入

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
            print(f"计算飞行持续时间出错: {e}")
            return 120  # 默认2小时
    
    def get_flight_status(self, obj):
        """获取航班状态"""
        if not obj.flight:
            return "scheduled"
        return getattr(obj.flight, 'status', 'scheduled')

class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=True)
    # 添加前端期望的字段
    total_amount = serializers.SerializerMethodField(read_only=True)
    order_number = serializers.CharField(read_only=True)
    status = serializers.CharField(read_only=True)
    
    class Meta:
        model = Order
        fields = '__all__'
    
    def get_total_amount(self, obj):
        # 为了兼容前端，将total_price映射为total_amount
        return obj.total_price

class PassengerInfoSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    gender = serializers.CharField(max_length=10, required=False) 
    id_type = serializers.CharField(max_length=20, default='身份证')
    id_number = serializers.CharField(max_length=30)
    birth_date = serializers.DateField(required=False)
    phone = serializers.CharField(max_length=20, required=False)

class ContactInfoSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    phone = serializers.CharField(max_length=20)
    email = serializers.EmailField()

class OrderCreateSerializer(serializers.ModelSerializer):
    flight_id = serializers.IntegerField(write_only=True)
    cabin_class = serializers.ChoiceField(choices=['economy', 'business', 'first'], write_only=True)
    seat_numbers = serializers.ListField(child=serializers.CharField(max_length=10), write_only=True)
    passengers = serializers.ListField(child=PassengerInfoSerializer(), write_only=True)
    contact_info = ContactInfoSerializer(write_only=True)
    payment_method = serializers.CharField(max_length=20, required=False)
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
        seat_numbers = validated_data.pop('seat_numbers')
        passengers_data = validated_data.pop('passengers')
        contact_info = validated_data.pop('contact_info')
        total_price = validated_data.pop('total_price')
        payment_method = validated_data.pop('payment_method', None)
        
        user = self.context['request'].user
        
        # 检查航班存在
        try:
            flight = Flight.objects.get(id=flight_id)
        except Flight.DoesNotExist:
            raise serializers.ValidationError('航班不存在')
        
        # 校验座位数量与乘客数量一致
        if len(seat_numbers) != len(passengers_data):
            raise serializers.ValidationError('座位数量必须与乘客数量一致')
        
        with transaction.atomic():
            # 创建订单
            order = Order.objects.create(
                user=user,
                total_price=total_price,
                status='pending',
                payment_method=payment_method,
                contact_name=contact_info.get('name'),
                contact_phone=contact_info.get('phone'),
                contact_email=contact_info.get('email')
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
            
            # 创建机票
            for i, passenger_data in enumerate(passengers_data):
                seat_number = seat_numbers[i]
                
                # 检查座位是否已被占用
                if Ticket.objects.filter(flight=flight, seat_number=seat_number, status='valid').exists():
                    raise serializers.ValidationError(f'座位{seat_number}已被占用')
                
                Ticket.objects.create(
                    order=order,
                    flight=flight,
                    passenger_name=passenger_data['name'],
                    passenger_id_type=passenger_data['id_type'],
                    passenger_id_number=passenger_data['id_number'],
                    seat_number=seat_number,
                    cabin_class=cabin_class,
                    price=base_price,
                    status='valid'
                )
            
            # 更新航班座位数
            flight.available_seats -= len(seat_numbers)
            if flight.available_seats <= 0:
                flight.status = 'full'
            flight.save()
            
        return order 