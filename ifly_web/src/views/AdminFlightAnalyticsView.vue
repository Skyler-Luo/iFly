<template>
    <div class="admin-flight-analytics">
        <h1 class="title">航班数据分析</h1>

        <div class="filter-section">
            <div class="date-range">
                <label>时间范围：</label>
                <select v-model="timeRange">
                    <option value="week">最近一周</option>
                    <option value="month">最近一个月</option>
                    <option value="quarter">最近三个月</option>
                    <option value="year">最近一年</option>
                    <option value="custom">自定义范围</option>
                </select>
                <div v-if="timeRange === 'custom'" class="custom-date">
                    <input type="date" v-model="customStartDate">
                    <span>至</span>
                    <input type="date" v-model="customEndDate">
                    <button class="btn btn-sm" @click="applyCustomDate">应用</button>
                </div>
            </div>

            <div class="route-filter">
                <label>航线筛选：</label>
                <select v-model="routeFilter">
                    <option value="">所有航线</option>
                    <option v-for="route in popularRoutes" :key="route.id" :value="route.id">
                        {{ route.departureCity }} - {{ route.arrivalCity }}
                    </option>
                </select>
            </div>
        </div>

        <div class="analytics-cards">
            <div class="analytics-card">
                <h2>座位利用率</h2>
                <div class="chart-container">
                    <div class="mock-chart seat-utilization">
                        <div class="chart-value">{{ seatUtilization }}%</div>
                        <div class="progress-bar">
                            <div class="progress" :style="{ width: seatUtilization + '%' }"></div>
                        </div>
                    </div>
                    <div class="chart-footer">
                        <div class="comparison">
                            <i class="fas fa-arrow-up"></i> 较上期上升 2.5%
                        </div>
                    </div>
                </div>
            </div>

            <div class="analytics-card">
                <h2>平均票价</h2>
                <div class="chart-container">
                    <div class="mock-chart average-price">
                        <div class="chart-value">¥{{ averagePrice }}</div>
                        <div class="trend-indicator positive">
                            <i class="fas fa-arrow-up"></i> 5.2%
                        </div>
                    </div>
                    <div class="price-distribution">
                        <div class="price-type">
                            <span>经济舱</span>
                            <span>¥{{ priceDistribution.economy }}</span>
                        </div>
                        <div class="price-type">
                            <span>商务舱</span>
                            <span>¥{{ priceDistribution.business }}</span>
                        </div>
                        <div class="price-type">
                            <span>头等舱</span>
                            <span>¥{{ priceDistribution.first }}</span>
                        </div>
                    </div>
                </div>
            </div>

            <div class="analytics-card">
                <h2>准点率</h2>
                <div class="chart-container">
                    <div class="mock-chart punctuality">
                        <div class="chart-value">{{ punctualityRate }}%</div>
                        <div class="trend-indicator" :class="punctualityTrend.type">
                            <i :class="punctualityTrend.icon"></i> {{ punctualityTrend.value }}%
                        </div>
                    </div>
                    <div class="status-breakdown">
                        <div class="status-item">
                            <span class="status-label">准点</span>
                            <div class="status-bar">
                                <div class="status-progress on-time"
                                    :style="{ width: punctualityBreakdown.onTime + '%' }"></div>
                            </div>
                            <span class="status-value">{{ punctualityBreakdown.onTime }}%</span>
                        </div>
                        <div class="status-item">
                            <span class="status-label">延误</span>
                            <div class="status-bar">
                                <div class="status-progress delayed"
                                    :style="{ width: punctualityBreakdown.delayed + '%' }"></div>
                            </div>
                            <span class="status-value">{{ punctualityBreakdown.delayed }}%</span>
                        </div>
                        <div class="status-item">
                            <span class="status-label">取消</span>
                            <div class="status-bar">
                                <div class="status-progress cancelled"
                                    :style="{ width: punctualityBreakdown.cancelled + '%' }"></div>
                            </div>
                            <span class="status-value">{{ punctualityBreakdown.cancelled }}%</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="charts-row">
            <div class="chart-card full-width">
                <h2>航班载客量趋势</h2>
                <div class="line-chart-container">
                    <div class="mock-line-chart">
                        <div class="chart-grid">
                            <div v-for="n in 5" :key="n" class="grid-line"></div>
                        </div>
                        <div class="line-path" :style="getPathStyle()"></div>
                        <div class="data-points">
                            <div v-for="(point, index) in passengerTrendData" :key="index" class="data-point"
                                :style="getPointStyle(point, index)">
                                <div class="point-tooltip">{{ point.date }}: {{ point.value }}人</div>
                            </div>
                        </div>
                    </div>
                    <div class="chart-legend">
                        <div v-for="(month, index) in trendMonths" :key="index" class="legend-item">
                            {{ month }}
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="analytics-tables">
            <div class="table-card">
                <h2>最受欢迎航线</h2>
                <table>
                    <thead>
                        <tr>
                            <th>排名</th>
                            <th>出发城市</th>
                            <th>到达城市</th>
                            <th>平均载客率</th>
                            <th>平均票价</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="(route, index) in topRoutes" :key="route.id">
                            <td class="rank">{{ index + 1 }}</td>
                            <td>{{ route.departureCity }}</td>
                            <td>{{ route.arrivalCity }}</td>
                            <td>{{ route.loadFactor }}%</td>
                            <td>¥{{ route.averagePrice }}</td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <div class="table-card">
                <h2>异常航班</h2>
                <table>
                    <thead>
                        <tr>
                            <th>航班号</th>
                            <th>日期</th>
                            <th>航线</th>
                            <th>状态</th>
                            <th>延误时间</th>
                            <th>原因</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="flight in irregularFlights" :key="flight.id">
                            <td>{{ flight.flightNumber }}</td>
                            <td>{{ flight.date }}</td>
                            <td>{{ flight.route }}</td>
                            <td><span :class="'status-' + flight.status.toLowerCase()">{{ getStatusText(flight.status)
                                    }}</span></td>
                            <td>{{ flight.delayTime || '-' }}</td>
                            <td>{{ flight.reason || '-' }}</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: 'AdminFlightAnalyticsView',
    data() {
        return {
            timeRange: 'month',
            customStartDate: '',
            customEndDate: '',
            routeFilter: '',
            seatUtilization: 78.5,
            averagePrice: 1250,
            punctualityRate: 86.5,
            punctualityTrend: {
                type: 'negative',
                icon: 'fas fa-arrow-down',
                value: 2.3
            },
            punctualityBreakdown: {
                onTime: 86.5,
                delayed: 10.8,
                cancelled: 2.7
            },
            priceDistribution: {
                economy: 820,
                business: 2600,
                first: 4800
            },
            passengerTrendData: [
                { date: '1月', value: 62 },
                { date: '2月', value: 58 },
                { date: '3月', value: 65 },
                { date: '4月', value: 75 },
                { date: '5月', value: 70 },
                { date: '6月', value: 85 },
                { date: '7月', value: 92 },
                { date: '8月', value: 88 }
            ],
            trendMonths: ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月'],
            topRoutes: [
                { id: 1, departureCity: '北京', arrivalCity: '上海', loadFactor: 92, averagePrice: 1200 },
                { id: 2, departureCity: '广州', arrivalCity: '北京', loadFactor: 88, averagePrice: 1450 },
                { id: 3, departureCity: '深圳', arrivalCity: '成都', loadFactor: 85, averagePrice: 1320 },
                { id: 4, departureCity: '上海', arrivalCity: '广州', loadFactor: 82, averagePrice: 1050 },
                { id: 5, departureCity: '成都', arrivalCity: '杭州', loadFactor: 79, averagePrice: 980 },
            ],
            popularRoutes: [
                { id: 1, departureCity: '北京', arrivalCity: '上海' },
                { id: 2, departureCity: '广州', arrivalCity: '北京' },
                { id: 3, departureCity: '深圳', arrivalCity: '成都' },
                { id: 4, departureCity: '上海', arrivalCity: '广州' },
                { id: 5, departureCity: '成都', arrivalCity: '杭州' },
            ],
            irregularFlights: [
                {
                    id: 1,
                    flightNumber: 'CA1235',
                    date: '2023-07-25',
                    route: '北京 - 上海',
                    status: 'DELAYED',
                    delayTime: '1小时30分钟',
                    reason: '天气原因'
                },
                {
                    id: 2,
                    flightNumber: 'MU5642',
                    date: '2023-07-24',
                    route: '广州 - 成都',
                    status: 'CANCELLED',
                    delayTime: null,
                    reason: '机械故障'
                },
                {
                    id: 3,
                    flightNumber: 'CZ3382',
                    date: '2023-07-25',
                    route: '深圳 - 北京',
                    status: 'DELAYED',
                    delayTime: '45分钟',
                    reason: '空中交通管制'
                },
                {
                    id: 4,
                    flightNumber: 'HU7809',
                    date: '2023-07-23',
                    route: '上海 - 西安',
                    status: 'DELAYED',
                    delayTime: '2小时15分钟',
                    reason: '天气原因'
                },
            ]
        }
    },
    methods: {
        applyCustomDate() {
            console.log('应用自定义日期范围:', this.customStartDate, '至', this.customEndDate);
            // 实际应用中这里需要调用API获取该时间段的数据
        },
        getStatusText(status) {
            const statusMap = {
                'DELAYED': '延误',
                'CANCELLED': '取消',
                'DIVERTED': '备降'
            };
            return statusMap[status] || status;
        },
        getPathStyle() {
            // 模拟生成趋势线路径
            // 实际项目中应使用数据点坐标生成SVG路径
            return {
                backgroundImage: 'linear-gradient(transparent, transparent), linear-gradient(to right, transparent, #3f51b5)'
            };
        },
        getPointStyle(point, index) {
            // 计算点的位置
            const x = (index / (this.passengerTrendData.length - 1)) * 100;
            const y = 100 - ((point.value - 50) / 50) * 100;
            return {
                left: `${x}%`,
                bottom: `${y}%`
            };
        }
    },
    mounted() {
        // 设置默认自定义日期为当前日期前30天到今天
        const today = new Date();
        const thirtyDaysAgo = new Date();
        thirtyDaysAgo.setDate(today.getDate() - 30);

        this.customEndDate = today.toISOString().split('T')[0];
        this.customStartDate = thirtyDaysAgo.toISOString().split('T')[0];
    }
}
</script>

<style scoped>
.admin-flight-analytics {
    padding: 20px;
    max-width: 1200px;
    margin: 0 auto;
}

.title {
    font-size: 24px;
    color: #333;
    margin-bottom: 20px;
    border-bottom: 2px solid #3f51b5;
    padding-bottom: 10px;
}

.filter-section {
    display: flex;
    flex-wrap: wrap;
    gap: 20px;
    margin-bottom: 30px;
    background: white;
    padding: 15px;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.date-range,
.route-filter {
    display: flex;
    align-items: center;
    gap: 10px;
}

.date-range label,
.route-filter label {
    font-weight: bold;
    white-space: nowrap;
}

.date-range select,
.route-filter select {
    padding: 8px;
    border: 1px solid #ddd;
    border-radius: 4px;
    background-color: white;
}

.custom-date {
    display: flex;
    align-items: center;
    gap: 8px;
}

.custom-date input {
    padding: 8px;
    border: 1px solid #ddd;
    border-radius: 4px;
}

.btn {
    padding: 8px 16px;
    border: none;
    border-radius: 4px;
    background-color: #3f51b5;
    color: white;
    cursor: pointer;
}

.btn-sm {
    padding: 6px 12px;
    font-size: 14px;
}

.analytics-cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 20px;
    margin-bottom: 30px;
}

.analytics-card {
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    padding: 20px;
}

.analytics-card h2 {
    font-size: 18px;
    margin-bottom: 15px;
    color: #333;
}

.chart-container {
    padding: 10px 0;
}

.chart-value {
    font-size: 36px;
    font-weight: bold;
    color: #333;
    text-align: center;
    margin-bottom: 10px;
}

.progress-bar {
    height: 10px;
    background-color: #e0e0e0;
    border-radius: 5px;
    margin: 15px 0;
    overflow: hidden;
}

.progress {
    height: 100%;
    background-color: #4CAF50;
    border-radius: 5px;
}

.chart-footer {
    display: flex;
    justify-content: center;
    margin-top: 15px;
}

.comparison {
    color: #4CAF50;
    font-size: 14px;
}

.trend-indicator {
    display: inline-block;
    margin-left: 10px;
    padding: 3px 8px;
    border-radius: 4px;
    font-size: 14px;
}

.trend-indicator.positive {
    background-color: rgba(76, 175, 80, 0.1);
    color: #4CAF50;
}

.trend-indicator.negative {
    background-color: rgba(244, 67, 54, 0.1);
    color: #F44336;
}

.price-distribution {
    margin-top: 20px;
}

.price-type {
    display: flex;
    justify-content: space-between;
    padding: 8px 0;
    border-bottom: 1px solid #eee;
}

.price-type:last-child {
    border-bottom: none;
}

.status-breakdown {
    margin-top: 20px;
}

.status-item {
    display: flex;
    align-items: center;
    margin-bottom: 10px;
}

.status-label {
    width: 40px;
    font-size: 14px;
}

.status-bar {
    flex: 1;
    height: 8px;
    background-color: #e0e0e0;
    border-radius: 4px;
    margin: 0 10px;
    overflow: hidden;
}

.status-progress {
    height: 100%;
    border-radius: 4px;
}

.status-progress.on-time {
    background-color: #4CAF50;
}

.status-progress.delayed {
    background-color: #FFC107;
}

.status-progress.cancelled {
    background-color: #F44336;
}

.status-value {
    width: 40px;
    text-align: right;
    font-size: 14px;
}

.charts-row {
    margin-bottom: 30px;
}

.chart-card {
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    padding: 20px;
}

.chart-card.full-width {
    grid-column: 1 / -1;
}

.chart-card h2 {
    font-size: 18px;
    margin-bottom: 15px;
    color: #333;
}

.line-chart-container {
    height: 250px;
    position: relative;
}

.mock-line-chart {
    height: 200px;
    position: relative;
    border-bottom: 1px solid #ddd;
    border-left: 1px solid #ddd;
}

.chart-grid .grid-line {
    position: absolute;
    left: 0;
    width: 100%;
    height: 1px;
    background-color: rgba(0, 0, 0, 0.05);
}

.chart-grid .grid-line:nth-child(1) {
    bottom: 20%;
}

.chart-grid .grid-line:nth-child(2) {
    bottom: 40%;
}

.chart-grid .grid-line:nth-child(3) {
    bottom: 60%;
}

.chart-grid .grid-line:nth-child(4) {
    bottom: 80%;
}

.chart-grid .grid-line:nth-child(5) {
    bottom: 100%;
}

.line-path {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 100%;
    background-repeat: no-repeat;
    background-size: 100% 100%;
}

.data-points {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
}

.data-point {
    position: absolute;
    width: 10px;
    height: 10px;
    background-color: #3f51b5;
    border-radius: 50%;
    transform: translate(-50%, 50%);
    cursor: pointer;
    z-index: 5;
}

.data-point:hover .point-tooltip {
    display: block;
}

.point-tooltip {
    display: none;
    position: absolute;
    bottom: 100%;
    left: 50%;
    transform: translateX(-50%);
    background-color: rgba(0, 0, 0, 0.8);
    color: white;
    padding: 5px 8px;
    border-radius: 4px;
    font-size: 12px;
    white-space: nowrap;
    margin-bottom: 5px;
}

.point-tooltip::after {
    content: '';
    position: absolute;
    top: 100%;
    left: 50%;
    margin-left: -5px;
    border-width: 5px;
    border-style: solid;
    border-color: rgba(0, 0, 0, 0.8) transparent transparent transparent;
}

.chart-legend {
    display: flex;
    justify-content: space-between;
    margin-top: 10px;
}

.legend-item {
    font-size: 12px;
    color: #666;
}

.analytics-tables {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
    gap: 20px;
}

.table-card {
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    padding: 20px;
    overflow: auto;
}

.table-card h2 {
    font-size: 18px;
    margin-bottom: 15px;
    color: #333;
}

table {
    width: 100%;
    border-collapse: collapse;
}

table th,
table td {
    padding: 12px;
    text-align: left;
    border-bottom: 1px solid #eee;
}

table th {
    font-weight: 600;
    color: #333;
    background-color: #f9f9f9;
}

.rank {
    font-weight: bold;
    color: #3f51b5;
}

.status-delayed {
    color: #FFC107;
    font-weight: bold;
}

.status-cancelled {
    color: #F44336;
    font-weight: bold;
}

.status-diverted {
    color: #9C27B0;
    font-weight: bold;
}

@media (max-width: 768px) {
    .filter-section {
        flex-direction: column;
        align-items: flex-start;
    }

    .analytics-cards {
        grid-template-columns: 1fr;
    }

    .analytics-tables {
        grid-template-columns: 1fr;
    }
}
</style>