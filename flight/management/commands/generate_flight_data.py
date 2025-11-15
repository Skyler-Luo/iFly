import random
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from flight.models import Flight
from django.utils import timezone

class Command(BaseCommand):
    help = '生成示例航班数据'

    def add_arguments(self, parser):
        parser.add_argument('count', type=int, help='要生成的航班数量')

    def handle(self, *args, **options):
        count = options['count']
        self.stdout.write(self.style.SUCCESS(f'开始生成 {count} 条航班数据'))

        # 清空已有航班数据（可选）
        if Flight.objects.count() > 0:
            confirm = input("这将删除现有的航班数据，是否继续? (y/n): ")
            if confirm.lower() != 'y':
                self.stdout.write(self.style.WARNING('操作已取消'))
                return
            Flight.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('已清空现有航班数据'))

        # 生成航班数据
        flights_created = 0
        
        # 常见城市和机场
        domestic_cities = [
            '北京', '上海', '广州', '深圳', '成都', '杭州', '西安', '重庆',
            '南京', '武汉', '厦门', '长沙', '青岛', '大连', '沈阳', '哈尔滨'
        ]
        
        international_cities = [
            '纽约', '东京', '伦敦', '巴黎', '悉尼', '迪拜', '新加坡', '曼谷'
        ]
        
        cities = domestic_cities + international_cities
        
        # 航空公司
        airlines = [
            '中国国际航空', '东方航空', '南方航空', '海南航空',
            '四川航空', '厦门航空', '山东航空', '深圳航空'
        ]
        
        # 飞机型号
        aircraft_types = [
            'Boeing 737-800', 'Airbus A320', 'Boeing 787', 'Airbus A330',
            'Boeing 777-300ER', 'Airbus A350', 'Boeing 747-8', 'Airbus A380'
        ]
        
        # 航班状态
        flight_statuses = ['scheduled', 'full', 'departed', 'canceled']
        status_weights = [0.8, 0.1, 0.05, 0.05]  # 80% scheduled, 10% full, 5% departed, 5% canceled
        
        # 生成航班
        for i in range(count):
            # 随机选择不同的出发地和目的地
            departure_city, arrival_city = random.sample(cities, 2)
            
            # 判断是否是国际航班
            is_international = (departure_city in international_cities or arrival_city in international_cities)
            
            # 随机生成起飞时间 (今天和未来一周内)
            days_ahead = random.randint(0, 7)
            departure_time = timezone.now() + timedelta(days=days_ahead)
            
            # 将小时设置为6点到23点之间
            departure_time = departure_time.replace(
                hour=random.randint(6, 23),
                minute=random.choice([0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55]),
                second=0,
                microsecond=0
            )
            
            # 计算飞行时长 (国内1-5小时，国际5-15小时)
            if is_international:
                flight_hours = random.uniform(5, 15)
            else:
                flight_hours = random.uniform(1, 5)
            arrival_time = departure_time + timedelta(hours=flight_hours)
            
            # 随机生成座位数和价格
            capacity = random.choice([180, 200, 240, 280, 320, 380, 420])
            available_seats = int(capacity * random.uniform(0.1, 0.9))  # 10%-90%的座位可用
            
            # 根据是否国际航班设置价格范围
            if is_international:
                price = random.randint(2000, 8000)  # 价格范围2000-8000元
            else:
                price = random.randint(500, 2500)  # 价格范围500-2500元
            
            # 随机生成折扣
            discount = round(random.uniform(0.7, 1.0), 2)  # 70%-100%折扣
            
            # 随机状态
            status = random.choices(flight_statuses, weights=status_weights, k=1)[0]
            
            # 生成唯一的航班号
            while True:
                airline = random.choice(airlines)
                airline_code = airline[:2].upper()
                flight_number = f"{airline_code}{random.randint(1000, 9999)}"
                if not Flight.objects.filter(flight_number=flight_number).exists():
                    break
            
            # 座位布局
            seat_rows = capacity // 6  # 假设每排6个座位
            seats_per_row = 6
            
            # 创建航班
            flight = Flight.objects.create(
                flight_number=flight_number,
                airline_name=airline,
                departure_city=departure_city,
                arrival_city=arrival_city,
                departure_time=departure_time,
                arrival_time=arrival_time,
                price=price,
                discount=discount,
                capacity=capacity,
                available_seats=available_seats,
                status=status,
                aircraft_type=random.choice(aircraft_types),
                seat_rows=seat_rows,
                seats_per_row=seats_per_row,
                is_international=is_international  # 根据城市判断是否为国际航班
            )
            
            flights_created += 1
            if flights_created % 10 == 0:
                self.stdout.write(f"已创建 {flights_created} 条航班记录...")
        
        self.stdout.write(self.style.SUCCESS(f'成功创建 {flights_created} 条航班数据')) 