<template>
    <div class="admin-analytics">
        <div class="page-header">
            <h1>数据分析中心</h1>
            <div class="date-range-picker">
                <el-date-picker v-model="dateRange" type="daterange" range-separator="至" start-placeholder="开始日期"
                    end-placeholder="结束日期" :shortcuts="dateRangeShortcuts" @change="handleDateRangeChange"
                    size="small" />
                <el-button type="primary" size="small" @click="refreshData">
                    <i class="fas fa-sync-alt"></i> 刷新数据
                </el-button>
            </div>
        </div>

        <el-row :gutter="20">
            <el-col :span="24">
                <el-card class="analytics-card">
                    <div class="card-header">
                        <h2>业务总览</h2>
                        <div class="card-actions">
                            <el-button-group>
                                <el-button size="small" :type="viewMode === 'value' ? 'primary' : ''"
                                    @click="viewMode = 'value'">绝对值</el-button>
                                <el-button size="small" :type="viewMode === 'percent' ? 'primary' : ''"
                                    @click="viewMode = 'percent'">环比</el-button>
                            </el-button-group>
                        </div>
                    </div>

                    <div class="metric-cards">
                        <div class="metric-card" v-for="(metric, index) in metrics" :key="index">
                            <div class="metric-icon"
                                :style="{ backgroundColor: metric.color + '15', color: metric.color }">
                                <i :class="metric.icon"></i>
                            </div>
                            <div class="metric-content">
                                <div class="metric-title">{{ metric.title }}</div>
                                <div class="metric-value" v-if="viewMode === 'value'">{{ formatNumber(metric.value) }}
                                </div>
                                <div class="metric-value" v-else>
                                    <span :class="{ 'text-up': metric.trend > 0, 'text-down': metric.trend < 0 }">
                                        {{ metric.trend > 0 ? '+' : '' }}{{ metric.trend }}%
                                    </span>
                                </div>
                            </div>
                        </div>
                    </div>
                </el-card>
            </el-col>
        </el-row>

        <el-row :gutter="20" class="mt-20">
            <el-col :span="16">
                <el-card class="analytics-card">
                    <div class="card-header">
                        <h2>销售趋势分析</h2>
                        <div class="card-actions">
                            <el-radio-group v-model="salesTrendTimeUnit" size="small" @change="updateSalesTrend">
                                <el-radio-button value="day">日</el-radio-button>
                                <el-radio-button value="week">周</el-radio-button>
                                <el-radio-button value="month">月</el-radio-button>
                            </el-radio-group>
                        </div>
                    </div>
                    <div class="chart-container" style="height: 400px;">
                        <v-chart :option="salesTrendOption" autoresize />
                    </div>
                </el-card>
            </el-col>

            <el-col :span="8">
                <el-card class="analytics-card">
                    <div class="card-header">
                        <h2>客户群体分析</h2>
                    </div>
                    <div class="chart-container" style="height: 400px;">
                        <v-chart :option="customerSegmentOption" autoresize />
                    </div>
                </el-card>
            </el-col>
        </el-row>

        <el-row :gutter="20" class="mt-20">
            <el-col :span="12">
                <el-card class="analytics-card">
                    <div class="card-header">
                        <h2>城市航线分析</h2>
                    </div>
                    <div class="chart-container" style="height: 400px;">
                        <v-chart :option="routeMapOption" autoresize />
                    </div>
                </el-card>
            </el-col>

            <el-col :span="12">
                <el-card class="analytics-card">
                    <div class="card-header">
                        <h2>客户忠诚度分析</h2>
                    </div>
                    <div class="chart-container" style="height: 400px;">
                        <v-chart :option="customerLoyaltyOption" autoresize />
                    </div>
                </el-card>
            </el-col>
        </el-row>

        <el-row :gutter="20" class="mt-20">
            <el-col :span="24">
                <el-card class="analytics-card">
                    <div class="card-header">
                        <h2>数据透视表</h2>
                        <div class="card-actions">
                            <el-select v-model="pivotDimension" placeholder="选择维度" size="small">
                                <el-option label="航班" value="flight" />
                                <el-option label="城市" value="city" />
                                <el-option label="用户类型" value="userType" />
                                <el-option label="支付方式" value="paymentMethod" />
                            </el-select>
                            <el-select v-model="pivotMetric" placeholder="选择指标" size="small" style="margin-left: 10px;">
                                <el-option label="销售额" value="revenue" />
                                <el-option label="订单数" value="orders" />
                                <el-option label="平均客单价" value="averageValue" />
                                <el-option label="退票率" value="refundRate" />
                            </el-select>
                            <el-button size="small" type="success" style="margin-left: 10px;">导出Excel</el-button>
                        </div>
                    </div>

                    <el-table :data="pivotTableData" style="width: 100%" :border="true" :stripe="true" height="400px">
                        <el-table-column prop="dimension" label="维度" fixed />
                        <el-table-column prop="value" :label="pivotMetricLabel" sortable>
                            <template #default="scope">
                                <div>
                                    {{ formatNumber(scope.row.value) }}
                                    <div class="trend-indicator"
                                        :class="{ 'trend-up': scope.row.trend > 0, 'trend-down': scope.row.trend < 0 }">
                                        {{ scope.row.trend > 0 ? '+' : '' }}{{ scope.row.trend }}%
                                    </div>
                                </div>
                            </template>
                        </el-table-column>
                        <el-table-column prop="previousValue" label="上期" sortable>
                            <template #default="scope">
                                {{ formatNumber(scope.row.previousValue) }}
                            </template>
                        </el-table-column>
                        <el-table-column prop="percentage" label="占比" sortable>
                            <template #default="scope">
                                <el-progress :percentage="scope.row.percentage"
                                    :color="getProgressColor(scope.row.percentage)" />
                            </template>
                        </el-table-column>
                    </el-table>
                </el-card>
            </el-col>
        </el-row>

        <el-row :gutter="20" class="mt-20">
            <el-col :span="24">
                <el-card class="analytics-card">
                    <div class="card-header">
                        <h2>实时监控</h2>
                    </div>

                    <el-row :gutter="20">
                        <el-col :span="8">
                            <div class="realtime-card">
                                <div class="realtime-header">
                                    <div class="realtime-title">在线用户数</div>
                                    <el-tag size="small" type="success">实时</el-tag>
                                </div>
                                <div class="realtime-value">{{ realtimeData.onlineUsers }}</div>
                                <div class="realtime-chart">
                                    <v-chart :option="onlineUserChartOption" autoresize />
                                </div>
                            </div>
                        </el-col>

                        <el-col :span="8">
                            <div class="realtime-card">
                                <div class="realtime-header">
                                    <div class="realtime-title">订单转化率</div>
                                    <el-tag size="small" type="success">实时</el-tag>
                                </div>
                                <div class="realtime-value">{{ realtimeData.conversionRate }}%</div>
                                <div class="realtime-chart">
                                    <v-chart :option="conversionRateChartOption" autoresize />
                                </div>
                            </div>
                        </el-col>

                        <el-col :span="8">
                            <div class="realtime-card">
                                <div class="realtime-header">
                                    <div class="realtime-title">每分钟搜索次数</div>
                                    <el-tag size="small" type="success">实时</el-tag>
                                </div>
                                <div class="realtime-value">{{ realtimeData.searchesPerMinute }}</div>
                                <div class="realtime-chart">
                                    <v-chart :option="searchRateChartOption" autoresize />
                                </div>
                            </div>
                        </el-col>
                    </el-row>
                </el-card>
            </el-col>
        </el-row>
    </div>
</template>

<script>
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import {
    BarChart,
    LineChart,
    PieChart,
    GaugeChart,
    RadarChart,
    ScatterChart
} from 'echarts/charts'
import {
    TitleComponent,
    TooltipComponent,
    LegendComponent,
    GridComponent,
    DataZoomComponent,
    ToolboxComponent,
    VisualMapComponent,
    GeoComponent
} from 'echarts/components'
import VChart from 'vue-echarts'
import api from '../services/api'
import { ElMessage } from 'element-plus'

use([
    CanvasRenderer,
    BarChart,
    LineChart,
    PieChart,
    GaugeChart,
    RadarChart,
    ScatterChart,
    TitleComponent,
    TooltipComponent,
    LegendComponent,
    GridComponent,
    DataZoomComponent,
    ToolboxComponent,
    VisualMapComponent,
    GeoComponent
])

export default {
    name: 'AdminAnalyticsView',
    components: {
        VChart
    },
    data() {
        return {
            dateRange: null,
            viewMode: 'value',
            salesTrendTimeUnit: 'day',
            pivotDimension: 'flight',
            pivotMetric: 'revenue',
            loading: false,
            error: null,

            metrics: [
                {
                    title: '总销售额',
                    icon: 'fas fa-yuan-sign',
                    color: '#4caf50',
                    value: 0,
                    trend: 0
                },
                {
                    title: '订单数量',
                    icon: 'fas fa-shopping-cart',
                    color: '#2196f3',
                    value: 0,
                    trend: 0
                },
                {
                    title: '客单价',
                    icon: 'fas fa-receipt',
                    color: '#ff9800',
                    value: 0,
                    trend: 0
                },
                {
                    title: '用户数',
                    icon: 'fas fa-users',
                    color: '#9c27b0',
                    value: 0,
                    trend: 0
                },
                {
                    title: '退票率',
                    icon: 'fas fa-undo',
                    color: '#f44336',
                    value: 0,
                    trend: 0
                }
            ],

            salesTrendData: {
                dates: [],
                revenue: [],
                orders: []
            },

            customerSegments: [],

            routeMapData: {
                cities: {},
                routes: []
            },

            customerLoyalty: {
                levels: [],
                trend: {
                    months: [],
                    rates: []
                },
                spending: []
            },

            pivotTableData: [],

            realtimeData: {
                onlineUsers: 0,
                conversionRate: 0,
                searchesPerMinute: 0
            },
            realtimeHistory: {
                timestamps: [],
                onlineUsers: [],
                conversionRate: [],
                searchesPerMinute: []
            }
        }
    },
    computed: {
        pivotMetricLabel() {
            const labels = {
                'revenue': '销售额',
                'orders': '订单数',
                'averageValue': '平均客单价',
                'refundRate': '退票率'
            }
            return labels[this.pivotMetric] || this.pivotMetric
        },
        dateRangeShortcuts() {
            return [
                {
                    text: '最近一周',
                    value: (() => {
                        const end = new Date()
                        const start = new Date()
                        start.setTime(start.getTime() - 3600 * 1000 * 24 * 7)
                        return [start, end]
                    })()
                },
                {
                    text: '最近一个月',
                    value: (() => {
                        const end = new Date()
                        const start = new Date()
                        start.setTime(start.getTime() - 3600 * 1000 * 24 * 30)
                        return [start, end]
                    })()
                },
                {
                    text: '最近三个月',
                    value: (() => {
                        const end = new Date()
                        const start = new Date()
                        start.setTime(start.getTime() - 3600 * 1000 * 24 * 90)
                        return [start, end]
                    })()
                }
            ]
        },
        salesTrendOption() {
            let xAxisData, revenueData, ordersData

            if (this.salesTrendTimeUnit === 'day') {
                xAxisData = this.salesTrendData.dates
                revenueData = this.salesTrendData.revenue
                ordersData = this.salesTrendData.orders
            } else if (this.salesTrendTimeUnit === 'week') {
                // 简化处理，实际应该根据日期计算周数据
                xAxisData = ['第1周', '第2周', '第3周', '第4周']
                revenueData = [524400, 639900, 753900, 847300]
                ordersData = [1991, 2321, 2615, 2956]
            } else {
                // 月数据
                xAxisData = ['4月', '5月', '6月']
                revenueData = [2852600, 3214500, 3682500]
                ordersData = [10125, 11453, 12567]
            }

            return {
                tooltip: {
                    trigger: 'axis',
                    axisPointer: {
                        type: 'cross',
                        label: {
                            backgroundColor: '#6a7985'
                        }
                    }
                },
                legend: {
                    data: ['销售额', '订单数']
                },
                toolbox: {
                    feature: {
                        saveAsImage: {}
                    }
                },
                grid: {
                    left: '3%',
                    right: '4%',
                    bottom: '3%',
                    containLabel: true
                },
                xAxis: [
                    {
                        type: 'category',
                        boundaryGap: false,
                        data: xAxisData
                    }
                ],
                yAxis: [
                    {
                        type: 'value',
                        name: '销售额',
                        axisLabel: {
                            formatter: '{value}元'
                        }
                    },
                    {
                        type: 'value',
                        name: '订单数',
                        axisLabel: {
                            formatter: '{value}单'
                        }
                    }
                ],
                series: [
                    {
                        name: '销售额',
                        type: 'line',
                        smooth: true,
                        lineStyle: {
                            width: 3,
                            color: '#3f51b5'
                        },
                        areaStyle: {
                            color: {
                                type: 'linear',
                                x: 0,
                                y: 0,
                                x2: 0,
                                y2: 1,
                                colorStops: [
                                    { offset: 0, color: 'rgba(63,81,181,0.3)' },
                                    { offset: 1, color: 'rgba(63,81,181,0.1)' }
                                ]
                            }
                        },
                        data: revenueData
                    },
                    {
                        name: '订单数',
                        type: 'line',
                        yAxisIndex: 1,
                        smooth: true,
                        lineStyle: {
                            width: 3,
                            color: '#ff9800'
                        },
                        areaStyle: {
                            color: {
                                type: 'linear',
                                x: 0,
                                y: 0,
                                x2: 0,
                                y2: 1,
                                colorStops: [
                                    { offset: 0, color: 'rgba(255,152,0,0.3)' },
                                    { offset: 1, color: 'rgba(255,152,0,0.1)' }
                                ]
                            }
                        },
                        data: ordersData
                    }
                ]
            }
        },
        customerSegmentOption() {
            return {
                tooltip: {
                    trigger: 'item',
                    formatter: '{b}: {c} ({d}%)'
                },
                legend: {
                    bottom: '0%',
                    left: 'center',
                    itemWidth: 12,
                    itemHeight: 12,
                    textStyle: {
                        fontSize: 12
                    }
                },
                color: ['#3f51b5', '#4caf50', '#ff9800', '#f44336'],
                series: [
                    {
                        name: '客户分布',
                        type: 'pie',
                        radius: ['40%', '70%'],
                        center: ['50%', '40%'],
                        avoidLabelOverlap: true,
                        itemStyle: {
                            borderRadius: 10,
                            borderColor: '#fff',
                            borderWidth: 2
                        },
                        label: {
                            show: true,
                            formatter: '{b}: {d}%'
                        },
                        labelLine: {
                            show: true
                        },
                        data: this.customerSegments
                    }
                ]
            }
        },
        routeMapOption() {
            return {
                tooltip: {
                    trigger: 'item'
                },
                legend: {
                    data: ['出发城市', '到达城市'],
                    bottom: 0,
                    left: 'center'
                },
                radar: {
                    indicator: [
                        { name: '北京', max: 5000 },
                        { name: '上海', max: 5000 },
                        { name: '广州', max: 5000 },
                        { name: '成都', max: 5000 },
                        { name: '深圳', max: 5000 },
                        { name: '西安', max: 5000 }
                    ],
                    radius: '60%',
                    center: ['50%', '45%'],
                    axisName: {
                        color: '#333',
                        fontSize: 12
                    },
                    splitArea: {
                        show: true,
                        areaStyle: {
                            color: ['#f5f5f5', '#fff']
                        }
                    }
                },
                series: [{
                    type: 'radar',
                    data: [
                        {
                            value: [4200, 3800, 3200, 2600, 2400, 1900],
                            name: '出发城市',
                            areaStyle: {
                                color: 'rgba(63,81,181,0.2)'
                            },
                            lineStyle: {
                                color: '#3f51b5'
                            },
                            itemStyle: {
                                color: '#3f51b5'
                            }
                        },
                        {
                            value: [3900, 3400, 2800, 2300, 2100, 1700],
                            name: '到达城市',
                            areaStyle: {
                                color: 'rgba(76,175,80,0.2)'
                            },
                            lineStyle: {
                                color: '#4caf50'
                            },
                            itemStyle: {
                                color: '#4caf50'
                            }
                        }
                    ]
                }]
            }
        },
        customerLoyaltyOption() {
            return {
                tooltip: {
                    trigger: 'item',
                    formatter: function (params) {
                        if (!params.data || !params.data.value) return ''
                        return '客户忠诚度分析<br/>' +
                            params.marker + (params.data.name || '') + '<br/>' +
                            '忠诚度指数: ' + params.data.value[0] + '<br/>' +
                            '乘机次数: ' + params.data.value[1] + '次<br/>' +
                            '平均消费: ' + params.data.value[2] + '元'
                    }
                },
                legend: {
                    data: ['低忠诚度', '中忠诚度', '高忠诚度'],
                    bottom: 0,
                    left: 'center'
                },
                grid: {
                    left: '10%',
                    right: '10%',
                    bottom: '15%',
                    top: '10%'
                },
                xAxis: {
                    name: '忠诚度指数',
                    nameLocation: 'center',
                    nameGap: 25,
                    type: 'value',
                    min: 0,
                    max: 1,
                    splitLine: {
                        show: true,
                        lineStyle: {
                            type: 'dashed'
                        }
                    }
                },
                yAxis: {
                    name: '乘机次数',
                    nameLocation: 'center',
                    nameGap: 35,
                    type: 'value',
                    splitLine: {
                        show: true,
                        lineStyle: {
                            type: 'dashed'
                        }
                    }
                },
                series: [
                    {
                        name: '低忠诚度',
                        type: 'scatter',
                        symbolSize: function (data) {
                            return Math.max(10, Math.sqrt(data[2]) / 8)
                        },
                        data: this.customerLoyalty.levels.filter(item => item.value[0] < 0.3),
                        itemStyle: {
                            color: '#ff9800'
                        }
                    },
                    {
                        name: '中忠诚度',
                        type: 'scatter',
                        symbolSize: function (data) {
                            return Math.max(10, Math.sqrt(data[2]) / 8)
                        },
                        data: this.customerLoyalty.levels.filter(item => item.value[0] >= 0.3 && item.value[0] < 0.6),
                        itemStyle: {
                            color: '#4caf50'
                        }
                    },
                    {
                        name: '高忠诚度',
                        type: 'scatter',
                        symbolSize: function (data) {
                            return Math.max(10, Math.sqrt(data[2]) / 8)
                        },
                        data: this.customerLoyalty.levels.filter(item => item.value[0] >= 0.6),
                        itemStyle: {
                            color: '#3f51b5'
                        }
                    }
                ]
            }
        },
        onlineUserChartOption() {
            return {
                grid: {
                    top: 0,
                    right: 0,
                    bottom: 0,
                    left: 0
                },
                xAxis: {
                    type: 'category',
                    show: false,
                    data: new Array(7).fill('')
                },
                yAxis: {
                    type: 'value',
                    show: false
                },
                series: [{
                    data: this.realtimeHistory.onlineUsers,
                    type: 'line',
                    showSymbol: false,
                    smooth: true,
                    lineStyle: {
                        width: 2,
                        color: '#3f51b5'
                    },
                    areaStyle: {
                        color: {
                            type: 'linear',
                            x: 0,
                            y: 0,
                            x2: 0,
                            y2: 1,
                            colorStops: [
                                { offset: 0, color: 'rgba(63,81,181,0.5)' },
                                { offset: 1, color: 'rgba(63,81,181,0)' }
                            ]
                        }
                    }
                }]
            }
        },
        conversionRateChartOption() {
            return {
                grid: {
                    top: 0,
                    right: 0,
                    bottom: 0,
                    left: 0
                },
                xAxis: {
                    type: 'category',
                    show: false,
                    data: new Array(7).fill('')
                },
                yAxis: {
                    type: 'value',
                    show: false
                },
                series: [{
                    data: this.realtimeHistory.conversionRate,
                    type: 'line',
                    showSymbol: false,
                    smooth: true,
                    lineStyle: {
                        width: 2,
                        color: '#4caf50'
                    },
                    areaStyle: {
                        color: {
                            type: 'linear',
                            x: 0,
                            y: 0,
                            x2: 0,
                            y2: 1,
                            colorStops: [
                                { offset: 0, color: 'rgba(76,175,80,0.5)' },
                                { offset: 1, color: 'rgba(76,175,80,0)' }
                            ]
                        }
                    }
                }]
            }
        },
        searchRateChartOption() {
            return {
                grid: {
                    top: 0,
                    right: 0,
                    bottom: 0,
                    left: 0
                },
                xAxis: {
                    type: 'category',
                    show: false,
                    data: new Array(7).fill('')
                },
                yAxis: {
                    type: 'value',
                    show: false
                },
                series: [{
                    data: this.realtimeHistory.searchesPerMinute,
                    type: 'line',
                    showSymbol: false,
                    smooth: true,
                    lineStyle: {
                        width: 2,
                        color: '#ff9800'
                    },
                    areaStyle: {
                        color: {
                            type: 'linear',
                            x: 0,
                            y: 0,
                            x2: 0,
                            y2: 1,
                            colorStops: [
                                { offset: 0, color: 'rgba(255,152,0,0.5)' },
                                { offset: 1, color: 'rgba(255,152,0,0)' }
                            ]
                        }
                    }
                }]
            }
        }
    },
    methods: {
        handleDateRangeChange() {
            this.fetchAllData()
        },

        refreshData() {
            this.fetchAllData()
        },

        updateSalesTrend() {
            this.fetchSalesTrendData()
        },

        formatNumber(num) {
            if (num === undefined || num === null) return '0'

            if (typeof num === 'number') {
                if (num >= 10000) {
                    return (num / 10000).toFixed(2) + '万'
                } else {
                    return num.toLocaleString()
                }
            }

            return num
        },

        getProgressColor(percentage) {
            if (percentage < 30) return '#f56c6c'
            if (percentage < 70) return '#e6a23c'
            return '#67c23a'
        },

        async fetchAllData() {
            this.loading = true
            this.error = null

            try {
                // 格式化日期
                const startDate = this.dateRange[0].toISOString().split('T')[0]
                const endDate = this.dateRange[1].toISOString().split('T')[0]

                // 并行获取所有需要的数据
                await Promise.all([
                    this.fetchAnalyticsOverview(startDate, endDate),
                    this.fetchSalesTrendData(startDate, endDate),
                    this.fetchCustomerSegments(startDate, endDate),
                    this.fetchRouteMapData(startDate, endDate),
                    this.fetchCustomerLoyalty(startDate, endDate),
                    this.fetchPivotData(startDate, endDate),
                    this.fetchRealtimeData()
                ])
            } catch (error) {
                this.error = '加载数据时出错，请重试'
                ElMessage.error('数据加载失败')
            } finally {
                this.loading = false
            }
        },

        async fetchAnalyticsOverview(startDate, endDate) {
            try {
                const response = await api.admin.analytics.getAnalyticsOverview({
                    params: {
                        start_date: startDate,
                        end_date: endDate
                    }
                })

                if (response && response.metrics) {
                    // 更新各个业务指标
                    const metrics = response.metrics

                    this.metrics = [
                        {
                            title: '总销售额',
                            icon: 'fas fa-yuan-sign',
                            color: '#4caf50',
                            value: metrics.total_revenue || 0,
                            trend: metrics.revenue_growth || 0
                        },
                        {
                            title: '订单数量',
                            icon: 'fas fa-shopping-cart',
                            color: '#2196f3',
                            value: metrics.total_orders || 0,
                            trend: metrics.order_growth || 0
                        },
                        {
                            title: '客单价',
                            icon: 'fas fa-receipt',
                            color: '#ff9800',
                            value: metrics.avg_order_value || 0,
                            trend: metrics.aov_growth || 0
                        },
                        {
                            title: '用户数',
                            icon: 'fas fa-users',
                            color: '#9c27b0',
                            value: metrics.total_users || 0,
                            trend: metrics.user_growth || 0
                        },
                        {
                            title: '退票率',
                            icon: 'fas fa-undo',
                            color: '#f44336',
                            value: metrics.refund_rate || 0,
                            trend: metrics.refund_rate_change || 0
                        }
                    ]
                }
            } catch (error) {
                // 静默处理错误
            }
        },

        async fetchSalesTrendData(startDate, endDate) {
            try {
                const response = await api.admin.analytics.getSalesAnalytics({
                    params: {
                        start_date: startDate,
                        end_date: endDate,
                        time_unit: this.salesTrendTimeUnit
                    }
                })

                if (response && response.sales_trend) {
                    const salesTrend = response.sales_trend

                    this.salesTrendData = {
                        dates: salesTrend.map(item => item.date.substring(5)),  // 只显示月-日部分
                        revenue: salesTrend.map(item => item.revenue),
                        orders: salesTrend.map(item => item.order_count)
                    }
                }
            } catch (error) {
                console.error('获取销售趋势数据失败:', error)
            }
        },

        async fetchCustomerSegments(startDate, endDate) {
            try {
                const response = await api.admin.analytics.getCustomerSegments({
                    params: {
                        start_date: startDate,
                        end_date: endDate
                    }
                })

                if (response && response.segments) {
                    this.customerSegments = response.segments
                }
            } catch (error) {
                console.error('获取客户分群数据失败:', error)
            }
        },

        async fetchRouteMapData(startDate, endDate) {
            try {
                const response = await api.admin.analytics.getRouteMap({
                    params: {
                        start_date: startDate,
                        end_date: endDate
                    }
                })

                if (response) {
                    this.routeMapData = {
                        cities: response.cities || [],
                        routes: response.routes || []
                    }
                }
            } catch (error) {
                console.error('获取航线地图数据失败:', error)
            }
        },

        async fetchCustomerLoyalty(startDate, endDate) {
            try {
                const response = await api.admin.analytics.getCustomerLoyalty({
                    params: {
                        start_date: startDate,
                        end_date: endDate
                    }
                })

                if (response) {
                    this.customerLoyalty = {
                        levels: response.loyalty_levels || [],
                        trend: response.retention_trend || { months: [], rates: [] },
                        spending: response.loyalty_spending || []
                    }
                }
            } catch (error) {
                console.error('获取客户忠诚度数据失败:', error)
            }
        },

        async fetchPivotData(startDate, endDate) {
            try {
                const response = await api.admin.analytics.getPivotTableData({
                    start_date: startDate,
                    end_date: endDate,
                    dimension: this.pivotDimension,
                    metric: this.pivotMetric
                })

                if (response && response.data) {
                    this.pivotTableData = response.data
                }
            } catch (error) {
                console.error('获取数据透视表数据失败:', error)
            }
        },

        async fetchRealtimeData() {
            try {
                const response = await api.admin.analytics.getRealtimeData()

                if (response) {
                    // 更新当前实时数据
                    const current = response.current || {}
                    this.realtimeData = {
                        onlineUsers: current.online_users || 0,
                        conversionRate: current.conversion_rate || 0,
                        searchesPerMinute: current.searches_per_minute || 0
                    }

                    // 更新历史数据
                    const history = response.history || {}
                    this.realtimeHistory = {
                        timestamps: history.timestamps || [],
                        onlineUsers: history.online_users || [],
                        conversionRate: history.conversion_rate || [],
                        searchesPerMinute: history.searches_per_minute || []
                    }
                }
            } catch (error) {
                console.error('获取实时监控数据失败:', error)
            }
        }
    },
    mounted() {
        // 设置默认日期范围为过去30天
        const endDate = new Date()
        const startDate = new Date()
        startDate.setDate(startDate.getDate() - 30)
        this.dateRange = [startDate, endDate]

        this.fetchAllData()

        // 定期刷新实时数据
        this.realtimeDataInterval = setInterval(() => {
            this.fetchRealtimeData()
        }, 60000)  // 每分钟刷新一次
    },
    beforeUnmount() {
        // 清除定时器
        if (this.realtimeDataInterval) {
            clearInterval(this.realtimeDataInterval)
        }
    }
}
</script>

<style scoped>
.admin-analytics {
    padding: 20px 40px;
    width: 100%;
    box-sizing: border-box;
}

.page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}

.page-header h1 {
    font-size: 24px;
    color: #333;
    margin: 0;
}

.date-range-picker {
    display: flex;
    align-items: center;
    gap: 10px;
}

.mt-20 {
    margin-top: 20px;
}

.analytics-card {
    margin-bottom: 0;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
    border-radius: 8px;
}

.card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
    padding-bottom: 10px;
    border-bottom: 1px solid #eee;
}

.card-header h2 {
    font-size: 16px;
    margin: 0;
    font-weight: 600;
    color: #333;
}

.card-actions {
    display: flex;
    align-items: center;
    gap: 10px;
}

.metric-cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 15px;
    margin-bottom: 10px;
}

.metric-card {
    background-color: #fff;
    border-radius: 8px;
    padding: 15px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    display: flex;
    align-items: center;
}

.metric-icon {
    width: 50px;
    height: 50px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 15px;
}

.metric-icon i {
    font-size: 20px;
}

.metric-content {
    flex: 1;
}

.metric-title {
    font-size: 13px;
    color: #666;
    margin-bottom: 5px;
}

.metric-value {
    font-size: 20px;
    font-weight: 600;
    color: #333;
}

.text-up {
    color: #4caf50;
}

.text-down {
    color: #f44336;
}

.chart-container {
    width: 100%;
}

.trend-indicator {
    font-size: 12px;
    font-weight: 500;
    margin-top: 3px;
}

.trend-up {
    color: #4caf50;
}

.trend-down {
    color: #f44336;
}

.realtime-card {
    background-color: #f9f9f9;
    border-radius: 8px;
    padding: 15px;
    height: 100%;
}

.realtime-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
}

.realtime-title {
    font-size: 14px;
    color: #666;
}

.realtime-value {
    font-size: 28px;
    font-weight: 600;
    color: #333;
    margin-bottom: 15px;
}

.realtime-chart {
    height: 80px;
}
</style>