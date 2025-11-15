#!/usr/bin/env python
import os
import sys
import random
import datetime
import django
from decimal import Decimal
from django.utils import timezone
from django.db import transaction

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'iFly.settings')
django.setup()

# 导入模型
from accounts.models import User, Passenger
from flight.models import Flight
from booking.models import Order, Ticket
from notifications.models import Notification
from promotions.models import Promotion, PromotionUse
from points.models import PointsAccount, PointsTransaction, ExchangeItem, PointsTask

# 更新常量定义
CITIES = ['北京', '上海', '广州', '深圳', '成都', '杭州', '西安', '南京', '武汉', '厦门', '长沙', '青岛', '天津', '重庆', '哈尔滨', '昆明', '郑州', '三亚']
AIRLINES = {
    'CA': '中国国际航空',
    'MU': '东方航空',
    'CZ': '南方航空',
    'HU': '海南航空',
    '3U': '四川航空',
    'MF': '厦门航空',
    'ZH': '深圳航空'
}
AIRCRAFT_TYPES = ['波音737', '波音777', '波音787', '空客A320', '空客A330', '空客A350', '国产C919']


def create_test_users():
    """创建测试用户"""
    print("创建测试用户...")
    test_users = []
    
    # 创建普通用户
    for i in range(1, 11):
        username = f'user{i}'
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': f'user{i}@example.com',
                'is_active': True,
                'role': 'user',
                'phone': f'1391234{i:04d}'
            }
        )
        if created:
            user.set_password('password123')
            user.save()
            print(f"创建用户: {username}")
        test_users.append(user)
    
    # 创建管理员用户
    admin, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@example.com',
            'is_active': True,
            'is_staff': True,
            'is_superuser': True,
            'role': 'admin',
            'phone': '13911112222'
        }
    )
    if created:
        admin.set_password('admin123')
        admin.save()
        print("创建管理员: admin")
    test_users.append(admin)
    
    return test_users


def create_test_passengers(users):
    """为用户创建测试乘客信息"""
    print("创建测试乘客信息...")
    test_passengers = []
    
    # 模拟姓名列表
    names = ['张三', '李四', '王五', '赵六', '钱七', '孙八', '周九', '吴十', '刘一', '陈二']
    genders = ['male', 'female']
    
    for user in users:
        # 为每个用户创建1-3个乘客
        num_passengers = random.randint(1, 3)
        for i in range(num_passengers):
            name = random.choice(names)
            gender = random.choice(genders)
            # 生成随机出生日期（18-70岁）
            years_ago = random.randint(18, 70)
            birth_date = timezone.now() - datetime.timedelta(days=365 * years_ago)
            
            # 生成随机身份证号码
            id_card = f"11010120{random.randint(0, 10)}{random.randint(1, 12):02d}{random.randint(1, 28):02d}{random.randint(1000, 9999)}"
            
            passenger, created = Passenger.objects.get_or_create(
                user=user,
                id_card=id_card,
                defaults={
                    'name': name,
                    'gender': gender,
                    'birth_date': birth_date
                }
            )
            
            if created:
                print(f"为用户 {user.username} 创建乘客: {name}")
            
            test_passengers.append(passenger)
    
    return test_passengers


@transaction.atomic
def create_test_flights():
    """创建测试航班数据"""
    print("创建测试航班数据...")
    test_flights = []
    
    # 创建30天内的航班（包括过去和未来的）
    today = timezone.now().date()
    start_date = today - datetime.timedelta(days=5)  # 5天前
    end_date = today + datetime.timedelta(days=30)  # 30天后
    
    # 特定创建北京到上海的航班数据（确保有搜索结果）
    for i in range(10):
        current_date = today + datetime.timedelta(days=i)
        
        # 早上、中午、晚上各安排一班航班
        for hour in [8, 13, 19]:
            airline_code = random.choice(list(AIRLINES.keys()))
            airline_name = AIRLINES[airline_code]
            flight_number = f"{airline_code}{random.randint(1000, 9999)}"
            
            # 随机选择飞机型号
            aircraft_type = random.choice(AIRCRAFT_TYPES)
            
            # 设置起飞时间和到达时间
            minute = random.choice([0, 5, 10, 15, 20, 30, 45, 50])
            departure_time = datetime.datetime.combine(current_date, datetime.time(hour, minute))
            departure_time = timezone.make_aware(departure_time, timezone.get_current_timezone())
            
            # 北京到上海约2小时
            flight_duration = random.randint(110, 140)  # 分钟
            arrival_time = departure_time + datetime.timedelta(minutes=flight_duration)
            
            # 座位设置
            capacity = random.choice([150, 180, 200, 220])
            seat_rows = capacity // 6  # 假设每行6个座位
            seats_per_row = 6
            
            # 随机设置剩余座位数
            available_seats = random.randint(capacity // 4, capacity)
            
            # 设置价格信息
            base_price = random.randint(800, 2500)
            price = Decimal(base_price)
            
            # 部分航班设置折扣
            discount = Decimal(random.choice([1.0, 0.9, 0.85, 0.8]))
            
            # 设置航班状态
            status = 'scheduled'
            
            flight, created = Flight.objects.get_or_create(
                flight_number=flight_number,
                defaults={
                    'airline_name': airline_name,
                    'departure_city': '北京',
                    'arrival_city': '上海',
                    'departure_time': departure_time,
                    'arrival_time': arrival_time,
                    'price': price,
                    'discount': discount,
                    'capacity': capacity,
                    'available_seats': available_seats,
                    'status': status,
                    'aircraft_type': aircraft_type,
                    'seat_rows': seat_rows,
                    'seats_per_row': seats_per_row
                }
            )
            
            if created:
                print(f"创建北京-上海航班: {flight_number} - 日期:{current_date.strftime('%Y-%m-%d')} {hour}:{minute}")
                test_flights.append(flight)
    
    # 创建其他随机航班
    current_date = start_date
    while current_date <= end_date:
        # 每天生成5-8个航班
        num_flights = random.randint(5, 8)
        
        for _ in range(num_flights):
            # 随机选择不同的出发地和目的地
            cities = random.sample(CITIES, 2)
            departure_city, arrival_city = cities[0], cities[1]
            
            # 随机选择航空公司和航班号
            airline_code = random.choice(list(AIRLINES.keys()))
            airline_name = AIRLINES[airline_code]
            flight_number = f"{airline_code}{random.randint(1000, 9999)}"
            
            # 随机选择飞机型号
            aircraft_type = random.choice(AIRCRAFT_TYPES)
            
            # 设置起飞时间和到达时间
            hour = random.randint(6, 22)
            minute = random.choice([0, 15, 30, 45])
            departure_time = datetime.datetime.combine(current_date, datetime.time(hour, minute))
            departure_time = timezone.make_aware(departure_time, timezone.get_current_timezone())
            
            # 飞行时间1-5小时
            flight_duration = random.randint(60, 300)  # 分钟
            arrival_time = departure_time + datetime.timedelta(minutes=flight_duration)
            
            # 座位设置
            capacity = random.choice([120, 150, 180, 200, 250])
            seat_rows = capacity // 6  # 假设每行6个座位
            seats_per_row = 6
            
            # 随机设置剩余座位数
            available_seats = random.randint(0, capacity)
            
            # 设置价格信息
            base_price = random.randint(600, 3500)
            price = Decimal(base_price)
            
            # 部分航班设置折扣
            discount = Decimal(random.choice([1.0, 0.95, 0.9, 0.85, 0.8, 0.75]))
            
            # 设置航班状态
            if current_date < today:
                status = 'departed'
            elif available_seats == 0:
                status = 'full'
            else:
                status = random.choices(['scheduled', 'canceled'], weights=[0.95, 0.05], k=1)[0]
            
            flight, created = Flight.objects.get_or_create(
                flight_number=flight_number,
                defaults={
                    'airline_name': airline_name,
                    'departure_city': departure_city,
                    'arrival_city': arrival_city,
                    'departure_time': departure_time,
                    'arrival_time': arrival_time,
                    'price': price,
                    'discount': discount,
                    'capacity': capacity,
                    'available_seats': available_seats,
                    'status': status,
                    'aircraft_type': aircraft_type,
                    'seat_rows': seat_rows,
                    'seats_per_row': seats_per_row
                }
            )
            
            if created:
                print(f"创建航班: {flight_number} - {departure_city} -> {arrival_city}")
                test_flights.append(flight)
        
        current_date += datetime.timedelta(days=1)
    
    return test_flights


def create_test_orders_tickets(users, flights, passengers):
    """创建测试订单和机票数据"""
    print("创建测试订单和机票数据...")
    test_orders = []
    
    # 确保已有航班
    if not flights:
        flights = Flight.objects.filter(status='scheduled')
    
    # 确保已有乘客
    if not passengers:
        passengers = Passenger.objects.all()
    
    for user in users:
        # 每个用户创建1-3个订单
        num_orders = random.randint(1, 3)
        user_passengers = Passenger.objects.filter(user=user)
        
        if not user_passengers:
            continue
            
        for _ in range(num_orders):
            # 随机选择一个航班
            flight = random.choice(flights)
            
            # 为这个订单选择1-3个乘客
            selected_passengers = random.sample(list(user_passengers), 
                                            min(random.randint(1, 3), len(user_passengers)))
            
            # 生成订单号
            order_number = f"ORD{timezone.now().strftime('%Y%m%d')}{random.randint(1000, 9999)}"
            
            # 计算订单总金额
            total_price = flight.price * flight.discount * len(selected_passengers)
            
            # 确定订单状态
            status = random.choice(['pending', 'paid', 'canceled'])
            
            # 支付时间
            paid_at = None
            if status in ['paid']:
                # 随机生成过去1-24小时内的支付时间
                hours_ago = random.randint(1, 24)
                paid_at = timezone.now() - datetime.timedelta(hours=hours_ago)
            
            # 随机生成联系人信息
            contact_name = random.choice(selected_passengers).name
            contact_phone = f"1{random.randint(3, 9)}8{random.randint(1000, 9999)}{random.randint(1000, 9999)}"
            contact_email = f"{user.username}@example.com"
            
            try:
                order, created = Order.objects.get_or_create(
                    order_number=order_number,
                    defaults={
                        'user': user,
                        'total_price': total_price,
                        'status': status,
                        'paid_at': paid_at,
                        'contact_name': contact_name,
                        'contact_phone': contact_phone,
                        'contact_email': contact_email
                    }
                )
                
                if created:
                    print(f"创建订单: {order_number} - 用户: {user.username} - 状态: {status}")
                    test_orders.append(order)
                
                    # 为每个乘客创建机票
                    for i, passenger in enumerate(selected_passengers):
                        # 生成座位号
                        row = random.randint(1, flight.seat_rows)
                        col = chr(ord('A') + random.randint(0, flight.seats_per_row - 1))
                        seat_number = f"{row}{col}"
                        
                        # 随机选择舱位等级，但大部分是经济舱
                        cabin_class = random.choices(
                            ['economy', 'business', 'first'], 
                            weights=[0.8, 0.15, 0.05], 
                            k=1
                        )[0]
                        
                        # 根据舱位等级调整价格
                        if cabin_class == 'business':
                            price = flight.price * 2.0
                        elif cabin_class == 'first':
                            price = flight.price * 3.5
                        else:
                            price = flight.price
                            
                        # 应用折扣
                        price = price * flight.discount
                        
                        ticket = Ticket.objects.create(
                            order=order,
                            flight=flight,
                            passenger_name=passenger.name,
                            passenger_id_type='身份证',
                            passenger_id_number=passenger.id_card,
                            seat_number=seat_number,
                            cabin_class=cabin_class,
                            price=price,
                            status='valid' if status == 'paid' else 'refunded' if status == 'canceled' else 'valid'
                        )
                        
                        print(f"  - 创建机票: {ticket.ticket_number} - 乘客: {passenger.name} - 座位: {seat_number}")
            except Exception as e:
                print(f"创建订单失败: {str(e)}")
    
    return test_orders


def create_test_notifications(users):
    """创建测试通知"""
    print("创建测试通知...")
    
    notification_templates = [
        {
            'title': '系统升级通知',
            'message': '亲爱的用户，我们将于2025年7月20日凌晨2:00-4:00进行系统升级，期间可能影响部分功能使用。',
            'notif_type': 'info'
        },
        {
            'title': '账户安全提示',
            'message': '我们检测到您的账号有异常登录尝试，请及时修改密码保障账户安全。',
            'notif_type': 'warning'
        },
        {
            'title': '订单状态更新',
            'message': '您的机票订单已出票，请在"我的订单"中查看详情。',
            'notif_type': 'info'
        },
        {
            'title': '积分即将到期',
            'message': '您有积分将于本月底过期，请及时使用。',
            'notif_type': 'warning'
        },
        {
            'title': '航班延误信息',
            'message': '您预订的航班因天气原因延误，预计延误时间约2小时，请合理安排行程。',
            'notif_type': 'alert'
        },
        {
            'title': '优惠活动通知',
            'message': '暑期特惠活动已开启，预订指定航线最低可享7折优惠！',
            'notif_type': 'info'
        },
        {
            'title': '会员等级提升',
            'message': '恭喜您！您的会员等级已升级为金卡会员，可享受更多专属权益。',
            'notif_type': 'info'
        }
    ]
    
    for user in users:
        # 为每个用户创建2-5条通知
        num_notifications = random.randint(2, 5)
        for _ in range(num_notifications):
            template = random.choice(notification_templates)
            is_read = random.choice([True, False])
            
            Notification.objects.create(
                user=user,
                title=template['title'],
                message=template['message'],
                notif_type=template['notif_type'],
                is_read=is_read
            )
            
    print(f"为{len(users)}个用户创建了通知")


def create_test_promotions():
    """创建测试优惠活动"""
    print("创建测试优惠活动...")
    
    promotions = [
        {
            'title': '新用户专享8折',
            'description': '新注册用户首次订票可享8折优惠',
            'promo_code': 'NEWUSER20',
            'discount_type': 'percentage',
            'discount_value': Decimal('0.8'),
            'min_purchase': Decimal('0'),
            'usage_limit': 1
        },
        {
            'title': '暑期特惠',
            'description': '暑期预订机票享受85折优惠',
            'promo_code': 'SUMMER15',
            'discount_type': 'percentage',
            'discount_value': Decimal('0.85'),
            'min_purchase': Decimal('500'),
            'usage_limit': 0
        },
        {
            'title': '满1000减100',
            'description': '订票满1000元立减100元',
            'promo_code': 'MINUS100',
            'discount_type': 'fixed',
            'discount_value': Decimal('100'),
            'min_purchase': Decimal('1000'),
            'usage_limit': 1000
        },
        {
            'title': '金卡用户专享',
            'description': '金卡及以上用户专享额外95折',
            'promo_code': 'GOLD5',
            'discount_type': 'percentage',
            'discount_value': Decimal('0.95'),
            'min_purchase': Decimal('0'),
            'usage_limit': 0
        },
        {
            'title': '周末特惠',
            'description': '周末出行享受特别优惠',
            'promo_code': 'WEEKEND25',
            'discount_type': 'percentage',
            'discount_value': Decimal('0.75'),
            'min_purchase': Decimal('800'),
            'usage_limit': 500
        },
        {
            'title': '亲子游优惠',
            'description': '亲子出行，儿童票额外9折',
            'promo_code': 'FAMILY10',
            'discount_type': 'percentage',
            'discount_value': Decimal('0.9'),
            'min_purchase': Decimal('0'),
            'usage_limit': 0
        }
    ]
    
    now = timezone.now()
    
    for promo_data in promotions:
        # 设置起止时间
        start_date = now - datetime.timedelta(days=random.randint(5, 20))
        end_date = now + datetime.timedelta(days=random.randint(30, 90))
        
        Promotion.objects.get_or_create(
            promo_code=promo_data['promo_code'],
            defaults={
                'title': promo_data['title'],
                'description': promo_data['description'],
                'discount_type': promo_data['discount_type'],
                'discount_value': promo_data['discount_value'],
                'min_purchase': promo_data['min_purchase'],
                'start_date': start_date,
                'end_date': end_date,
                'usage_limit': promo_data['usage_limit'],
                'is_active': True
            }
        )
    
    print(f"创建了{len(promotions)}个优惠活动")


def create_test_points_data(users):
    """创建测试积分数据"""
    print("创建测试积分数据...")
    
    # 创建积分兑换商品
    exchange_items = [
        {
            'name': '星巴克电子券',
            'description': '价值50元的星巴克电子券',
            'points_required': 1000,
            'total_stock': 100,
            'available_stock': 80,
        },
        {
            'name': '机票优惠券',
            'description': '100元机票抵用券',
            'points_required': 2000,
            'total_stock': 500,
            'available_stock': 450,
        },
        {
            'name': 'VIP休息室体验',
            'description': '一次机场VIP休息室体验',
            'points_required': 3000,
            'total_stock': 50,
            'available_stock': 30,
        },
        {
            'name': '行李额外额度',
            'description': '额外10KG托运行李额度',
            'points_required': 1500,
            'total_stock': 200,
            'available_stock': 180,
        },
        {
            'name': '头等舱升级券',
            'description': '经济舱升级头等舱优惠券',
            'points_required': 5000,
            'total_stock': 20,
            'available_stock': 15,
        },
        {
            'name': '专车接送服务',
            'description': '机场专车接送一次',
            'points_required': 2500,
            'total_stock': 50,
            'available_stock': 40,
        }
    ]
    
    # 创建积分任务
    tasks = [
        {
            'title': '每日签到',
            'description': '每日登录APP签到获取积分',
            'points_reward': 10,
            'task_type': 'daily',
        },
        {
            'title': '完善个人资料',
            'description': '完善个人资料获得额外积分',
            'points_reward': 100,
            'task_type': 'onetime',
        },
        {
            'title': '分享航班',
            'description': '分享航班信息到社交媒体',
            'points_reward': 50,
            'task_type': 'weekly',
        },
        {
            'title': '首次购票',
            'description': '首次成功预订机票获得积分奖励',
            'points_reward': 200,
            'task_type': 'onetime',
        },
        {
            'title': '评价航班体验',
            'description': '完成航班体验评价',
            'points_reward': 30,
            'task_type': 'repeatable',
        },
        {
            'title': '生日特别奖励',
            'description': '生日当月登录获得额外积分',
            'points_reward': 500,
            'task_type': 'annual',
        }
    ]
    
    # 创建兑换商品
    for item_data in exchange_items:
        ExchangeItem.objects.get_or_create(
            name=item_data['name'],
            defaults={
                'description': item_data['description'],
                'points_required': item_data['points_required'],
                'total_stock': item_data['total_stock'],
                'available_stock': item_data['available_stock'],
                'is_active': True
            }
        )
    
    # 创建积分任务
    for task_data in tasks:
        PointsTask.objects.get_or_create(
            title=task_data['title'],
            defaults={
                'description': task_data['description'],
                'points_reward': task_data['points_reward'],
                'task_type': task_data['task_type'],
                'is_active': True
            }
        )
    
    # 为用户创建积分账户和交易
    for user in users:
        # 创建积分账户
        account, created = PointsAccount.objects.get_or_create(
            user=user,
            defaults={
                'points_balance': random.randint(0, 5000),
                'lifetime_points': random.randint(5000, 10000),
                'member_level': random.choice(['regular', 'silver', 'gold', 'platinum'])
            }
        )
        
        if created:
            # 创建一些积分交易记录
            transaction_types = ['flight_purchase', 'check_in', 'task_completion', 'promotion', 'exchange']
            for _ in range(random.randint(3, 8)):
                points = random.randint(10, 500) if random.random() > 0.2 else -random.randint(100, 1000)
                trans_type = random.choice(transaction_types)
                
                PointsTransaction.objects.create(
                    account=account,
                    points=points,
                    transaction_type=trans_type,
                    description=f"{trans_type.replace('_', ' ')} - {'获得' if points > 0 else '消费'}{abs(points)}积分",
                    created_at=timezone.now() - datetime.timedelta(days=random.randint(0, 60))
                )
    
    print(f"为{len(users)}个用户创建了积分数据")


def create_all_test_data():
    """创建所有测试数据"""
    print("开始创建测试数据...")
    
    # 创建测试用户
    users = create_test_users()
    
    # 创建乘客信息
    passengers = create_test_passengers(users)
    
    # 创建航班数据
    flights = create_test_flights()
    
    # 创建订单和机票
    orders = create_test_orders_tickets(users, flights, passengers)
    
    # 创建通知
    create_test_notifications(users)
    
    # 创建优惠活动
    create_test_promotions()
    
    # 创建积分数据
    create_test_points_data(users)
    
    print("测试数据创建完成！")


if __name__ == "__main__":
    create_all_test_data() 