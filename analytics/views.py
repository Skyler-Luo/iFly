import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from django.db.models import Sum, Count, Avg, F, Q
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth
from booking.models import Order, Ticket
from django.utils.timezone import now
from flight.models import Flight
from accounts.models import User
import datetime
import random

class AnalyticsOverview(APIView):
    """提供数据分析与报表概览接口，仅管理员可访问"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        if not hasattr(user, 'role') or user.role != 'admin':
            return Response({'detail': '权限不足'}, status=403)
        
        # 获取时间周期参数
        period = request.query_params.get('period', 'week')  # 默认显示本周数据
        today = now().date()
        
        if period == 'day':
            # 今日与昨日对比
            start_date = today
            compare_start_date = today - datetime.timedelta(days=1)
            compare_end_date = today - datetime.timedelta(days=1)
        elif period == 'month':
            # 本月与上月对比
            start_date = today.replace(day=1)
            last_month = today.month - 1 if today.month > 1 else 12
            last_month_year = today.year if today.month > 1 else today.year - 1
            compare_start_date = datetime.date(last_month_year, last_month, 1)
            # 获取上月的最后一天
            if last_month == 12:
                compare_end_date = datetime.date(last_month_year, 12, 31)
            else:
                compare_end_date = datetime.date(last_month_year, last_month + 1, 1) - datetime.timedelta(days=1)
        else:  # week
            # 本周与上周对比
            start_of_week = today - datetime.timedelta(days=today.weekday())
            start_date = start_of_week
            compare_start_date = start_of_week - datetime.timedelta(weeks=1)
            compare_end_date = start_date - datetime.timedelta(days=1)
        
        # 计算当前统计数据
        current_flights = Flight.objects.filter(departure_time__date__gte=start_date).count()
        current_users = User.objects.filter(date_joined__date__gte=start_date).count()
        current_orders = Order.objects.filter(created_at__date__gte=start_date).count()
        current_revenue = Order.objects.filter(
            status='paid', 
            paid_at__date__gte=start_date
        ).aggregate(total=Sum('total_price'))['total'] or 0
        
        print(f"==== 调试信息 ====")
        print(f"计算期间: {start_date} 到 {today}")
        print(f"当前航班数: {current_flights}")
        print(f"当前用户数: {current_users}")
        print(f"当前订单数: {current_orders}")
        print(f"当前收入: {current_revenue}")
        
        # 计算对比周期数据
        compare_flights = Flight.objects.filter(
            departure_time__date__gte=compare_start_date,
            departure_time__date__lte=compare_end_date
        ).count()
        compare_users = User.objects.filter(
            date_joined__date__gte=compare_start_date,
            date_joined__date__lte=compare_end_date
        ).count()
        compare_orders = Order.objects.filter(
            created_at__date__gte=compare_start_date,
            created_at__date__lte=compare_end_date
        ).count()
        compare_revenue = Order.objects.filter(
            status='paid',
            paid_at__date__gte=compare_start_date,
            paid_at__date__lte=compare_end_date
        ).aggregate(total=Sum('total_price'))['total'] or 0
        
        # 计算增长率
        flights_growth = calculate_growth(current_flights, compare_flights)
        users_growth = calculate_growth(current_users, compare_users)
        orders_growth = calculate_growth(current_orders, compare_orders)
        revenue_growth = calculate_growth(current_revenue, compare_revenue)
        
        # 获取总数据
        total_flights = Flight.objects.count()
        total_users = User.objects.count()
        total_orders = Order.objects.count()
        total_revenue = Order.objects.filter(status='paid').aggregate(total=Sum('total_price'))['total'] or 0
        
        print(f"总航班数: {total_flights}")
        print(f"总用户数: {total_users}")
        print(f"总订单数: {total_orders}")
        print(f"总收入: {total_revenue}")
        
        # 最近7天销售趋势
        trend = []
        for i in range(6, -1, -1):  # 从6天前到今天
            day = today - datetime.timedelta(days=i)
            revenue = Order.objects.filter(status='paid', paid_at__date=day).aggregate(sum=Sum('total_price'))['sum'] or 0
            orders = Order.objects.filter(created_at__date=day).count()
            trend.append([day.strftime('%Y-%m-%d'), float(revenue), orders])
        
        # 获取热门目的地
        popular_destinations = []
        destinations = Flight.objects.values('arrival_city').annotate(
            count=Count('id')
        ).order_by('-count')[:5]  # 获取前5名目的地
        
        # 计算总航班数用于计算百分比
        total_destination_count = sum(d['count'] for d in destinations)
        for dest in destinations:
            popular_destinations.append({
                'name': dest['arrival_city'],
                'value': dest['count']
            })
        
        # 如果目的地少于5个，添加"其他"类别
        if len(popular_destinations) < 5:
            other_count = total_flights - sum(d['value'] for d in popular_destinations)
            if other_count > 0:
                popular_destinations.append({
                    'name': '其他',
                    'value': other_count
                })
        
        # 获取航班座位利用率
        domestic_flights = Flight.objects.filter(is_international=False).annotate(
            occupancy=100 * (1 - F('available_seats') / F('capacity'))
        ).aggregate(avg=Avg('occupancy'))['avg'] or 0
        
        international_flights = Flight.objects.filter(is_international=True).annotate(
            occupancy=100 * (1 - F('available_seats') / F('capacity'))
        ).aggregate(avg=Avg('occupancy'))['avg'] or 0
        
        seat_utilization = [
            {'name': '国内航线', 'value': round(domestic_flights)},
            {'name': '国际航线', 'value': round(international_flights)}
        ]
        
        # 获取用户增长趋势
        user_growth_data = []
        for i in range(6, -1, -1):  # 从6天前到今天
            day = today - datetime.timedelta(days=i)
            new_users = User.objects.filter(date_joined__date=day).count()
            user_growth_data.append([day.strftime('%Y-%m-%d'), new_users])
        
        # 订单完成情况
        order_status = Order.objects.values('status').annotate(count=Count('id'))
        order_status_map = {
            'completed': '已完成',
            'paid': '已支付',
            'pending': '待付款',
            'canceled': '已取消',
            'cancelled': '已取消',
            'refunded': '已退款'
        }
        
        order_status_data = []
        for status in order_status:
            status_name = order_status_map.get(status['status'], status['status'])
            order_status_data.append({
                'name': status_name,
                'value': status['count']
            })
        
        # 实时监控数据
        # 使用last_login代替last_activity
        current_online = User.objects.filter(last_login__gte=now() - datetime.timedelta(minutes=15)).count() 
        # 如果没有足够的活跃用户，提供一个合理的估计值
        if current_online < 10:
            current_online = max(total_users // 20, 10)  # 假设约5%的用户在线，至少10人
        
        return Response({
            'stats': {
                'flights': total_flights,
                'flightsGrowth': flights_growth,
                'users': total_users,
                'usersGrowth': users_growth,
                'orders': total_orders,
                'ordersGrowth': orders_growth,
                'revenue': float(total_revenue or 0),  # 确保转换为float
                'revenueGrowth': revenue_growth
            },
            'revenueData': trend,
            'popularDestinations': popular_destinations,
            'seatUtilization': seat_utilization,
            'userGrowthData': user_growth_data,
            'orderStatusData': order_status_data,
            'realtimeStats': {
                'onlineUsers': current_online,
                'activeOrders': Order.objects.filter(status='pending').count(),
                'cpuUsage': 42,  # 模拟值
                'memoryUsage': 68,  # 模拟值 
                'diskUsage': 35   # 模拟值
            }
        })

def calculate_growth(current, previous):
    """计算增长率百分比"""
    if previous == 0:
        return 100.0 if current > 0 else 0.0
    return round((current - previous) / previous * 100, 1)

class FlightAnalytics(APIView):
    """航班数据分析接口，仅管理员可访问"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        if not hasattr(user, 'role') or user.role != 'admin':
            return Response({'detail': '权限不足'}, status=403)
            
        # 获取时间范围参数
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        queryset = Flight.objects.all()
        if start_date:
            queryset = queryset.filter(departure_time__gte=start_date)
        if end_date:
            queryset = queryset.filter(departure_time__lte=end_date)
            
        # 热门航线统计
        popular_routes = queryset.values('departure_city', 'arrival_city')\
            .annotate(count=Count('id'))\
            .order_by('-count')[:10]
            
        # 平均上座率
        flights = queryset.annotate(
            occupancy_rate=100 * (1 - F('available_seats') / F('capacity'))
        ).aggregate(avg_occupancy=Avg('occupancy_rate'))
        
        # 按航线分类的收入
        route_revenue = []
        for route in popular_routes:
            departure = route['departure_city']
            arrival = route['arrival_city']
            flights_ids = queryset.filter(
                departure_city=departure, 
                arrival_city=arrival
            ).values_list('id', flat=True)
            
            revenue = Ticket.objects.filter(
                flight_id__in=flights_ids, 
                status='valid'
            ).aggregate(
                total=Sum('price')
            )['total'] or 0
            
            route_revenue.append({
                'route': f"{departure} - {arrival}",
                'revenue': revenue,
                'flight_count': route['count']
            })
        
        return Response({
            'popular_routes': popular_routes,
            'avg_occupancy_rate': flights['avg_occupancy'],
            'route_revenue': route_revenue
        })
        
class RevenueAnalytics(APIView):
    """收入分析接口，仅管理员可访问"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        if not hasattr(user, 'role') or user.role != 'admin':
            return Response({'detail': '权限不足'}, status=403)
            
        # 获取时间范围参数
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        orders = Order.objects.filter(status='paid')
        if start_date:
            orders = orders.filter(paid_at__date__gte=start_date)
        if end_date:
            orders = orders.filter(paid_at__date__lte=end_date)
            
        # 总收入
        total_revenue = orders.aggregate(total=Sum('total_price'))['total'] or 0
        
        # 按月收入趋势
        monthly_trend = orders.annotate(
            month=TruncMonth('paid_at')
        ).values('month').annotate(
            revenue=Sum('total_price')
        ).order_by('month')
        
        # 将日期转为字符串以便前端使用
        monthly_result = []
        for item in monthly_trend:
            if item['month']:
                monthly_result.append({
                    'month': item['month'].strftime('%Y-%m'),
                    'revenue': item['revenue'] or 0
                })
        
        # 按支付方式收入
        payment_methods = orders.values('payment_method').annotate(
            revenue=Sum('total_price'),
            count=Count('id')
        ).order_by('-revenue')
        
        return Response({
            'total_revenue': total_revenue,
            'monthly_trend': monthly_result,
            'payment_methods': list(payment_methods)
        })
        
class BusinessIntelligence(APIView):
    """商业智能分析接口，仅管理员可访问"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        if not hasattr(user, 'role') or user.role != 'admin':
            return Response({'detail': '权限不足'}, status=403)
            
        # 获取时间范围参数
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        # 计算客户平均价值
        orders = Order.objects.filter(status='paid')
        if start_date:
            orders = orders.filter(paid_at__date__gte=start_date)
        if end_date:
            orders = orders.filter(paid_at__date__lte=end_date)
            
        user_stats = orders.values('user').annotate(
            total_spent=Sum('total_price'),
            order_count=Count('id')
        ).aggregate(
            avg_value=Avg('total_spent'),
            avg_orders=Avg('order_count')
        )
        
        # 销售转化率（假设以访问航班详情为起点，预订为转化）
        # 注意：这里是模拟数据，实际应该结合前端日志
        conversion_rate = {
            'viewed': 1000,  # 模拟数据
            'booked': orders.count(),
            'rate': orders.count() / 1000 * 100 if orders.count() else 0
        }
        
        # 预订提前期分析
        advance_booking = []
        for days in [7, 14, 30, 60, 90]:
            count = Ticket.objects.filter(
                order__status='paid',
                flight__departure_time__gt=F('created_at'),
                flight__departure_time__lte=F('created_at') + datetime.timedelta(days=days)
            ).count()
            advance_booking.append({
                'days': days,
                'count': count,
                'percentage': count / Ticket.objects.filter(order__status='paid').count() * 100 if count else 0
            })
            
        return Response({
            'user_stats': user_stats,
            'conversion_rate': conversion_rate,
            'advance_booking': advance_booking
        })

class DataVisualization(APIView):
    """数据可视化接口，仅管理员可访问"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        if not hasattr(user, 'role') or user.role != 'admin':
            return Response({'detail': '权限不足'}, status=403)
            
        # 各个城市出发/到达的航班数
        city_flights = {}
        departures = Flight.objects.values('departure_city').annotate(count=Count('id'))
        arrivals = Flight.objects.values('arrival_city').annotate(count=Count('id'))
        
        for city in departures:
            if city['departure_city'] not in city_flights:
                city_flights[city['departure_city']] = {'departures': 0, 'arrivals': 0}
            city_flights[city['departure_city']]['departures'] = city['count']
            
        for city in arrivals:
            if city['arrival_city'] not in city_flights:
                city_flights[city['arrival_city']] = {'departures': 0, 'arrivals': 0}
            city_flights[city['arrival_city']]['arrivals'] = city['count']
            
        # 转换为列表格式
        city_data = []
        for city, data in city_flights.items():
            city_data.append({
                'city': city,
                'departures': data['departures'],
                'arrivals': data['arrivals'],
                'total': data['departures'] + data['arrivals']
            })
        city_data.sort(key=lambda x: x['total'], reverse=True)
        
        # 按舱位等级销售分布（假设有舱位等级字段）
        # 注意：这是模拟数据，实际实现需要在Ticket模型中添加cabin_class字段
        cabin_distribution = [
            {'cabin_class': '经济舱', 'count': 1000, 'revenue': 500000},
            {'cabin_class': '商务舱', 'count': 200, 'revenue': 300000},
            {'cabin_class': '头等舱', 'count': 50, 'revenue': 200000}
        ]
        
        # 添加票价区间分布数据
        # 从数据库获取票价数据
        tickets = Ticket.objects.filter(status='confirmed')
        
        # 定义票价区间
        price_ranges = [
            {'min': 0, 'max': 500, 'name': '0-500元'},
            {'min': 500, 'max': 1000, 'name': '500-1000元'},
            {'min': 1000, 'max': 1500, 'name': '1000-1500元'},
            {'min': 1500, 'max': 2000, 'name': '1500-2000元'},
            {'min': 2000, 'max': 9999999, 'name': '2000元以上'}
        ]
        
        # 计算每个区间的票数
        ticket_price_ranges = []
        for price_range in price_ranges:
            count = tickets.filter(price__gte=price_range['min'], price__lt=price_range['max']).count()
            ticket_price_ranges.append({
                'name': price_range['name'],
                'value': count
            })
            
        # 如果没有数据，提供一些默认数据以便前端显示
        if sum(item['value'] for item in ticket_price_ranges) == 0:
            ticket_price_ranges = [
                {'name': '0-500元', 'value': 120},
                {'name': '500-1000元', 'value': 350},
                {'name': '1000-1500元', 'value': 280},
                {'name': '1500-2000元', 'value': 180},
                {'name': '2000元以上', 'value': 70}
            ]
            
        return Response({
            'city_data': city_data[:10],  # 只返回前10个城市
            'cabin_distribution': cabin_distribution,
            'ticket_price_ranges': ticket_price_ranges,  # 添加票价区间数据
            'payment_methods': [  # 添加支付方式数据
                {'name': '支付宝', 'value': 450},
                {'name': '微信支付', 'value': 380},
                {'name': '银行卡', 'value': 220},
                {'name': '信用卡', 'value': 150}
            ]
        })

class SystemLog(APIView):
    """系统日志接口，仅管理员可访问"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        if not hasattr(user, 'role') or user.role != 'admin':
            return Response({'detail': '权限不足'}, status=403)
        
        # 这里应该是从实际日志系统获取数据
        # 目前返回模拟数据作为示例
        system_logs = [
            {
                'timestamp': '2023-04-01T12:34:56',
                'level': 'INFO',
                'message': '系统启动',
                'source': 'system'
            },
            {
                'timestamp': '2023-04-01T13:45:12',
                'level': 'ERROR',
                'message': '数据库连接失败',
                'source': 'database'
            },
            {
                'timestamp': '2023-04-01T14:22:45',
                'level': 'WARNING',
                'message': '用户尝试访问未授权资源',
                'source': 'security'
            }
        ]
        
        return Response({
            'logs': system_logs,
            'total': len(system_logs)
        })

class SalesTrend(APIView):
    """销售趋势分析接口"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        if not hasattr(user, 'role') or user.role != 'admin':
            return Response({'detail': '权限不足'}, status=403)
        
        # 获取时间范围参数
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        # 获取时间单位参数(day, week, month)
        time_unit = request.query_params.get('time_unit', 'day')
        
        # 准备销售数据
        orders = Order.objects.filter(status='paid')
        if start_date:
            orders = orders.filter(created_at__gte=start_date)
        if end_date:
            orders = orders.filter(created_at__lte=end_date)
        
        # 根据时间单位聚合数据
        if time_unit == 'week':
            # 按周聚合
            sales_data = orders.annotate(
                date=TruncWeek('created_at')
            ).values('date').annotate(
                revenue=Sum('total_price'),
                count=Count('id')
            ).order_by('date')
        elif time_unit == 'month':
            # 按月聚合
            sales_data = orders.annotate(
                date=TruncMonth('created_at')
            ).values('date').annotate(
                revenue=Sum('total_price'),
                count=Count('id')
            ).order_by('date')
        else:
            # 默认按天聚合
            sales_data = orders.annotate(
                date=TruncDay('created_at')
            ).values('date').annotate(
                revenue=Sum('total_price'),
                count=Count('id')
            ).order_by('date')
        
        # 格式化结果
        result = []
        for item in sales_data:
            result.append({
                'date': item['date'].strftime('%Y-%m-%d'),
                'revenue': float(item['revenue']) if item['revenue'] else 0,
                'count': item['count']
            })
        
        return Response({
            'sales_trend': result,
            'time_unit': time_unit
        })

class UserAnalytics(APIView):
    """用户分析接口"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        if not hasattr(user, 'role') or user.role != 'admin':
            return Response({'detail': '权限不足'}, status=403)
        
        # 用户年龄分布（假设有age字段）
        # 注意：这是模拟数据，实际实现需要在User模型中添加age或出生日期字段
        age_distribution = [
            {'age_range': '18岁以下', 'count': 50},
            {'age_range': '18-25岁', 'count': 280},
            {'age_range': '26-35岁', 'count': 350},
            {'age_range': '36-50岁', 'count': 220},
            {'age_range': '50岁以上', 'count': 100}
        ]
        
        # 用户属性雷达图数据
        user_attributes = {
            'indicators': [
                {'name': '消费能力', 'max': 100},
                {'name': '出行频率', 'max': 100},
                {'name': '忠诚度', 'max': 100},
                {'name': '对价格敏感度', 'max': 100},
                {'name': '对服务要求', 'max': 100}
            ],
            'series': [
                {
                    'name': '商务客户',
                    'value': [85, 90, 70, 40, 85]
                },
                {
                    'name': '休闲旅客',
                    'value': [50, 45, 60, 80, 65]
                }
            ]
        }
        
        # 用户增长趋势
        # 注意：这需要User模型中的date_joined字段
        end_date = now().date()
        start_date = end_date - datetime.timedelta(days=365)  # 过去一年
        
        # 按月聚合新用户数据
        user_growth = []
        current_date = start_date.replace(day=1)  # 从开始月份的第一天开始
        
        while current_date <= end_date:
            next_month = current_date.month + 1 if current_date.month < 12 else 1
            next_month_year = current_date.year if current_date.month < 12 else current_date.year + 1
            next_month_date = current_date.replace(year=next_month_year, month=next_month, day=1)
            
            # 当月新注册用户数
            new_users = User.objects.filter(
                date_joined__gte=current_date,
                date_joined__lt=next_month_date
            ).count()
            
            # 当月活跃用户数（假设有last_login字段）
            active_users = User.objects.filter(
                last_login__gte=current_date,
                last_login__lt=next_month_date
            ).count()
            
            user_growth.append({
                'month': current_date.strftime('%Y-%m'),
                'new_users': new_users,
                'active_users': active_users
            })
            
            # 移至下个月
            current_date = next_month_date
        
        return Response({
            'age_distribution': age_distribution,
            'user_attributes': user_attributes,
            'user_growth': user_growth
        })

class FlightVisualization(APIView):
    """航班可视化分析接口"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        if not hasattr(user, 'role') or user.role != 'admin':
            return Response({'detail': '权限不足'}, status=403)
        
        # 获取航线载客率数据
        routes = Flight.objects.values('departure_city', 'arrival_city').annotate(
            avg_occupancy=Avg(100 * (1 - F('available_seats') / F('capacity'))),
            flight_count=Count('id')
        ).order_by('-flight_count')[:10]  # 取前10条热门航线
        
        flight_load = []
        for route in routes:
            flight_load.append({
                'name': f"{route['departure_city']}-{route['arrival_city']}",
                'value': round(route['avg_occupancy']) if route['avg_occupancy'] else 0
            })
        
        # 航班准点率数据（假设有actual_departure_time和scheduled_departure_time字段）
        # 这里使用模拟数据，实际实现需要在Flight模型中添加相关字段
        on_time_data = [
            {'name': '北京-上海', 'value': 87},
            {'name': '上海-广州', 'value': 92},
            {'name': '北京-成都', 'value': 84},
            {'name': '广州-深圳', 'value': 95},
            {'name': '成都-西安', 'value': 90}
        ]
        
        # 航班地图数据（获取所有航线的坐标信息）
        # 注意：这需要城市坐标信息，这里使用模拟数据
        city_coordinates = {
            '北京': [116.405285, 39.904989],
            '上海': [121.472644, 31.231706],
            '广州': [113.280637, 23.125178],
            '深圳': [114.085947, 22.547],
            '成都': [104.065735, 30.659462],
            '西安': [108.948024, 34.263161]
        }
        
        # 构建航线数据
        route_lines = []
        for route in routes:
            dep = route['departure_city']
            arr = route['arrival_city']
            
            # 检查两个城市是否都有坐标
            if dep in city_coordinates and arr in city_coordinates:
                route_lines.append({
                    'from': dep,
                    'to': arr,
                    'coords': [city_coordinates[dep], city_coordinates[arr]],
                    'value': route['flight_count']
                })
        
        return Response({
            'flight_load': flight_load,
            'on_time_data': on_time_data,
            'route_map': {
                'cities': city_coordinates,
                'routes': route_lines
            }
        })

class SalesPrediction(APIView):
    """销售预测分析接口"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        if not hasattr(user, 'role') or user.role != 'admin':
            return Response({'detail': '权限不足'}, status=403)
        
        # 获取预测周期参数(week, month, quarter)
        prediction_period = request.query_params.get('period', 'week')
        
        # 获取历史销售数据作为预测基础
        end_date = now().date()
        
        if prediction_period == 'month':
            # 预测未来30天
            days_to_predict = 30
            # 使用过去90天数据预测
            start_date = end_date - datetime.timedelta(days=90)
        elif prediction_period == 'quarter':
            # 预测未来90天
            days_to_predict = 90
            # 使用过去一年数据预测
            start_date = end_date - datetime.timedelta(days=365)
        else:
            # 默认预测未来7天
            days_to_predict = 7
            # 使用过去30天数据预测
            start_date = end_date - datetime.timedelta(days=30)
        
        # 获取历史订单数据
        historical_orders = Order.objects.filter(
            created_at__gte=start_date,
            created_at__lte=end_date,
            status='paid'
        )
        
        # 按天聚合历史销售数据
        historical_data = historical_orders.annotate(
            date=TruncDay('created_at')
        ).values('date').annotate(
            revenue=Sum('total_price'),
            orders=Count('id')
        ).order_by('date')
        
        # 准备历史数据列表
        dates = []
        revenues = []
        order_counts = []
        
        for item in historical_data:
            dates.append(item['date'].strftime('%Y-%m-%d'))
            revenues.append(float(item['revenue'] or 0))
            order_counts.append(item['orders'])
        
        # 在实际应用中，这里应该使用统计模型进行预测
        # 这里简单使用移动平均+随机波动模拟预测结果
        
        # 计算移动平均
        if len(revenues) > 0:
            avg_revenue = sum(revenues) / len(revenues)
            avg_orders = sum(order_counts) / len(order_counts)
        else:
            avg_revenue = 0
            avg_orders = 0
        
        # 生成预测数据
        prediction_dates = []
        predicted_revenues = []
        predicted_orders = []
        
        import random
        current_date = end_date + datetime.timedelta(days=1)
        
        for _ in range(days_to_predict):
            # 增加一点随机波动（±15%）
            revenue_fluctuation = random.uniform(0.85, 1.15)
            order_fluctuation = random.uniform(0.85, 1.15)
            
            predicted_revenue = avg_revenue * revenue_fluctuation
            predicted_order_count = int(avg_orders * order_fluctuation)
            
            prediction_dates.append(current_date.strftime('%Y-%m-%d'))
            predicted_revenues.append(round(predicted_revenue, 2))
            predicted_orders.append(predicted_order_count)
            
            current_date += datetime.timedelta(days=1)
        
        # 计算总预测结果与增长率
        total_historical_revenue = sum(revenues)
        total_historical_orders = sum(order_counts)
        total_predicted_revenue = sum(predicted_revenues)
        total_predicted_orders = sum(predicted_orders)
        
        # 计算上一个相同周期的历史数据
        previous_start = start_date - datetime.timedelta(days=days_to_predict)
        previous_end = end_date - datetime.timedelta(days=days_to_predict)
        
        previous_orders = Order.objects.filter(
            created_at__gte=previous_start,
            created_at__lte=previous_end,
            status='paid'
        )
        
        previous_revenue = previous_orders.aggregate(total=Sum('total_price'))['total'] or 0
        previous_order_count = previous_orders.count()
        
        # 计算增长率
        revenue_growth = calculate_growth(total_predicted_revenue, previous_revenue)
        order_growth = calculate_growth(total_predicted_orders, previous_order_count)
        
        # 计算平均订单价值和增长率
        avg_order_value = total_predicted_revenue / total_predicted_orders if total_predicted_orders else 0
        previous_avg_order_value = previous_revenue / previous_order_count if previous_order_count else 0
        aov_growth = calculate_growth(avg_order_value, previous_avg_order_value)
        
        return Response({
            'historical_data': {
                'dates': dates,
                'revenues': revenues,
                'order_counts': order_counts
            },
            'prediction_data': {
                'dates': prediction_dates,
                'revenues': predicted_revenues,
                'order_counts': predicted_orders
            },
            'summary': {
                'total_revenue': total_predicted_revenue,
                'total_orders': total_predicted_orders,
                'average_order_value': avg_order_value,
                'growth_rate': revenue_growth,
                'order_growth_rate': order_growth,
                'aov_growth_rate': aov_growth
            }
        })

class RouteAnalytics(APIView):
    """航线收益分析接口"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        if not hasattr(user, 'role') or user.role != 'admin':
            return Response({'detail': '权限不足'}, status=403)
        
        # 获取分析指标参数(revenue, profit, roi)
        metric = request.query_params.get('metric', 'revenue')
        
        # 获取热门航线数据
        routes = Flight.objects.values('departure_city', 'arrival_city').annotate(
            flight_count=Count('id'),
            revenue=Sum(F('price') * (F('capacity') - F('available_seats')))
        ).order_by('-flight_count')[:10]  # 取前10条热门航线
        
        # 处理不同指标
        route_data = []
        for route in routes:
            # 模拟成本数据（实际应该来自数据库）
            # 假设成本为收入的60%-80%（不同航线成本率不同）
            import random
            cost_ratio = random.uniform(0.6, 0.8)
            cost = float(route['revenue']) * cost_ratio if route['revenue'] else 0
            profit = float(route['revenue']) - cost if route['revenue'] else 0
            roi = (profit / cost) * 100 if cost > 0 else 0
            
            route_name = f"{route['departure_city']}-{route['arrival_city']}"
            
            if metric == 'profit':
                route_data.append({
                    'route': route_name,
                    'value': round(profit, 2),
                    'flights': route['flight_count']
                })
            elif metric == 'roi':
                route_data.append({
                    'route': route_name,
                    'value': round(roi, 2),
                    'flights': route['flight_count']
                })
            else:  # 默认revenue
                route_data.append({
                    'route': route_name,
                    'value': float(route['revenue']) if route['revenue'] else 0,
                    'flights': route['flight_count']
                })
        
        # 按指标值排序
        route_data.sort(key=lambda x: x['value'], reverse=True)
        
        return Response({
            'metric': metric,
            'route_data': route_data
        })

class PriceElasticity(APIView):
    """价格弹性分析接口"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        if not hasattr(user, 'role') or user.role != 'admin':
            return Response({'detail': '权限不足'}, status=403)
        
        # 获取航线参数
        route = request.query_params.get('route', 'beijing-shanghai')
        
        # 在实际应用中，应该通过分析历史价格变化和销量数据来计算价格弹性
        # 这里使用模拟数据
        
        # 价格区间和对应的销量数据（模拟）
        price_points = [800, 1000, 1200, 1400, 1600, 1800, 2000]
        sales_volume = [95, 88, 76, 65, 54, 42, 30]  # 越贵卖得越少
        
        # 计算各个点的弹性值
        elasticity_data = []
        for i in range(1, len(price_points)):
            price_change = (price_points[i] - price_points[i-1]) / price_points[i-1]
            volume_change = (sales_volume[i] - sales_volume[i-1]) / sales_volume[i-1]
            elasticity = volume_change / price_change if price_change != 0 else 0
            
            elasticity_data.append({
                'price': price_points[i],
                'volume': sales_volume[i],
                'elasticity': abs(round(elasticity, 2))  # 取绝对值
            })
        
        # 计算最优定价点（这通常是弹性接近于1的价格点）
        # 实际中需要更复杂的模型
        optimal_price = 0
        min_distance_to_one = float('inf')
        
        for item in elasticity_data:
            distance_to_one = abs(item['elasticity'] - 1.0)
            if distance_to_one < min_distance_to_one:
                min_distance_to_one = distance_to_one
                optimal_price = item['price']
        
        return Response({
            'route': route,
            'price_volume_data': [
                {'price': price_points[i], 'volume': sales_volume[i]} 
                for i in range(len(price_points))
            ],
            'elasticity_data': elasticity_data,
            'optimal_price': optimal_price
        })

class CustomerLTV(APIView):
    """客户终身价值分析接口"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        if not hasattr(user, 'role') or user.role != 'admin':
            return Response({'detail': '权限不足'}, status=403)
        
        # 在实际应用中，应该通过计算客户平均订单价值、购买频率和客户留存率来计算LTV
        # 这里使用模拟数据
        
        # 按用户类型划分的LTV数据
        user_segments = [
            {
                'segment': '商务旅客',
                'ltv': 12500,
                'avg_order_value': 2500,
                'purchase_frequency': 5,  # 每年
                'retention_rate': 0.85,   # 留存率85%
                'percentage': 20          # 占用户总数的百分比
            },
            {
                'segment': '经常出行者',
                'ltv': 8000,
                'avg_order_value': 2000,
                'purchase_frequency': 4,
                'retention_rate': 0.75,
                'percentage': 30
            },
            {
                'segment': '休闲旅客',
                'ltv': 4000,
                'avg_order_value': 1600,
                'purchase_frequency': 2.5,
                'retention_rate': 0.65,
                'percentage': 40
            },
            {
                'segment': '偶尔出行者',
                'ltv': 1500,
                'avg_order_value': 1500,
                'purchase_frequency': 1,
                'retention_rate': 0.40,
                'percentage': 10
            }
        ]
        
        # 计算平均LTV
        weighted_ltv_sum = sum(segment['ltv'] * segment['percentage'] for segment in user_segments)
        total_percentage = sum(segment['percentage'] for segment in user_segments)
        avg_ltv = weighted_ltv_sum / total_percentage if total_percentage > 0 else 0
        
        return Response({
            'user_segments': user_segments,
            'average_ltv': avg_ltv
        })

class SeasonalityAnalysis(APIView):
    """季节性分析接口"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        if not hasattr(user, 'role') or user.role != 'admin':
            return Response({'detail': '权限不足'}, status=403)
        
        # 获取航线参数
        route = request.query_params.get('route', 'beijing-shanghai')
        
        # 在实际应用中，应该分析最近几年同一航线在不同月份的销售数据
        # 这里使用模拟数据
        
        # 一年12个月的销售指标数据
        months = ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']
        
        # 不同航线的季节性数据
        route_data = {
            'beijing-shanghai': {
                'load_factor': [75, 68, 82, 85, 89, 92, 95, 96, 90, 88, 83, 78],  # 载客率
                'ticket_price': [1200, 1150, 1300, 1350, 1400, 1500, 1600, 1650, 1400, 1350, 1300, 1250]  # 票价
            },
            'beijing-guangzhou': {
                'load_factor': [80, 72, 78, 82, 85, 88, 92, 94, 86, 84, 82, 85],
                'ticket_price': [1800, 1700, 1750, 1800, 1850, 1900, 2000, 2100, 1900, 1850, 1800, 1850]
            },
            'shanghai-chengdu': {
                'load_factor': [76, 70, 75, 80, 84, 88, 90, 92, 85, 82, 78, 76],
                'ticket_price': [1500, 1450, 1500, 1550, 1600, 1650, 1700, 1750, 1600, 1550, 1500, 1500]
            }
        }
        
        # 获取选定航线的数据或默认数据
        selected_data = route_data.get(route, route_data['beijing-shanghai'])
        
        # 计算季节性指标
        peak_month_index = selected_data['load_factor'].index(max(selected_data['load_factor']))
        peak_month = months[peak_month_index]
        low_month_index = selected_data['load_factor'].index(min(selected_data['load_factor']))
        low_month = months[low_month_index]
        
        seasonality_ratio = max(selected_data['load_factor']) / min(selected_data['load_factor']) if min(selected_data['load_factor']) > 0 else 0
        
        return Response({
            'route': route,
            'months': months,
            'load_factor': selected_data['load_factor'],
            'ticket_price': selected_data['ticket_price'],
            'peak_month': peak_month,
            'low_month': low_month,
            'seasonality_ratio': round(seasonality_ratio, 2),
            'available_routes': list(route_data.keys())
        })

class AnomalyDetection(APIView):
    """异常检测分析接口"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        if not hasattr(user, 'role') or user.role != 'admin':
            return Response({'detail': '权限不足'}, status=403)
        
        # 在实际应用中，应该使用统计方法或机器学习模型来检测销售数据中的异常
        # 这里使用模拟数据
        
        # 获取过去30天的销售数据
        end_date = now().date()
        start_date = end_date - datetime.timedelta(days=30)
        
        # 模拟每日销售数据和标准差
        dates = []
        sales = []
        expected_values = []
        upper_bounds = []
        lower_bounds = []
        
        # 生成日期序列
        current_date = start_date
        while current_date <= end_date:
            dates.append(current_date.strftime('%Y-%m-%d'))
            current_date += datetime.timedelta(days=1)
        
        # 生成模拟数据
        import random
        import numpy as np
        
        baseline = 50000  # 基准日销售额
        std_dev = baseline * 0.15  # 标准差
        
        for i in range(len(dates)):
            # 正常范围内的随机波动
            expected = baseline + random.uniform(-baseline*0.1, baseline*0.1)
            expected_values.append(expected)
            
            # 上下限（3个标准差）
            upper_bounds.append(expected + 3 * std_dev)
            lower_bounds.append(max(0, expected - 3 * std_dev))
            
            # 有10%的概率生成异常值
            if random.random() < 0.1:
                # 生成异常值
                if random.random() < 0.5:
                    # 异常高值
                    sales.append(expected + random.uniform(3 * std_dev, 5 * std_dev))
                else:
                    # 异常低值
                    sales.append(max(0, expected - random.uniform(3 * std_dev, 5 * std_dev)))
            else:
                # 正常值
                sales.append(expected + random.normalvariate(0, std_dev))
        
        # 检测异常
        anomalies = []
        for i in range(len(sales)):
            if sales[i] > upper_bounds[i] or sales[i] < lower_bounds[i]:
                severity = 'high' if abs(sales[i] - expected_values[i]) > 4 * std_dev else 'medium'
                anomalies.append({
                    'date': dates[i],
                    'value': round(sales[i], 2),
                    'expected': round(expected_values[i], 2),
                    'deviation': round((sales[i] - expected_values[i]) / expected_values[i] * 100, 2),
                    'severity': severity,
                    'description': f"销售额{'高于' if sales[i] > expected_values[i] else '低于'}预期 ({round(abs(sales[i] - expected_values[i]) / expected_values[i] * 100, 2)}%)"
                })
        
        return Response({
            'dates': dates,
            'sales': [round(x, 2) for x in sales],
            'expected_values': [round(x, 2) for x in expected_values],
            'upper_bounds': [round(x, 2) for x in upper_bounds],
            'lower_bounds': [round(x, 2) for x in lower_bounds],
            'anomalies': anomalies
        })

class SalesAnalytics(APIView):
    """销售分析接口"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        if not hasattr(user, 'role') or user.role != 'admin':
            return Response({'detail': '权限不足'}, status=403)
        
        # 获取时间范围参数
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        # 获取时间单位参数(day, week, month)
        time_unit = request.query_params.get('time_unit', 'day')
        
        # 准备销售数据
        orders = Order.objects.filter(status='paid')
        if start_date:
            orders = orders.filter(created_at__gte=start_date)
        if end_date:
            orders = orders.filter(created_at__lte=end_date)
        
        # 根据时间单位聚合数据
        if time_unit == 'week':
            # 按周聚合
            sales_data = orders.annotate(
                date=TruncWeek('created_at')
            ).values('date').annotate(
                revenue=Sum('total_price'),
                order_count=Count('id'),
                avg_order_value=Avg('total_price')
            ).order_by('date')
        elif time_unit == 'month':
            # 按月聚合
            sales_data = orders.annotate(
                date=TruncMonth('created_at')
            ).values('date').annotate(
                revenue=Sum('total_price'),
                order_count=Count('id'),
                avg_order_value=Avg('total_price')
            ).order_by('date')
        else:
            # 默认按天聚合
            sales_data = orders.annotate(
                date=TruncDay('created_at')
            ).values('date').annotate(
                revenue=Sum('total_price'),
                order_count=Count('id'),
                avg_order_value=Avg('total_price')
            ).order_by('date')
        
        # 计算同比增长率（假设有去年同期数据）
        # 这里使用模拟数据
        import random
        for item in sales_data:
            item['growth_rate'] = round(random.uniform(-15, 25), 2)  # 随机增长率
            
        # 格式化结果
        result = []
        for item in sales_data:
            result.append({
                'date': item['date'].strftime('%Y-%m-%d'),
                'revenue': float(item['revenue']) if item['revenue'] else 0,
                'order_count': item['order_count'],
                'avg_order_value': float(item['avg_order_value']) if item['avg_order_value'] else 0,
                'growth_rate': item.get('growth_rate', 0)
            })
        
        return Response({
            'sales_trend': result,
            'time_unit': time_unit
        })

class CustomerSegments(APIView):
    """客户分群分析接口"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        if not hasattr(user, 'role') or user.role != 'admin':
            return Response({'detail': '权限不足'}, status=403)
        
        # 在实际应用中，应该根据用户的订单历史、消费金额等进行客户分群
        # 这里使用模拟数据
        
        segments = [
            {
                'name': '商务精英',
                'value': 25,
                'avg_spend': 2800,
                'avg_frequency': 8.5,  # 每年平均乘坐航班次数
                'attributes': {
                    '年龄段': '30-45岁',
                    '偏好': '商务舱、头等舱',
                    '出行特点': '短途频繁、多为工作日出行',
                    '敏感因素': '时间 > 价格'
                }
            },
            {
                'name': '休闲家庭',
                'value': 35,
                'avg_spend': 1600,
                'avg_frequency': 3.2,
                'attributes': {
                    '年龄段': '25-40岁',
                    '偏好': '经济舱',
                    '出行特点': '节假日出行、多人同行',
                    '敏感因素': '价格 > 时间'
                }
            },
            {
                'name': '学生群体',
                'value': 20,
                'avg_spend': 1100,
                'avg_frequency': 4.5,
                'attributes': {
                    '年龄段': '18-25岁',
                    '偏好': '经济舱、特价票',
                    '出行特点': '学期初末、假期',
                    '敏感因素': '价格 >> 时间'
                }
            },
            {
                'name': '退休旅行者',
                'value': 10,
                'avg_spend': 2200,
                'avg_frequency': 2.8,
                'attributes': {
                    '年龄段': '60岁以上',
                    '偏好': '舒适座位、特殊服务',
                    '出行特点': '淡季、长途',
                    '敏感因素': '服务 > 时间 > 价格'
                }
            },
            {
                'name': '其他',
                'value': 10,
                'avg_spend': 1500,
                'avg_frequency': 1.5,
                'attributes': {
                    '特点': '混合群体',
                }
            }
        ]
        
        return Response({
            'segments': segments,
            'total_users': sum(segment['value'] for segment in segments)
        })

class RouteMap(APIView):
    """航线地图分析接口"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        if not hasattr(user, 'role') or user.role != 'admin':
            return Response({'detail': '权限不足'}, status=403)
        
        # 获取所有航线数据
        routes = Flight.objects.values('departure_city', 'arrival_city').annotate(
            count=Count('id'),
            revenue=Sum(F('price') * (F('capacity') - F('available_seats')))
        ).order_by('-count')
        
        # 城市坐标数据（实际应该从地理数据库获取）
        city_coordinates = {
            '北京': [116.405285, 39.904989],
            '上海': [121.472644, 31.231706],
            '广州': [113.280637, 23.125178],
            '深圳': [114.085947, 22.547],
            '成都': [104.065735, 30.659462],
            '西安': [108.948024, 34.263161],
            '杭州': [120.153576, 30.287459],
            '重庆': [106.504962, 29.533155],
            '南京': [118.767413, 32.041544],
            '武汉': [114.298572, 30.584355]
        }
        
        # 获取城市列表
        cities = set()
        for route in routes:
            cities.add(route['departure_city'])
            cities.add(route['arrival_city'])
        
        # 计算每个城市的航班总数
        city_traffic = {}
        for city in cities:
            departures = Flight.objects.filter(departure_city=city).count()
            arrivals = Flight.objects.filter(arrival_city=city).count()
            city_traffic[city] = departures + arrivals
        
        # 生成航线数据
        route_data = []
        for route in routes:
            dep = route['departure_city']
            arr = route['arrival_city']
            
            # 如果有坐标信息（如果没有，可以考虑使用地理编码服务）
            if dep in city_coordinates and arr in city_coordinates:
                route_data.append({
                    'route': f"{dep}-{arr}",
                    'from': dep,
                    'to': arr,
                    'coords': [city_coordinates[dep], city_coordinates[arr]],
                    'count': route['count'],
                    'revenue': float(route['revenue']) if route['revenue'] else 0
                })
        
        city_data = []
        for city, traffic in city_traffic.items():
            if city in city_coordinates:
                city_data.append({
                    'name': city,
                    'coords': city_coordinates[city],
                    'traffic': traffic,
                    'value': traffic
                })
        
        return Response({
            'routes': route_data,
            'cities': city_data
        })

class CustomerLoyalty(APIView):
    """客户忠诚度分析接口"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        if not hasattr(user, 'role') or user.role != 'admin':
            return Response({'detail': '权限不足'}, status=403)
        
        # 在实际应用中，应该根据用户的复购率、会员等级、积分情况等分析忠诚度
        # 这里使用模拟数据
        
        # 忠诚度等级分布
        loyalty_levels = [
            {'name': '钻石会员', 'value': 5, 'retention_rate': 92},
            {'name': '白金会员', 'value': 10, 'retention_rate': 85},
            {'name': '金卡会员', 'value': 15, 'retention_rate': 78},
            {'name': '银卡会员', 'value': 30, 'retention_rate': 65},
            {'name': '普通会员', 'value': 40, 'retention_rate': 45}
        ]
        
        # 忠诚度随时间变化的趋势（模拟数据）
        months = ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']
        retention_trend = [68, 67, 70, 72, 73, 75, 78, 80, 79, 77, 76, 79]  # 月度留存率
        
        # 忠诚度与消费关系
        loyalty_spending = [
            {'loyalty_score': 10, 'avg_spending': 800},
            {'loyalty_score': 20, 'avg_spending': 1200},
            {'loyalty_score': 30, 'avg_spending': 1500},
            {'loyalty_score': 40, 'avg_spending': 1800},
            {'loyalty_score': 50, 'avg_spending': 2100},
            {'loyalty_score': 60, 'avg_spending': 2400},
            {'loyalty_score': 70, 'avg_spending': 2800},
            {'loyalty_score': 80, 'avg_spending': 3200},
            {'loyalty_score': 90, 'avg_spending': 3800},
            {'loyalty_score': 100, 'avg_spending': 4500}
        ]
        
        return Response({
            'loyalty_levels': loyalty_levels,
            'retention_trend': {
                'months': months,
                'rates': retention_trend
            },
            'loyalty_spending': loyalty_spending,
            'overall_retention_rate': sum(retention_trend) / len(retention_trend)
        })

class PivotData(APIView):
    """数据透视表接口"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        if not hasattr(user, 'role') or user.role != 'admin':
            return Response({'detail': '权限不足'}, status=403)
        
        # 获取维度和指标参数
        dimension = request.query_params.get('dimension', 'flight')  # flight, city, userType, paymentMethod
        metric = request.query_params.get('metric', 'revenue')  # revenue, orders, averageValue, refundRate
        
        # 在实际应用中，应该根据参数从数据库聚合数据
        # 这里使用模拟数据
        
        pivot_data = []
        
        if dimension == 'flight':
            # 按航班号维度
            flights = ['CA1234', 'MU5678', 'CZ9012', 'HU3456', 'FM7890', 
                      'CA5432', 'MU9876', 'CZ5432', 'HU1098', 'FM7654']
            for flight in flights:
                # 随机生成数据
                value = random.uniform(80000, 500000) if metric == 'revenue' else \
                        random.randint(100, 500) if metric == 'orders' else \
                        random.uniform(800, 3000) if metric == 'averageValue' else \
                        random.uniform(0.01, 0.15)  # refundRate
                
                pivot_data.append({
                    'dimension': flight,
                    'value': round(value, 2 if metric in ['revenue', 'averageValue', 'refundRate'] else 0),
                    'previousValue': round(value * random.uniform(0.8, 1.2), 2 if metric in ['revenue', 'averageValue', 'refundRate'] else 0),
                    'trend': round((random.uniform(-20, 30)), 2),
                    'percentage': round(random.uniform(1, 20), 2)
                })
        
        elif dimension == 'city':
            # 按城市维度
            cities = ['北京', '上海', '广州', '深圳', '成都', '武汉', '西安', '重庆', '杭州', '南京']
            for city in cities:
                value = random.uniform(500000, 2500000) if metric == 'revenue' else \
                        random.randint(800, 5000) if metric == 'orders' else \
                        random.uniform(1000, 2500) if metric == 'averageValue' else \
                        random.uniform(0.02, 0.12)  # refundRate
                
                pivot_data.append({
                    'dimension': city,
                    'value': round(value, 2 if metric in ['revenue', 'averageValue', 'refundRate'] else 0),
                    'previousValue': round(value * random.uniform(0.85, 1.15), 2 if metric in ['revenue', 'averageValue', 'refundRate'] else 0),
                    'trend': round((random.uniform(-15, 25)), 2),
                    'percentage': round(random.uniform(5, 25), 2)
                })
        
        elif dimension == 'userType':
            # 按用户类型维度
            user_types = ['商务旅客', '休闲旅客', '家庭出行', '学生', '老年人', '其他']
            for user_type in user_types:
                value = random.uniform(300000, 1500000) if metric == 'revenue' else \
                        random.randint(300, 2000) if metric == 'orders' else \
                        random.uniform(900, 3500) if metric == 'averageValue' else \
                        random.uniform(0.01, 0.18)  # refundRate
                
                pivot_data.append({
                    'dimension': user_type,
                    'value': round(value, 2 if metric in ['revenue', 'averageValue', 'refundRate'] else 0),
                    'previousValue': round(value * random.uniform(0.9, 1.1), 2 if metric in ['revenue', 'averageValue', 'refundRate'] else 0),
                    'trend': round((random.uniform(-12, 20)), 2),
                    'percentage': round(random.uniform(10, 35), 2)
                })
        
        else:  # paymentMethod
            # 按支付方式维度
            payment_methods = ['支付宝', '微信支付', '银联', '信用卡', '储蓄卡', '其他']
            for method in payment_methods:
                value = random.uniform(250000, 1800000) if metric == 'revenue' else \
                        random.randint(250, 2500) if metric == 'orders' else \
                        random.uniform(1000, 3000) if metric == 'averageValue' else \
                        random.uniform(0.01, 0.1)  # refundRate
                
                pivot_data.append({
                    'dimension': method,
                    'value': round(value, 2 if metric in ['revenue', 'averageValue', 'refundRate'] else 0),
                    'previousValue': round(value * random.uniform(0.9, 1.1), 2 if metric in ['revenue', 'averageValue', 'refundRate'] else 0),
                    'trend': round((random.uniform(-10, 18)), 2),
                    'percentage': round(random.uniform(8, 30), 2)
                })
        
        # 排序
        pivot_data.sort(key=lambda x: x['value'], reverse=True)
        
        # 指标名称映射
        metric_labels = {
            'revenue': '销售额',
            'orders': '订单数',
            'averageValue': '平均客单价',
            'refundRate': '退票率'
        }
        
        return Response({
            'dimension': dimension,
            'metric': metric,
            'metric_label': metric_labels.get(metric, metric),
            'data': pivot_data
        })

class RealtimeData(APIView):
    """实时数据监控接口"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        if not hasattr(user, 'role') or user.role != 'admin':
            return Response({'detail': '权限不足'}, status=403)
        
        # 在实际应用中，应该从缓存或实时计算获取这些数据
        # 这里使用模拟数据
        
        # 当前在线用户数
        online_users = random.randint(80, 300)
        
        # 实时转化率
        conversion_rate = round(random.uniform(2.5, 8.5), 2)
        
        # 每分钟搜索次数
        searches_per_minute = random.randint(15, 80)
        
        # 生成过去30分钟的历史数据
        timestamps = []
        online_history = []
        conversion_history = []
        search_history = []
        
        current_time = now()
        for i in range(30, 0, -1):
            timestamp = (current_time - datetime.timedelta(minutes=i)).strftime('%H:%M')
            timestamps.append(timestamp)
            
            # 生成历史数据点，添加一些波动
            online_history.append(max(10, online_users + random.randint(-50, 50)))
            conversion_history.append(max(0.1, conversion_rate + random.uniform(-2.0, 2.0)))
            search_history.append(max(5, searches_per_minute + random.randint(-15, 15)))
        
        # 添加当前数据点
        timestamps.append(current_time.strftime('%H:%M'))
        online_history.append(online_users)
        conversion_history.append(conversion_rate)
        search_history.append(searches_per_minute)
        
        # 实时订单统计
        recent_order_count = random.randint(5, 30)  # 最近10分钟的订单数
        pending_payments = random.randint(2, 15)  # 待支付订单
        
        return Response({
            'current': {
                'online_users': online_users,
                'conversion_rate': conversion_rate,
                'searches_per_minute': searches_per_minute,
                'recent_order_count': recent_order_count,
                'pending_payments': pending_payments,
                'timestamp': current_time.strftime('%Y-%m-%d %H:%M:%S')
            },
            'history': {
                'timestamps': timestamps,
                'online_users': online_history,
                'conversion_rate': conversion_history,
                'searches_per_minute': search_history
            }
        }) 