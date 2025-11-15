import random
from django.core.management.base import BaseCommand
from flight.models import Flight
from booking.models import Ticket, Order
from accounts.models import User
import string
from decimal import Decimal

class Command(BaseCommand):
    help = '为航班生成随机座位占用数据'

    def add_arguments(self, parser):
        parser.add_argument('--flight_id', type=int, help='要生成座位数据的航班ID，不指定则为所有航班生成数据')
        parser.add_argument('--occupation_rate', type=float, default=0.4, help='座位占用率，默认40%')

    def handle(self, *args, **options):
        flight_id = options.get('flight_id')
        occupation_rate = options.get('occupation_rate')
        
        if flight_id:
            flights = Flight.objects.filter(id=flight_id)
            if not flights.exists():
                self.stdout.write(self.style.ERROR(f'找不到ID为{flight_id}的航班'))
                return
        else:
            flights = Flight.objects.filter(status='scheduled')
        
        self.stdout.write(self.style.SUCCESS(f'开始为{flights.count()}个航班生成座位数据，占用率: {occupation_rate * 100}%'))
        
        # 确保至少有一个用户
        if User.objects.count() == 0:
            User.objects.create_user(username='test_user', password='password', email='test@example.com')
        
        test_user = User.objects.first()
        
        # 清除现有座位数据
        if Ticket.objects.count() > 0:
            confirm = input("这将删除现有的所有机票和座位数据，是否继续? (y/n): ")
            if confirm.lower() != 'y':
                self.stdout.write(self.style.WARNING('操作已取消'))
                return
            Ticket.objects.all().delete()
            Order.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('已清空现有座位数据'))
        
        # 座位类型和价格倍数
        cabin_classes = {
            'economy': {'rows': (11, 30), 'price_multiplier': 1.0},
            'business': {'rows': (6, 10), 'price_multiplier': 2.5},
            'first': {'rows': (1, 5), 'price_multiplier': 4.0}
        }
        
        total_tickets = 0
        total_orders = 0
        
        # 为每个航班生成座位数据
        for flight in flights:
            # 创建一个订单
            order = Order.objects.create(
                user=test_user,
                status='completed',
                total_price=0,
                created_at=flight.created_at,
                order_number='ORD' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            )
            
            total_orders += 1
            order_total = 0
            flight_tickets = 0
            seat_columns = ['A', 'B', 'C', 'D', 'E', 'F']
            
            # 为每种舱位类型生成座位
            for cabin_class, config in cabin_classes.items():
                row_start, row_end = config['rows']
                rows = list(range(row_start, row_end + 1))
                total_seats = len(rows) * len(seat_columns)
                occupied_count = int(total_seats * occupation_rate)
                
                # 随机选择要占用的座位
                occupied_positions = random.sample(range(total_seats), occupied_count)
                
                # 生成票
                for pos in occupied_positions:
                    row_idx = pos // len(seat_columns)
                    col_idx = pos % len(seat_columns)
                    
                    if row_idx >= len(rows):
                        continue
                    
                    row = rows[row_idx]
                    col = seat_columns[col_idx]
                    seat_number = f"{row}{col}"
                    
                    # 计算票价
                    price = flight.price * Decimal(str(config['price_multiplier']))
                    
                    # 创建票
                    ticket = Ticket.objects.create(
                        order=order,
                        flight=flight,
                        passenger_name=f"乘客{total_tickets + 1}",
                        passenger_id_type='身份证',
                        passenger_id_number=f"1{random.randint(10000000, 99999999)}",
                        seat_number=seat_number,
                        cabin_class=cabin_class,
                        price=price,
                        status='valid'
                    )
                    
                    total_tickets += 1
                    flight_tickets += 1
                    order_total += price
            
            # 更新订单总价
            order.total_price = order_total
            order.save()
            
            # 使用航班特定的票数更新航班已用座位数
            flight.available_seats = flight.capacity - flight_tickets
            flight.save()
            
            self.stdout.write(f"已为航班 {flight.flight_number} 生成 {flight_tickets} 张机票")
        
        self.stdout.write(self.style.SUCCESS(f"总共生成 {total_orders} 个订单, {total_tickets} 张机票")) 