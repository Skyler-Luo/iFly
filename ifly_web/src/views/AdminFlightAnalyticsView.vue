<template>
    <div class="admin-flight-analytics">
        <h1 class="title">航班数据分析</h1>

        <!-- 加载状态 -->
        <div v-if="loading" class="loading-container">
            <i class="el-icon-loading"></i>
            <span>加载中...</span>
        </div>

        <!-- 错误提示 -->
        <div v-else-if="error" class="error-container">
            <i class="fas fa-exclamation-circle"></i>
            <span>{{ error }}</span>
            <button class="btn-retry" @click="fetchData">重试</button>
        </div>

        <template v-else>
            <div class="filter-section">
                <div class="date-range">
                    <label>时间范围：</label>
                    <select v-model="timeRange" @change="updateData">
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
                    <select v-model="routeFilter" @change="updateData">
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
                            <div class="chart-value" v-if="seatUtilization !== null">{{ seatUtilization }}%</div>
                            <div class="chart-value no-data" v-else>数据暂无</div>
                            <div class="progress-bar" v-if="seatUtilization !== null">
                                <div class="progress" :style="{ width: seatUtilization + '%' }"></div>
                            </div>
                        </div>
                        <div class="chart-footer" v-if="seatUtilizationTrend !== null">
                            <div class="comparison" :class="seatUtilizationTrend >= 0 ? 'positive' : 'negative'">
                                <i :class="seatUtilizationTrend >= 0 ? 'fas fa-arrow-up' : 'fas fa-arrow-down'"></i>
                                较上期{{ seatUtilizationTrend >= 0 ? '上升' : '下降' }} {{ Math.abs(seatUtilizationTrend) }}%
                            </div>
                        </div>
                    </div>
                </div>

                <div class="analytics-card">
                    <h2>平均票价</h2>
                    <div class="chart-container">
                        <div class="mock-chart average-price">
                            <div class="chart-value" v-if="averagePrice !== null">¥{{ averagePrice }}</div>
                            <div class="chart-value no-data" v-else>数据暂无</div>
                            <div class="trend-indicator" :class="averagePriceTrend >= 0 ? 'positive' : 'negative'" v-if="averagePriceTrend !== null">
                                <i :class="averagePriceTrend >= 0 ? 'fas fa-arrow-up' : 'fas fa-arrow-down'"></i> {{ Math.abs(averagePriceTrend) }}%
                            </div>
                        </div>
                        <div class="price-distribution" v-if="priceDistribution.economy !== null">
                            <div class="price-type">
                                <span>经济舱</span>
                                <span>¥{{ priceDistribution.economy || '暂无' }}</span>
                            </div>
                            <div class="price-type">
                                <span>商务舱</span>
                                <span>¥{{ priceDistribution.business || '暂无' }}</span>
                            </div>
                            <div class="price-type">
                                <span>头等舱</span>
                                <span>¥{{ priceDistribution.first || '暂无' }}</span>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="analytics-card">
                    <h2>准点率</h2>
                    <div class="chart-container">
                        <div class="mock-chart punctuality">
                            <div class="chart-value" v-if="punctualityRate !== null">{{ punctualityRate }}%</div>
                            <div class="chart-value no-data" v-else>数据暂无</div>
                            <div class="trend-indicator" :class="punctualityTrend.type" v-if="punctualityTrend.value !== null">
                                <i :class="punctualityTrend.icon"></i> {{ Math.abs(punctualityTrend.value) }}%
                            </div>
                        </div>
                        <div class="status-breakdown" v-if="punctualityBreakdown.onTime !== null">
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
                        <div class="mock-line-chart" v-if="passengerTrendData.length > 0">
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
                        <div v-else class="no-data-chart">
                            <i class="fas fa-chart-line"></i>
                            <span>数据暂无</span>
                        </div>
                        <div class="chart-legend" v-if="trendMonths.length > 0">
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
                    <table v-if="topRoutes.length > 0">
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
                            <tr v-for="(route, index) in topRoutes" :key="route.id || index">
                                <td class="rank">{{ index + 1 }}</td>
                                <td>{{ route.departureCity || route.departure_city }}</td>
                                <td>{{ route.arrivalCity || route.arrival_city }}</td>
                                <td>{{ route.loadFactor || route.count || 0 }}%</td>
                                <td>¥{{ route.averagePrice || '-' }}</td>
                            </tr>
                        </tbody>
                    </table>
                    <div v-else class="no-data-table">
                        <i class="fas fa-inbox"></i>
                        <span>数据暂无</span>
                    </div>
                </div>

                <div class="table-card">
                    <h2>异常航班</h2>
                    <table v-if="irregularFlights.length > 0">
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
                                <td><span :class="'status-' + flight.status.toLowerCase()">{{ getStatusText(flight.status) }}</span></td>
                                <td>{{ flight.delayTime || '-' }}</td>
                                <td>{{ flight.reason || '-' }}</td>
                            </tr>
                        </tbody>
                    </table>
                    <div v-else class="no-data-table">
                        <i class="fas fa-inbox"></i>
                        <span>数据暂无</span>
                    </div>
                </div>
            </div>
        </template>
    </div>
</template>


<script>
import api from '@/services/api'

export default {
    name: 'AdminFlightAnalyticsView',
    data() {
        return {
            // 加载状态
            loading: false,
            error: null,
            
            // 筛选条件
            timeRange: 'month',
            customStartDate: '',
            customEndDate: '',
            routeFilter: '',
            
            // 座位利用率
            seatUtilization: null,
            seatUtilizationTrend: null,
            
            // 平均票价
            averagePrice: null,
            averagePriceTrend: null,
            
            // 准点率
            punctualityRate: null,
            punctualityTrend: {
                type: 'positive',
                icon: 'fas fa-arrow-up',
                value: null
            },
            punctualityBreakdown: {
                onTime: null,
                delayed: null,
                cancelled: null
            },
            
            // 票价分布
            priceDistribution: {
                economy: null,
                business: null,
                first: null
            },
            
            // 载客趋势数据
            passengerTrendData: [],
            trendMonths: [],
            
            // 热门航线
            topRoutes: [],
            popularRoutes: [],
            
            // 异常航班
            irregularFlights: []
        }
    },
    methods: {
        // 获取日期范围参数
        getDateParams() {
            const today = new Date()
            let startDate, endDate
            
            switch (this.timeRange) {
                case 'week':
                    startDate = new Date(today)
                    startDate.setDate(today.getDate() - 7)
                    endDate = today
                    break
                case 'month':
                    startDate = new Date(today)
                    startDate.setDate(today.getDate() - 30)
                    endDate = today
                    break
                case 'quarter':
                    startDate = new Date(today)
                    startDate.setDate(today.getDate() - 90)
                    endDate = today
                    break
                case 'year':
                    startDate = new Date(today)
                    startDate.setFullYear(today.getFullYear() - 1)
                    endDate = today
                    break
                case 'custom':
                    startDate = this.customStartDate ? new Date(this.customStartDate) : null
                    endDate = this.customEndDate ? new Date(this.customEndDate) : null
                    break
                default:
                    startDate = new Date(today)
                    startDate.setDate(today.getDate() - 30)
                    endDate = today
            }
            
            return {
                start_date: startDate ? startDate.toISOString().split('T')[0] : undefined,
                end_date: endDate ? endDate.toISOString().split('T')[0] : undefined
            }
        },
        
        async fetchData() {
            this.loading = true
            this.error = null
            
            try {
                const params = this.getDateParams()
                const response = await api.admin.analytics.getFlightStats(params)
                
                // 处理返回数据
                this.processFlightData(response)
            } catch (err) {
                console.error('获取航班分析数据失败:', err)
                this.error = err.message || '获取数据失败，请稍后重试'
                // 清空数据
                this.clearData()
            } finally {
                this.loading = false
            }
        },

        processFlightData(data) {
            // 处理平均上座率
            if (data.avg_occupancy_rate !== undefined && data.avg_occupancy_rate !== null) {
                this.seatUtilization = Math.round(data.avg_occupancy_rate * 10) / 10
            } else {
                this.seatUtilization = null
            }
            
            // 处理热门航线
            if (data.popular_routes && data.popular_routes.length > 0) {
                this.topRoutes = data.popular_routes.map((route, index) => ({
                    id: index + 1,
                    departureCity: route.departure_city,
                    arrivalCity: route.arrival_city,
                    loadFactor: route.count || 0,
                    averagePrice: '-'
                }))
                
                // 同时更新筛选器中的航线列表
                this.popularRoutes = this.topRoutes.slice(0, 5)
            } else {
                this.topRoutes = []
                this.popularRoutes = []
            }
            
            // 处理航线收入数据
            if (data.route_revenue && data.route_revenue.length > 0) {
                // 更新热门航线的票价信息
                data.route_revenue.forEach(routeRev => {
                    const matchingRoute = this.topRoutes.find(r => 
                        `${r.departureCity} - ${r.arrivalCity}` === routeRev.route
                    )
                    if (matchingRoute && routeRev.revenue && routeRev.flight_count) {
                        matchingRoute.averagePrice = Math.round(routeRev.revenue / routeRev.flight_count)
                    }
                })
            }
            
            // 准点率数据（后端暂不支持，显示为暂无）
            this.punctualityRate = null
            this.punctualityTrend.value = null
            this.punctualityBreakdown = {
                onTime: null,
                delayed: null,
                cancelled: null
            }
            
            // 票价分布（后端暂不支持，显示为暂无）
            this.priceDistribution = {
                economy: null,
                business: null,
                first: null
            }
            this.averagePrice = null
            this.averagePriceTrend = null
            
            // 载客趋势数据（后端暂不支持）
            this.passengerTrendData = []
            this.trendMonths = []
            
            // 异常航班（后端暂不支持）
            this.irregularFlights = []
        },
        
        clearData() {
            this.seatUtilization = null
            this.seatUtilizationTrend = null
            this.averagePrice = null
            this.averagePriceTrend = null
            this.punctualityRate = null
            this.punctualityTrend = {
                type: 'positive',
                icon: 'fas fa-arrow-up',
                value: null
            }
            this.punctualityBreakdown = {
                onTime: null,
                delayed: null,
                cancelled: null
            }
            this.priceDistribution = {
                economy: null,
                business: null,
                first: null
            }
            this.passengerTrendData = []
            this.trendMonths = []
            this.topRoutes = []
            this.popularRoutes = []
            this.irregularFlights = []
        },
        
        updateData() {
            this.fetchData()
        },
        
        applyCustomDate() {
            this.fetchData()
        },
        
        getStatusText(status) {
            const statusMap = {
                'DELAYED': '延误',
                'CANCELLED': '取消',
                'DIVERTED': '备降'
            }
            return statusMap[status] || status
        },
        
        getPathStyle() {
            return {
                backgroundImage: 'linear-gradient(transparent, transparent), linear-gradient(to right, transparent, #3f51b5)'
            }
        },
        
        getPointStyle(point, index) {
            if (this.passengerTrendData.length === 0) return {}
            const x = (index / (this.passengerTrendData.length - 1)) * 100
            const maxValue = Math.max(...this.passengerTrendData.map(p => p.value)) || 100
            const y = ((point.value / maxValue) * 80) + 10
            return {
                left: `${x}%`,
                bottom: `${y}%`
            }
        }
    },
    mounted() {
        // 设置默认自定义日期
        const today = new Date()
        const thirtyDaysAgo = new Date()
        thirtyDaysAgo.setDate(today.getDate() - 30)

        this.customEndDate = today.toISOString().split('T')[0]
        this.customStartDate = thirtyDaysAgo.toISOString().split('T')[0]
        
        // 获取数据
        this.fetchData()
    }
}
</script>


<style scoped>
.admin-flight-analytics {
    padding: 20px 40px;
    width: 100%;
    box-sizing: border-box;
}

.title {
    font-size: 24px;
    color: #333;
    margin-bottom: 20px;
    border-bottom: 2px solid #3f51b5;
    padding-bottom: 10px;
}

.loading-container,
.error-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 60px 20px;
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.loading-container i,
.error-container i {
    font-size: 48px;
    color: #999;
    margin-bottom: 16px;
}

.error-container i {
    color: #F44336;
}

.btn-retry {
    margin-top: 16px;
    padding: 8px 24px;
    background-color: #3f51b5;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
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

.chart-value.no-data {
    color: #999;
    font-size: 18px;
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
    font-size: 14px;
}

.comparison.positive {
    color: #4CAF50;
}

.comparison.negative {
    color: #F44336;
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

.no-data-chart,
.no-data-table {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 200px;
    color: #999;
}

.no-data-chart i,
.no-data-table i {
    font-size: 48px;
    margin-bottom: 12px;
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

.chart-grid .grid-line:nth-child(1) { bottom: 20%; }
.chart-grid .grid-line:nth-child(2) { bottom: 40%; }
.chart-grid .grid-line:nth-child(3) { bottom: 60%; }
.chart-grid .grid-line:nth-child(4) { bottom: 80%; }
.chart-grid .grid-line:nth-child(5) { bottom: 100%; }

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
