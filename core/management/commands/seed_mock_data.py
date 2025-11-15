from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db import transaction
from django.conf import settings
from datetime import datetime, timedelta
import random
import os
import base64
from decimal import Decimal

from flight.models import Flight
from booking.models import Order, Ticket
from promotions.models import Promotion
from accounts.models import Passenger
from core.models import City, PopularRoute, WeatherCache

User = get_user_model()

class Command(BaseCommand):
    help = '将前端模拟数据添加到后端数据库'

    def handle(self, *args, **kwargs):
        self.stdout.write('开始添加模拟数据...')
        
        try:
            with transaction.atomic():
                # 创建城市数据
                self.create_cities()
                
                # 创建测试用户（如果不存在）
                self.create_test_users()
                
                # 添加航班数据
                self.create_flights()
                
                # 添加订单数据
                self.create_orders()
                
                # 添加促销活动数据
                self.create_promotions()
                
                # 添加热门航线数据
                self.create_popular_routes()
                
                # 添加城市天气缓存数据
                self.create_weather_cache()
                
            self.stdout.write(self.style.SUCCESS('成功添加所有模拟数据!'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'添加模拟数据失败: {str(e)}'))
    
    def create_cities(self):
        """创建基本城市数据"""
        # 检查是否已有足够的城市数据
        if City.objects.count() >= 10:
            self.stdout.write('城市数据已足够，跳过创建')
            return
            
        # 中国主要城市
        cities_data = [
            {'name': '北京', 'code': 'BJS', 'longitude': Decimal('116.407395'), 'latitude': Decimal('39.904211')},
            {'name': '上海', 'code': 'SHA', 'longitude': Decimal('121.473701'), 'latitude': Decimal('31.230416')},
            {'name': '广州', 'code': 'CAN', 'longitude': Decimal('113.264434'), 'latitude': Decimal('23.129162')},
            {'name': '深圳', 'code': 'SZX', 'longitude': Decimal('114.057868'), 'latitude': Decimal('22.543099')},
            {'name': '成都', 'code': 'CTU', 'longitude': Decimal('104.065735'), 'latitude': Decimal('30.659462')},
            {'name': '杭州', 'code': 'HGH', 'longitude': Decimal('120.209947'), 'latitude': Decimal('30.245853')},
            {'name': '武汉', 'code': 'WUH', 'longitude': Decimal('114.305392'), 'latitude': Decimal('30.593098')},
            {'name': '西安', 'code': 'SIA', 'longitude': Decimal('108.939840'), 'latitude': Decimal('34.341574')},
            {'name': '重庆', 'code': 'CKG', 'longitude': Decimal('106.551556'), 'latitude': Decimal('29.563009')},
            {'name': '南京', 'code': 'NKG', 'longitude': Decimal('118.796877'), 'latitude': Decimal('32.060255')},
            {'name': '厦门', 'code': 'XMN', 'longitude': Decimal('118.089425'), 'latitude': Decimal('24.479833')},
        ]
        
        for city_data in cities_data:
            City.objects.get_or_create(name=city_data['name'], defaults=city_data)
            
        self.stdout.write(self.style.SUCCESS(f'成功创建{len(cities_data)}个城市数据'))
    
    def create_test_users(self):
        """创建测试用户"""
        # 确保管理员用户存在
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                'admin', 
                'admin@example.com', 
                'admin123',
                real_name='管理员',
                phone='13800000000'
            )
            self.stdout.write(self.style.SUCCESS('创建超级用户: admin'))
        
        # 创建普通测试用户
        test_users = [
            {'username': 'test1', 'email': 'test1@example.com', 'password': 'test123', 'real_name': '张三', 'phone': '13812345671'},
            {'username': 'test2', 'email': 'test2@example.com', 'password': 'test123', 'real_name': '李四', 'phone': '13812345672'},
            {'username': 'test3', 'email': 'test3@example.com', 'password': 'test123', 'real_name': '王五', 'phone': '13812345673'},
        ]
        
        for user_data in test_users:
            if not User.objects.filter(username=user_data['username']).exists():
                user = User.objects.create_user(
                    username=user_data['username'],
                    email=user_data['email'],
                    password=user_data['password'],
                    real_name=user_data['real_name'],
                    phone=user_data['phone']
                )
                
                # 为用户添加乘客信息
                id_card = f'11010119900101{random.randint(1000, 9999)}'
                Passenger.objects.create(
                    user=user,
                    name=user_data['real_name'],
                    id_card=id_card,
                    gender='male' if random.random() > 0.5 else 'female',
                    birth_date=timezone.now().date() - timedelta(days=365*30)
                )
                
                self.stdout.write(self.style.SUCCESS(f'创建测试用户: {user_data["username"]}'))
    
    def create_flights(self):
        """创建模拟航班数据"""
        # 检查是否已有足够的航班数据
        if Flight.objects.count() >= 20:
            self.stdout.write('航班数据已足够，跳过创建')
            return
            
        # 航空公司数据
        airlines = [
            {'name': '南方航空', 'code': 'CZ'},
            {'name': '东方航空', 'code': 'MU'},
            {'name': '海南航空', 'code': 'HU'},
            {'name': '中国国航', 'code': 'CA'}
        ]
        
        # 获取所有城市
        cities = list(City.objects.all())
        if len(cities) < 2:
            self.stdout.write(self.style.ERROR('城市数据不足，请先创建城市数据'))
            return
        
        # 飞机型号
        aircraft_types = ['波音737', '空客A320', '波音777', '空客A330']
        
        now = timezone.now()
        
        # 生成20个航班
        for i in range(1, 21):
            airline = random.choice(airlines)
            # 随机选择两个不同的城市
            from_city, to_city = random.sample(cities, 2)
            aircraft = random.choice(aircraft_types)
            
            # 生成航班起飞时间（未来30天内随机时间）
            departure_time = now + timedelta(
                days=random.randint(1, 30),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )
            
            # 飞行时间60-240分钟
            duration_minutes = 60 + random.randint(0, 180)
            arrival_time = departure_time + timedelta(minutes=duration_minutes)
            
            # 价格500-2500
            base_price = Decimal(500 + random.randint(0, 2000))
            discount = Decimal(0.7 + random.random() * 0.3) if random.random() < 0.7 else Decimal(1.0)
            discount = round(discount, 2)
            
            # 座位总数100-200
            capacity = 100 + random.randint(0, 100)
            # 已售出0-50%的座位
            sold_seats = int(capacity * random.random() * 0.5)
            available_seats = capacity - sold_seats
            
            flight_number = f"{airline['code']}{1000 + i}"
            
            Flight.objects.create(
                flight_number=flight_number,
                departure_city=from_city.name,
                arrival_city=to_city.name,
                departure_time=departure_time,
                arrival_time=arrival_time,
                price=base_price,
                discount=discount,
                capacity=capacity,
                available_seats=available_seats,
                status='scheduled',
                aircraft_type=aircraft,
                seat_rows=int(capacity/6),
                seats_per_row=6
            )
            
        self.stdout.write(self.style.SUCCESS(f'创建了20个模拟航班'))
    
    def create_orders(self):
        """创建模拟订单数据"""
        # 检查是否已有足够的订单数据
        if Order.objects.count() >= 10:
            self.stdout.write('订单数据已足够，跳过创建')
            return
            
        # 获取所有用户和航班
        users = User.objects.filter(is_staff=False)
        flights = Flight.objects.all()
        
        if not users or not flights:
            self.stdout.write(self.style.ERROR('没有足够的用户或航班数据来创建订单'))
            return
            
        # 订单状态
        statuses = ['pending', 'paid', 'paid']  # 更多机会创建已支付订单
        
        now = timezone.now()
        
        # 为每个用户创建1-3个订单
        for user in users:
            # 获取该用户的所有乘客
            passengers = Passenger.objects.filter(user=user)
            if not passengers:
                self.stdout.write(f'用户 {user.username} 没有乘客信息，跳过')
                continue
                
            # 为用户创建1-3个订单
            for _ in range(random.randint(1, 3)):
                # 随机选择一个航班和1-3位乘客
                flight = random.choice(flights)
                order_passengers = random.sample(
                    list(passengers), 
                    min(random.randint(1, 3), passengers.count())
                )
                
                # 计算总价
                base_price = flight.price * flight.discount
                total_amount = base_price * len(order_passengers)
                
                # 生成订单号
                order_number = f"ORD{random.randrange(10000000, 99999999)}"
                
                # 随机状态
                status = random.choice(statuses)
                
                # 创建订单
                order_date = now - timedelta(days=random.randint(1, 30))
                paid_date = order_date + timedelta(hours=2) if status == 'paid' else None
                
                order = Order.objects.create(
                    order_number=order_number,
                    user=user,
                    total_amount=total_amount,
                    status=status,
                    payment_method='alipay' if status == 'paid' else None,
                    created_at=order_date,
                    paid_at=paid_date
                )
                
                # 为订单创建机票
                for passenger in order_passengers:
                    # 生成座位号
                    row = random.randint(1, flight.seat_rows)
                    col = random.choice(['A', 'B', 'C', 'D', 'E', 'F'])
                    seat_number = f"{row}{col}"
                    
                    # 生成机票号
                    ticket_number = f"TKT{random.randrange(10000000, 99999999)}"
                    
                    # 创建机票
                    Ticket.objects.create(
                        ticket_number=ticket_number,
                        order=order,
                        flight=flight,
                        passenger=passenger,
                        seat_number=seat_number,
                        price=base_price,
                        status='valid',
                        created_at=order_date
                    )
                    
            self.stdout.write(f'为用户 {user.username} 创建了订单')
                
        self.stdout.write(self.style.SUCCESS('成功创建模拟订单数据'))
    
    def create_promotions(self):
        """创建促销活动数据"""
        # 检查是否已有足够的促销活动
        if Promotion.objects.count() >= 3:
            self.stdout.write('促销活动数据已足够，跳过创建')
            return
            
        # 参考PromotionCarousel.vue中的模拟数据
        promotions_data = [
            {
                'title': '暑假特惠',
                'description': '暑期学生订票享受八折优惠，提前预订立享折上折！',
                'promo_code': 'SUMMER2023',
                'discount_type': 'percentage',
                'discount_value': Decimal('0.8'),
                'start_date': timezone.now() - timedelta(days=10),
                'end_date': timezone.now() + timedelta(days=80)
            },
            {
                'title': '会员福利',
                'description': '新注册会员首单立减100元，老会员专享积分双倍！',
                'promo_code': 'MEMBER100',
                'discount_type': 'fixed',
                'discount_value': Decimal('100.00'),
                'start_date': timezone.now() - timedelta(days=5),
                'end_date': timezone.now() + timedelta(days=30)
            },
            {
                'title': '早鸟计划',
                'description': '提前30天预订国际航班，最高可享7折优惠！',
                'promo_code': 'EARLY30',
                'discount_type': 'percentage',
                'discount_value': Decimal('0.7'),
                'start_date': timezone.now(),
                'end_date': timezone.now() + timedelta(days=180)
            }
        ]
        
        for promo_data in promotions_data:
            Promotion.objects.create(**promo_data)
            
        self.stdout.write(self.style.SUCCESS('成功创建促销活动数据'))
    
    def create_popular_routes(self):
        """创建热门航线数据"""
        # 检查是否已有足够的热门航线
        if PopularRoute.objects.count() >= 6:
            self.stdout.write('热门航线数据已足够，跳过创建')
            return
            
        # 参考PopularRoutes.vue中的模拟数据
        popular_routes_data = [
            { 'from': '北京', 'to': '上海', 'price': 520, 'discount': 0.9, 'popularity': 100 },
            { 'from': '广州', 'to': '北京', 'price': 780, 'discount': 0.85, 'popularity': 90 },
            { 'from': '深圳', 'to': '上海', 'price': 620, 'discount': 0.95, 'popularity': 85 },
            { 'from': '成都', 'to': '广州', 'price': 650, 'discount': 1, 'popularity': 80 },
            { 'from': '杭州', 'to': '厦门', 'price': 450, 'discount': 0.8, 'popularity': 75 },
            { 'from': '西安', 'to': '北京', 'price': 580, 'discount': 0.9, 'popularity': 70 }
        ]
        
        cities = {city.name: city for city in City.objects.all()}
        
        for route_data in popular_routes_data:
            from_city = cities.get(route_data['from'])
            to_city = cities.get(route_data['to'])
            
            if not from_city or not to_city:
                self.stdout.write(self.style.WARNING(f"跳过航线 {route_data['from']} -> {route_data['to']}, 城市不存在"))
                continue
                
            PopularRoute.objects.get_or_create(
                from_city=from_city,
                to_city=to_city,
                defaults={
                    'price': Decimal(route_data['price']),
                    'discount': Decimal(route_data['discount']),
                    'popularity': route_data['popularity']
                }
            )
            
        self.stdout.write(self.style.SUCCESS('成功创建热门航线数据'))
    
    def create_weather_cache(self):
        """创建城市天气缓存数据"""
        # 检查是否已有足够的天气数据
        if WeatherCache.objects.count() >= 5:
            self.stdout.write('天气缓存数据已足够，跳过创建')
            return
            
        # 清除现有数据，确保获取最新天气数据
        WeatherCache.objects.all().delete()
        
        # 为主要城市创建模拟天气数据
        cities = City.objects.all()[:10]  # 限制为前10个城市
        
        # 天气描述
        descriptions = ['晴朗', '多云', '小雨', '阴天', '雷阵雨', '小雪', '雾']
        # 图标代码 (开放天气API的图标代码)
        icons = ['01d', '02d', '03d', '04d', '09d', '10d', '11d', '13d', '50d']
        
        for city in cities:
            # 温度: 5-35度
            temperature = random.randint(5, 35)
            # 湿度: 30-90%
            humidity = random.randint(30, 90)
            # 风速: 0.5-8.5 m/s
            wind_speed = Decimal(0.5 + random.random() * 8).quantize(Decimal('0.1'))
            
            WeatherCache.objects.create(
                city=city,
                temperature=temperature,
                description=random.choice(descriptions),
                humidity=humidity,
                wind_speed=wind_speed,
                icon=f"https://openweathermap.org/img/wn/{random.choice(icons)}@2x.png"
            )
            
        self.stdout.write(self.style.SUCCESS(f'成功创建{cities.count()}个城市的天气数据')) 