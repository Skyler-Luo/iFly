"""航班视图模块，提供航班查询、预订、管理等 API 接口。"""
import logging
from decimal import Decimal

from rest_framework import viewsets, permissions, filters as drf_filters, status
from rest_framework.decorators import action
from rest_framework.response import Response

from booking.models import Ticket
from core.config.airport_data import get_airport_info, get_airline_info
from .filters import FlightFilter
from .models import Flight
from .serializers import FlightSerializer

class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.select_related().prefetch_related('ticket_set')
    serializer_class = FlightSerializer
    filter_backends = [drf_filters.OrderingFilter, drf_filters.SearchFilter]
    filterset_class = FlightFilter
    search_fields = ['flight_number', 'departure_city', 'arrival_city', 'aircraft_type']
    ordering_fields = ['departure_time', 'arrival_time', 'price']
    ordering = ['departure_time']

    def get_permissions(self):
        admin_actions = [
            'create', 'update', 'partial_update', 'destroy',
            'import_csv', 'export_csv', 'depart', 'cancel_flight'
        ]
        if self.action in admin_actions:
            permission_classes = [permissions.IsAdminUser]
        elif self.action in ['book', 'cancel_seat']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]

    @action(detail=False, methods=['get'])
    def search(self, request):
        """搜索航班接口，支持多种过滤条件"""
        from django.utils import timezone
        
        queryset = self.get_queryset()
        
        # 获取查询参数
        departure_city = request.query_params.get('departure_city')
        arrival_city = request.query_params.get('arrival_city')
        departure_date = request.query_params.get('departure_date')
        min_price = request.query_params.get('min_price')
        max_price = request.query_params.get('max_price')
        available_seats = request.query_params.get('available_seats')
        
        # 使用logging替代print
        logger = logging.getLogger(__name__)
        logger.info(f"搜索航班: 出发城市={departure_city}, 到达城市={arrival_city}, 日期={departure_date}")
        
        # 默认只显示未起飞的航班（起飞时间大于当前时间）
        queryset = queryset.filter(departure_time__gt=timezone.now())
        
        # 排除已取消和已起飞的航班
        queryset = queryset.exclude(status__in=['canceled', 'departed'])
        
        # 应用过滤
        if departure_city:
            queryset = queryset.filter(departure_city__icontains=departure_city)
        if arrival_city:
            queryset = queryset.filter(arrival_city__icontains=arrival_city)
        if departure_date:
            # 假设格式为YYYY-MM-DD，查询当天所有航班
            queryset = queryset.filter(departure_time__date=departure_date)
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        if available_seats:
            queryset = queryset.filter(available_seats__gte=available_seats)
            
        # 默认按起飞时间排序
        queryset = queryset.order_by('departure_time')
        
        # 记录查询结果数量
        logger.info(f"查询结果: {queryset.count()}条航班记录")
        
        # 序列化结果
        serializer = self.get_serializer(queryset, many=True)
        
        # 简化返回，不添加任何缓存控制头
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def book(self, request, pk=None):
        flight = self.get_object()
        if flight.available_seats <= 0:
            return Response({'detail': '无剩余座位'}, status=status.HTTP_400_BAD_REQUEST)
        flight.available_seats -= 1
        if flight.available_seats == 0:
            flight.status = 'full'
        flight.save()
        return Response(self.get_serializer(flight).data)

    @action(detail=True, methods=['post'])
    def cancel_seat(self, request, pk=None):
        flight = self.get_object()
        flight.available_seats = min(flight.available_seats + 1, flight.capacity)
        if flight.status == 'full' and flight.available_seats > 0:
            flight.status = 'scheduled'
        flight.save()
        return Response(self.get_serializer(flight).data)

    @action(detail=True, methods=['post'])
    def depart(self, request, pk=None):
        flight = self.get_object()
        flight.status = 'departed'
        flight.save()
        return Response(self.get_serializer(flight).data)

    @action(detail=True, methods=['post'])
    def cancel_flight(self, request, pk=None):
        flight = self.get_object()
        flight.status = 'canceled'
        flight.save()
        return Response(self.get_serializer(flight).data)

    @action(detail=False, methods=['get'])
    def export_csv(self, request):
        import csv
        from django.http import HttpResponse
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="flights.csv"'
        writer = csv.writer(response)
        headers = [
            'flight_number', 'airline_name', 'departure_city', 'arrival_city',
            'departure_time', 'arrival_time', 'price', 'discount',
            'capacity', 'available_seats', 'status', 'aircraft_type'
        ]
        writer.writerow(headers)
        for flight in self.get_queryset():
            writer.writerow([
                flight.flight_number, flight.airline_name,
                flight.departure_city, flight.arrival_city,
                flight.departure_time, flight.arrival_time,
                flight.price, flight.discount,
                flight.capacity, flight.available_seats,
                flight.status, flight.aircraft_type
            ])
        return response

    @action(detail=False, methods=['post'])
    def import_csv(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({'detail': '请上传 CSV 文件'}, status=status.HTTP_400_BAD_REQUEST)
        import csv, io
        decoded = file.read().decode('utf-8')
        reader = csv.DictReader(io.StringIO(decoded))
        created = updated = 0
        for row in reader:
            obj, created_flag = Flight.objects.update_or_create(
                flight_number=row['flight_number'],
                defaults={
                    'airline_name': row.get('airline_name', ''),
                    'departure_city': row['departure_city'],
                    'arrival_city': row['arrival_city'],
                    'departure_time': row['departure_time'],
                    'arrival_time': row['arrival_time'],
                    'price': row['price'],
                    'discount': row.get('discount',1),
                    'capacity': row['capacity'],
                    'available_seats': row.get('available_seats', row['capacity']),
                    'status': row.get('status','scheduled'),
                    'aircraft_type': row['aircraft_type']
                }
            )
            if created_flag:
                created += 1
            else:
                updated += 1
        return Response({'created': created, 'updated': updated})

    @action(detail=True, methods=['get'])
    def seats(self, request, pk=None):
        """返回航班座位布局及占用情况
        
        支持 cabin_class 参数过滤舱位：
        - first: 头等舱，1-3 排
        - business: 商务舱，4-9 排
        - economy: 经济舱，10-30 排（默认）
        """
        flight = self.get_object()
        
        # 确保flight对象存在
        if not flight:
            return Response({'error': '航班不存在'}, status=status.HTTP_404_NOT_FOUND)
            
        rows = flight.seat_rows or 30  # 默认30排
        per_row = flight.seats_per_row or 6  # 默认每排6个座位
        
        # 根据舱位类别确定座位范围
        cabin_class = request.query_params.get('cabin_class', 'economy')
        
        # 定义舱位对应的行范围
        cabin_row_ranges = {
            'first': (1, 3),      # 头等舱 1-3 排
            'business': (4, 9),   # 商务舱 4-9 排
            'economy': (10, 30),  # 经济舱 10-30 排
        }
        
        # 获取舱位对应的行范围，默认为经济舱
        start_row, end_row = cabin_row_ranges.get(cabin_class, cabin_row_ranges['economy'])
        
        # 确保行范围不超过航班实际座位排数
        end_row = min(end_row, rows)
        
        # 获取已占用座位
        occupied_seats = []
        tickets = Ticket.objects.filter(flight=flight, status='valid')
        for ticket in tickets:
            if ticket.seat_number:
                occupied_seats.append(ticket.seat_number)
                
        # 构建座位图（仅包含指定舱位的行）
        seat_map = []
        for r in range(start_row, end_row + 1):
            row_list = []
            for c in range(per_row):
                seat = f"{r}{chr(ord('A')+c)}"
                taken = seat in occupied_seats
                row_list.append({'seat': seat, 'taken': taken})
            seat_map.append(row_list)
        
        # 过滤出当前舱位范围内的已占用座位
        cabin_occupied_seats = [
            seat for seat in occupied_seats 
            if self._get_seat_row(seat) >= start_row and self._get_seat_row(seat) <= end_row
        ]
            
        # 返回前端需要的格式
        return Response({
            'flight_id': flight.id,
            'seat_map': seat_map,
            'occupied_seats': cabin_occupied_seats,
            'cabin_class': cabin_class,
            'rows': end_row - start_row + 1,
            'columns': per_row,
            'start_row': start_row,
            'end_row': end_row
        })
    
    def _get_seat_row(self, seat_number: str) -> int:
        """从座位号中提取行号，如 '12A' -> 12"""
        row_str = ''.join(filter(str.isdigit, seat_number))
        return int(row_str) if row_str else 0

    @action(detail=True, methods=['get'])
    def fare(self, request, pk=None):
        """返回航班票价信息，包括各种舱位和折扣"""
        flight = self.get_object()
        base_price = flight.price
        
        # 获取参数
        passengers = int(request.query_params.get('passengers', 1))
        cabin_class = request.query_params.get('cabin_class', 'economy')  # 默认经济舱
        
        # 根据舱位计算价格调整
        cabin_multiplier = Decimal('1.0')  # 默认经济舱倍数
        if cabin_class == 'business':
            cabin_multiplier = Decimal('2.0')
        elif cabin_class == 'first_class':
            cabin_multiplier = Decimal('4.0')
            
        # 确保discount是Decimal类型
        discount = Decimal(str(flight.discount))
        
        # 计算票价
        fare_per_person = base_price * cabin_multiplier * discount
        total_fare = fare_per_person * Decimal(str(passengers))
        
        return Response({
            'base_price': base_price,
            'cabin_class': cabin_class,
            'cabin_multiplier': cabin_multiplier,
            'discount': discount,
            'fare_per_person': fare_per_person,
            'passengers': passengers,
            'total_fare': total_fare,
            'currency': 'CNY'  # 假设使用人民币
        })

    @action(detail=True, methods=['get'])
    def booking_info(self, request, pk=None):
        """返回航班预订详细信息，包括机场、时间、飞行距离等详细信息"""
        flight = self.get_object()
        
        # 获取参数
        cabin_class = request.query_params.get('cabin_class', 'economy')
        
        # 计算飞行时长（分钟）
        duration_minutes = int((flight.arrival_time - flight.departure_time).total_seconds() / 60)
        
        # 计算对应舱位的票价
        cabin_multiplier = 1.0
        if cabin_class == 'business':
            cabin_multiplier = 2.5
        elif cabin_class == 'first':
            cabin_multiplier = 4.0
        
        cabin_price = float(flight.price) * cabin_multiplier
        
        # 使用配置文件获取机场信息
        departure_info = get_airport_info(flight.departure_city)
        arrival_info = get_airport_info(flight.arrival_city)
        
        airport_info = {
            'departure': {
                'name': departure_info['name'],
                'code': departure_info['code'],
                'terminal': departure_info['terminal'],
                'city': flight.departure_city
            },
            'arrival': {
                'name': arrival_info['name'],
                'code': arrival_info['code'],
                'terminal': arrival_info['terminal'],
                'city': flight.arrival_city
            }
        }
        
        # 使用配置文件获取航空公司信息
        airline_info = get_airline_info(flight.airline_name)
        airline_logo = airline_info['logo_url']
        
        # 返回详细信息，确保与前端期望的格式一致
        return Response({
            # 基本信息 - 确保ID字段存在
            'id': flight.id,
            'flightNumber': flight.flight_number,
            'flight_number': flight.flight_number,  # 兼容两种命名格式
            
            # 航空公司信息
            'airlineName': flight.airline_name,
            'airline_name': flight.airline_name,
            'airlineLogo': airline_logo,
            'airline_logo': airline_logo,
            
            # 城市信息
            'departureCity': flight.departure_city,
            'departure_city': flight.departure_city,
            'arrivalCity': flight.arrival_city,
            'arrival_city': flight.arrival_city,
            
            # 时间信息
            'departureTime': flight.departure_time,
            'departure_time': flight.departure_time,
            'arrivalTime': flight.arrival_time,
            'arrival_time': flight.arrival_time,
            'duration': duration_minutes,
            
            # 价格信息
            'price': float(flight.price),
            'cabinPrice': cabin_price,
            'cabin_price': cabin_price,
            'discount': float(flight.discount),
            
            # 座位信息
            'availableSeats': flight.available_seats,
            'available_seats': flight.available_seats,
            
            # 航班信息
            'aircraft': flight.aircraft_type,
            'status': flight.status,
            
            # 机场详细信息
            'airports': airport_info,
            
            # 额外信息
            'baggageAllowance': flight.baggage_allowance,
            'baggage_allowance': flight.baggage_allowance,
            'mealService': flight.meal_service,
            'meal_service': flight.meal_service,
            'wifi': flight.aircraft_type in ['Boeing 787', 'Airbus A350'],  # 是否有WiFi
            'entertainment': flight.aircraft_type not in ['Boeing 737', 'Airbus A320'],  # 是否有娱乐系统
            'powerOutlets': True,  # 是否有电源插座
            'power_outlets': True,
            'seatPitch': 31 if cabin_class == 'economy' else (38 if cabin_class == 'business' else 45),  # 座椅间距
            'seat_pitch': 31 if cabin_class == 'economy' else (38 if cabin_class == 'business' else 45),
            
            # 当前查询的舱位类型
            'cabinClass': cabin_class,
            'cabin_class': cabin_class
        })
