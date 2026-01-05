import datetime
import random

from django.db.models import Sum, Count, Avg, F
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth
from django.utils.timezone import now
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import User
from booking.models import Order, Ticket
from flight.models import Flight

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
        
        return Response({
            'stats': {
                'flights': total_flights,
                'flightsGrowth': flights_growth,
                'users': total_users,
                'usersGrowth': users_growth,
                'orders': total_orders,
                'ordersGrowth': orders_growth,
                'revenue': float(total_revenue or 0),
                'revenueGrowth': revenue_growth
            },
            'revenueData': trend,
            'popularDestinations': popular_destinations,
            'seatUtilization': seat_utilization,
            'userGrowthData': user_growth_data,
            'orderStatusData': order_status_data
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
        
        # 按舱位等级销售分布 - 从 Ticket.cabin_class 聚合计算真实数据
        cabin_class_labels = {
            'economy': '经济舱',
            'business': '商务舱',
            'first': '头等舱'
        }
        cabin_data = Ticket.objects.values('cabin_class').annotate(
            count=Count('id'),
            revenue=Sum('price')
        )
        cabin_distribution = []
        for item in cabin_data:
            cabin_distribution.append({
                'cabin_class': cabin_class_labels.get(item['cabin_class'], item['cabin_class']),
                'count': item['count'],
                'revenue': float(item['revenue']) if item['revenue'] else 0
            })
        
        # 票价区间分布 - 从 Ticket.price 聚合计算真实数据
        tickets = Ticket.objects.all()
        
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
        
        # 支付方式分布 - 从 Order.payment_method 聚合计算真实数据
        payment_data = Order.objects.filter(
            status='paid',
            payment_method__isnull=False
        ).exclude(
            payment_method=''
        ).values('payment_method').annotate(
            value=Count('id')
        )
        payment_methods = []
        for item in payment_data:
            payment_methods.append({
                'name': item['payment_method'],
                'value': item['value']
            })
            
        return Response({
            'city_data': city_data[:10],  # 只返回前10个城市
            'cabin_distribution': cabin_distribution,
            'ticket_price_ranges': ticket_price_ranges,
            'payment_methods': payment_methods
        })

class SystemLog(APIView):
    """系统日志接口，仅管理员可访问
    
    从 Django 日志文件读取真实日志记录。
    
    参数:
    - level: 日志级别筛选 (INFO, WARNING, ERROR)
    - start_date: 开始日期 (YYYY-MM-DD)
    - end_date: 结束日期 (YYYY-MM-DD)
    - limit: 返回数量限制 (默认 100)
    
    日志文件格式: LEVEL YYYY-MM-DD HH:MM:SS,mmm source PID TID message
    """
    permission_classes = [permissions.IsAuthenticated]
    
    # 日志文件路径
    LOG_FILE_PATH = 'logs/django.log'
    
    # 支持的日志级别
    SUPPORTED_LEVELS = ['INFO', 'WARNING', 'ERROR']
    
    # 默认返回数量
    DEFAULT_LIMIT = 100
    
    def get(self, request):
        user = request.user
        if not hasattr(user, 'role') or user.role != 'admin':
            return Response({'detail': '权限不足'}, status=403)
        
        # 获取筛选参数
        level = request.query_params.get('level')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        limit = request.query_params.get('limit', self.DEFAULT_LIMIT)
        
        try:
            limit = int(limit)
            if limit <= 0:
                limit = self.DEFAULT_LIMIT
        except (ValueError, TypeError):
            limit = self.DEFAULT_LIMIT
        
        # 验证日志级别参数
        if level and level.upper() not in self.SUPPORTED_LEVELS:
            level = None
        elif level:
            level = level.upper()
        
        # 解析日期参数
        parsed_start_date = None
        parsed_end_date = None
        
        if start_date:
            try:
                parsed_start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
            except ValueError:
                pass
        
        if end_date:
            try:
                parsed_end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
            except ValueError:
                pass
        
        # 读取并解析日志文件
        logs, message = self._read_log_file(level, parsed_start_date, parsed_end_date, limit)
        
        response_data = {
            'logs': logs,
            'total': len(logs)
        }
        
        if message:
            response_data['message'] = message
        
        return Response(response_data)
    
    def _read_log_file(self, level=None, start_date=None, end_date=None, limit=100):
        """从日志文件读取并解析日志记录
        
        Args:
            level: 日志级别筛选
            start_date: 开始日期
            end_date: 结束日期
            limit: 返回数量限制
            
        Returns:
            tuple: (日志列表, 消息)
        """
        import os
        from django.conf import settings
        
        log_file_path = os.path.join(settings.BASE_DIR, self.LOG_FILE_PATH)
        
        # 检查日志文件是否存在
        if not os.path.exists(log_file_path):
            return [], '日志文件不存在'
        
        logs = []
        
        try:
            with open(log_file_path, 'r', encoding='utf-8', errors='replace') as f:
                # 读取所有行
                lines = f.readlines()
                
                # 从后往前读取，获取最新的日志
                for line in reversed(lines):
                    log_entry = self._parse_log_line(line.strip())
                    
                    if log_entry is None:
                        continue
                    
                    # 应用日志级别筛选
                    if level and log_entry['level'] != level:
                        continue
                    
                    # 应用时间范围筛选
                    if start_date or end_date:
                        try:
                            log_date = datetime.datetime.strptime(
                                log_entry['timestamp'][:10], '%Y-%m-%d'
                            ).date()
                            
                            if start_date and log_date < start_date:
                                continue
                            if end_date and log_date > end_date:
                                continue
                        except (ValueError, IndexError):
                            continue
                    
                    logs.append(log_entry)
                    
                    # 达到数量限制时停止
                    if len(logs) >= limit:
                        break
            
            return logs, None
            
        except IOError as e:
            return [], f'读取日志文件失败: {str(e)}'
    
    def _parse_log_line(self, line):
        """解析单行日志
        
        日志格式: LEVEL YYYY-MM-DD HH:MM:SS,mmm source PID TID message
        
        Args:
            line: 日志行字符串
            
        Returns:
            dict: 解析后的日志条目，解析失败返回 None
        """
        if not line:
            return None
        
        # 尝试解析日志行
        # 格式: LEVEL YYYY-MM-DD HH:MM:SS,mmm source PID TID message
        parts = line.split(' ', 6)
        
        if len(parts) < 5:
            return None
        
        level = parts[0]
        
        # 验证日志级别
        if level not in self.SUPPORTED_LEVELS:
            return None
        
        try:
            # 解析日期和时间
            date_str = parts[1]
            time_str = parts[2]
            timestamp = f"{date_str}T{time_str.replace(',', '.')}"
            
            # 解析来源
            source = parts[3] if len(parts) > 3 else 'unknown'
            
            # 解析消息（剩余部分）
            # 跳过 PID 和 TID
            if len(parts) >= 7:
                message = parts[6]
            elif len(parts) >= 6:
                message = parts[5]
            else:
                message = ' '.join(parts[4:]) if len(parts) > 4 else ''
            
            return {
                'timestamp': timestamp,
                'level': level,
                'message': message,
                'source': source
            }
            
        except (IndexError, ValueError):
            return None

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
        
        # 用户年龄分布 - 从 Passenger.birth_date 计算真实年龄
        from accounts.models import Passenger
        
        today = now().date()
        
        # 定义年龄区间
        age_ranges = [
            {'name': '18岁以下', 'min': 0, 'max': 18},
            {'name': '18-25岁', 'min': 18, 'max': 26},
            {'name': '26-35岁', 'min': 26, 'max': 36},
            {'name': '36-50岁', 'min': 36, 'max': 51},
            {'name': '50岁以上', 'min': 51, 'max': 200}
        ]
        
        # 计算每个年龄区间的乘客数量
        age_distribution = []
        for age_range in age_ranges:
            # 计算出生日期范围
            # 年龄 >= min_age 意味着 birth_date <= today - min_age 年
            # 年龄 < max_age 意味着 birth_date > today - max_age 年
            max_birth_date = today.replace(year=today.year - age_range['min'])
            min_birth_date = today.replace(year=today.year - age_range['max'])
            
            count = Passenger.objects.filter(
                birth_date__gt=min_birth_date,
                birth_date__lte=max_birth_date
            ).count()
            
            age_distribution.append({
                'age_range': age_range['name'],
                'count': count
            })
        
        # 用户增长趋势 - 从 User.date_joined 聚合计算真实数据
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
            
            # 当月活跃用户数（基于 last_login 字段）
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
            'user_growth': user_growth
        })

class FlightVisualization(APIView):
    """航班可视化分析接口
    
    提供航班上座率和航线地图数据，所有数据均来自真实数据库查询。
    
    返回数据:
    - flight_load: 各航线的平均上座率
    - route_map: 航线地图数据（城市坐标和航线信息）
    """
    permission_classes = [permissions.IsAuthenticated]
    
    # 城市坐标数据（用于航线地图展示）
    CITY_COORDINATES = {
        '北京': [116.405285, 39.904989],
        '上海': [121.472644, 31.231706],
        '广州': [113.280637, 23.125178],
        '深圳': [114.085947, 22.547],
        '成都': [104.065735, 30.659462],
        '西安': [108.948024, 34.263161],
        '杭州': [120.153576, 30.287459],
        '重庆': [106.504962, 29.533155],
        '南京': [118.767413, 32.041544],
        '武汉': [114.298572, 30.584355],
        '天津': [117.190182, 39.125596],
        '青岛': [120.355173, 36.082982],
        '大连': [121.618622, 38.914590],
        '厦门': [118.089425, 24.479834],
        '昆明': [102.712251, 25.040609],
        '长沙': [112.982279, 28.19409],
        '郑州': [113.665412, 34.757975],
        '沈阳': [123.429096, 41.796767],
        '哈尔滨': [126.642464, 45.756967],
        '三亚': [109.508268, 18.247872],
        '海口': [110.33119, 20.031971],
        '贵阳': [106.713478, 26.578343],
        '南宁': [108.320004, 22.82402],
        '福州': [119.306239, 26.075302],
        '合肥': [117.283042, 31.86119],
        '济南': [117.000923, 36.675807],
        '石家庄': [114.502461, 38.045474],
        '太原': [112.549248, 37.857014],
        '兰州': [103.823557, 36.058039],
        '乌鲁木齐': [87.617733, 43.792818],
        '拉萨': [91.132212, 29.660361],
        '银川': [106.278179, 38.46637],
        '西宁': [101.778916, 36.623178],
        '呼和浩特': [111.670801, 40.818311],
        '长春': [125.3245, 43.886841],
        '南昌': [115.892151, 28.676493],
        '珠海': [113.553986, 22.224979],
        '无锡': [120.301663, 31.574729],
        '宁波': [121.549792, 29.868388],
        '温州': [120.672111, 28.000575],
        '烟台': [121.391382, 37.539297],
    }
    
    def get(self, request):
        user = request.user
        if not hasattr(user, 'role') or user.role != 'admin':
            return Response({'detail': '权限不足'}, status=403)
        
        # 获取航线载客率数据 - 使用真实数据
        # 上座率 = (capacity - available_seats) / capacity * 100
        routes = Flight.objects.values('departure_city', 'arrival_city').annotate(
            avg_occupancy=Avg(100 * (F('capacity') - F('available_seats')) / F('capacity')),
            flight_count=Count('id')
        ).order_by('-flight_count')[:10]  # 取前10条热门航线
        
        flight_load = []
        for route in routes:
            flight_load.append({
                'name': f"{route['departure_city']}-{route['arrival_city']}",
                'value': round(route['avg_occupancy']) if route['avg_occupancy'] else 0
            })
        
        # 构建航线地图数据 - 使用真实航线数据
        # 获取所有航线及其航班数量
        all_routes = Flight.objects.values('departure_city', 'arrival_city').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # 收集所有涉及的城市
        cities_in_routes = set()
        for route in all_routes:
            cities_in_routes.add(route['departure_city'])
            cities_in_routes.add(route['arrival_city'])
        
        # 构建城市坐标数据（只包含有航线的城市）
        city_coordinates = {}
        for city in cities_in_routes:
            if city in self.CITY_COORDINATES:
                city_coordinates[city] = self.CITY_COORDINATES[city]
        
        # 构建航线数据
        route_lines = []
        for route in all_routes:
            dep = route['departure_city']
            arr = route['arrival_city']
            
            # 检查两个城市是否都有坐标
            if dep in city_coordinates and arr in city_coordinates:
                route_lines.append({
                    'from': dep,
                    'to': arr,
                    'coords': [city_coordinates[dep], city_coordinates[arr]],
                    'value': route['count']
                })
        
        return Response({
            'flight_load': flight_load,
            'route_map': {
                'cities': city_coordinates,
                'routes': route_lines
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
    """客户分群分析接口
    
    基于用户消费总额将用户分为高/中/低价值三个群体：
    - 高价值: 消费总额 >= 3000 元
    - 中价值: 1000 元 <= 消费总额 < 3000 元
    - 低价值: 消费总额 < 1000 元
    """
    permission_classes = [permissions.IsAuthenticated]
    
    # 分群阈值常量
    HIGH_VALUE_THRESHOLD = 3000
    MEDIUM_VALUE_THRESHOLD = 1000
    
    def get(self, request):
        user = request.user
        if not hasattr(user, 'role') or user.role != 'admin':
            return Response({'detail': '权限不足'}, status=403)
        
        # 基于 Order.total_price 聚合计算每个用户的消费总额
        user_spending = Order.objects.filter(
            status='paid'
        ).values('user').annotate(
            total_spend=Sum('total_price')
        )
        
        # 初始化分群数据
        high_value = {'count': 0, 'total_spend': 0, 'users': []}
        medium_value = {'count': 0, 'total_spend': 0, 'users': []}
        low_value = {'count': 0, 'total_spend': 0, 'users': []}
        
        # 按消费金额分群
        for user_data in user_spending:
            spend = float(user_data['total_spend']) if user_data['total_spend'] else 0
            
            if spend >= self.HIGH_VALUE_THRESHOLD:
                high_value['count'] += 1
                high_value['total_spend'] += spend
            elif spend >= self.MEDIUM_VALUE_THRESHOLD:
                medium_value['count'] += 1
                medium_value['total_spend'] += spend
            else:
                low_value['count'] += 1
                low_value['total_spend'] += spend
        
        # 计算总用户数
        total_users = high_value['count'] + medium_value['count'] + low_value['count']
        
        # 构建返回数据
        segments = []
        
        # 高价值客户
        if high_value['count'] > 0:
            segments.append({
                'name': '高价值客户',
                'count': high_value['count'],
                'avg_spend': round(high_value['total_spend'] / high_value['count'], 2),
                'total_spend': round(high_value['total_spend'], 2),
                'percentage': round(high_value['count'] / total_users * 100, 1) if total_users > 0 else 0
            })
        else:
            segments.append({
                'name': '高价值客户',
                'count': 0,
                'avg_spend': 0,
                'total_spend': 0,
                'percentage': 0
            })
        
        # 中价值客户
        if medium_value['count'] > 0:
            segments.append({
                'name': '中价值客户',
                'count': medium_value['count'],
                'avg_spend': round(medium_value['total_spend'] / medium_value['count'], 2),
                'total_spend': round(medium_value['total_spend'], 2),
                'percentage': round(medium_value['count'] / total_users * 100, 1) if total_users > 0 else 0
            })
        else:
            segments.append({
                'name': '中价值客户',
                'count': 0,
                'avg_spend': 0,
                'total_spend': 0,
                'percentage': 0
            })
        
        # 低价值客户
        if low_value['count'] > 0:
            segments.append({
                'name': '低价值客户',
                'count': low_value['count'],
                'avg_spend': round(low_value['total_spend'] / low_value['count'], 2),
                'total_spend': round(low_value['total_spend'], 2),
                'percentage': round(low_value['count'] / total_users * 100, 1) if total_users > 0 else 0
            })
        else:
            segments.append({
                'name': '低价值客户',
                'count': 0,
                'avg_spend': 0,
                'total_spend': 0,
                'percentage': 0
            })
        
        return Response({
            'segments': segments,
            'total_users': total_users
        })

class CustomerLoyalty(APIView):
    """客户忠诚度分析接口
    
    分析客户的忠诚度指数、乘机频率和消费水平，用于散点图展示。
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        if not hasattr(user, 'role') or user.role != 'admin':
            return Response({'detail': '权限不足'}, status=403)
        
        # 获取时间范围参数
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        # 基础查询
        orders = Order.objects.filter(status='paid')
        if start_date:
            orders = orders.filter(created_at__date__gte=start_date)
        if end_date:
            orders = orders.filter(created_at__date__lte=end_date)
        
        # 计算每个用户的订单数和消费总额
        user_stats = orders.values('user').annotate(
            order_count=Count('id'),
            total_spend=Sum('total_price')
        )
        
        # 计算最大订单数用于归一化忠诚度指数
        max_orders = max([u['order_count'] for u in user_stats], default=1)
        
        # 构建忠诚度数据点
        loyalty_levels = []
        for user_data in user_stats:
            order_count = user_data['order_count']
            total_spend = float(user_data['total_spend']) if user_data['total_spend'] else 0
            avg_spend = total_spend / order_count if order_count > 0 else 0
            
            # 忠诚度指数 = 订单数 / 最大订单数 (0-1)
            loyalty_index = round(order_count / max_orders, 2) if max_orders > 0 else 0
            
            loyalty_levels.append({
                'name': f'用户{user_data["user"]}',
                'value': [loyalty_index, order_count, round(avg_spend, 2)]
            })
        
        # 计算留存趋势（按月统计回购用户比例）
        retention_trend = self._calculate_retention_trend(orders)
        
        # 按忠诚度分组的消费统计
        loyalty_spending = self._calculate_loyalty_spending(user_stats)
        
        return Response({
            'loyalty_levels': loyalty_levels,
            'retention_trend': retention_trend,
            'loyalty_spending': loyalty_spending
        })
    
    def _calculate_retention_trend(self, orders):
        """计算留存趋势"""
        from django.db.models.functions import TruncMonth
        
        # 按月统计有订单的用户数
        monthly_users = orders.annotate(
            month=TruncMonth('created_at')
        ).values('month').annotate(
            user_count=Count('user', distinct=True)
        ).order_by('month')
        
        months = []
        rates = []
        prev_users = set()
        
        for month_data in monthly_users:
            month_str = month_data['month'].strftime('%Y-%m') if month_data['month'] else ''
            months.append(month_str)
            
            # 获取当月用户
            current_month_users = set(orders.filter(
                created_at__year=month_data['month'].year,
                created_at__month=month_data['month'].month
            ).values_list('user', flat=True))
            
            # 计算回购率（当月用户中有多少是之前的用户）
            if prev_users:
                returning = len(current_month_users & prev_users)
                rate = round(returning / len(current_month_users) * 100, 1) if current_month_users else 0
            else:
                rate = 0
            
            rates.append(rate)
            prev_users = prev_users | current_month_users
        
        return {
            'months': months,
            'rates': rates
        }
    
    def _calculate_loyalty_spending(self, user_stats):
        """按忠诚度分组计算消费统计"""
        # 分组：低频(1-2次)、中频(3-5次)、高频(6次以上)
        low_freq = {'count': 0, 'total_spend': 0}
        mid_freq = {'count': 0, 'total_spend': 0}
        high_freq = {'count': 0, 'total_spend': 0}
        
        for user_data in user_stats:
            order_count = user_data['order_count']
            spend = float(user_data['total_spend']) if user_data['total_spend'] else 0
            
            if order_count <= 2:
                low_freq['count'] += 1
                low_freq['total_spend'] += spend
            elif order_count <= 5:
                mid_freq['count'] += 1
                mid_freq['total_spend'] += spend
            else:
                high_freq['count'] += 1
                high_freq['total_spend'] += spend
        
        return [
            {
                'name': '低频用户(1-2次)',
                'user_count': low_freq['count'],
                'avg_spend': round(low_freq['total_spend'] / low_freq['count'], 2) if low_freq['count'] > 0 else 0
            },
            {
                'name': '中频用户(3-5次)',
                'user_count': mid_freq['count'],
                'avg_spend': round(mid_freq['total_spend'] / mid_freq['count'], 2) if mid_freq['count'] > 0 else 0
            },
            {
                'name': '高频用户(6次+)',
                'user_count': high_freq['count'],
                'avg_spend': round(high_freq['total_spend'] / high_freq['count'], 2) if high_freq['count'] > 0 else 0
            }
        ]

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

class PivotData(APIView):
    """数据透视表接口
    
    支持的维度:
    - city: 按城市聚合航班和收入数据
    - paymentMethod: 按支付方式聚合订单数据
    - flight: 按航班聚合数据
    - userType: 按用户类型聚合数据
    
    支持的指标:
    - revenue: 销售额
    - orders: 订单数
    - averageValue: 平均客单价
    - refundRate: 退票率
    """
    permission_classes = [permissions.IsAuthenticated]
    
    # 支持的维度列表
    SUPPORTED_DIMENSIONS = ['city', 'paymentMethod', 'flight', 'userType']
    
    def get(self, request):
        user = request.user
        if not hasattr(user, 'role') or user.role != 'admin':
            return Response({'detail': '权限不足'}, status=403)
        
        # 获取维度和指标参数
        dimension = request.query_params.get('dimension', 'city')
        metric = request.query_params.get('metric', 'revenue')
        
        # 验证维度参数
        if dimension not in self.SUPPORTED_DIMENSIONS:
            return Response({
                'detail': f'不支持的维度: {dimension}',
                'supported_dimensions': self.SUPPORTED_DIMENSIONS
            }, status=400)
        
        pivot_data = []
        
        if dimension == 'city':
            pivot_data = self._aggregate_by_city(metric)
        elif dimension == 'paymentMethod':
            pivot_data = self._aggregate_by_payment_method(metric)
        elif dimension == 'flight':
            pivot_data = self._aggregate_by_flight(metric)
        elif dimension == 'userType':
            pivot_data = self._aggregate_by_user_type(metric)
        
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
    
    def _calculate_refund_rate(self, tickets_queryset):
        """计算退票率"""
        total_tickets = tickets_queryset.count()
        if total_tickets == 0:
            return 0
        refunded_tickets = tickets_queryset.filter(status='refunded').count()
        return round(refunded_tickets / total_tickets * 100, 2)
    
    def _aggregate_by_city(self, metric):
        """按城市维度聚合数据"""
        # 获取所有城市（出发城市和到达城市）
        cities = set()
        
        departure_cities = Flight.objects.values_list('departure_city', flat=True).distinct()
        arrival_cities = Flight.objects.values_list('arrival_city', flat=True).distinct()
        
        cities.update(departure_cities)
        cities.update(arrival_cities)
        
        pivot_data = []
        total_value = 0
        
        for city in cities:
            # 获取该城市相关的航班（出发或到达）
            city_flights = Flight.objects.filter(
                departure_city=city
            ) | Flight.objects.filter(
                arrival_city=city
            )
            flight_ids = city_flights.values_list('id', flat=True)
            
            # 获取该城市相关的机票
            city_tickets = Ticket.objects.filter(flight_id__in=flight_ids)
            
            if metric == 'revenue':
                # 销售额：该城市相关机票的总收入
                value = city_tickets.aggregate(total=Sum('price'))['total'] or 0
                value = float(value)
            elif metric == 'orders':
                # 订单数：该城市相关机票的订单数
                value = city_tickets.values('order_id').distinct().count()
            elif metric == 'averageValue':
                # 平均客单价：该城市相关订单的平均金额
                order_ids = city_tickets.values_list('order_id', flat=True).distinct()
                avg_result = Order.objects.filter(id__in=order_ids, status='paid').aggregate(
                    avg=Avg('total_price')
                )
                value = float(avg_result['avg']) if avg_result['avg'] else 0
            elif metric == 'refundRate':
                # 退票率：该城市相关机票的退票率
                value = self._calculate_refund_rate(city_tickets)
            else:
                value = 0
            
            total_value += value
            
            pivot_data.append({
                'dimension': city,
                'value': round(value, 2) if metric in ['revenue', 'averageValue'] else value,
                'flight_count': city_flights.count()
            })
        
        # 计算百分比
        for item in pivot_data:
            if total_value > 0:
                item['percentage'] = round(item['value'] / total_value * 100, 2)
            else:
                item['percentage'] = 0
        
        return pivot_data
    
    def _aggregate_by_payment_method(self, metric):
        """按支付方式维度聚合数据"""
        # 获取所有支付方式
        payment_methods = Order.objects.filter(
            status='paid',
            payment_method__isnull=False
        ).exclude(
            payment_method=''
        ).values_list('payment_method', flat=True).distinct()
        
        pivot_data = []
        total_value = 0
        
        for payment_method in payment_methods:
            # 获取该支付方式的订单
            method_orders = Order.objects.filter(
                status='paid',
                payment_method=payment_method
            )
            
            if metric == 'revenue':
                # 销售额：该支付方式的总收入
                value = method_orders.aggregate(total=Sum('total_price'))['total'] or 0
                value = float(value)
            elif metric == 'orders':
                # 订单数：该支付方式的订单数量
                value = method_orders.count()
            elif metric == 'averageValue':
                # 平均客单价：该支付方式的平均订单金额
                avg_result = method_orders.aggregate(avg=Avg('total_price'))
                value = float(avg_result['avg']) if avg_result['avg'] else 0
            elif metric == 'refundRate':
                # 退票率：该支付方式订单的退票率
                order_ids = method_orders.values_list('id', flat=True)
                method_tickets = Ticket.objects.filter(order_id__in=order_ids)
                value = self._calculate_refund_rate(method_tickets)
            else:
                value = 0
            
            total_value += value
            
            pivot_data.append({
                'dimension': payment_method,
                'value': round(value, 2) if metric in ['revenue', 'averageValue'] else value,
                'order_count': method_orders.count()
            })
        
        # 计算百分比
        for item in pivot_data:
            if total_value > 0:
                item['percentage'] = round(item['value'] / total_value * 100, 2)
            else:
                item['percentage'] = 0
        
        return pivot_data
    
    def _aggregate_by_flight(self, metric):
        """按航班维度聚合数据"""
        # 获取有机票的航班
        flights = Flight.objects.filter(tickets__isnull=False).distinct()[:20]  # 限制前20个
        
        pivot_data = []
        total_value = 0
        
        for flight in flights:
            flight_tickets = Ticket.objects.filter(flight=flight)
            flight_label = f"{flight.flight_number} ({flight.departure_city}-{flight.arrival_city})"
            
            if metric == 'revenue':
                value = flight_tickets.aggregate(total=Sum('price'))['total'] or 0
                value = float(value)
            elif metric == 'orders':
                value = flight_tickets.values('order_id').distinct().count()
            elif metric == 'averageValue':
                order_ids = flight_tickets.values_list('order_id', flat=True).distinct()
                avg_result = Order.objects.filter(id__in=order_ids, status='paid').aggregate(
                    avg=Avg('total_price')
                )
                value = float(avg_result['avg']) if avg_result['avg'] else 0
            elif metric == 'refundRate':
                value = self._calculate_refund_rate(flight_tickets)
            else:
                value = 0
            
            total_value += value
            
            pivot_data.append({
                'dimension': flight_label,
                'value': round(value, 2) if metric in ['revenue', 'averageValue', 'refundRate'] else value,
                'ticket_count': flight_tickets.count()
            })
        
        # 计算百分比
        for item in pivot_data:
            if total_value > 0:
                item['percentage'] = round(item['value'] / total_value * 100, 2)
            else:
                item['percentage'] = 0
        
        return pivot_data
    
    def _aggregate_by_user_type(self, metric):
        """按用户类型维度聚合数据"""
        # 用户类型定义：根据订单数量分类
        # VIP: 订单数 >= 5
        # 常客: 订单数 >= 2
        # 新用户: 订单数 = 1
        
        user_types = [
            {'name': 'VIP用户', 'min_orders': 5, 'max_orders': None},
            {'name': '常客', 'min_orders': 2, 'max_orders': 4},
            {'name': '新用户', 'min_orders': 1, 'max_orders': 1},
        ]
        
        pivot_data = []
        total_value = 0
        
        for user_type in user_types:
            # 获取符合条件的用户
            user_order_counts = Order.objects.filter(status='paid').values('user').annotate(
                order_count=Count('id')
            )
            
            if user_type['max_orders'] is None:
                qualified_users = user_order_counts.filter(order_count__gte=user_type['min_orders'])
            else:
                qualified_users = user_order_counts.filter(
                    order_count__gte=user_type['min_orders'],
                    order_count__lte=user_type['max_orders']
                )
            
            user_ids = [u['user'] for u in qualified_users]
            type_orders = Order.objects.filter(user_id__in=user_ids, status='paid')
            
            if metric == 'revenue':
                value = type_orders.aggregate(total=Sum('total_price'))['total'] or 0
                value = float(value)
            elif metric == 'orders':
                value = type_orders.count()
            elif metric == 'averageValue':
                avg_result = type_orders.aggregate(avg=Avg('total_price'))
                value = float(avg_result['avg']) if avg_result['avg'] else 0
            elif metric == 'refundRate':
                order_ids = type_orders.values_list('id', flat=True)
                type_tickets = Ticket.objects.filter(order_id__in=order_ids)
                value = self._calculate_refund_rate(type_tickets)
            else:
                value = 0
            
            total_value += value
            
            pivot_data.append({
                'dimension': user_type['name'],
                'value': round(value, 2) if metric in ['revenue', 'averageValue', 'refundRate'] else value,
                'user_count': len(user_ids)
            })
        
        # 计算百分比
        for item in pivot_data:
            if total_value > 0:
                item['percentage'] = round(item['value'] / total_value * 100, 2)
            else:
                item['percentage'] = 0
        
        return pivot_data

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


# ============================================================================
# 多维度分析模块 API - 满足 Requirements 3, 4, 5
# ============================================================================

class MultiDimensionAnalysisView(APIView):
    """
    多维度分析 API - 满足 Requirement 3。
    
    POST /api/analytics/business-intelligence/multi-dimension/
    
    支持按时间、航线、舱位、用户分群等维度进行数据分析，
    计算收入、订单数、平均票价等关键指标。
    
    请求参数:
    - dimensions: 分析维度列表 ['time', 'route', 'cabin_class', 'user_segment']
    - metrics: 指标列表 ['revenue', 'order_count', 'avg_price', 'ticket_count']
    - start_date: 开始日期 (YYYY-MM-DD 或 ISO 格式)
    - end_date: 结束日期 (YYYY-MM-DD 或 ISO 格式)
    - time_granularity: 时间粒度 (day, week, month, quarter, year)
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """POST /api/analytics/business-intelligence/multi-dimension/"""
        user = request.user
        if not hasattr(user, 'role') or user.role != 'admin':
            return Response({'detail': '权限不足'}, status=403)
        
        from .services import MultiDimensionAnalytics
        
        # 解析请求参数
        dimensions = request.data.get('dimensions', ['time'])
        metrics = request.data.get('metrics', ['revenue', 'order_count'])
        start_date = self._parse_date(request.data.get('start_date'))
        end_date = self._parse_date(request.data.get('end_date'))
        time_granularity = request.data.get('time_granularity', 'month')
        
        # 验证维度参数
        valid_dimensions = ['time', 'route', 'cabin_class', 'user_segment']
        for dim in dimensions:
            if dim not in valid_dimensions:
                return Response({
                    'detail': f'不支持的维度: {dim}',
                    'valid_dimensions': valid_dimensions
                }, status=400)
        
        # 验证指标参数
        valid_metrics = ['revenue', 'order_count', 'avg_price', 'ticket_count']
        for metric in metrics:
            if metric not in valid_metrics:
                return Response({
                    'detail': f'不支持的指标: {metric}',
                    'valid_metrics': valid_metrics
                }, status=400)
        
        # 执行多维度分析
        analytics = MultiDimensionAnalytics()
        result = analytics.analyze(
            dimensions=dimensions,
            metrics=metrics,
            start_date=start_date,
            end_date=end_date,
            time_granularity=time_granularity,
        )
        
        return Response(result)
    
    def _parse_date(self, date_str):
        """解析日期字符串为 datetime 对象"""
        if not date_str:
            return None
        
        try:
            # 尝试解析 ISO 格式
            if 'T' in str(date_str):
                return datetime.datetime.fromisoformat(str(date_str).replace('Z', '+00:00'))
            # 尝试解析 YYYY-MM-DD 格式
            return datetime.datetime.strptime(str(date_str), '%Y-%m-%d')
        except (ValueError, TypeError):
            return None



class PivotDataView(APIView):
    """
    透视表数据 API - 满足 Requirement 4。
    
    POST /api/analytics/pivot-data/
    
    支持动态配置行维度、列维度和聚合方式，生成透视表数据。
    
    请求参数:
    - row_dimensions: 行维度列表 ['departure_city', 'arrival_city', 'cabin_class', 'payment_method']
    - col_dimensions: 列维度列表
    - value_metric: 值指标 (total_price, revenue, ticket_price, ticket_count)
    - aggregation: 聚合方式 (sum, count, avg)
    - start_date: 开始日期
    - end_date: 结束日期
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """POST /api/analytics/pivot-data/"""
        user = request.user
        if not hasattr(user, 'role') or user.role != 'admin':
            return Response({'detail': '权限不足'}, status=403)
        
        from .services import PivotTableEngine
        
        # 解析请求参数
        row_dimensions = request.data.get('row_dimensions', [])
        col_dimensions = request.data.get('col_dimensions', [])
        value_metric = request.data.get('value_metric', 'total_price')
        aggregation = request.data.get('aggregation', 'sum')
        start_date = self._parse_date(request.data.get('start_date'))
        end_date = self._parse_date(request.data.get('end_date'))
        
        # 验证聚合方式
        valid_aggregations = ['sum', 'count', 'avg']
        if aggregation not in valid_aggregations:
            return Response({
                'detail': f'不支持的聚合方式: {aggregation}',
                'valid_aggregations': valid_aggregations
            }, status=400)
        
        # 生成透视表数据
        engine = PivotTableEngine()
        result = engine.generate(
            row_dimensions=row_dimensions,
            col_dimensions=col_dimensions,
            value_metric=value_metric,
            aggregation=aggregation,
            start_date=start_date,
            end_date=end_date,
        )
        
        return Response(result)
    
    def _parse_date(self, date_str):
        """解析日期字符串为 datetime 对象"""
        if not date_str:
            return None
        
        try:
            if 'T' in str(date_str):
                return datetime.datetime.fromisoformat(str(date_str).replace('Z', '+00:00'))
            return datetime.datetime.strptime(str(date_str), '%Y-%m-%d')
        except (ValueError, TypeError):
            return None


class PivotExportView(APIView):
    """
    透视表导出 API - 满足 Requirement 4.5。
    
    POST /api/analytics/pivot-data/export/
    
    将透视表数据导出为 CSV 格式。
    
    请求参数与 PivotDataView 相同。
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """POST /api/analytics/pivot-data/export/"""
        user = request.user
        if not hasattr(user, 'role') or user.role != 'admin':
            return Response({'detail': '权限不足'}, status=403)
        
        from django.http import HttpResponse
        from .services import PivotTableEngine
        
        # 解析请求参数
        row_dimensions = request.data.get('row_dimensions', [])
        col_dimensions = request.data.get('col_dimensions', [])
        value_metric = request.data.get('value_metric', 'total_price')
        aggregation = request.data.get('aggregation', 'sum')
        start_date = self._parse_date(request.data.get('start_date'))
        end_date = self._parse_date(request.data.get('end_date'))
        
        # 生成透视表数据
        engine = PivotTableEngine()
        pivot_result = engine.generate(
            row_dimensions=row_dimensions,
            col_dimensions=col_dimensions,
            value_metric=value_metric,
            aggregation=aggregation,
            start_date=start_date,
            end_date=end_date,
        )
        
        # 导出为 CSV
        csv_content = engine.export_csv(pivot_result['data'])
        
        # 返回 CSV 文件响应
        response = HttpResponse(csv_content, content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="pivot_data.csv"'
        return response
    
    def _parse_date(self, date_str):
        """解析日期字符串为 datetime 对象"""
        if not date_str:
            return None
        
        try:
            if 'T' in str(date_str):
                return datetime.datetime.fromisoformat(str(date_str).replace('Z', '+00:00'))
            return datetime.datetime.strptime(str(date_str), '%Y-%m-%d')
        except (ValueError, TypeError):
            return None



class TrendsView(APIView):
    """
    趋势分析 API - 满足 Requirement 5。
    
    GET /api/analytics/business-intelligence/trends/
    
    提供移动平均计算、同比分析、异常检测和季节性模式识别功能。
    
    查询参数:
    - start_date: 开始日期 (YYYY-MM-DD)
    - end_date: 结束日期 (YYYY-MM-DD)
    - metric: 分析指标 (revenue, order_count)，默认 revenue
    - window_size: 移动平均窗口大小，默认 7
    - anomaly_threshold: 异常检测阈值（Z-score），默认 2.0
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """GET /api/analytics/business-intelligence/trends/"""
        user = request.user
        if not hasattr(user, 'role') or user.role != 'admin':
            return Response({'detail': '权限不足'}, status=403)
        
        try:
            from .services import MultiDimensionAnalytics, TrendAnalyzer
            
            # 解析查询参数
            start_date = self._parse_date(request.query_params.get('start_date'))
            end_date = self._parse_date(request.query_params.get('end_date'))
            metric = request.query_params.get('metric', 'revenue')
            
            try:
                window_size = int(request.query_params.get('window_size', 7))
                if window_size < 1:
                    window_size = 7
            except (ValueError, TypeError):
                window_size = 7
            
            try:
                anomaly_threshold = float(request.query_params.get('anomaly_threshold', 2.0))
                if anomaly_threshold <= 0:
                    anomaly_threshold = 2.0
            except (ValueError, TypeError):
                anomaly_threshold = 2.0
            
            # 验证指标参数
            valid_metrics = ['revenue', 'order_count']
            if metric not in valid_metrics:
                return Response({
                    'detail': f'不支持的指标: {metric}',
                    'valid_metrics': valid_metrics
                }, status=400)
            
            # 获取基础时间序列数据
            analytics = MultiDimensionAnalytics()
            base_data = analytics.analyze(
                dimensions=['time'],
                metrics=['revenue', 'order_count'],
                start_date=start_date,
                end_date=end_date,
                time_granularity='day',
            )
            
            data = base_data.get('data', [])
            
            # 为数据添加 period 字段（用于季节性分析）
            for item in data:
                if 'time_period' in item:
                    item['period'] = item['time_period']
            
            # 初始化趋势分析器
            analyzer = TrendAnalyzer()
            
            # 计算移动平均 - 满足 Requirement 5.1
            with_ma = analyzer.calculate_moving_average(data, metric, window_size)
            
            # 检测异常 - 满足 Requirement 5.5
            with_anomalies = analyzer.detect_anomalies(with_ma, metric, anomaly_threshold)
            
            # 识别季节性模式 - 满足 Requirement 5.2
            seasonal = analyzer.identify_seasonal_patterns(data, metric)
            
            # 计算同比数据 - 满足 Requirement 5.3
            # 获取去年同期数据
            yoy_data = []
            if start_date and end_date:
                prev_start = start_date.replace(year=start_date.year - 1)
                prev_end = end_date.replace(year=end_date.year - 1)
                
                prev_data = analytics.analyze(
                    dimensions=['time'],
                    metrics=['revenue', 'order_count'],
                    start_date=prev_start,
                    end_date=prev_end,
                    time_granularity='day',
                )
                
                prev_items = prev_data.get('data', [])
                for item in prev_items:
                    if 'time_period' in item:
                        item['period'] = item['time_period']
                
                yoy_data = analyzer.year_over_year(data, prev_items, metric)
            
            # 计算整体置信度 - 满足 Requirement 5.4
            anomaly_count = sum(1 for item in with_anomalies if item.get('is_anomaly', False))
            total_count = len(with_anomalies)
            
            if total_count == 0:
                confidence = 'low'
            elif anomaly_count / total_count > 0.2:
                confidence = 'low'
            elif anomaly_count / total_count > 0.1:
                confidence = 'medium'
            else:
                confidence = 'high'
            
            return Response({
                'trend_data': with_anomalies,
                'seasonal_patterns': seasonal,
                'year_over_year': yoy_data,
                'confidence': confidence,
                'parameters': {
                    'metric': metric,
                    'window_size': window_size,
                    'anomaly_threshold': anomaly_threshold,
                },
                'summary': {
                    'total_records': total_count,
                    'anomaly_count': anomaly_count,
                    'peak_month': seasonal.get('peak_month'),
                    'low_month': seasonal.get('low_month'),
                }
            })
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"趋势分析失败: {str(e)}", exc_info=True)
            return Response({
                'trend_data': [],
                'seasonal_patterns': {},
                'year_over_year': [],
                'confidence': 'low',
                'error': str(e),
                'summary': {
                    'total_records': 0,
                    'anomaly_count': 0,
                    'peak_month': None,
                    'low_month': None,
                }
            })
    
    def _parse_date(self, date_str):
        """解析日期字符串为 datetime 对象"""
        if not date_str:
            return None
        
        try:
            if 'T' in str(date_str):
                return datetime.datetime.fromisoformat(str(date_str).replace('Z', '+00:00'))
            return datetime.datetime.strptime(str(date_str), '%Y-%m-%d')
        except (ValueError, TypeError):
            return None


class RouteRecommendationView(APIView):
    """
    航线推荐 API - 满足 Requirement 4。

    为用户提供个性化航线推荐：
    - 已登录用户：基于协同过滤算法的个性化推荐
    - 未登录用户或冷启动用户：热门航线推荐

    Query Params:
        limit: int (default=5) - 返回推荐数量

    Response:
        {
            'recommendation_type': 'collaborative' | 'popular',
            'recommendations': [...],
            'total': int
        }
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        """
        GET /api/analytics/recommendations/routes/

        返回当前用户的航线推荐。
        """
        from .services import CollaborativeFilteringEngine, PopularRouteService

        # 获取 limit 参数，默认为 5
        try:
            limit = int(request.query_params.get('limit', 5))
            if limit <= 0:
                limit = 5
        except (ValueError, TypeError):
            limit = 5

        # 检查用户是否已登录
        user = request.user
        if user.is_authenticated:
            # 已登录用户：尝试协同过滤推荐
            engine = CollaborativeFilteringEngine()
            recommendations = engine.generate_recommendations(
                user_id=user.id,
                limit=limit
            )

            if recommendations:
                # 有推荐结果，返回协同过滤推荐
                return Response({
                    'recommendation_type': 'collaborative',
                    'recommendations': recommendations,
                    'total': len(recommendations)
                })

        # 未登录用户或冷启动用户：返回热门航线推荐
        popular_service = PopularRouteService()
        popular_routes = popular_service.get_popular_routes(limit=limit)

        # 为热门航线添加 predicted_score 字段以保持响应格式一致
        for route in popular_routes:
            if 'predicted_score' not in route:
                route['predicted_score'] = None

        return Response({
            'recommendation_type': 'popular',
            'recommendations': popular_routes,
            'total': len(popular_routes)
        })
