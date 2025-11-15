<template>
    <div class="data-visualization">
        <div class="page-header">
            <h1>数据可视化中心</h1>
            <div class="date-filter">
                <el-date-picker v-model="dateRange" type="daterange" range-separator="至" start-placeholder="开始日期"
                    end-placeholder="结束日期" @change="handleDateChange" />
            </div>
        </div>

        <!-- 调试信息开关 -->
        <div class="debug-toggle">
            <el-button type="primary" size="small" @click="showDebug = !showDebug">
                {{ showDebug ? '隐藏调试信息' : '显示调试信息' }}
            </el-button>
        </div>

        <!-- 调试信息区域 -->
        <div v-if="showDebug" class="debug-info">
            <h3>调试信息</h3>
            <div class="debug-section">
                <h4>API响应状态</h4>
                <p>加载状态: {{ loading ? '加载中' : '已完成' }}</p>
                <p>错误信息: {{ error || '无' }}</p>
            </div>
            <div class="debug-section">
                <h4>销售数据</h4>
                <p>日期数量: {{ salesData.dates.length }}</p>
                <p>收入数据: {{ salesData.revenue.length > 0 ? '已加载' : '未加载' }}</p>
                <p>订单数据: {{ salesData.count.length > 0 ? '已加载' : '未加载' }}</p>
            </div>
            <div class="debug-section">
                <h4>用户数据</h4>
                <p>年龄分布: {{ userAgeData.length > 0 ? '已加载' : '未加载' }}</p>
                <p>用户属性: {{ userAttributesData.indicators.length > 0 ? '已加载' : '未加载' }}</p>
                <p>增长趋势: {{ userGrowthData.dates.length > 0 ? '已加载' : '未加载' }}</p>
            </div>
            <div class="debug-section">
                <h4>航班数据</h4>
                <p>载客率: {{ flightLoadData.length > 0 ? '已加载' : '未加载' }}</p>
                <p>准点率: {{ flightOnTimeData.length > 0 ? '已加载' : '未加载' }}</p>
                <p>路线图: {{ Object.keys(routeMapData.cities).length > 0 ? '已加载' : '未加载' }}</p>
            </div>
            <el-button type="primary" size="small" @click="refreshData">刷新数据</el-button>
        </div>

        <el-tabs v-model="activeTab" class="visualization-tabs">
            <el-tab-pane label="销售分析" name="sales">
                <div class="chart-container">
                    <div class="chart-wrapper large">
                        <h3>销售趋势</h3>
                        <v-chart :option="salesTrendOption" autoresize />
                    </div>
                </div>

                <div class="chart-container">
                    <div class="chart-wrapper">
                        <h3>支付方式分布</h3>
                        <v-chart :option="paymentMethodOption" autoresize />
                    </div>

                    <div class="chart-wrapper">
                        <h3>机票价格区间分布</h3>
                        <v-chart :option="ticketPriceRangeOption" autoresize />
                    </div>
                </div>
            </el-tab-pane>

            <el-tab-pane label="用户画像" name="users">
                <div class="chart-container">
                    <div class="chart-wrapper">
                        <h3>用户年龄分布</h3>
                        <v-chart :option="userAgeOption" autoresize />
                    </div>

                    <div class="chart-wrapper">
                        <h3>用户属性</h3>
                        <v-chart :option="userAttributesOption" autoresize />
                    </div>
                </div>

                <div class="chart-container">
                    <div class="chart-wrapper large">
                        <h3>用户增长趋势</h3>
                        <v-chart :option="userGrowthOption" autoresize />
                    </div>
                </div>
            </el-tab-pane>

            <el-tab-pane label="航班分析" name="flights">
                <div class="chart-container">
                    <div class="chart-wrapper large">
                        <h3>热门航线图</h3>
                        <v-chart :option="routeMapOption" autoresize />
                    </div>
                </div>

                <div class="chart-container">
                    <div class="chart-wrapper">
                        <h3>航线载客率</h3>
                        <v-chart :option="flightLoadOption" autoresize />
                    </div>

                    <div class="chart-wrapper">
                        <h3>航班准点率</h3>
                        <v-chart :option="flightOnTimeOption" autoresize />
                    </div>
                </div>
            </el-tab-pane>
        </el-tabs>
    </div>
</template>

<script>
// 直接导入Vue-ECharts组件
import { defineComponent } from 'vue'
import VChart from 'vue-echarts'
import api from '../services/api'
import { ElMessage } from 'element-plus'

export default defineComponent({
    name: 'AdminDataVisualizationView',
    components: {
        VChart
    },
    data() {
        return {
            activeTab: 'sales',
            dateRange: [
                new Date(new Date().setMonth(new Date().getMonth() - 1)),
                new Date()
            ],
            loading: false,
            error: null,
            showDebug: false,

            // 销售数据
            salesData: {
                dates: [],
                revenue: [],
                count: []
            },

            paymentMethods: [],
            ticketPriceRanges: [
                // 添加默认票价区间数据，防止图表空白
                { name: '0-500元', value: 10 },
                { name: '500-1000元', value: 30 },
                { name: '1000-1500元', value: 25 },
                { name: '1500-2000元', value: 15 },
                { name: '2000元以上', value: 20 }
            ],

            // 用户数据
            userAgeData: [],
            userAttributesData: {
                indicators: [],
                series: []
            },
            userGrowthData: {
                dates: [],
                newUsers: [],
                activeUsers: []
            },

            // 航班数据
            flightLoadData: [],
            flightOnTimeData: [],
            routeMapData: {
                cities: {},
                routes: []
            }
        }
    },
    computed: {
        salesTrendOption() {
            return {
                tooltip: {
                    trigger: 'axis',
                    axisPointer: {
                        type: 'cross'
                    }
                },
                legend: {
                    data: ['销售额', '订单数']
                },
                grid: {
                    left: '3%',
                    right: '4%',
                    bottom: '3%',
                    containLabel: true
                },
                xAxis: {
                    type: 'category',
                    data: this.salesData.dates
                },
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
                        type: 'bar',
                        data: this.salesData.revenue,
                        itemStyle: {
                            color: '#3f51b5'
                        }
                    },
                    {
                        name: '订单数',
                        type: 'line',
                        yAxisIndex: 1,
                        data: this.salesData.count,
                        lineStyle: {
                            color: '#ff9800'
                        },
                        symbolSize: 8
                    }
                ]
            }
        },

        paymentMethodOption() {
            return {
                tooltip: {
                    trigger: 'item',
                    formatter: '{b}: {c} ({d}%)'
                },
                legend: {
                    orient: 'vertical',
                    left: 'left'
                },
                series: [
                    {
                        name: '支付方式',
                        type: 'pie',
                        radius: '70%',
                        center: ['55%', '50%'],
                        data: this.paymentMethods,
                        itemStyle: {
                            borderRadius: 5,
                            borderColor: '#fff',
                            borderWidth: 1
                        },
                        emphasis: {
                            itemStyle: {
                                shadowBlur: 10,
                                shadowOffsetX: 0,
                                shadowColor: 'rgba(0, 0, 0, 0.5)'
                            }
                        },
                        label: {
                            formatter: '{b}: {d}%'
                        }
                    }
                ]
            }
        },

        ticketPriceRangeOption() {
            return {
                tooltip: {
                    trigger: 'item',
                    formatter: '{b}: {c} ({d}%)'
                },
                series: [
                    {
                        name: '票价分布',
                        type: 'pie',
                        radius: ['30%', '70%'],
                        center: ['50%', '50%'],
                        roseType: 'area',
                        itemStyle: {
                            borderRadius: 5,
                            borderColor: '#fff',
                            borderWidth: 1
                        },
                        data: this.ticketPriceRanges
                    }
                ]
            }
        },

        userAgeOption() {
            return {
                tooltip: {
                    trigger: 'item',
                    formatter: '{b}: {c} ({d}%)'
                },
                series: [
                    {
                        name: '年龄分布',
                        type: 'pie',
                        radius: '70%',
                        center: ['50%', '50%'],
                        data: this.userAgeData,
                        emphasis: {
                            itemStyle: {
                                shadowBlur: 10,
                                shadowOffsetX: 0,
                                shadowColor: 'rgba(0, 0, 0, 0.5)'
                            }
                        }
                    }
                ]
            }
        },

        userAttributesOption() {
            return {
                tooltip: {
                    trigger: 'item'
                },
                legend: {
                    data: ['商务客户', '休闲旅客'],
                    orient: 'vertical',
                    right: 0,
                    top: 'center'
                },
                radar: {
                    indicator: this.userAttributesData.indicators,
                    radius: '65%',
                    center: ['40%', '50%']
                },
                series: [
                    {
                        type: 'radar',
                        data: this.userAttributesData.series,
                        areaStyle: {}
                    }
                ]
            }
        },

        userGrowthOption() {
            return {
                tooltip: {
                    trigger: 'axis'
                },
                legend: {
                    data: ['新增用户', '活跃用户']
                },
                xAxis: {
                    type: 'category',
                    data: this.userGrowthData.dates,
                    name: '月份'
                },
                yAxis: [
                    {
                        type: 'value',
                        name: '新增用户',
                        axisLabel: {
                            formatter: '{value}人'
                        }
                    },
                    {
                        type: 'value',
                        name: '活跃用户',
                        axisLabel: {
                            formatter: '{value}人'
                        }
                    }
                ],
                series: [
                    {
                        name: '新增用户',
                        type: 'bar',
                        data: this.userGrowthData.newUsers,
                        itemStyle: {
                            color: '#4caf50'
                        }
                    },
                    {
                        name: '活跃用户',
                        type: 'line',
                        yAxisIndex: 1,
                        data: this.userGrowthData.activeUsers,
                        itemStyle: {
                            color: '#2196f3'
                        },
                        lineStyle: {
                            width: 3
                        },
                        symbolSize: 8,
                        smooth: true
                    }
                ]
            }
        },

        routeMapOption() {
            return {
                tooltip: {
                    trigger: 'axis'
                },
                xAxis: {
                    type: 'category',
                    data: ['北京-上海', '上海-广州', '北京-成都', '广州-深圳', '成都-西安']
                },
                yAxis: {
                    type: 'value',
                    name: '订单数量'
                },
                series: [
                    {
                        data: [1200, 980, 850, 720, 680],
                        type: 'bar',
                        barWidth: '40%',
                        itemStyle: {
                            color: function (params) {
                                const colorList = ['#3f51b5', '#4caf50', '#ff9800', '#f44336', '#9c27b0']
                                return colorList[params.dataIndex]
                            },
                            borderRadius: [5, 5, 0, 0]
                        },
                        label: {
                            show: true,
                            position: 'top'
                        }
                    }
                ]
            }
        },

        flightLoadOption() {
            return {
                tooltip: {
                    formatter: '{b}: {c}%'
                },
                series: [
                    {
                        type: 'gauge',
                        startAngle: 90,
                        endAngle: -270,
                        pointer: {
                            show: false
                        },
                        progress: {
                            show: true,
                            overlap: false,
                            roundCap: true,
                            clip: false
                        },
                        axisLine: {
                            lineStyle: {
                                width: 30
                            }
                        },
                        splitLine: {
                            show: false
                        },
                        axisTick: {
                            show: false
                        },
                        axisLabel: {
                            show: false
                        },
                        title: {
                            fontSize: 14
                        },
                        detail: {
                            width: 50,
                            height: 14,
                            fontSize: 14,
                            color: 'auto',
                            formatter: '{value}%'
                        },
                        data: this.flightLoadData
                    }
                ]
            }
        },

        flightOnTimeOption() {
            return {
                tooltip: {
                    trigger: 'axis',
                    axisPointer: {
                        type: 'shadow'
                    }
                },
                grid: {
                    left: '3%',
                    right: '4%',
                    bottom: '3%',
                    containLabel: true
                },
                xAxis: {
                    type: 'value',
                    name: '准点率(%)',
                    max: 100
                },
                yAxis: {
                    type: 'category',
                    data: this.flightOnTimeData.map(item => item.name)
                },
                series: [
                    {
                        name: '准点率',
                        type: 'bar',
                        data: this.flightOnTimeData.map(item => item.value),
                        itemStyle: {
                            color: function (params) {
                                const value = params.value
                                if (value >= 90) return '#4caf50'
                                if (value >= 80) return '#ff9800'
                                return '#f44336'
                            },
                            borderRadius: [0, 5, 5, 0]
                        },
                        label: {
                            show: true,
                            position: 'right',
                            formatter: '{c}%'
                        }
                    }
                ]
            }
        }
    },
    mounted() {
        this.fetchData()
    },
    methods: {
        handleDateChange() {
            this.fetchData()
        },
        async fetchData() {
            this.loading = true
            this.error = null

            try {
                // 格式化日期
                const startDate = this.dateRange[0].toISOString().split('T')[0]
                const endDate = this.dateRange[1].toISOString().split('T')[0]

                console.log(`获取数据，时间段: ${startDate} 至 ${endDate}，当前标签页: ${this.activeTab}`)

                // 根据当前激活的标签页获取相应数据
                if (this.activeTab === 'sales') {
                    await this.fetchSalesData(startDate, endDate)
                } else if (this.activeTab === 'users') {
                    await this.fetchUserData(startDate, endDate)
                } else if (this.activeTab === 'flights') {
                    await this.fetchFlightData(startDate, endDate)
                }
            } catch (error) {
                console.error('获取数据失败:', error)
                this.error = `加载数据时出错: ${error.message || '未知错误'}`

                if (error.response) {
                    console.error('API响应错误:', error.response.status, error.response.data)
                    this.error += ` (状态码: ${error.response.status})`
                }

                ElMessage.error('数据加载失败，请检查控制台获取详细信息')
            } finally {
                this.loading = false
            }
        },
        async fetchSalesData(startDate, endDate) {
            // 获取销售趋势数据
            const salesTrendResponse = await api.admin.analytics.getSalesTrend({
                params: { start_date: startDate, end_date: endDate }
            })

            // 打印原始响应，用于调试
            console.log('销售趋势原始响应:', salesTrendResponse)

            // 提取data属性
            const salesTrendData = salesTrendResponse.data || salesTrendResponse

            if (salesTrendData && salesTrendData.sales_trend) {
                const salesTrend = salesTrendData.sales_trend
                this.salesData = {
                    dates: salesTrend.map(item => item.date.substring(5)), // 只显示月-日部分
                    revenue: salesTrend.map(item => item.revenue),
                    count: salesTrend.map(item => item.order_count)
                }
            } else {
                console.warn('未找到销售趋势数据')
            }

            // 获取支付方式分布
            const visualizationResponse = await api.admin.analytics.getVisualizationData({
                params: { start_date: startDate, end_date: endDate }
            })

            // 打印原始响应，用于调试
            console.log('可视化数据原始响应:', visualizationResponse)

            // 提取data属性
            const visualizationData = visualizationResponse.data || visualizationResponse

            if (visualizationData) {
                if (visualizationData.payment_methods) {
                    this.paymentMethods = visualizationData.payment_methods
                } else {
                    console.warn('未找到支付方式数据')
                }

                // 处理票价区间数据
                console.log('检查票价区间数据:', visualizationData.ticket_price_ranges)
                if (visualizationData.ticket_price_ranges && Array.isArray(visualizationData.ticket_price_ranges) && visualizationData.ticket_price_ranges.length > 0) {
                    console.log('使用API返回的票价区间数据:', visualizationData.ticket_price_ranges)
                    this.ticketPriceRanges = visualizationData.ticket_price_ranges
                } else {
                    console.warn('未找到票价区间数据或数据格式不正确，使用默认数据')
                    // 保留默认数据，不做修改
                }
            }
        },
        async fetchUserData(startDate, endDate) {
            // 获取用户数据
            const userAnalyticsResponse = await api.admin.analytics.getUserAnalytics({
                params: { start_date: startDate, end_date: endDate }
            })

            // 打印原始响应，用于调试
            console.log('用户分析原始响应:', userAnalyticsResponse)

            // 提取data属性
            const userAnalyticsData = userAnalyticsResponse.data || userAnalyticsResponse

            if (userAnalyticsData) {
                if (userAnalyticsData.age_distribution) {
                    this.userAgeData = userAnalyticsData.age_distribution
                } else {
                    console.warn('未找到用户年龄分布数据')
                }

                if (userAnalyticsData.user_attributes) {
                    this.userAttributesData = userAnalyticsData.user_attributes
                } else {
                    console.warn('未找到用户属性数据')
                }

                if (userAnalyticsData.user_growth) {
                    const growth = userAnalyticsData.user_growth
                    this.userGrowthData = {
                        dates: growth.map(item => item.month),
                        newUsers: growth.map(item => item.new_users),
                        activeUsers: growth.map(item => item.active_users)
                    }
                } else {
                    console.warn('未找到用户增长数据')
                }
            }
        },
        async fetchFlightData(startDate, endDate) {
            // 获取航班数据
            const flightAnalyticsResponse = await api.admin.analytics.getFlightAnalytics({
                params: { start_date: startDate, end_date: endDate }
            })

            // 打印原始响应，用于调试
            console.log('航班分析原始响应:', flightAnalyticsResponse)

            // 提取data属性
            const flightAnalyticsData = flightAnalyticsResponse.data || flightAnalyticsResponse

            if (flightAnalyticsData) {
                if (flightAnalyticsData.flight_load) {
                    this.flightLoadData = flightAnalyticsData.flight_load
                } else {
                    console.warn('未找到航班载客率数据')
                }

                if (flightAnalyticsData.on_time_data) {
                    this.flightOnTimeData = flightAnalyticsData.on_time_data
                } else {
                    console.warn('未找到航班准点率数据')
                }

                if (flightAnalyticsData.route_map) {
                    this.routeMapData = flightAnalyticsData.route_map
                } else {
                    console.warn('未找到航线地图数据')
                }
            }
        },
        refreshData() {
            this.fetchData()
        }
    }
})
</script>

<style scoped>
.data-visualization {
    padding: 20px;
}

.page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}

.page-header h1 {
    font-size: 24px;
    margin: 0;
    color: #333;
}

.chart-container {
    display: flex;
    gap: 20px;
    margin-bottom: 20px;
}

.chart-wrapper {
    flex: 1;
    background-color: white;
    border-radius: 10px;
    padding: 15px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
    height: 400px;
    display: flex;
    flex-direction: column;
}

.chart-wrapper.large {
    width: 100%;
}

.chart-wrapper h3 {
    font-size: 16px;
    margin-top: 0;
    margin-bottom: 15px;
    color: #333;
    font-weight: 500;
    border-bottom: 1px solid #eee;
    padding-bottom: 10px;
}

.visualization-tabs {
    margin-bottom: 20px;
}

@media (max-width: 992px) {
    .chart-container {
        flex-direction: column;
    }
}

.debug-toggle {
    margin-bottom: 20px;
}

.debug-info {
    background-color: white;
    border-radius: 10px;
    padding: 20px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.debug-section {
    margin-bottom: 10px;
}

.debug-section h4 {
    font-size: 16px;
    margin-top: 0;
    margin-bottom: 5px;
    color: #333;
    font-weight: 500;
}

.debug-section p {
    margin: 0;
    color: #666;
}
</style>