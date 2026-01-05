#!/usr/bin/env python
"""
iFly 测试数据生成脚本

生成测试用户、乘客、航班、订单、机票、改签记录和通知数据。
包含历史数据以支持趋势图表展示，数据分布更加真实。
"""
import os
import random
import datetime
import uuid
from decimal import Decimal

import django
from django.utils import timezone
from django.db import transaction

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'iFly.settings')
django.setup()

# 导入核心模型
from accounts.models import User, Passenger
from flight.models import Flight
from booking.models import Order, Ticket, RescheduleLog
from notifications.models import Notification

# ============ 常量定义 ============

# 城市与机场代码映射
CITY_AIRPORTS = {
    '北京': {'code': 'PEK', 'name': '首都国际机场'},
    '北京大兴': {'code': 'PKX', 'name': '大兴国际机场'},
    '上海虹桥': {'code': 'SHA', 'name': '虹桥国际机场'},
    '上海浦东': {'code': 'PVG', 'name': '浦东国际机场'},
    '广州': {'code': 'CAN', 'name': '白云国际机场'},
    '深圳': {'code': 'SZX', 'name': '宝安国际机场'},
    '成都': {'code': 'CTU', 'name': '双流国际机场'},
    '成都天府': {'code': 'TFU', 'name': '天府国际机场'},
    '杭州': {'code': 'HGH', 'name': '萧山国际机场'},
    '西安': {'code': 'XIY', 'name': '咸阳国际机场'},
    '南京': {'code': 'NKG', 'name': '禄口国际机场'},
    '武汉': {'code': 'WUH', 'name': '天河国际机场'},
    '厦门': {'code': 'XMN', 'name': '高崎国际机场'},
    '长沙': {'code': 'CSX', 'name': '黄花国际机场'},
    '青岛': {'code': 'TAO', 'name': '胶东国际机场'},
    '天津': {'code': 'TSN', 'name': '滨海国际机场'},
    '重庆': {'code': 'CKG', 'name': '江北国际机场'},
    '哈尔滨': {'code': 'HRB', 'name': '太平国际机场'},
    '昆明': {'code': 'KMG', 'name': '长水国际机场'},
    '三亚': {'code': 'SYX', 'name': '凤凰国际机场'},
    '大连': {'code': 'DLC', 'name': '周水子国际机场'},
    '郑州': {'code': 'CGO', 'name': '新郑国际机场'},
    '沈阳': {'code': 'SHE', 'name': '桃仙国际机场'},
    '海口': {'code': 'HAK', 'name': '美兰国际机场'},
    '贵阳': {'code': 'KWE', 'name': '龙洞堡国际机场'},
    '乌鲁木齐': {'code': 'URC', 'name': '地窝堡国际机场'},
    '兰州': {'code': 'LHW', 'name': '中川国际机场'},
    '拉萨': {'code': 'LXA', 'name': '贡嘎机场'},
}

CITIES = list(CITY_AIRPORTS.keys())

INTERNATIONAL_CITIES = {
    '东京成田': {'code': 'NRT', 'country': '日本'},
    '东京羽田': {'code': 'HND', 'country': '日本'},
    '大阪': {'code': 'KIX', 'country': '日本'},
    '首尔仁川': {'code': 'ICN', 'country': '韩国'},
    '新加坡': {'code': 'SIN', 'country': '新加坡'},
    '曼谷': {'code': 'BKK', 'country': '泰国'},
    '吉隆坡': {'code': 'KUL', 'country': '马来西亚'},
    '悉尼': {'code': 'SYD', 'country': '澳大利亚'},
    '墨尔本': {'code': 'MEL', 'country': '澳大利亚'},
    '洛杉矶': {'code': 'LAX', 'country': '美国'},
    '纽约': {'code': 'JFK', 'country': '美国'},
    '旧金山': {'code': 'SFO', 'country': '美国'},
    '伦敦': {'code': 'LHR', 'country': '英国'},
    '巴黎': {'code': 'CDG', 'country': '法国'},
    '迪拜': {'code': 'DXB', 'country': '阿联酋'},
    '法兰克福': {'code': 'FRA', 'country': '德国'},
    '温哥华': {'code': 'YVR', 'country': '加拿大'},
    '多伦多': {'code': 'YYZ', 'country': '加拿大'},
}

# 航空公司详细信息
AIRLINES = {
    'CA': {'name': '中国国际航空', 'alliance': '星空联盟', 'hub': '北京'},
    'MU': {'name': '东方航空', 'alliance': '天合联盟', 'hub': '上海浦东'},
    'CZ': {'name': '南方航空', 'alliance': '天合联盟', 'hub': '广州'},
    'HU': {'name': '海南航空', 'alliance': '无', 'hub': '海口'},
    '3U': {'name': '四川航空', 'alliance': '无', 'hub': '成都'},
    'MF': {'name': '厦门航空', 'alliance': '天合联盟', 'hub': '厦门'},
    'ZH': {'name': '深圳航空', 'alliance': '星空联盟', 'hub': '深圳'},
    'SC': {'name': '山东航空', 'alliance': '无', 'hub': '青岛'},
    'FM': {'name': '上海航空', 'alliance': '天合联盟', 'hub': '上海虹桥'},
    'GS': {'name': '天津航空', 'alliance': '无', 'hub': '天津'},
    'KN': {'name': '联合航空', 'alliance': '无', 'hub': '北京'},
    '9C': {'name': '春秋航空', 'alliance': '无', 'hub': '上海浦东'},  # 廉价航空
    'G5': {'name': '华夏航空', 'alliance': '无', 'hub': '重庆'},
}

# 飞机型号与配置
AIRCRAFT_TYPES = {
    '波音737-800': {'capacity': 162, 'rows': 27, 'seats_per_row': 6, 'range': 'short'},
    '波音737 MAX 8': {'capacity': 178, 'rows': 30, 'seats_per_row': 6, 'range': 'short'},
    '波音777-300ER': {'capacity': 396, 'rows': 44, 'seats_per_row': 9, 'range': 'long'},
    '波音787-9': {'capacity': 290, 'rows': 36, 'seats_per_row': 8, 'range': 'long'},
    '空客A320neo': {'capacity': 165, 'rows': 28, 'seats_per_row': 6, 'range': 'short'},
    '空客A321neo': {'capacity': 195, 'rows': 33, 'seats_per_row': 6, 'range': 'medium'},
    '空客A330-300': {'capacity': 292, 'rows': 36, 'seats_per_row': 8, 'range': 'long'},
    '空客A350-900': {'capacity': 314, 'rows': 40, 'seats_per_row': 8, 'range': 'long'},
    '国产C919': {'capacity': 158, 'rows': 26, 'seats_per_row': 6, 'range': 'short'},
    '国产ARJ21': {'capacity': 90, 'rows': 18, 'seats_per_row': 5, 'range': 'short'},
}

# 更真实的中国姓名库
SURNAMES = ['王', '李', '张', '刘', '陈', '杨', '黄', '赵', '周', '吴',
            '徐', '孙', '马', '朱', '胡', '郭', '何', '林', '高', '罗',
            '郑', '梁', '谢', '宋', '唐', '许', '邓', '冯', '韩', '曹']

MALE_NAMES = ['伟', '强', '磊', '军', '勇', '杰', '涛', '明', '超', '华',
              '刚', '平', '辉', '鹏', '飞', '波', '斌', '宇', '浩', '凯',
              '俊', '健', '峰', '龙', '威', '彬', '博', '毅', '翔', '鑫']

FEMALE_NAMES = ['芳', '娟', '敏', '静', '丽', '艳', '红', '玲', '霞', '燕',
                '秀', '英', '华', '慧', '萍', '婷', '雪', '琳', '晶', '倩',
                '颖', '洁', '蕾', '欣', '薇', '莉', '娜', '琴', '露', '瑶']

# 省份与城市
PROVINCES = {
    '北京市': ['北京'],
    '上海市': ['上海'],
    '广东省': ['广州', '深圳', '东莞', '佛山', '珠海'],
    '江苏省': ['南京', '苏州', '无锡', '常州', '南通'],
    '浙江省': ['杭州', '宁波', '温州', '嘉兴', '绍兴'],
    '四川省': ['成都', '绵阳', '德阳', '宜宾', '泸州'],
    '湖北省': ['武汉', '宜昌', '襄阳', '荆州', '黄石'],
    '山东省': ['济南', '青岛', '烟台', '潍坊', '临沂'],
    '河南省': ['郑州', '洛阳', '开封', '新乡', '安阳'],
    '陕西省': ['西安', '咸阳', '宝鸡', '渭南', '汉中'],
    '辽宁省': ['沈阳', '大连', '鞍山', '抚顺', '本溪'],
    '湖南省': ['长沙', '株洲', '湘潭', '衡阳', '岳阳'],
    '福建省': ['福州', '厦门', '泉州', '漳州', '莆田'],
    '重庆市': ['重庆'],
    '天津市': ['天津'],
    '云南省': ['昆明', '大理', '丽江', '曲靖', '玉溪'],
    '海南省': ['海口', '三亚', '儋州', '琼海'],
}

PAYMENT_METHODS = ['alipay', 'wechat', 'credit_card', 'debit_card', 'unionpay']

# 登机口
GATES = ['A1', 'A2', 'A3', 'A4', 'A5', 'B1', 'B2', 'B3', 'B4', 'B5',
         'C1', 'C2', 'C3', 'C4', 'C5', 'D1', 'D2', 'D3', 'D4', 'D5',
         'E1', 'E2', 'E3', 'E4', 'E5', 'F1', 'F2', 'F3', 'F4', 'F5']


# ============ 工具函数 ============

def generate_name(gender='male'):
    """生成真实的中文姓名"""
    surname = random.choice(SURNAMES)
    if gender == 'male':
        given_name = random.choice(MALE_NAMES)
        # 有时候用两个字的名
        if random.random() < 0.3:
            given_name += random.choice(MALE_NAMES)
    else:
        given_name = random.choice(FEMALE_NAMES)
        if random.random() < 0.3:
            given_name += random.choice(FEMALE_NAMES)
    return surname + given_name


def generate_id_card(birth_date, gender='male'):
    """生成符合规则的身份证号"""
    # 地区码（北京、上海、广东等常见地区）
    area_codes = ['110101', '310101', '440106', '330102', '510104',
                  '320102', '420102', '370102', '610102', '500101']
    area = random.choice(area_codes)
    
    # 出生日期
    birth_str = birth_date.strftime('%Y%m%d')
    
    # 顺序码（奇数为男，偶数为女）
    seq = random.randint(0, 99)
    if gender == 'male':
        seq_code = f"{seq:02d}{random.choice([1, 3, 5, 7, 9])}"
    else:
        seq_code = f"{seq:02d}{random.choice([0, 2, 4, 6, 8])}"
    
    # 前17位
    id_17 = area + birth_str + seq_code
    
    # 计算校验码
    weights = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
    check_codes = '10X98765432'
    total = sum(int(id_17[i]) * weights[i] for i in range(17))
    check_code = check_codes[total % 11]
    
    return id_17 + check_code


def generate_phone():
    """生成真实的手机号"""
    prefixes = ['130', '131', '132', '133', '134', '135', '136', '137', '138', '139',
                '150', '151', '152', '153', '155', '156', '157', '158', '159',
                '170', '171', '172', '173', '175', '176', '177', '178',
                '180', '181', '182', '183', '184', '185', '186', '187', '188', '189',
                '191', '193', '195', '196', '197', '198', '199']
    return random.choice(prefixes) + ''.join([str(random.randint(0, 9)) for _ in range(8)])


def generate_address():
    """生成真实的地址"""
    province = random.choice(list(PROVINCES.keys()))
    city = random.choice(PROVINCES[province])
    districts = ['朝阳区', '海淀区', '西城区', '东城区', '丰台区', '浦东新区', '徐汇区',
                 '天河区', '越秀区', '福田区', '南山区', '武侯区', '锦江区', '西湖区']
    streets = ['中山路', '人民路', '解放路', '建设路', '和平路', '文化路', '科技路',
               '学院路', '长安街', '南京路', '淮海路', '北京路', '广州大道']
    
    district = random.choice(districts)
    street = random.choice(streets)
    number = random.randint(1, 500)
    building = random.randint(1, 30)
    unit = random.randint(1, 6)
    room = random.randint(101, 2505)
    
    return f"{province}{city}{district}{street}{number}号{building}栋{unit}单元{room}室"


def generate_passport():
    """生成护照号码"""
    # 中国护照格式：E + 8位数字 或 G + 8位数字
    prefix = random.choice(['E', 'G'])
    return prefix + ''.join([str(random.randint(0, 9)) for _ in range(8)])


def create_city_data():
    """创建城市和机场数据"""
    from core.models import City, Airport, Airline, PopularRoute
    
    print("创建城市和机场数据...")
    
    # 清除旧数据
    PopularRoute.objects.all().delete()
    Airport.objects.all().delete()
    Airline.objects.all().delete()
    City.objects.all().delete()
    
    # 城市坐标数据
    city_coords = {
        '北京': {'lat': 39.9042, 'lng': 116.4074, 'code': 'BJS'},
        '北京大兴': {'lat': 39.5098, 'lng': 116.4105, 'code': 'PKX'},
        '上海虹桥': {'lat': 31.1979, 'lng': 121.3363, 'code': 'SHA'},
        '上海浦东': {'lat': 31.1443, 'lng': 121.8083, 'code': 'PVG'},
        '广州': {'lat': 23.3924, 'lng': 113.2988, 'code': 'CAN'},
        '深圳': {'lat': 22.6397, 'lng': 113.8107, 'code': 'SZX'},
        '成都': {'lat': 30.5728, 'lng': 103.9422, 'code': 'CTU'},
        '成都天府': {'lat': 30.3147, 'lng': 104.4412, 'code': 'TFU'},
        '杭州': {'lat': 30.2294, 'lng': 120.4343, 'code': 'HGH'},
        '西安': {'lat': 34.4371, 'lng': 108.7519, 'code': 'XIY'},
        '南京': {'lat': 31.7420, 'lng': 118.8622, 'code': 'NKG'},
        '武汉': {'lat': 30.7838, 'lng': 114.2081, 'code': 'WUH'},
        '厦门': {'lat': 24.5440, 'lng': 118.1277, 'code': 'XMN'},
        '长沙': {'lat': 28.1891, 'lng': 113.2192, 'code': 'CSX'},
        '青岛': {'lat': 36.2661, 'lng': 120.3744, 'code': 'TAO'},
        '天津': {'lat': 39.1246, 'lng': 117.3462, 'code': 'TSN'},
        '重庆': {'lat': 29.7192, 'lng': 106.6413, 'code': 'CKG'},
        '哈尔滨': {'lat': 45.6234, 'lng': 126.2500, 'code': 'HRB'},
        '昆明': {'lat': 24.9925, 'lng': 102.7432, 'code': 'KMG'},
        '三亚': {'lat': 18.3029, 'lng': 109.4120, 'code': 'SYX'},
        '大连': {'lat': 39.0065, 'lng': 121.5395, 'code': 'DLC'},
        '郑州': {'lat': 34.5196, 'lng': 113.8413, 'code': 'CGO'},
        '沈阳': {'lat': 41.6398, 'lng': 123.4830, 'code': 'SHE'},
        '海口': {'lat': 19.9349, 'lng': 110.4590, 'code': 'HAK'},
        '贵阳': {'lat': 26.5385, 'lng': 106.8008, 'code': 'KWE'},
        '乌鲁木齐': {'lat': 43.9073, 'lng': 87.4742, 'code': 'URC'},
        '兰州': {'lat': 36.5152, 'lng': 103.6204, 'code': 'LHW'},
        '拉萨': {'lat': 29.2980, 'lng': 90.9118, 'code': 'LXA'},
    }
    
    # 国际城市坐标
    international_coords = {
        '东京成田': {'lat': 35.7647, 'lng': 140.3864, 'code': 'NRT', 'country': '日本'},
        '东京羽田': {'lat': 35.5494, 'lng': 139.7798, 'code': 'HND', 'country': '日本'},
        '大阪': {'lat': 34.4347, 'lng': 135.2441, 'code': 'KIX', 'country': '日本'},
        '首尔仁川': {'lat': 37.4602, 'lng': 126.4407, 'code': 'ICN', 'country': '韩国'},
        '新加坡': {'lat': 1.3644, 'lng': 103.9915, 'code': 'SIN', 'country': '新加坡'},
        '曼谷': {'lat': 13.6900, 'lng': 100.7501, 'code': 'BKK', 'country': '泰国'},
        '吉隆坡': {'lat': 2.7456, 'lng': 101.7072, 'code': 'KUL', 'country': '马来西亚'},
        '悉尼': {'lat': -33.9399, 'lng': 151.1753, 'code': 'SYD', 'country': '澳大利亚'},
        '墨尔本': {'lat': -37.6690, 'lng': 144.8410, 'code': 'MEL', 'country': '澳大利亚'},
        '洛杉矶': {'lat': 33.9416, 'lng': -118.4085, 'code': 'LAX', 'country': '美国'},
        '纽约': {'lat': 40.6413, 'lng': -73.7781, 'code': 'JFK', 'country': '美国'},
        '旧金山': {'lat': 37.6213, 'lng': -122.3790, 'code': 'SFO', 'country': '美国'},
        '伦敦': {'lat': 51.4700, 'lng': -0.4543, 'code': 'LHR', 'country': '英国'},
        '巴黎': {'lat': 49.0097, 'lng': 2.5479, 'code': 'CDG', 'country': '法国'},
        '迪拜': {'lat': 25.2532, 'lng': 55.3657, 'code': 'DXB', 'country': '阿联酋'},
        '法兰克福': {'lat': 50.0379, 'lng': 8.5622, 'code': 'FRA', 'country': '德国'},
        '温哥华': {'lat': 49.1967, 'lng': -123.1815, 'code': 'YVR', 'country': '加拿大'},
        '多伦多': {'lat': 43.6777, 'lng': -79.6248, 'code': 'YYZ', 'country': '加拿大'},
    }
    
    cities_created = {}
    
    # 创建国内城市
    for name, data in city_coords.items():
        city = City.objects.create(
            name=name,
            code=data['code'],
            country='中国',
            latitude=data['lat'],
            longitude=data['lng']
        )
        cities_created[name] = city
    
    # 创建国际城市
    for name, data in international_coords.items():
        city = City.objects.create(
            name=name,
            code=data['code'],
            country=data['country'],
            latitude=data['lat'],
            longitude=data['lng']
        )
        cities_created[name] = city
    
    print(f"  创建了 {len(cities_created)} 个城市")
    
    # 创建航空公司
    airlines_data = [
        ('CA', '中国国际航空'),
        ('MU', '东方航空'),
        ('CZ', '南方航空'),
        ('HU', '海南航空'),
        ('3U', '四川航空'),
        ('MF', '厦门航空'),
        ('ZH', '深圳航空'),
        ('SC', '山东航空'),
        ('FM', '上海航空'),
        ('GS', '天津航空'),
        ('KN', '联合航空'),
        ('9C', '春秋航空'),
        ('G5', '华夏航空'),
    ]
    
    for code, name in airlines_data:
        Airline.objects.create(code=code, name=name)
    
    print(f"  创建了 {len(airlines_data)} 个航空公司")
    
    # 热门航线将在订单创建后根据实际数据更新
    print("  热门航线将在订单数据生成后更新...")
    
    return cities_created


def update_popular_routes():
    """根据实际订单数据更新热门航线"""
    from core.models import City, PopularRoute
    from django.db.models import Count, Avg
    
    print("更新热门航线数据...")
    
    # 清除旧的热门航线
    PopularRoute.objects.all().delete()
    
    # 统计各航线的实际订票量
    route_stats = Ticket.objects.filter(
        order__status__in=['paid', 'completed'],
        status__in=['valid', 'used']
    ).values(
        'flight__departure_city',
        'flight__arrival_city'
    ).annotate(
        booking_count=Count('id'),
        avg_price=Avg('price')
    ).order_by('-booking_count')[:20]  # 取前20条热门航线
    
    # 获取城市映射
    cities = {city.name: city for city in City.objects.all()}
    
    created_count = 0
    for stat in route_stats:
        dep_city_name = stat['flight__departure_city']
        arr_city_name = stat['flight__arrival_city']
        
        dep_city = cities.get(dep_city_name)
        arr_city = cities.get(arr_city_name)
        
        if dep_city and arr_city:
            # 热度值 = 订票数量（真实数据）
            popularity = stat['booking_count']
            avg_price = stat['avg_price'] or 1000
            
            PopularRoute.objects.create(
                from_city=dep_city,
                to_city=arr_city,
                price=Decimal(str(round(avg_price, 2))),
                discount=Decimal('0.90'),
                popularity=popularity
            )
            created_count += 1
    
    print(f"  根据订单数据创建了 {created_count} 条热门航线")
    
    # 打印热门航线排名
    print("\n📊 热门航线排名 (基于实际订票量):")
    for i, stat in enumerate(route_stats[:10], 1):
        print(f"  {i}. {stat['flight__departure_city']} → {stat['flight__arrival_city']}: {stat['booking_count']} 张票")


def clear_existing_data():
    """清除现有测试数据"""
    print("清除现有数据...")
    from django.db import connection
    
    # 先获取要删除的用户ID
    test_user_ids = list(User.objects.filter(
        username__startswith='user'
    ).values_list('id', flat=True))
    admin_ids = list(User.objects.filter(username='admin').values_list('id', flat=True))
    user_ids_to_delete = test_user_ids + admin_ids
    
    if not user_ids_to_delete:
        print("  没有需要清除的测试用户")
        RescheduleLog.objects.all().delete()
        Flight.objects.all().delete()
        return
    
    # 使用原始SQL禁用外键检查（SQLite）
    with connection.cursor() as cursor:
        cursor.execute('PRAGMA foreign_keys = OFF;')
    
    try:
        # 删除所有相关数据（按依赖顺序）
        RescheduleLog.objects.all().delete()
        Notification.objects.filter(user_id__in=user_ids_to_delete).delete()
        Ticket.objects.filter(order__user_id__in=user_ids_to_delete).delete()
        Order.objects.filter(user_id__in=user_ids_to_delete).delete()
        Passenger.objects.filter(user_id__in=user_ids_to_delete).delete()
        Flight.objects.all().delete()
        
        # 删除用户消息
        try:
            from user_messages.models import Message
            Message.objects.filter(user_id__in=user_ids_to_delete).delete()
        except Exception:
            pass
        
        # 删除用户
        User.objects.filter(id__in=user_ids_to_delete).delete()
    finally:
        # 重新启用外键检查
        with connection.cursor() as cursor:
            cursor.execute('PRAGMA foreign_keys = ON;')
    
    print("  数据清除完成")


def create_test_users():
    """创建测试用户（更真实的用户画像）"""
    print("创建测试用户...")
    test_users = []
    today = timezone.now()

    # 用户画像模板
    user_profiles = [
        # 商务旅客（频繁出差）
        {'type': 'business', 'count': 8, 'order_freq': 'high'},
        # 普通旅客（偶尔出行）
        {'type': 'casual', 'count': 15, 'order_freq': 'medium'},
        # 学生/年轻人（价格敏感）
        {'type': 'student', 'count': 10, 'order_freq': 'low'},
        # 家庭用户（节假日出行）
        {'type': 'family', 'count': 7, 'order_freq': 'medium'},
    ]

    user_index = 1
    for profile in user_profiles:
        for _ in range(profile['count']):
            username = f'user{user_index}'
            gender = random.choice(['male', 'female'])
            
            # 根据用户类型设置年龄范围
            if profile['type'] == 'student':
                age = random.randint(18, 28)
            elif profile['type'] == 'business':
                age = random.randint(28, 50)
            elif profile['type'] == 'family':
                age = random.randint(30, 55)
            else:
                age = random.randint(22, 60)
            
            birth_date = (today - datetime.timedelta(days=365 * age + random.randint(0, 364))).date()
            
            # 注册时间分布（更多用户是近期注册）
            if random.random() < 0.4:
                days_ago = random.randint(0, 30)  # 40% 近一个月
            elif random.random() < 0.7:
                days_ago = random.randint(30, 90)  # 30% 1-3个月
            else:
                days_ago = random.randint(90, 365)  # 30% 更早
            
            join_date = today - datetime.timedelta(days=days_ago)
            real_name = generate_name(gender)
            id_card = generate_id_card(birth_date, gender)
            
            # 确保身份证唯一
            while User.objects.filter(id_card=id_card).exists():
                id_card = generate_id_card(birth_date, gender)
            
            user = User.objects.create(
                username=username,
                email=f'{username}@{"gmail.com" if random.random() < 0.3 else "qq.com" if random.random() < 0.5 else "163.com"}',
                is_active=True,
                role='user',
                phone=generate_phone(),
                real_name=real_name,
                id_card=id_card,
                gender=gender,
                address=generate_address(),
                date_joined=join_date,
                created_at=join_date
            )
            user.set_password('password123')
            user.save()
            
            # 存储用户画像信息（用于后续生成订单）
            user._profile_type = profile['type']
            user._order_freq = profile['order_freq']
            
            print(f"  创建用户: {username} ({real_name}, {profile['type']})")
            test_users.append(user)
            user_index += 1

    # 创建管理员用户
    admin = User.objects.create(
        username='admin',
        email='admin@ifly.com',
        is_active=True,
        is_staff=True,
        is_superuser=True,
        role='admin',
        phone='13800000001',
        real_name='系统管理员',
        gender='male'
    )
    admin.set_password('admin123')
    admin.save()
    print("  创建管理员: admin")
    test_users.append(admin)

    return test_users


def create_test_passengers(users):
    """为用户创建测试乘客信息（更真实的家庭关系）"""
    print("创建测试乘客信息...")
    test_passengers = []
    today = timezone.now()

    for user in users:
        if user.role == 'admin':
            continue
        
        profile_type = getattr(user, '_profile_type', 'casual')
        
        # 首先添加用户自己作为乘客
        user_birth = (today - datetime.timedelta(days=365 * random.randint(25, 50))).date()
        user_id_card = user.id_card or generate_id_card(user_birth, user.gender)
        
        # 确保身份证唯一
        while Passenger.objects.filter(id_card=user_id_card).exists():
            user_id_card = generate_id_card(user_birth, user.gender)
        
        self_passenger = Passenger.objects.create(
            user=user,
            name=user.real_name,
            id_card=user_id_card,
            passport_number=generate_passport() if random.random() < 0.3 else None,
            gender=user.gender,
            birth_date=user_birth
        )
        test_passengers.append(self_passenger)
        
        # 根据用户类型添加其他乘客
        if profile_type == 'family':
            # 家庭用户：添加配偶和孩子
            spouse_gender = 'female' if user.gender == 'male' else 'male'
            spouse_birth = (today - datetime.timedelta(days=365 * random.randint(25, 50))).date()
            spouse_id = generate_id_card(spouse_birth, spouse_gender)
            while Passenger.objects.filter(id_card=spouse_id).exists():
                spouse_id = generate_id_card(spouse_birth, spouse_gender)
            
            spouse = Passenger.objects.create(
                user=user,
                name=generate_name(spouse_gender),
                id_card=spouse_id,
                passport_number=generate_passport() if random.random() < 0.3 else None,
                gender=spouse_gender,
                birth_date=spouse_birth
            )
            test_passengers.append(spouse)
            
            # 添加1-2个孩子
            for _ in range(random.randint(1, 2)):
                child_age = random.randint(3, 18)
                child_gender = random.choice(['male', 'female'])
                child_birth = (today - datetime.timedelta(days=365 * child_age + random.randint(0, 364))).date()
                child_id = generate_id_card(child_birth, child_gender)
                while Passenger.objects.filter(id_card=child_id).exists():
                    child_id = generate_id_card(child_birth, child_gender)
                
                child = Passenger.objects.create(
                    user=user,
                    name=user.real_name[0] + random.choice(MALE_NAMES if child_gender == 'male' else FEMALE_NAMES),
                    id_card=child_id,
                    gender=child_gender,
                    birth_date=child_birth
                )
                test_passengers.append(child)
        
        elif profile_type == 'business':
            # 商务用户：可能添加同事
            if random.random() < 0.5:
                colleague_gender = random.choice(['male', 'female'])
                colleague_birth = (today - datetime.timedelta(days=365 * random.randint(25, 45))).date()
                colleague_id = generate_id_card(colleague_birth, colleague_gender)
                while Passenger.objects.filter(id_card=colleague_id).exists():
                    colleague_id = generate_id_card(colleague_birth, colleague_gender)
                
                colleague = Passenger.objects.create(
                    user=user,
                    name=generate_name(colleague_gender),
                    id_card=colleague_id,
                    passport_number=generate_passport() if random.random() < 0.4 else None,
                    gender=colleague_gender,
                    birth_date=colleague_birth
                )
                test_passengers.append(colleague)
        
        else:
            # 其他用户：随机添加0-2个乘客（朋友/家人）
            for _ in range(random.randint(0, 2)):
                p_gender = random.choice(['male', 'female'])
                p_age = random.randint(18, 65)
                p_birth = (today - datetime.timedelta(days=365 * p_age + random.randint(0, 364))).date()
                p_id = generate_id_card(p_birth, p_gender)
                while Passenger.objects.filter(id_card=p_id).exists():
                    p_id = generate_id_card(p_birth, p_gender)
                
                passenger = Passenger.objects.create(
                    user=user,
                    name=generate_name(p_gender),
                    id_card=p_id,
                    passport_number=generate_passport() if random.random() < 0.2 else None,
                    gender=p_gender,
                    birth_date=p_birth
                )
                test_passengers.append(passenger)

    print(f"  共创建 {len(test_passengers)} 个乘客")
    return test_passengers



@transaction.atomic
def create_test_flights():
    """创建测试航班数据（更真实的航班信息）"""
    print("创建测试航班数据...")
    test_flights = []
    today = timezone.now().date()
    used_flight_numbers = set()

    def generate_flight_number(airline_code):
        """生成唯一航班号"""
        while True:
            flight_num = f"{airline_code}{random.randint(1000, 9999)}"
            if flight_num not in used_flight_numbers:
                used_flight_numbers.add(flight_num)
                return flight_num

    def get_flight_duration(departure, arrival, is_international):
        """根据航线计算合理的飞行时间"""
        if is_international:
            # 国际航班
            long_haul = ['洛杉矶', '纽约', '旧金山', '伦敦', '巴黎', '法兰克福', '悉尼', '墨尔本', '温哥华', '多伦多']
            if any(city in arrival for city in long_haul):
                return random.randint(600, 900)  # 10-15小时
            else:
                return random.randint(180, 420)  # 3-7小时（亚洲航线）
        else:
            # 国内航班
            short_routes = [('北京', '天津'), ('上海虹桥', '上海浦东'), ('广州', '深圳')]
            if (departure, arrival) in short_routes or (arrival, departure) in short_routes:
                return random.randint(45, 70)
            
            # 远距离航线
            far_cities = ['乌鲁木齐', '拉萨', '哈尔滨', '三亚', '海口']
            if departure in far_cities or arrival in far_cities:
                return random.randint(180, 300)
            
            return random.randint(90, 180)

    def get_base_price(departure, arrival, is_international, cabin_type='economy'):
        """根据航线计算基础票价"""
        if is_international:
            long_haul = ['洛杉矶', '纽约', '旧金山', '伦敦', '巴黎', '法兰克福', '悉尼', '墨尔本', '温哥华', '多伦多']
            if any(city in arrival for city in long_haul):
                base = random.randint(4000, 12000)
            else:
                base = random.randint(1500, 4000)
        else:
            far_cities = ['乌鲁木齐', '拉萨', '哈尔滨', '三亚', '海口', '昆明']
            if departure in far_cities or arrival in far_cities:
                base = random.randint(800, 2500)
            else:
                base = random.randint(400, 1500)
        
        return base

    def create_flight(departure, arrival, date, hour, airline_code, is_international=False):
        """创建单个航班"""
        airline_info = AIRLINES[airline_code]
        flight_number = generate_flight_number(airline_code)
        
        # 起飞时间（整点或半点）
        minute = random.choice([0, 30])
        departure_time = datetime.datetime.combine(date, datetime.time(hour, minute))
        departure_time = timezone.make_aware(departure_time, timezone.get_current_timezone())

        # 飞行时间
        flight_duration = get_flight_duration(departure, arrival, is_international)
        arrival_time = departure_time + datetime.timedelta(minutes=flight_duration)
        
        # 选择合适的机型
        if is_international or flight_duration > 180:
            aircraft_choices = ['波音777-300ER', '波音787-9', '空客A330-300', '空客A350-900']
        else:
            aircraft_choices = ['波音737-800', '波音737 MAX 8', '空客A320neo', '空客A321neo', '国产C919', '国产ARJ21']
        
        # 春秋航空只用窄体机
        if airline_code == '9C':
            aircraft_choices = ['空客A320neo', '空客A321neo']
        
        aircraft_type = random.choice(aircraft_choices)
        aircraft_config = AIRCRAFT_TYPES[aircraft_type]
        
        capacity = aircraft_config['capacity']
        seat_rows = aircraft_config['rows']
        seats_per_row = aircraft_config['seats_per_row']
        
        # 票价
        base_price = get_base_price(departure, arrival, is_international)
        
        # 折扣（廉价航空折扣更大）
        if airline_code == '9C':
            discount = Decimal(random.choice(['0.60', '0.65', '0.70', '0.75', '0.80']))
        else:
            discount = Decimal(random.choice(['0.85', '0.90', '0.95', '1.00']))
        
        # 座位和状态
        if date < today:
            # 历史航班
            available_seats = random.randint(0, capacity // 4)
            status = random.choices(
                ['departed', 'canceled'],
                weights=[0.95, 0.05]
            )[0]
        elif date == today:
            # 今天的航班
            if hour < timezone.now().hour:
                available_seats = 0
                status = 'departed'
            else:
                available_seats = random.randint(5, capacity // 2)
                status = 'scheduled'
        else:
            # 未来航班
            days_ahead = (date - today).days
            if days_ahead <= 3:
                # 近期航班座位较少
                available_seats = random.randint(capacity // 4, capacity // 2)
            elif days_ahead <= 7:
                available_seats = random.randint(capacity // 2, int(capacity * 0.8))
            else:
                available_seats = random.randint(int(capacity * 0.7), capacity)
            
            status = 'scheduled' if available_seats > 0 else 'full'
        
        # 服务配置
        is_long_haul = flight_duration > 180
        
        flight = Flight.objects.create(
            flight_number=flight_number,
            airline_name=airline_info['name'],
            departure_city=departure,
            arrival_city=arrival,
            departure_time=departure_time,
            arrival_time=arrival_time,
            price=Decimal(base_price),
            discount=discount,
            capacity=capacity,
            available_seats=available_seats,
            status=status,
            aircraft_type=aircraft_type,
            seat_rows=seat_rows,
            seats_per_row=seats_per_row,
            is_international=is_international,
            meal_service=airline_code != '9C',  # 廉价航空无餐食
            baggage_allowance=20 if not is_international else 23,
            wifi=is_long_haul and random.random() < 0.6,
            power_outlet=is_long_haul or random.random() < 0.3,
            entertainment=is_long_haul
        )
        return flight

    # 1. 创建热门国内航线（高频次）
    hot_domestic_routes = [
        ('北京', '上海浦东'), ('上海浦东', '北京'),
        ('北京', '上海虹桥'), ('上海虹桥', '北京'),
        ('北京', '广州'), ('广州', '北京'),
        ('北京', '深圳'), ('深圳', '北京'),
        ('上海浦东', '广州'), ('广州', '上海浦东'),
        ('上海浦东', '深圳'), ('深圳', '上海浦东'),
        ('北京', '成都'), ('成都', '北京'),
        ('上海浦东', '成都'), ('成都', '上海浦东'),
        ('北京', '杭州'), ('杭州', '北京'),
        ('广州', '杭州'), ('杭州', '广州'),
        ('北京', '西安'), ('西安', '北京'),
        ('上海浦东', '西安'), ('西安', '上海浦东'),
    ]
    
    print("  创建热门国内航线...")
    for departure, arrival in hot_domestic_routes:
        for i in range(-45, 31):  # 过去45天到未来30天
            current_date = today + datetime.timedelta(days=i)
            # 每天4-8班
            num_flights = random.randint(4, 8)
            hours = random.sample([6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22], num_flights)
            for hour in hours:
                airline_code = random.choice(['CA', 'MU', 'CZ', 'HU', '3U', 'MF', 'ZH', 'FM', '9C'])
                flight = create_flight(departure, arrival, current_date, hour, airline_code)
                test_flights.append(flight)

    # 2. 创建普通国内航线
    print("  创建普通国内航线...")
    other_routes = []
    for dep in CITIES:
        for arr in CITIES:
            if dep != arr and (dep, arr) not in hot_domestic_routes:
                other_routes.append((dep, arr))
    
    # 随机选择200条航线
    selected_routes = random.sample(other_routes, min(200, len(other_routes)))
    for departure, arrival in selected_routes:
        for i in range(-30, 20):
            current_date = today + datetime.timedelta(days=i)
            # 每天1-3班
            if random.random() < 0.7:  # 70%的天数有航班
                num_flights = random.randint(1, 3)
                hours = random.sample(range(6, 23), num_flights)
                for hour in hours:
                    airline_code = random.choice(list(AIRLINES.keys()))
                    flight = create_flight(departure, arrival, current_date, hour, airline_code)
                    test_flights.append(flight)

    # 3. 创建国际航线
    print("  创建国际航线...")
    domestic_hubs = ['北京', '上海浦东', '广州', '深圳', '成都']
    
    for domestic in domestic_hubs:
        for international, info in INTERNATIONAL_CITIES.items():
            for i in range(-30, 20):
                current_date = today + datetime.timedelta(days=i)
                # 国际航班频次较低
                if random.random() < 0.5:
                    hour = random.choice([8, 9, 10, 14, 15, 21, 22, 23])
                    airline_code = random.choice(['CA', 'MU', 'CZ', 'HU'])
                    
                    # 去程
                    flight = create_flight(domestic, international, current_date, hour, airline_code, is_international=True)
                    test_flights.append(flight)
                    
                    # 返程（1-3天后）
                    return_days = random.randint(1, 3)
                    return_date = current_date + datetime.timedelta(days=return_days)
                    if return_date <= today + datetime.timedelta(days=20):
                        return_hour = random.choice([8, 9, 10, 14, 15, 21, 22])
                        flight = create_flight(international, domestic, return_date, return_hour, airline_code, is_international=True)
                        test_flights.append(flight)

    print(f"  共创建 {len(test_flights)} 个航班")
    return test_flights


@transaction.atomic
def create_test_orders_tickets(users, flights, passengers):
    """创建测试订单和机票数据（更真实的订单场景）"""
    print("创建测试订单和机票数据...")
    test_orders = []
    today = timezone.now()

    # 按日期分组航班
    past_flights = [f for f in flights if f.departure_time.date() < today.date()]
    future_flights = [f for f in flights if f.departure_time.date() >= today.date() and f.status == 'scheduled']
    
    regular_users = [u for u in users if u.role != 'admin']
    
    # 用户乘客映射
    user_passengers_map = {}
    for user in regular_users:
        user_passengers_map[user.id] = list(Passenger.objects.filter(user=user))

    def create_order_with_tickets(user, flight, passengers_list, order_date, status, cabin_class='economy'):
        """创建订单及其机票"""
        # 计算价格
        price_multiplier = {'economy': 1, 'business': 2.5, 'first': 4}
        ticket_price = flight.price * flight.discount * Decimal(str(price_multiplier[cabin_class]))
        total_price = ticket_price * len(passengers_list)
        
        # 支付方式
        payment_method = None
        paid_at = None
        if status in ['paid', 'completed']:
            payment_method = random.choice(PAYMENT_METHODS)
            paid_at = order_date + datetime.timedelta(minutes=random.randint(3, 45))
        
        order = Order(
            user=user,
            total_price=total_price,
            status=status,
            payment_method=payment_method,
            contact_name=passengers_list[0].name,
            contact_phone=user.phone or generate_phone(),
            contact_email=user.email
        )
        order.save()
        
        # 更新时间
        Order.objects.filter(pk=order.pk).update(
            created_at=order_date,
            paid_at=paid_at
        )
        order.refresh_from_db()
        
        # 创建机票
        tickets = []
        for idx, passenger in enumerate(passengers_list):
            row = random.randint(1, flight.seat_rows or 30)
            col = chr(ord('A') + (idx % (flight.seats_per_row or 6)))
            seat_number = f"{row}{col}"
            
            # 机票状态
            if status == 'completed':
                ticket_status = 'used'
                checked_in = True
                checked_in_at = flight.departure_time - datetime.timedelta(hours=random.randint(2, 24))
                boarding_pass = f"BP{uuid.uuid4().hex[:8].upper()}"
                gate = random.choice(GATES)
            elif status == 'paid':
                ticket_status = 'valid'
                # 部分已值机
                checked_in = random.random() < 0.3
                checked_in_at = (flight.departure_time - datetime.timedelta(hours=random.randint(2, 24))) if checked_in else None
                boarding_pass = f"BP{uuid.uuid4().hex[:8].upper()}" if checked_in else None
                gate = random.choice(GATES) if checked_in else None
            elif status == 'canceled':
                ticket_status = 'canceled'
                checked_in = False
                checked_in_at = None
                boarding_pass = None
                gate = None
            else:  # pending
                ticket_status = 'valid'
                checked_in = False
                checked_in_at = None
                boarding_pass = None
                gate = None
            
            ticket = Ticket.objects.create(
                order=order,
                flight=flight,
                passenger_name=passenger.name,
                passenger_id_type='身份证' if not flight.is_international else random.choice(['身份证', '护照']),
                passenger_id_number=passenger.id_card,
                seat_number=seat_number,
                cabin_class=cabin_class,
                price=ticket_price,
                status=ticket_status,
                checked_in=checked_in,
                checked_in_at=checked_in_at,
                boarding_pass_number=boarding_pass,
                gate=gate
            )
            tickets.append(ticket)
        
        return order, tickets

    # 1. 创建历史订单（过去45天）
    print("  创建历史订单...")
    for days_ago in range(45, 0, -1):
        order_date = today - datetime.timedelta(days=days_ago)
        
        # 工作日订单更多
        is_weekend = order_date.weekday() >= 5
        base_orders = 8 if is_weekend else 12
        num_orders = random.randint(base_orders - 3, base_orders + 5)
        
        for _ in range(num_orders):
            user = random.choice(regular_users)
            user_passengers = user_passengers_map.get(user.id, [])
            if not user_passengers:
                continue

            # 选择合适的航班（订单日期之后的航班）
            suitable_flights = [f for f in past_flights if f.departure_time > order_date]
            if not suitable_flights:
                suitable_flights = [f for f in flights if f.departure_time > order_date]
            if not suitable_flights:
                continue

            flight = random.choice(suitable_flights)
            
            # 根据用户类型选择乘客数量
            profile_type = getattr(user, '_profile_type', 'casual')
            if profile_type == 'family':
                num_passengers = min(random.randint(2, 4), len(user_passengers))
            elif profile_type == 'business':
                num_passengers = min(random.randint(1, 2), len(user_passengers))
            else:
                num_passengers = min(random.randint(1, 2), len(user_passengers))
            
            selected_passengers = random.sample(user_passengers, num_passengers)

            # 舱位选择
            if profile_type == 'business':
                cabin_class = random.choices(['economy', 'business', 'first'], weights=[0.4, 0.5, 0.1])[0]
            elif profile_type == 'student':
                cabin_class = 'economy'
            else:
                cabin_class = random.choices(['economy', 'business', 'first'], weights=[0.85, 0.12, 0.03])[0]

            # 历史订单状态分布
            status = random.choices(
                ['completed', 'paid', 'canceled'],
                weights=[0.65, 0.20, 0.15]
            )[0]

            order_time = order_date.replace(
                hour=random.randint(7, 23),
                minute=random.randint(0, 59)
            )
            
            order, tickets = create_order_with_tickets(
                user, flight, selected_passengers, order_time, status, cabin_class
            )
            test_orders.append(order)

    # 2. 创建最近7天的订单（确保趋势图有数据）
    print("  创建最近7天订单...")
    for days_ago in range(7, -1, -1):
        order_date = today - datetime.timedelta(days=days_ago)
        
        # 最近几天订单更多
        num_orders = random.randint(10, 20)
        
        for _ in range(num_orders):
            user = random.choice(regular_users)
            user_passengers = user_passengers_map.get(user.id, [])
            if not user_passengers:
                continue

            flight = random.choice(future_flights) if future_flights else random.choice(flights)
            
            profile_type = getattr(user, '_profile_type', 'casual')
            if profile_type == 'family':
                num_passengers = min(random.randint(2, 4), len(user_passengers))
            else:
                num_passengers = min(random.randint(1, 2), len(user_passengers))
            
            selected_passengers = random.sample(user_passengers, num_passengers)

            if profile_type == 'business':
                cabin_class = random.choices(['economy', 'business'], weights=[0.5, 0.5])[0]
            else:
                cabin_class = random.choices(['economy', 'business', 'first'], weights=[0.88, 0.10, 0.02])[0]

            # 最近订单更多是已支付状态
            status = random.choices(
                ['paid', 'pending', 'completed'],
                weights=[0.55, 0.30, 0.15]
            )[0]

            order_time = order_date.replace(
                hour=random.randint(7, 23),
                minute=random.randint(0, 59)
            )
            
            order, tickets = create_order_with_tickets(
                user, flight, selected_passengers, order_time, status, cabin_class
            )
            test_orders.append(order)

    # 3. 创建待支付订单（模拟购物车场景）
    print("  创建待支付订单...")
    for _ in range(15):
        user = random.choice(regular_users)
        user_passengers = user_passengers_map.get(user.id, [])
        if not user_passengers:
            continue

        flight = random.choice(future_flights) if future_flights else random.choice(flights)
        passenger = random.choice(user_passengers)

        order_time = today - datetime.timedelta(hours=random.randint(1, 48))
        
        order, tickets = create_order_with_tickets(
            user, flight, [passenger], order_time, 'pending', 'economy'
        )
        
        # 设置过期时间
        Order.objects.filter(pk=order.pk).update(
            expires_at=order_time + datetime.timedelta(hours=2)
        )
        test_orders.append(order)

    # 4. 创建一些退票订单
    print("  创建退票订单...")
    for _ in range(20):
        user = random.choice(regular_users)
        user_passengers = user_passengers_map.get(user.id, [])
        if not user_passengers:
            continue

        flight = random.choice(future_flights) if future_flights else random.choice(flights)
        passenger = random.choice(user_passengers)

        days_ago = random.randint(3, 30)
        order_time = today - datetime.timedelta(days=days_ago)
        
        order, tickets = create_order_with_tickets(
            user, flight, [passenger], order_time, 'paid', 'economy'
        )
        
        # 将机票状态改为已退票
        for ticket in tickets:
            ticket.status = 'refunded'
            ticket.save()
        
        test_orders.append(order)

    print(f"  共创建 {len(test_orders)} 个订单")
    return test_orders


def create_reschedule_logs(orders, flights):
    """创建改签记录"""
    print("创建改签记录...")
    reschedule_logs = []
    today = timezone.now()
    
    # 筛选可以改签的订单（已支付且有有效机票）
    paid_orders = [o for o in orders if o.status in ['paid', 'completed']]
    future_flights = [f for f in flights if f.departure_time > today and f.status == 'scheduled']
    
    if not paid_orders or not future_flights:
        print("  没有可用的订单或航班用于创建改签记录")
        return reschedule_logs
    
    # 随机选择一些订单进行改签
    num_reschedules = min(25, len(paid_orders) // 5)
    selected_orders = random.sample(paid_orders, num_reschedules)
    
    for order in selected_orders:
        tickets = list(Ticket.objects.filter(order=order, status='valid'))
        if not tickets:
            continue
        
        original_ticket = random.choice(tickets)
        original_flight = original_ticket.flight
        
        # 找一个同航线或相似航线的航班
        same_route_flights = [
            f for f in future_flights 
            if f.departure_city == original_flight.departure_city 
            and f.arrival_city == original_flight.arrival_city
            and f.id != original_flight.id
            and f.available_seats > 0
        ]
        
        if not same_route_flights:
            # 如果没有同航线，选择任意未来航班
            same_route_flights = [f for f in future_flights if f.id != original_flight.id and f.available_seats > 0]
        
        if not same_route_flights:
            continue
        
        new_flight = random.choice(same_route_flights)
        
        # 计算差价
        price_diff = new_flight.price * new_flight.discount - original_ticket.price
        reschedule_fee = Decimal('50.00') if price_diff <= 0 else Decimal('100.00')
        
        # 创建新机票
        new_ticket = Ticket.objects.create(
            order=order,
            flight=new_flight,
            passenger_name=original_ticket.passenger_name,
            passenger_id_type=original_ticket.passenger_id_type,
            passenger_id_number=original_ticket.passenger_id_number,
            seat_number=f"{random.randint(1, new_flight.seat_rows or 30)}{chr(ord('A') + random.randint(0, 5))}",
            cabin_class=original_ticket.cabin_class,
            price=new_flight.price * new_flight.discount,
            status='valid'
        )
        
        # 更新原机票状态
        original_ticket.status = 'rescheduled'
        original_ticket.save()
        
        # 创建改签记录
        log = RescheduleLog.objects.create(
            original_ticket=original_ticket,
            new_ticket=new_ticket,
            original_flight=original_flight,
            new_flight=new_flight,
            price_difference=price_diff,
            reschedule_fee=reschedule_fee
        )
        reschedule_logs.append(log)
    
    print(f"  共创建 {len(reschedule_logs)} 条改签记录")
    return reschedule_logs


def create_test_notifications(users, orders):
    """创建测试通知（更真实的通知场景）"""
    print("创建测试通知...")
    today = timezone.now()
    
    # 通知模板（按类型分组）
    notification_templates = {
        'system': [
            ('系统升级通知', '系统将于本周六凌晨2:00-6:00进行升级维护，届时部分功能可能暂时不可用，请提前安排好您的行程。'),
            ('新功能上线', 'iFly 新增在线选座功能，您可以在值机时自由选择心仪的座位，快来体验吧！'),
            ('安全提醒', '为保障您的账户安全，请定期修改密码，不要将账户信息泄露给他人。'),
            ('服务条款更新', 'iFly 服务条款已更新，请查阅最新版本了解详情。'),
        ],
        'order': [
            ('订单创建成功', '您的机票订单已创建成功，请在30分钟内完成支付，逾期订单将自动取消。'),
            ('订单支付成功', '您的机票订单已支付成功，电子客票已发送至您的邮箱，请注意查收。'),
            ('订单已完成', '您的行程已结束，感谢您选择 iFly，期待下次为您服务！'),
            ('订单取消通知', '您的订单已取消，如有疑问请联系客服。'),
        ],
        'flight': [
            ('航班时间变更', '您预订的航班起飞时间有变动，请及时查看最新航班信息并调整您的出行计划。'),
            ('航班取消通知', '很抱歉，您预订的航班因天气原因已取消，我们将为您安排改签或退票，请查看详情。'),
            ('值机提醒', '您预订的航班将于24小时后起飞，请及时办理网上值机或前往机场柜台办理。'),
            ('登机提醒', '您的航班即将开始登机，请前往登机口候机。'),
            ('航班延误通知', '您预订的航班因流量控制延误约1小时，请关注最新动态。'),
        ],
        'payment': [
            ('支付成功', '您已成功支付订单，金额：¥{amount}，支付方式：{method}。'),
            ('退款处理中', '您的退票申请已受理，退款将在3-5个工作日内原路返回。'),
            ('退款成功', '您的退款已到账，金额：¥{amount}，请查收。'),
        ],
        'refund': [
            ('退票申请已提交', '您的退票申请已提交，我们将在1-2个工作日内处理。'),
            ('退票成功', '您的退票已处理完成，退款金额将在3-5个工作日内到账。'),
            ('改签成功', '您的机票改签已完成，新航班信息已更新，请查看订单详情。'),
        ],
        'info': [
            ('欢迎使用 iFly', '感谢您注册 iFly 飞机订票系统，祝您旅途愉快！'),
            ('会员积分到账', '您本次出行获得 {points} 积分，可用于兑换优惠券。'),
            ('生日祝福', '亲爱的用户，祝您生日快乐！iFly 为您准备了专属优惠，快来查看吧！'),
            ('节日问候', '值此佳节，iFly 祝您节日快乐，阖家幸福！'),
        ],
        'warning': [
            ('账户异常登录', '您的账户在新设备上登录，如非本人操作，请立即修改密码。'),
            ('订单即将过期', '您有一笔订单即将过期，请尽快完成支付。'),
            ('证件即将过期', '您保存的证件信息即将过期，请及时更新以免影响出行。'),
        ],
        'alert': [
            ('紧急通知', '因机场临时管制，部分航班可能延误，请关注航班动态。'),
            ('天气预警', '目的地城市发布暴雨预警，请做好出行准备。'),
        ],
    }

    for user in users:
        # 每个用户5-12条通知
        num_notifications = random.randint(5, 12)
        
        for _ in range(num_notifications):
            notif_type = random.choices(
                list(notification_templates.keys()),
                weights=[0.15, 0.25, 0.20, 0.15, 0.10, 0.08, 0.05, 0.02]
            )[0]
            
            title, message = random.choice(notification_templates[notif_type])
            
            # 替换占位符
            message = message.replace('{amount}', str(random.randint(200, 5000)))
            message = message.replace('{method}', random.choice(['支付宝', '微信支付', '银行卡']))
            message = message.replace('{points}', str(random.randint(50, 500)))
            
            days_ago = random.randint(0, 30)
            created_time = today - datetime.timedelta(
                days=days_ago,
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )
            
            # 越早的通知越可能已读
            is_read = random.random() < (0.9 if days_ago > 7 else 0.5 if days_ago > 1 else 0.2)
            
            notif = Notification(
                user=user,
                title=title,
                message=message,
                notif_type=notif_type,
                is_read=is_read
            )
            notif.save()
            Notification.objects.filter(pk=notif.pk).update(created_at=created_time)

    print(f"  为 {len(users)} 个用户创建了通知")


def print_summary():
    """打印数据统计摘要"""
    from django.db.models import Sum, Count, Avg
    
    print("\n" + "=" * 70)
    print("数据统计摘要")
    print("=" * 70)
    
    print(f"\n📊 基础数据统计:")
    print(f"  用户总数: {User.objects.count()}")
    print(f"  乘客总数: {Passenger.objects.count()}")
    print(f"  航班总数: {Flight.objects.count()}")
    print(f"  订单总数: {Order.objects.count()}")
    print(f"  机票总数: {Ticket.objects.count()}")
    print(f"  改签记录: {RescheduleLog.objects.count()}")
    print(f"  通知总数: {Notification.objects.count()}")
    
    print(f"\n📋 订单状态分布:")
    for status in Order.objects.values('status').annotate(count=Count('id')).order_by('-count'):
        status_name = {'pending': '待支付', 'paid': '已支付', 'completed': '已完成', 'canceled': '已取消'}
        print(f"  {status_name.get(status['status'], status['status'])}: {status['count']}")
    
    print(f"\n🎫 机票状态分布:")
    for status in Ticket.objects.values('status').annotate(count=Count('id')).order_by('-count'):
        status_name = {'valid': '有效', 'used': '已使用', 'refunded': '已退票', 'rescheduled': '已改签', 'canceled': '已取消'}
        print(f"  {status_name.get(status['status'], status['status'])}: {status['count']}")
    
    print(f"\n✈️ 航班统计:")
    print(f"  国内航班: {Flight.objects.filter(is_international=False).count()}")
    print(f"  国际航班: {Flight.objects.filter(is_international=True).count()}")
    print(f"  已起飞: {Flight.objects.filter(status='departed').count()}")
    print(f"  计划中: {Flight.objects.filter(status='scheduled').count()}")
    print(f"  已取消: {Flight.objects.filter(status='canceled').count()}")
    
    print(f"\n💰 收入统计:")
    total_revenue = Order.objects.filter(status__in=['paid', 'completed']).aggregate(
        total=Sum('total_price')
    )['total'] or 0
    avg_order = Order.objects.filter(status__in=['paid', 'completed']).aggregate(
        avg=Avg('total_price')
    )['avg'] or 0
    print(f"  总收入: ¥{total_revenue:,.2f}")
    print(f"  平均订单金额: ¥{avg_order:,.2f}")
    
    print(f"\n📈 最近7天订单趋势:")
    today = timezone.now().date()
    for i in range(6, -1, -1):
        day = today - datetime.timedelta(days=i)
        day_orders = Order.objects.filter(created_at__date=day)
        revenue = day_orders.filter(status__in=['paid', 'completed']).aggregate(sum=Sum('total_price'))['sum'] or 0
        orders_count = day_orders.count()
        weekday = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'][day.weekday()]
        print(f"  {day} ({weekday}): 订单={orders_count:3d}, 收入=¥{revenue:>10,.2f}")
    
    print(f"\n🏢 航空公司航班分布 (Top 5):")
    airlines = Flight.objects.values('airline_name').annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    for airline in airlines:
        print(f"  {airline['airline_name']}: {airline['count']} 班")
    
    print(f"\n🛫 热门航线 (Top 5):")
    routes = Flight.objects.values('departure_city', 'arrival_city').annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    for route in routes:
        print(f"  {route['departure_city']} → {route['arrival_city']}: {route['count']} 班")
    
    print(f"\n💺 舱位预订分布:")
    for cabin in Ticket.objects.values('cabin_class').annotate(count=Count('id')).order_by('-count'):
        cabin_name = {'economy': '经济舱', 'business': '商务舱', 'first': '头等舱'}
        print(f"  {cabin_name.get(cabin['cabin_class'], cabin['cabin_class'])}: {cabin['count']}")


def main():
    """主函数"""
    print("=" * 70)
    print("iFly 测试数据生成 v2.0")
    print("=" * 70)

    # 清除旧数据
    clear_existing_data()
    
    # 创建城市和机场数据（地图需要）
    create_city_data()

    # 创建新数据
    users = create_test_users()
    passengers = create_test_passengers(users)
    flights = create_test_flights()
    orders = create_test_orders_tickets(users, flights, passengers)
    create_reschedule_logs(orders, flights)
    create_test_notifications(users, orders)
    
    # 根据实际订单数据更新热门航线
    update_popular_routes()

    # 打印统计
    print_summary()

    print("\n" + "=" * 70)
    print("✅ 测试数据创建完成！")
    print("=" * 70)
    print("测试账号:")
    print("  普通用户: user1 ~ user40 / password123")
    print("  管理员: admin / admin123")
    print("=" * 70)


if __name__ == "__main__":
    main()
