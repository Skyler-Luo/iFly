"""
商业智能分析服务模块。

本模块提供多维度数据分析、透视表生成和趋势分析功能。
满足 Requirements 3, 4, 5。
"""
import csv
import io
from datetime import datetime, timedelta
from statistics import mean, stdev
from typing import Dict, List, Literal, Optional

from django.db.models import Avg, Case, Count, F, Sum, Value, When
from django.db.models.functions import (
    TruncDay,
    TruncMonth,
    TruncQuarter,
    TruncWeek,
    TruncYear,
)

from booking.models import Order, Ticket
from flight.models import Flight


class MultiDimensionAnalytics:
    """
    多维度分析引擎 - 满足 Requirement 3。

    支持按时间、航线、舱位、用户分群等维度进行数据分析，
    计算收入、订单数、平均票价、上座率等关键指标。
    """

    TIME_DIMENSIONS = {
        'day': TruncDay,
        'week': TruncWeek,
        'month': TruncMonth,
        'quarter': TruncQuarter,
        'year': TruncYear,
    }

    def analyze(
        self,
        dimensions: List[str],
        metrics: List[str],
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        time_granularity: str = 'month',
    ) -> Dict:
        """
        执行多维度分析 - 满足 Requirements 3.1-3.7。

        Args:
            dimensions: 分析维度列表 ['time', 'route', 'cabin_class', 'user_segment']
            metrics: 指标列表 ['revenue', 'order_count', 'avg_price', 'load_factor']
            start_date: 开始日期
            end_date: 结束日期
            time_granularity: 时间粒度 (day, week, month, quarter, year)

        Returns:
            包含分析结果的字典
        """
        queryset = Order.objects.filter(status='paid')

        # 日期范围过滤 - 满足 Requirement 3.7
        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)

        # 构建分组字段和注解
        group_fields = []
        annotations = {}

        for dim in dimensions:
            if dim == 'time':
                # 时间维度 - 满足 Requirement 3.1
                trunc_func = self.TIME_DIMENSIONS.get(time_granularity, TruncMonth)
                annotations['time_period'] = trunc_func('created_at')
                group_fields.append('time_period')

            elif dim == 'route':
                # 航线维度 - 满足 Requirement 3.2
                # 需要通过 tickets 关联到 flight
                group_fields.extend([
                    'tickets__flight__departure_city',
                    'tickets__flight__arrival_city'
                ])

            elif dim == 'cabin_class':
                # 舱位维度 - 满足 Requirement 3.3
                group_fields.append('tickets__cabin_class')

            elif dim == 'user_segment':
                # 用户分群维度 - 满足 Requirement 3.4
                annotations['user_segment'] = self._get_user_segment_case()
                group_fields.append('user_segment')

        # 计算指标 - 满足 Requirement 3.6
        metric_annotations = {}
        if 'revenue' in metrics:
            metric_annotations['revenue'] = Sum('total_price')
        if 'order_count' in metrics:
            metric_annotations['order_count'] = Count('id', distinct=True)
        if 'avg_price' in metrics:
            metric_annotations['avg_price'] = Avg('total_price')
        if 'ticket_count' in metrics:
            metric_annotations['ticket_count'] = Count('tickets__id')

        # 执行聚合查询 - 满足 Requirement 3.5 (交叉表)
        if annotations:
            queryset = queryset.annotate(**annotations)

        if group_fields:
            result = queryset.values(*group_fields).annotate(**metric_annotations)
        else:
            # 无分组时返回总计
            result = [queryset.aggregate(**metric_annotations)]

        # 格式化结果
        formatted_data = self._format_result(list(result), dimensions)

        return {
            'dimensions': dimensions,
            'metrics': metrics,
            'data': formatted_data,
            'total_records': len(formatted_data),
        }

    def _get_user_segment_case(self):
        """
        用户分群逻辑。

        根据用户订单数量进行分群：
        - VIP: 订单数 >= 10
        - returning: 订单数 >= 2
        - new: 其他
        """
        return Case(
            When(user__orders__count__gte=10, then=Value('vip')),
            When(user__orders__count__gte=2, then=Value('returning')),
            default=Value('new'),
        )

    def _format_result(self, data: List[Dict], dimensions: List[str]) -> List[Dict]:
        """格式化查询结果，处理日期时间等特殊类型。"""
        formatted = []
        for item in data:
            formatted_item = {}
            for key, value in item.items():
                if hasattr(value, 'isoformat'):
                    # 日期时间类型转为 ISO 格式字符串
                    formatted_item[key] = value.isoformat()
                elif isinstance(value, (int, float, str, type(None))):
                    formatted_item[key] = value
                else:
                    formatted_item[key] = str(value)
            formatted.append(formatted_item)
        return formatted

    def get_load_factor(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict:
        """
        计算上座率 - 满足 Requirement 3.6 中的 load_factor 指标。

        Returns:
            包含上座率数据的字典
        """
        queryset = Flight.objects.all()

        if start_date:
            queryset = queryset.filter(departure_time__gte=start_date)
        if end_date:
            queryset = queryset.filter(departure_time__lte=end_date)

        # 计算上座率 = (总座位数 - 剩余座位数) / 总座位数 * 100
        result = queryset.annotate(
            load_factor=100 * (1 - F('available_seats') * 1.0 / F('capacity'))
        ).aggregate(
            avg_load_factor=Avg('load_factor'),
            total_flights=Count('id'),
        )

        return {
            'avg_load_factor': round(result['avg_load_factor'] or 0, 2),
            'total_flights': result['total_flights'],
        }



class PivotTableEngine:
    """
    数据透视表引擎 - 满足 Requirement 4。

    支持动态配置行维度、列维度和聚合方式，生成透视表数据并导出为 CSV。
    """

    # 支持的聚合函数映射
    AGG_FUNCS = {
        'sum': Sum,
        'count': Count,
        'avg': Avg,
    }

    # 支持的值指标字段映射
    VALUE_FIELDS = {
        'total_price': 'total_price',
        'revenue': 'total_price',
        'ticket_price': 'tickets__price',
        'ticket_count': 'tickets__id',
    }

    def generate(
        self,
        row_dimensions: List[str],
        col_dimensions: List[str],
        value_metric: str = 'total_price',
        aggregation: Literal['sum', 'count', 'avg'] = 'sum',
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict:
        """
        生成透视表数据 - 满足 Requirements 4.1-4.4。

        Args:
            row_dimensions: 行维度 - 满足 Requirement 4.1
            col_dimensions: 列维度 - 满足 Requirement 4.2
            value_metric: 值指标字段
            aggregation: 聚合方式 (sum/count/avg) - 满足 Requirement 4.3
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            透视表数据结构 - 满足 Requirement 4.4
        """
        queryset = Order.objects.filter(status='paid')

        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)

        # 获取聚合函数
        agg_func = self.AGG_FUNCS.get(aggregation, Sum)

        # 获取值字段
        value_field = self.VALUE_FIELDS.get(value_metric, value_metric)

        # 映射维度字段
        mapped_row_dims = self._map_dimensions(row_dimensions)
        mapped_col_dims = self._map_dimensions(col_dimensions)

        # 所有维度
        all_dimensions = mapped_row_dims + mapped_col_dims

        if not all_dimensions:
            # 无维度时返回总计
            total = queryset.aggregate(value=agg_func(value_field))
            return {
                'row_dimensions': row_dimensions,
                'col_dimensions': col_dimensions,
                'aggregation': aggregation,
                'data': {
                    'rows': [['Total']],
                    'columns': [['Total']],
                    'matrix': {"(('Total',), ('Total',))": total.get('value', 0)},
                },
            }

        # 执行聚合查询
        if aggregation == 'count':
            result = queryset.values(*all_dimensions).annotate(
                value=agg_func(value_field, distinct=True)
            )
        else:
            result = queryset.values(*all_dimensions).annotate(
                value=agg_func(value_field)
            )

        # 构建透视表结构 - 满足 Requirement 4.4
        pivot_data = self._build_pivot_structure(
            list(result), mapped_row_dims, mapped_col_dims
        )

        return {
            'row_dimensions': row_dimensions,
            'col_dimensions': col_dimensions,
            'aggregation': aggregation,
            'data': pivot_data,
        }

    def _map_dimensions(self, dimensions: List[str]) -> List[str]:
        """将用户友好的维度名称映射到数据库字段。"""
        mapping = {
            'departure_city': 'tickets__flight__departure_city',
            'arrival_city': 'tickets__flight__arrival_city',
            'cabin_class': 'tickets__cabin_class',
            'payment_method': 'payment_method',
            'status': 'status',
        }
        return [mapping.get(dim, dim) for dim in dimensions]

    def _build_pivot_structure(
        self,
        raw_data: List[Dict],
        row_dims: List[str],
        col_dims: List[str],
    ) -> Dict:
        """构建透视表数据结构。"""
        # 提取唯一的行和列值
        row_values = set()
        col_values = set()

        for row in raw_data:
            row_key = tuple(row.get(d) for d in row_dims) if row_dims else ('Total',)
            col_key = tuple(row.get(d) for d in col_dims) if col_dims else ('Total',)
            row_values.add(row_key)
            col_values.add(col_key)

        # 构建数据矩阵
        matrix = {}
        for row in raw_data:
            row_key = tuple(row.get(d) for d in row_dims) if row_dims else ('Total',)
            col_key = tuple(row.get(d) for d in col_dims) if col_dims else ('Total',)
            value = row.get('value', 0)
            # 处理 Decimal 类型
            if hasattr(value, '__float__'):
                value = float(value)
            matrix[(row_key, col_key)] = value

        # 排序行和列
        sorted_rows = sorted(list(row_values), key=lambda x: str(x))
        sorted_cols = sorted(list(col_values), key=lambda x: str(x))

        return {
            'rows': [list(r) for r in sorted_rows],
            'columns': [list(c) for c in sorted_cols],
            'matrix': {str(k): v for k, v in matrix.items()},
        }

    def export_csv(self, pivot_data: Dict) -> str:
        """
        导出为 CSV 格式 - 满足 Requirement 4.5。

        Args:
            pivot_data: 透视表数据（来自 generate 方法的 data 字段）

        Returns:
            CSV 格式字符串
        """
        output = io.StringIO()
        writer = csv.writer(output)

        rows = pivot_data.get('rows', [])
        columns = pivot_data.get('columns', [])
        matrix = pivot_data.get('matrix', {})

        # 写入表头
        headers = ['Row'] + ['/'.join(str(c) for c in col) for col in columns]
        writer.writerow(headers)

        # 写入数据行
        for row in rows:
            row_label = '/'.join(str(r) for r in row)
            row_data = [row_label]
            for col in columns:
                key = str((tuple(row), tuple(col)))
                value = matrix.get(key, 0)
                row_data.append(value if value is not None else 0)
            writer.writerow(row_data)

        return output.getvalue()



class TrendAnalyzer:
    """
    趋势分析器 - 满足 Requirement 5。

    提供移动平均计算、同比分析、异常检测和季节性模式识别功能。
    """

    def calculate_moving_average(
        self,
        data: List[Dict],
        value_field: str,
        window_size: int = 7,
    ) -> List[Dict]:
        """
        计算移动平均 - 满足 Requirement 5.1。

        Args:
            data: 时间序列数据列表
            value_field: 值字段名
            window_size: 窗口大小

        Returns:
            包含移动平均值的数据列表
        """
        if not data:
            return []

        # 确保值为数字类型
        def to_number(val):
            if val is None:
                return 0
            try:
                return float(val)
            except (ValueError, TypeError):
                return 0

        values = [to_number(d.get(value_field, 0)) for d in data]
        moving_averages = []

        for i in range(len(values)):
            if i < window_size - 1:
                # 窗口不足时使用可用数据
                window = values[:i + 1]
            else:
                window = values[i - window_size + 1:i + 1]

            ma = sum(window) / len(window) if window else 0
            moving_averages.append({
                **data[i],
                'moving_average': round(ma, 2),
            })

        return moving_averages

    def year_over_year(
        self,
        current_data: List[Dict],
        previous_data: List[Dict],
        value_field: str,
    ) -> List[Dict]:
        """
        计算同比数据 - 满足 Requirement 5.3。

        Args:
            current_data: 当期数据列表
            previous_data: 上期数据列表
            value_field: 值字段名

        Returns:
            包含同比增长率的数据列表
        """
        # 辅助函数：确保值为数字类型
        def to_number(val):
            if val is None:
                return 0
            try:
                return float(val)
            except (ValueError, TypeError):
                return 0

        # 构建上年数据映射
        prev_map = {}
        for d in previous_data:
            period = d.get('period')
            if period:
                prev_map[period] = to_number(d.get(value_field, 0))

        result = []
        for item in current_data:
            period = item.get('period')
            current_value = to_number(item.get(value_field, 0))
            prev_value = prev_map.get(period, 0)

            # 计算同比增长率
            if prev_value > 0:
                yoy_rate = (current_value - prev_value) / prev_value * 100
            else:
                yoy_rate = 100.0 if current_value > 0 else 0.0

            result.append({
                **item,
                'previous_value': prev_value,
                'yoy_rate': round(yoy_rate, 2),
            })

        return result

    def detect_anomalies(
        self,
        data: List[Dict],
        value_field: str,
        threshold: float = 2.0,
    ) -> List[Dict]:
        """
        检测异常值 - 满足 Requirement 5.5。

        使用 Z-score 方法，标记偏离均值超过 threshold 个标准差的数据点。

        Args:
            data: 数据列表
            value_field: 值字段名
            threshold: Z-score 阈值（默认 2.0）

        Returns:
            包含异常标记的数据列表
        """
        if not data:
            return []

        # 辅助函数：确保值为数字类型
        def to_number(val):
            if val is None:
                return 0
            try:
                return float(val)
            except (ValueError, TypeError):
                return 0

        values = [to_number(d.get(value_field, 0)) for d in data]

        if len(values) < 2:
            # 数据点不足，无法计算标准差
            return [{
                **item,
                'z_score': 0.0,
                'is_anomaly': False,
                'confidence': 'low',
            } for item in data]

        avg = mean(values)
        std = stdev(values) if len(values) > 1 else 0

        result = []
        for item in data:
            value = to_number(item.get(value_field, 0))

            # 计算 Z-score 并四舍五入，确保判断和存储使用一致的值
            raw_z_score = (value - avg) / std if std > 0 else 0.0
            z_score = round(raw_z_score, 2)
            
            is_anomaly = abs(z_score) > threshold

            # 置信度 - 满足 Requirement 5.4
            # 使用四舍五入后的 z_score 确保一致性
            if abs(z_score) > 3:
                confidence = 'high'
            elif abs(z_score) > 2:
                confidence = 'medium'
            else:
                confidence = 'low'

            result.append({
                **item,
                'z_score': z_score,
                'is_anomaly': is_anomaly,
                'confidence': confidence,
            })

        return result

    def identify_seasonal_patterns(
        self,
        data: List[Dict],
        value_field: str,
    ) -> Dict:
        """
        识别季节性模式 - 满足 Requirement 5.2。

        按月份分组计算平均值，识别高峰和低谷月份。

        Args:
            data: 数据列表
            value_field: 值字段名

        Returns:
            季节性模式分析结果
        """
        if not data:
            return {
                'pattern': {},
                'peak_month': None,
                'low_month': None,
            }

        # 辅助函数：确保值为数字类型
        def to_number(val):
            if val is None:
                return 0
            try:
                return float(val)
            except (ValueError, TypeError):
                return 0

        monthly_data = {}

        for item in data:
            period = item.get('period')
            if period:
                # 尝试从不同格式提取月份
                month = None
                if hasattr(period, 'month'):
                    month = period.month
                elif isinstance(period, str):
                    try:
                        # 尝试解析 YYYY-MM 或 YYYY-MM-DD 格式
                        if len(period) >= 7:
                            month = int(period[5:7])
                    except (ValueError, IndexError):
                        pass

                if month is not None:
                    if month not in monthly_data:
                        monthly_data[month] = []
                    value = to_number(item.get(value_field, 0))
                    monthly_data[month].append(value)

        # 计算每月平均值
        seasonal_pattern = {}
        for month, values in monthly_data.items():
            seasonal_pattern[month] = {
                'average': round(mean(values), 2) if values else 0,
                'sample_count': len(values),
            }

        # 找出高峰和低谷月份
        peak_month = None
        low_month = None
        if seasonal_pattern:
            peak_month = max(
                seasonal_pattern.keys(),
                key=lambda m: seasonal_pattern[m]['average']
            )
            low_month = min(
                seasonal_pattern.keys(),
                key=lambda m: seasonal_pattern[m]['average']
            )

        return {
            'pattern': seasonal_pattern,
            'peak_month': peak_month,
            'low_month': low_month,
        }



import math
from collections import defaultdict
from typing import Dict, List, Optional, Set, Tuple


class CollaborativeFilteringEngine:
    """
    协同过滤推荐引擎 - 满足 Requirements 1-3, 5。

    基于用户-用户协同过滤算法，通过分析用户历史订票行为，
    找到相似用户群体，并基于相似用户的购买记录为目标用户推荐航线。
    """

    def __init__(self, min_orders: int = 1, top_k_users: int = 10):
        """
        初始化推荐引擎。

        Args:
            min_orders: 用户最少订单数，低于此值不参与相似度计算
            top_k_users: 选取最相似的 K 个用户进行推荐
        """
        self.min_orders = min_orders
        self.top_k_users = top_k_users

    def calculate_implicit_rating(
        self,
        order_count: int,
        total_amount: float
    ) -> float:
        """
        计算隐式评分 - 满足 Requirement 1.3, 1.4。

        使用对数平滑公式避免极端值影响：
        rating = log(1 + order_count) + 0.1 * log(1 + total_amount / 1000)

        Args:
            order_count: 订票次数
            total_amount: 订单总金额

        Returns:
            隐式评分值
        """
        return math.log(1 + order_count) + 0.1 * math.log(1 + total_amount / 1000)

    def build_user_route_matrix(self) -> Dict[int, Dict[str, float]]:
        """
        构建用户-航线评分矩阵 - 满足 Requirement 1.1, 1.2。

        从 Order/Ticket/Flight 数据构建评分矩阵。

        Returns:
            {user_id: {route_key: implicit_rating}}
            route_key 格式: "departure_city->arrival_city"
        """
        # 查询已支付订单的航线数据
        orders = Order.objects.filter(
            status='paid'
        ).select_related('user').prefetch_related(
            'tickets__flight'
        )

        # 聚合用户-航线数据
        user_route_data: Dict[int, Dict[str, Dict[str, float]]] = defaultdict(
            lambda: defaultdict(lambda: {'count': 0, 'amount': 0.0})
        )

        for order in orders:
            user_id = order.user_id
            for ticket in order.tickets.all():
                flight = ticket.flight
                route_key = f"{flight.departure_city}->{flight.arrival_city}"
                user_route_data[user_id][route_key]['count'] += 1
                user_route_data[user_id][route_key]['amount'] += float(ticket.price)

        # 计算隐式评分
        user_route_matrix: Dict[int, Dict[str, float]] = {}
        for user_id, routes in user_route_data.items():
            user_route_matrix[user_id] = {}
            for route_key, data in routes.items():
                rating = self.calculate_implicit_rating(
                    data['count'],
                    data['amount']
                )
                user_route_matrix[user_id][route_key] = rating

        return user_route_matrix

    def calculate_user_similarity(
        self,
        user_id: int,
        matrix: Dict[int, Dict[str, float]]
    ) -> List[Tuple[int, float]]:
        """
        计算目标用户与其他用户的余弦相似度 - 满足 Requirement 2.1-2.4。

        Args:
            user_id: 目标用户 ID
            matrix: 用户-航线评分矩阵

        Returns:
            [(other_user_id, similarity_score), ...] 按相似度降序排列
        """
        if user_id not in matrix:
            return []

        target_routes = matrix[user_id]
        similarities: List[Tuple[int, float]] = []

        for other_user_id, other_routes in matrix.items():
            if other_user_id == user_id:
                continue

            # 检查用户是否有足够的订单记录 - 满足 Requirement 2.3
            if len(other_routes) < self.min_orders:
                continue

            # 计算余弦相似度
            similarity = self._cosine_similarity(target_routes, other_routes)
            if similarity > 0:
                similarities.append((other_user_id, similarity))

        # 按相似度降序排列
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities

    def _cosine_similarity(
        self,
        vec1: Dict[str, float],
        vec2: Dict[str, float]
    ) -> float:
        """
        计算两个向量的余弦相似度。

        Args:
            vec1: 第一个向量（航线->评分）
            vec2: 第二个向量（航线->评分）

        Returns:
            余弦相似度值，范围 [0, 1]
        """
        # 找到共同的航线
        common_routes = set(vec1.keys()) & set(vec2.keys())

        if not common_routes:
            # 无共同航线，相似度为 0 - 满足 Requirement 2.2
            return 0.0

        # 计算点积
        dot_product = sum(vec1[route] * vec2[route] for route in common_routes)

        # 计算向量模长
        norm1 = math.sqrt(sum(v ** 2 for v in vec1.values()))
        norm2 = math.sqrt(sum(v ** 2 for v in vec2.values()))

        if norm1 == 0 or norm2 == 0:
            return 0.0

        similarity = dot_product / (norm1 * norm2)
        # 限制在 [0, 1] 范围内，处理浮点数精度问题
        return max(0.0, min(1.0, similarity))

    def generate_recommendations(
        self,
        user_id: int,
        limit: int = 5
    ) -> List[Dict]:
        """
        为用户生成航线推荐 - 满足 Requirement 3.1-3.4, 3.6, 5.1-5.4。

        Args:
            user_id: 目标用户 ID
            limit: 返回推荐数量

        Returns:
            推荐航线列表，每项包含：
            - route: 航线标识
            - departure_city: 出发城市
            - arrival_city: 到达城市
            - predicted_score: 预测评分
            - confidence: 置信度
            - reason: 推荐理由
        """
        # 构建用户-航线矩阵
        matrix = self.build_user_route_matrix()

        if user_id not in matrix:
            # 用户无历史记录，返回空列表（由调用方处理冷启动）
            return []

        # 获取用户已购买的航线
        user_routes: Set[str] = set(matrix[user_id].keys())

        # 计算相似用户 - 满足 Requirement 5.1, 5.2
        similar_users = self.calculate_user_similarity(user_id, matrix)

        # 限制相似用户数量
        top_similar_users = similar_users[:self.top_k_users]

        if not top_similar_users:
            return []

        # 基于相似用户预测评分
        route_scores: Dict[str, Dict[str, float]] = defaultdict(
            lambda: {'weighted_sum': 0.0, 'similarity_sum': 0.0}
        )

        for other_user_id, similarity in top_similar_users:
            other_routes = matrix[other_user_id]
            for route, rating in other_routes.items():
                # 排除用户已购买的航线 - 满足 Requirement 3.3
                if route not in user_routes:
                    route_scores[route]['weighted_sum'] += similarity * rating
                    route_scores[route]['similarity_sum'] += similarity

        # 计算预测评分
        predictions: List[Tuple[str, float, float]] = []
        for route, scores in route_scores.items():
            if scores['similarity_sum'] > 0:
                predicted_score = scores['weighted_sum'] / scores['similarity_sum']
                confidence = min(scores['similarity_sum'], 1.0)
                predictions.append((route, predicted_score, confidence))

        # 按预测评分降序排列 - 满足 Requirement 3.4
        predictions.sort(key=lambda x: x[1], reverse=True)

        # 归一化评分到 [0, 1] 范围
        if predictions:
            max_score = predictions[0][1]  # 最高分（已排序）
            min_score = predictions[-1][1]  # 最低分
            score_range = max_score - min_score
            if score_range > 0:
                predictions = [
                    (route, (score - min_score) / score_range, conf)
                    for route, score, conf in predictions
                ]
            else:
                # 所有评分相同时，统一设为 1.0
                predictions = [(route, 1.0, conf) for route, score, conf in predictions]

        # 过滤已取消航班的航线 - 满足 Requirement 5.3
        valid_routes = self._get_valid_routes()

        # 生成推荐结果
        recommendations: List[Dict] = []
        for route, predicted_score, confidence in predictions:
            if route not in valid_routes:
                continue

            departure_city, arrival_city = route.split('->')
            recommendations.append({
                'route': route,
                'departure_city': departure_city,
                'arrival_city': arrival_city,
                'predicted_score': round(predicted_score, 4),
                'confidence': round(confidence, 4),
                'reason': '基于相似用户的购买偏好'
            })

            # 限制返回数量 - 满足 Requirement 3.6
            if len(recommendations) >= limit:
                break

        return recommendations

    def _get_valid_routes(self) -> Set[str]:
        """
        获取有效航线集合（排除已取消航班）。

        Returns:
            有效航线的集合
        """
        valid_flights = Flight.objects.exclude(
            status='canceled'
        ).values_list('departure_city', 'arrival_city').distinct()

        return {
            f"{dep}->{arr}" for dep, arr in valid_flights
        }


class PopularRouteService:
    """
    热门航线服务 - 满足 Requirement 3.5, 5.3。

    用于冷启动场景，基于订票量统计热门航线。
    """

    def get_popular_routes(self, limit: int = 5) -> List[Dict]:
        """
        获取热门航线（基于订票量）。

        Args:
            limit: 返回数量

        Returns:
            热门航线列表，每项包含：
            - route: 航线标识
            - departure_city: 出发城市
            - arrival_city: 到达城市
            - booking_count: 订票数量
            - reason: 推荐理由
        """
        # 统计已支付订单中各航线的订票量
        # 排除已取消航班 - 满足 Requirement 5.3
        route_stats = Ticket.objects.filter(
            order__status='paid',
            status='valid'
        ).exclude(
            flight__status='canceled'
        ).values(
            'flight__departure_city',
            'flight__arrival_city'
        ).annotate(
            booking_count=Count('id')
        ).order_by('-booking_count')[:limit]

        recommendations: List[Dict] = []
        for stat in route_stats:
            departure_city = stat['flight__departure_city']
            arrival_city = stat['flight__arrival_city']
            route = f"{departure_city}->{arrival_city}"

            recommendations.append({
                'route': route,
                'departure_city': departure_city,
                'arrival_city': arrival_city,
                'booking_count': stat['booking_count'],
                'reason': '热门航线推荐'
            })

        return recommendations
