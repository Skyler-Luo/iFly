<template>
    <div class="business-intelligence">
        <div class="page-header">
            <h1>商务智能中心</h1>
            <div class="header-actions">
                <el-button type="primary" @click="generateReport">
                    <i class="fas fa-file-export"></i> 导出报表
                </el-button>
            </div>
        </div>

        <el-row :gutter="20">
            <el-col :span="24">
                <el-card class="prediction-card">
                    <div class="card-header">
                        <h2>销售预测</h2>
                        <div class="prediction-actions">
                            <el-select v-model="predictionPeriod" placeholder="预测周期" size="small">
                                <el-option label="未来7天" value="week" />
                                <el-option label="未来30天" value="month" />
                                <el-option label="未来90天" value="quarter" />
                            </el-select>
                            <el-button size="small" type="primary" @click="updatePrediction">更新预测</el-button>
                        </div>
                    </div>
                    <div class="chart-container" style="height: 350px">
                        <v-chart :option="salesPredictionOption" autoresize />
                    </div>
                    <div class="prediction-summary">
                        <div class="summary-item">
                            <div class="summary-label">预测总销售额</div>
                            <div class="summary-value">
                                <span class="amount">¥{{ formatNumber(predictionSummary.totalRevenue) }}</span>
                                <span class="trend"
                                    :class="{ 'up': predictionSummary.growthRate > 0, 'down': predictionSummary.growthRate < 0 }">
                                    {{ predictionSummary.growthRate > 0 ? '+' : '' }}{{ predictionSummary.growthRate }}%
                                </span>
                            </div>
                        </div>
                        <div class="summary-item">
                            <div class="summary-label">预测订单量</div>
                            <div class="summary-value">
                                <span class="amount">{{ formatNumber(predictionSummary.totalOrders) }}</span>
                                <span class="trend"
                                    :class="{ 'up': predictionSummary.orderGrowthRate > 0, 'down': predictionSummary.orderGrowthRate < 0 }">
                                    {{ predictionSummary.orderGrowthRate > 0 ? '+' : '' }}{{
                                        predictionSummary.orderGrowthRate }}%
                                </span>
                            </div>
                        </div>
                        <div class="summary-item">
                            <div class="summary-label">预测客单价</div>
                            <div class="summary-value">
                                <span class="amount">¥{{ formatNumber(predictionSummary.averageOrderValue) }}</span>
                                <span class="trend"
                                    :class="{ 'up': predictionSummary.aovGrowthRate > 0, 'down': predictionSummary.aovGrowthRate < 0 }">
                                    {{ predictionSummary.aovGrowthRate > 0 ? '+' : '' }}{{
                                        predictionSummary.aovGrowthRate }}%
                                </span>
                            </div>
                        </div>
                    </div>
                </el-card>
            </el-col>
        </el-row>

        <el-row :gutter="20" class="mt-20">
            <el-col :span="12">
                <el-card class="bi-card">
                    <div class="card-header">
                        <h2>航线收益分析</h2>
                        <div class="card-actions">
                            <el-radio-group v-model="routeMetric" size="small" @change="updateRouteAnalysis">
                                <el-radio-button label="revenue">收入</el-radio-button>
                                <el-radio-button label="profit">利润</el-radio-button>
                                <el-radio-button label="roi">ROI</el-radio-button>
                            </el-radio-group>
                        </div>
                    </div>
                    <div class="chart-container" style="height: 380px">
                        <v-chart :option="routeProfitOption" autoresize />
                    </div>
                </el-card>
            </el-col>

            <el-col :span="12">
                <el-card class="bi-card">
                    <div class="card-header">
                        <h2>价格弹性分析</h2>
                    </div>
                    <div class="chart-container" style="height: 380px">
                        <v-chart :option="priceElasticityOption" autoresize />
                    </div>
                </el-card>
            </el-col>
        </el-row>

        <el-row :gutter="20" class="mt-20">
            <el-col :span="8">
                <el-card class="bi-card">
                    <div class="card-header">
                        <h2>客户终身价值</h2>
                    </div>
                    <div class="chart-container" style="height: 340px">
                        <v-chart :option="customerLtvOption" autoresize />
                    </div>
                </el-card>
            </el-col>

            <el-col :span="8">
                <el-card class="bi-card">
                    <div class="card-header">
                        <h2>季节性分析</h2>
                        <div class="card-actions">
                            <el-select v-model="seasonalRoute" placeholder="选择航线" size="small">
                                <el-option label="北京-上海" value="beijing-shanghai" />
                                <el-option label="北京-广州" value="beijing-guangzhou" />
                                <el-option label="上海-成都" value="shanghai-chengdu" />
                            </el-select>
                        </div>
                    </div>
                    <div class="chart-container" style="height: 340px">
                        <v-chart :option="seasonalityOption" autoresize />
                    </div>
                </el-card>
            </el-col>

            <el-col :span="8">
                <el-card class="bi-card">
                    <div class="card-header">
                        <h2>异常检测</h2>
                    </div>
                    <div class="chart-container" style="height: 340px">
                        <v-chart :option="anomalyDetectionOption" autoresize />
                    </div>
                    <div class="anomaly-list">
                        <div class="anomaly-header">检测到的异常</div>
                        <div v-for="(item, index) in anomalyItems" :key="index" class="anomaly-item">
                            <el-tag :type="item.severity === 'high' ? 'danger' : 'warning'" size="small">
                                {{ item.severity === 'high' ? '高' : '中' }}
                            </el-tag>
                            <span class="anomaly-text">{{ item.description }}</span>
                            <span class="anomaly-date">{{ item.date }}</span>
                        </div>
                    </div>
                </el-card>
            </el-col>
        </el-row>

        <el-row :gutter="20" class="mt-20">
            <el-col :span="24">
                <el-card class="bi-card">
                    <div class="card-header">
                        <h2>多维度分析</h2>
                        <div class="card-actions">
                            <el-select v-model="dimensionX" placeholder="X维度" size="small" style="width: 120px">
                                <el-option label="年龄段" value="age" />
                                <el-option label="用户类型" value="userType" />
                                <el-option label="预订周期" value="leadTime" />
                                <el-option label="旅行目的" value="purpose" />
                            </el-select>
                            <el-select v-model="dimensionY" placeholder="Y维度" size="small"
                                style="width: 120px; margin-left: 10px">
                                <el-option label="平均支付金额" value="avgPayment" />
                                <el-option label="订票频率" value="frequency" />
                                <el-option label="忠诚度指数" value="loyalty" />
                                <el-option label="退改率" value="refundRate" />
                            </el-select>
                            <el-button size="small" type="primary" style="margin-left: 10px"
                                @click="updateMultiDimensionView">分析</el-button>
                        </div>
                    </div>
                    <div class="chart-container" style="height: 450px">
                        <v-chart :option="multiDimensionOption" autoresize />
                    </div>
                </el-card>
            </el-col>
        </el-row>
    </div>
</template>

<script>
// 直接导入Vue-ECharts组件
import VChart from 'vue-echarts'
import api from '../services/api'
import { ElMessage } from 'element-plus'

export default {
    name: 'AdminBusinessIntelligenceView',
    components: {
        VChart
    },
    data() {
        return {
            predictionPeriod: 'week',
            routeMetric: 'revenue',
            seasonalRoute: 'beijing-shanghai',
            dimensionX: 'age',
            dimensionY: 'avgPayment',
            loading: false,
            error: null,

            // 预测数据
            predictionSummary: {
                totalRevenue: 0,
                growthRate: 0,
                totalOrders: 0,
                orderGrowthRate: 0,
                averageOrderValue: 0,
                aovGrowthRate: 0
            },
            predictionData: {
                dates: [],
                predictions: [],
                historical: []
            },

            // 航线数据
            routeData: [],

            // 价格弹性数据
            priceElasticityData: {
                priceVolume: [],
                elasticity: []
            },
            optimalPrice: 0,

            // 客户终身价值
            customerSegments: [],
            averageLtv: 0,

            // 季节性数据
            seasonalityData: {
                months: [],
                loadFactor: [],
                ticketPrice: []
            },
            availableRoutes: [],

            // 异常检测
            anomalyData: {
                dates: [],
                sales: [],
                expectedValues: [],
                upperBounds: [],
                lowerBounds: []
            },
            anomalyItems: [],

            // 多维度分析数据
            multiDimensionData: {
                age: {
                    categories: ['18-24岁', '25-34岁', '35-44岁', '45-54岁', '55岁以上'],
                    avgPayment: [1200, 2500, 3200, 2800, 2400],
                    frequency: [1.2, 3.5, 4.2, 3.8, 2.5],
                    loyalty: [60, 75, 85, 80, 70],
                    refundRate: [8, 5, 3, 4, 6]
                },
                userType: {
                    categories: ['散客', '商务', '团队', '会员', 'VIP'],
                    avgPayment: [1800, 3500, 1500, 2200, 4500],
                    frequency: [2.1, 6.5, 1.8, 4.2, 8.5],
                    loyalty: [55, 80, 50, 75, 90],
                    refundRate: [7, 2, 10, 5, 1]
                },
                leadTime: {
                    categories: ['提前1天', '提前1周', '提前2周', '提前1月', '提前2月+'],
                    avgPayment: [3500, 2800, 2400, 1800, 1500],
                    frequency: [1.8, 2.5, 3.2, 4.1, 2.2],
                    loyalty: [60, 65, 70, 80, 75],
                    refundRate: [8, 6, 5, 3, 2]
                },
                purpose: {
                    categories: ['商务', '休闲', '探亲', '学习', '其他'],
                    avgPayment: [3800, 2500, 2200, 1800, 1500],
                    frequency: [5.5, 2.8, 1.5, 2.2, 1.1],
                    loyalty: [75, 70, 85, 60, 50],
                    refundRate: [3, 6, 2, 5, 8]
                }
            }
        }
    },
    computed: {
        salesPredictionOption() {
            return {
                tooltip: {
                    trigger: 'axis',
                    formatter: function (params) {
                        let result = params[0].axisValue + '<br/>'
                        params.forEach(param => {
                            // color变量在此未使用
                            let value = param.value
                            if (param.seriesName === '预测上限' || param.seriesName === '预测下限') {
                                return
                            }
                            result += param.marker + ' ' + param.seriesName + ': ¥' + value.toLocaleString() + '<br/>'
                        })
                        return result
                    }
                },
                legend: {
                    data: ['历史数据', '预测值']
                },
                grid: {
                    left: '3%',
                    right: '4%',
                    bottom: '3%',
                    containLabel: true
                },
                xAxis: {
                    type: 'category',
                    boundaryGap: false,
                    data: this.predictionData.dates
                },
                yAxis: {
                    type: 'value',
                    axisLabel: {
                        formatter: '¥{value}'
                    }
                },
                series: [
                    {
                        name: '历史数据',
                        type: 'line',
                        data: this.predictionData.historical,
                        itemStyle: {
                            color: '#3f51b5'
                        },
                        lineStyle: {
                            width: 3
                        },
                        symbolSize: 8
                    },
                    {
                        name: '预测值',
                        type: 'line',
                        data: this.predictionData.predictions,
                        itemStyle: {
                            color: '#ff9800'
                        },
                        lineStyle: {
                            width: 3,
                            type: 'dashed'
                        },
                        symbolSize: 8
                    },
                    {
                        name: '预测上限',
                        type: 'line',
                        data: this.predictionData.upperBounds,
                        lineStyle: {
                            width: 0
                        },
                        symbol: 'none',
                        areaStyle: {
                            color: 'rgba(255, 152, 0, 0.2)'
                        },
                        stack: 'confidence-band'
                    },
                    {
                        name: '预测下限',
                        type: 'line',
                        data: this.predictionData.lowerBounds,
                        lineStyle: {
                            width: 0
                        },
                        symbol: 'none',
                        areaStyle: {
                            color: 'rgba(255, 152, 0, 0)'
                        },
                        stack: 'confidence-band'
                    }
                ]
            }
        },
        routeProfitOption() {
            // 根据选择的指标返回不同配置
            const metricData = this.routeData[this.routeMetric]
            const metricName = this.routeMetric === 'revenue' ? '收入' :
                this.routeMetric === 'profit' ? '利润' : 'ROI'
            const formatter = this.routeMetric === 'roi' ? '{c}%' : '¥{c}'

            return {
                tooltip: {
                    trigger: 'axis',
                    axisPointer: {
                        type: 'shadow'
                    },
                    formatter: this.routeMetric === 'roi' ?
                        '{b}: {c}%' : '{b}: ¥{c}'
                },
                grid: {
                    left: '3%',
                    right: '4%',
                    bottom: '3%',
                    containLabel: true
                },
                xAxis: {
                    type: 'category',
                    data: this.routeData.routes,
                    axisLabel: {
                        interval: 0,
                        rotate: 30
                    }
                },
                yAxis: {
                    type: 'value',
                    name: metricName,
                    axisLabel: {
                        formatter: this.routeMetric === 'roi' ? '{value}%' : '¥{value}'
                    }
                },
                series: [
                    {
                        data: metricData,
                        type: 'bar',
                        barWidth: '40%',
                        itemStyle: {
                            color: function (params) {
                                // 为不同航线使用不同颜色
                                const colorList = ['#3f51b5', '#4caf50', '#ff9800', '#9c27b0', '#f44336']
                                return colorList[params.dataIndex % colorList.length]
                            }
                        },
                        label: {
                            show: true,
                            position: 'top',
                            formatter: formatter
                        }
                    }
                ]
            }
        },
        priceElasticityOption() {
            return {
                tooltip: {
                    trigger: 'axis',
                    formatter: function (params) {
                        const price = params[0].data[0]
                        const volume = params[0].data[1]
                        const revenue = params[0].data[2]
                        return `价格倍数: ${price}<br/>销量: ${volume}<br/>收入: ¥${revenue}`
                    }
                },
                xAxis: {
                    type: 'value',
                    name: '价格系数',
                    min: 0.75,
                    max: 1.25
                },
                yAxis: [
                    {
                        type: 'value',
                        name: '销量',
                        position: 'left',
                        axisLine: {
                            show: true,
                            lineStyle: {
                                color: '#3f51b5'
                            }
                        },
                        axisLabel: {
                            formatter: '{value}'
                        }
                    },
                    {
                        type: 'value',
                        name: '收入',
                        position: 'right',
                        axisLine: {
                            show: true,
                            lineStyle: {
                                color: '#ff9800'
                            }
                        },
                        axisLabel: {
                            formatter: '¥{value}'
                        }
                    }
                ],
                series: [
                    {
                        name: '价格弹性',
                        type: 'scatter',
                        symbolSize: 15,
                        data: this.priceElasticityData.elasticity,
                        itemStyle: {
                            color: '#3f51b5'
                        },
                        markLine: {
                            data: [
                                {
                                    name: '最佳价格点',
                                    xAxis: 1,
                                    lineStyle: {
                                        color: '#f44336',
                                        type: 'dashed'
                                    },
                                    label: {
                                        formatter: '当前价格',
                                        position: 'insideStartTop'
                                    }
                                }
                            ]
                        }
                    },
                    {
                        name: '收入曲线',
                        type: 'line',
                        yAxisIndex: 1,
                        smooth: true,
                        symbol: 'none',
                        data: this.priceElasticityData.priceVolume.map(item => [item[0], item[2]]),
                        itemStyle: {
                            color: '#ff9800'
                        },
                        markPoint: {
                            data: [
                                {
                                    name: '收入最高点',
                                    coord: [0.95, 860],
                                    symbolSize: 30,
                                    itemStyle: {
                                        color: '#f44336'
                                    },
                                    label: {
                                        formatter: '收入最优点'
                                    }
                                }
                            ]
                        }
                    }
                ]
            }
        },
        customerLtvOption() {
            return {
                tooltip: {
                    trigger: 'item',
                    formatter: '{b}: ¥{c} ({d}%)'
                },
                series: [
                    {
                        name: '客户终身价值',
                        type: 'pie',
                        radius: ['40%', '70%'],
                        avoidLabelOverlap: false,
                        itemStyle: {
                            borderRadius: 10,
                            borderColor: '#fff',
                            borderWidth: 2
                        },
                        label: {
                            show: true,
                            formatter: '{b}: ¥{c}'
                        },
                        emphasis: {
                            label: {
                                show: true,
                                fontSize: 16,
                                fontWeight: 'bold'
                            }
                        },
                        data: this.customerSegments
                    }
                ]
            }
        },
        seasonalityOption() {
            return {
                tooltip: {
                    trigger: 'axis'
                },
                xAxis: {
                    type: 'category',
                    data: this.seasonalityData.months
                },
                yAxis: {
                    type: 'value',
                    name: '指数',
                    min: 50,
                    max: 150,
                    axisLabel: {
                        formatter: '{value}%'
                    }
                },
                series: [
                    {
                        name: '季节性指数',
                        type: 'line',
                        data: this.seasonalityData.loadFactor,
                        smooth: true,
                        lineStyle: {
                            width: 3,
                            color: '#3f51b5'
                        },
                        symbol: 'circle',
                        symbolSize: 8,
                        markPoint: {
                            data: [
                                { type: 'max', name: '最高点' },
                                { type: 'min', name: '最低点' }
                            ]
                        },
                        markLine: {
                            data: [
                                { type: 'average', name: '平均值' }
                            ]
                        },
                        areaStyle: {
                            color: {
                                type: 'linear',
                                x: 0,
                                y: 0,
                                x2: 0,
                                y2: 1,
                                colorStops: [
                                    { offset: 0, color: 'rgba(63,81,181,0.4)' },
                                    { offset: 1, color: 'rgba(63,81,181,0.1)' }
                                ]
                            }
                        }
                    }
                ]
            }
        },
        anomalyDetectionOption() {
            return {
                tooltip: {
                    trigger: 'axis',
                    formatter: function (params) {
                        let result = params[0].axisValue + '<br/>'
                        params.forEach(param => {
                            result += param.marker + ' ' + param.seriesName + ': ' + param.value + '<br/>'
                        })
                        return result
                    }
                },
                xAxis: {
                    type: 'category',
                    data: this.anomalyData.dates
                },
                yAxis: {
                    type: 'value',
                    name: '订单数'
                },
                series: [
                    {
                        name: '订单量',
                        type: 'line',
                        data: this.anomalyData.sales,
                        smooth: true,
                        lineStyle: {
                            width: 3
                        },
                        symbol: 'circle',
                        symbolSize: 8,
                        markPoint: {
                            data: this.anomalyData.expectedValues.map(item => {
                                return {
                                    name: '预期值',
                                    coord: [item[0], item[1]],
                                    value: item[1],
                                    itemStyle: {
                                        color: '#ff9800'
                                    }
                                }
                            }),
                            symbolSize: 40,
                            label: {
                                formatter: '{c}'
                            }
                        }
                    }
                ]
            }
        },
        multiDimensionOption() {
            // 获取当前选择的X维度和Y维度数据
            if (!this.multiDimensionData || !this.multiDimensionData[this.dimensionX]) {
                // 如果数据不存在，返回一个空图表配置
                return {
                    tooltip: {
                        trigger: 'axis'
                    },
                    xAxis: {
                        type: 'category',
                        data: []
                    },
                    yAxis: {
                        type: 'value'
                    },
                    series: [{
                        name: '',
                        type: 'bar',
                        data: []
                    }]
                };
            }

            const dimensionData = this.multiDimensionData[this.dimensionX];
            const categories = dimensionData.categories;
            const values = dimensionData[this.dimensionY];

            // 确定Y轴名称
            let yAxisName = '';
            if (this.dimensionY === 'avgPayment') yAxisName = '平均支付金额';
            else if (this.dimensionY === 'frequency') yAxisName = '订票频率';
            else if (this.dimensionY === 'loyalty') yAxisName = '忠诚度指数';
            else if (this.dimensionY === 'refundRate') yAxisName = '退改率';

            // 确定Y轴格式化方式
            let formatter = '{value}';
            if (this.dimensionY === 'avgPayment') formatter = '¥{value}';
            else if (this.dimensionY === 'refundRate') formatter = '{value}%';

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
                    type: 'category',
                    data: categories
                },
                yAxis: {
                    type: 'value',
                    name: yAxisName,
                    axisLabel: {
                        formatter: formatter
                    }
                },
                series: [
                    {
                        name: yAxisName,
                        type: 'bar',
                        data: values.map((value, index) => {
                            return {
                                value: value,
                                itemStyle: {
                                    color: getColorByIndex(index)
                                }
                            }
                        }),
                        barWidth: '40%',
                        label: {
                            show: true,
                            position: 'top',
                            formatter: this.dimensionY === 'avgPayment' ? '¥{c}' :
                                this.dimensionY === 'refundRate' ? '{c}%' : '{c}'
                        }
                    }
                ]
            }

            function getColorByIndex(index) {
                const colorList = ['#3f51b5', '#4caf50', '#ff9800', '#9c27b0', '#f44336']
                return colorList[index % colorList.length]
            }
        }
    },
    methods: {
        formatNumber(num) {
            if (num === undefined || num === null) return '0'

            if (num >= 10000) {
                return (num / 10000).toFixed(2) + '万'
            } else {
                return num.toLocaleString()
            }
        },
        updatePrediction() {
            this.fetchSalesPrediction()
        },
        updateRouteAnalysis() {
            this.fetchRouteAnalysis()
        },
        updateMultiDimensionView() {
            this.fetchMultiDimensionData()
        },
        async fetchAllData() {
            this.loading = true
            this.error = null

            try {
                console.log('开始获取商业智能数据...')
                // 并行获取所有需要的数据
                await Promise.all([
                    this.fetchSalesPrediction(),
                    this.fetchRouteAnalysis(),
                    this.fetchPriceElasticity(),
                    this.fetchCustomerLtv(),
                    this.fetchSeasonalityData(),
                    this.fetchAnomalyData(),
                    this.fetchMultiDimensionData()
                ])
                console.log('所有商业智能数据获取完成')
            } catch (error) {
                console.error('获取商业智能数据失败:', error)
                this.error = '加载数据时出错，请重试'
                ElMessage.error('数据加载失败')
            } finally {
                this.loading = false
            }
        },
        async fetchSalesPrediction() {
            try {
                console.log('正在获取销售预测数据...')
                const response = await api.admin.analytics.getSalesPrediction({
                    params: { period: this.predictionPeriod }
                })
                console.log('销售预测数据响应:', response)

                if (response) {
                    // 更新预测摘要
                    if (response.summary) {
                        this.predictionSummary = {
                            totalRevenue: response.summary.total_revenue || 0,
                            growthRate: response.summary.growth_rate || 0,
                            totalOrders: response.summary.total_orders || 0,
                            orderGrowthRate: response.summary.order_growth_rate || 0,
                            averageOrderValue: response.summary.average_order_value || 0,
                            aovGrowthRate: response.summary.aov_growth_rate || 0
                        }
                    } else {
                        console.warn('销售预测数据缺少summary字段')
                    }

                    // 更新图表数据
                    const historical = response.historical_data || {}
                    const prediction = response.prediction_data || {}

                    this.predictionData = {
                        dates: [...(historical.dates || []), ...(prediction.dates || [])],
                        historical: historical.revenues || [],
                        predictions: [...new Array(historical.dates?.length || 0).fill(null), ...(prediction.revenues || [])]
                    }

                    console.log('销售预测数据已更新')
                } else {
                    console.warn('销售预测数据返回为空')
                }
            } catch (error) {
                console.error('获取销售预测数据失败:', error)
                if (error.response) {
                    console.error('错误状态码:', error.response.status)
                    console.error('错误数据:', error.response.data)
                }
            }
        },
        async fetchRouteAnalysis() {
            try {
                const response = await api.admin.analytics.getRouteAnalytics({
                    params: { metric: this.routeMetric }
                })

                if (response && response.route_data) {
                    this.routeData = response.route_data
                }
            } catch (error) {
                console.error('获取航线分析数据失败:', error)
            }
        },
        async fetchPriceElasticity() {
            try {
                const response = await api.admin.analytics.getPriceElasticity({
                    params: { route: 'beijing-shanghai' }
                })

                if (response) {
                    this.priceElasticityData = {
                        priceVolume: response.price_volume_data || [],
                        elasticity: response.elasticity_data || []
                    }

                    this.optimalPrice = response.optimal_price || 0
                }
            } catch (error) {
                console.error('获取价格弹性数据失败:', error)
            }
        },
        async fetchCustomerLtv() {
            try {
                const response = await api.admin.analytics.getCustomerLTV()

                if (response) {
                    this.customerSegments = response.user_segments || []
                    this.averageLtv = response.average_ltv || 0
                }
            } catch (error) {
                console.error('获取客户终身价值数据失败:', error)
            }
        },
        async fetchSeasonalityData() {
            try {
                const response = await api.admin.analytics.getSeasonalityData({
                    params: { route: this.seasonalRoute }
                })

                if (response) {
                    this.seasonalityData = {
                        months: response.months || [],
                        loadFactor: response.load_factor || [],
                        ticketPrice: response.ticket_price || []
                    }

                    this.availableRoutes = response.available_routes || []
                }
            } catch (error) {
                console.error('获取季节性分析数据失败:', error)
            }
        },
        async fetchAnomalyData() {
            try {
                const response = await api.admin.analytics.getAnomalyDetection()

                if (response) {
                    this.anomalyData = {
                        dates: response.dates || [],
                        sales: response.sales || [],
                        expectedValues: response.expected_values || [],
                        upperBounds: response.upper_bounds || [],
                        lowerBounds: response.lower_bounds || []
                    }

                    this.anomalyItems = response.anomalies || []
                }
            } catch (error) {
                console.error('获取异常检测数据失败:', error)
            }
        },
        async fetchMultiDimensionData() {
            try {
                // 在实际应用中，这应该是一个API调用
                // const response = await api.admin.analytics.getMultiDimensionData({
                //     params: { dimensionX: this.dimensionX, dimensionY: this.dimensionY }
                // });

                // 目前使用已初始化的模拟数据
                console.log(`分析维度: ${this.dimensionX} vs ${this.dimensionY}`);

                // 如果后续需要从API获取数据，可以这样设置
                // if (response && response.data) {
                //     this.multiDimensionData = response.data;
                // }
            } catch (error) {
                console.error('获取多维度分析数据失败:', error);
            }
        },
        generateReport() {
            ElMessage.success('报表生成功能开发中')
            // 实际应用中这里应该调用API导出报表
        }
    },
    mounted() {
        this.fetchAllData()
    }
}
</script>

<style scoped>
.business-intelligence {
    padding: 20px;
    max-width: 1600px;
    margin: 0 auto;
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

.mt-20 {
    margin-top: 20px;
}

.prediction-card,
.bi-card {
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
    border-radius: 8px;
    margin-bottom: 0;
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

.prediction-actions,
.card-actions {
    display: flex;
    align-items: center;
    gap: 10px;
}

.chart-container {
    width: 100%;
}

.prediction-summary {
    display: flex;
    justify-content: space-around;
    margin-top: 20px;
    border-top: 1px solid #eee;
    padding-top: 15px;
    text-align: center;
}

.summary-item {
    flex: 1;
}

.summary-label {
    font-size: 14px;
    color: #666;
    margin-bottom: 5px;
}

.summary-value {
    font-weight: 600;
    color: #333;
}

.summary-value .amount {
    font-size: 20px;
    margin-right: 8px;
}

.summary-value .trend {
    font-size: 14px;
}

.trend.up {
    color: #4caf50;
}

.trend.down {
    color: #f44336;
}

.anomaly-list {
    margin-top: 15px;
    max-height: 120px;
    overflow-y: auto;
}

.anomaly-header {
    font-weight: 600;
    margin-bottom: 8px;
    color: #333;
}

.anomaly-item {
    display: flex;
    align-items: center;
    padding: 5px 0;
    border-bottom: 1px dashed #eee;
}

.anomaly-text {
    margin-left: 8px;
    flex: 1;
    font-size: 13px;
    color: #666;
}

.anomaly-date {
    font-size: 12px;
    color: #999;
}
</style>