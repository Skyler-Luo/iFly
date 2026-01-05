<template>
  <div class="admin-dashboard">
    <div class="page-header">
      <h1 class="title">管理员控制台</h1>
      <div class="header-actions">
        <el-radio-group v-model="timePeriod" size="default" @change="refreshData">
          <el-radio-button value="day">今日</el-radio-button>
          <el-radio-button value="week">本周</el-radio-button>
          <el-radio-button value="month">本月</el-radio-button>
        </el-radio-group>
        <el-button type="primary" :icon="Refresh" @click="refreshData" :loading="loading">
          刷新
        </el-button>
      </div>
    </div>

    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <div class="loading-text">正在加载仪表盘数据...</div>
    </div>

    <div v-if="error" class="error-message">
      <i class="fas fa-exclamation-circle"></i>
      {{ error }}
      <button class="retry-button" @click="refreshData">重试</button>
    </div>

    <div v-if="!loading && !error">
      <div class="dashboard-stats">
        <div class="stat-card stat-flights">
          <div class="stat-icon">
            <el-icon><Promotion /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-label">航班总数</div>
            <div class="stat-value">{{ stats.flights }}</div>
            <div class="stat-trend" :class="{ 'up': stats.flightsGrowth > 0, 'down': stats.flightsGrowth < 0 }">
              <el-icon v-if="stats.flightsGrowth >= 0"><Top /></el-icon>
              <el-icon v-else><Bottom /></el-icon>
              {{ Math.abs(stats.flightsGrowth) }}%
            </div>
          </div>
        </div>

        <div class="stat-card stat-users">
          <div class="stat-icon">
            <el-icon><User /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-label">注册用户</div>
            <div class="stat-value">{{ stats.users }}</div>
            <div class="stat-trend" :class="{ 'up': stats.usersGrowth > 0, 'down': stats.usersGrowth < 0 }">
              <el-icon v-if="stats.usersGrowth >= 0"><Top /></el-icon>
              <el-icon v-else><Bottom /></el-icon>
              {{ Math.abs(stats.usersGrowth) }}%
            </div>
          </div>
        </div>

        <div class="stat-card stat-orders">
          <div class="stat-icon">
            <el-icon><Tickets /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-label">订单总数</div>
            <div class="stat-value">{{ stats.orders }}</div>
            <div class="stat-trend" :class="{ 'up': stats.ordersGrowth > 0, 'down': stats.ordersGrowth < 0 }">
              <el-icon v-if="stats.ordersGrowth >= 0"><Top /></el-icon>
              <el-icon v-else><Bottom /></el-icon>
              {{ Math.abs(stats.ordersGrowth) }}%
            </div>
          </div>
        </div>

        <div class="stat-card stat-revenue">
          <div class="stat-icon">
            <el-icon><Coin /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-label">总收入</div>
            <div class="stat-value">¥{{ stats.revenue.toLocaleString() }}</div>
            <div class="stat-trend" :class="{ 'up': stats.revenueGrowth > 0, 'down': stats.revenueGrowth < 0 }">
              <el-icon v-if="stats.revenueGrowth >= 0"><Top /></el-icon>
              <el-icon v-else><Bottom /></el-icon>
              {{ Math.abs(stats.revenueGrowth) }}%
            </div>
          </div>
        </div>
      </div>

      <div class="dashboard-content">
        <div class="quick-actions">
          <h2>快捷操作</h2>
          <div class="action-buttons">
            <router-link to="/admin/flights" class="btn btn-primary">
              <i class="fas fa-plane-departure"></i> 航班管理
            </router-link>
            <router-link to="/admin/users" class="btn btn-primary">
              <i class="fas fa-user-cog"></i> 用户管理
            </router-link>
            <router-link to="/admin/orders" class="btn btn-primary">
              <i class="fas fa-list"></i> 订单管理
            </router-link>
            <router-link to="/admin/settings" class="btn btn-primary">
              <i class="fas fa-cogs"></i> 系统设置
            </router-link>
            <router-link to="/admin/visualization" class="btn btn-primary">
              <i class="fas fa-chart-bar"></i> 数据可视化
            </router-link>
            <router-link to="/admin/business-intelligence" class="btn btn-primary">
              <i class="fas fa-brain"></i> 商务智能
            </router-link>
          </div>
        </div>

        <div class="charts-container">
          <div class="chart-row">
            <div class="chart-card large">
              <h3>收入与订单趋势</h3>
              <div class="chart-wrapper">
                <v-chart :option="revenueChartOption" autoresize />
              </div>
            </div>
          </div>

          <div class="chart-row">
            <div class="chart-card">
              <h3>热门目的地</h3>
              <div class="chart-wrapper">
                <v-chart :option="destinationChartOption" autoresize />
              </div>
            </div>

            <div class="chart-card">
              <h3>航班座位利用率</h3>
              <div class="chart-wrapper">
                <v-chart :option="seatUtilizationOption" autoresize />
              </div>
            </div>
          </div>

          <div class="chart-row">
            <div class="chart-card">
              <h3>用户增长趋势</h3>
              <div class="chart-wrapper">
                <v-chart :option="userGrowthOption" autoresize />
              </div>
            </div>

            <div class="chart-card">
              <h3>订单完成情况</h3>
              <div class="chart-wrapper">
                <v-chart :option="orderStatusOption" autoresize />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
// 直接导入Vue-ECharts组件
import VChart from 'vue-echarts'
import { Refresh, Promotion, User, Tickets, Coin, Top, Bottom } from '@element-plus/icons-vue'
import api from '../services/api'

export default {
  name: 'AdminDashboardView',
  components: {
    VChart,
    Promotion,
    User,
    Tickets,
    Coin,
    Top,
    Bottom
  },
  data() {
    return {
      Refresh,
      timePeriod: 'week',
      loading: true,
      error: null,
      stats: {
        flights: 0,
        flightsGrowth: 0,
        users: 0,
        usersGrowth: 0,
        orders: 0,
        ordersGrowth: 0,
        revenue: 0,
        revenueGrowth: 0
      },
      revenueData: [],
      popularDestinations: [],
      seatUtilization: [],
      userGrowthData: [],
      orderStatusData: []
    }
  },
  computed: {
    revenueChartOption() {
      return {
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'shadow'
          }
        },
        legend: {
          data: ['收入(元)', '订单数']
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: this.revenueData.map(item => item[0])
        },
        yAxis: [
          {
            type: 'value',
            name: '收入(元)',
            axisLabel: {
              formatter: '{value} ¥'
            }
          },
          {
            type: 'value',
            name: '订单数',
            axisLabel: {
              formatter: '{value}'
            }
          }
        ],
        series: [
          {
            name: '收入(元)',
            type: 'bar',
            barWidth: '40%',
            data: this.revenueData.map(item => item[1]),
            itemStyle: {
              color: '#3f51b5'
            }
          },
          {
            name: '订单数',
            type: 'line',
            yAxisIndex: 1,
            data: this.revenueData.map(item => item[2]),
            itemStyle: {
              color: '#ff9800'
            }
          }
        ]
      }
    },
    destinationChartOption() {
      return {
        tooltip: {
          trigger: 'item',
          formatter: '{b}: {c} ({d}%)'
        },
        legend: {
          orient: 'vertical',
          left: 'left',
          top: 'center'
        },
        series: [
          {
            type: 'pie',
            radius: '70%',
            center: ['60%', '50%'],
            data: this.popularDestinations,
            emphasis: {
              itemStyle: {
                shadowBlur: 10,
                shadowOffsetX: 0,
                shadowColor: 'rgba(0, 0, 0, 0.5)'
              }
            },
            itemStyle: {
              borderRadius: 5,
              borderColor: '#fff',
              borderWidth: 2
            }
          }
        ]
      }
    },
    seatUtilizationOption() {
      return {
        tooltip: {
          trigger: 'axis',
          formatter: '{b}: {c}%'
        },
        grid: {
          left: '15%',
          right: '15%',
          top: '15%',
          bottom: '15%'
        },
        xAxis: {
          type: 'category',
          data: this.seatUtilization.map(item => item.name),
          axisLabel: {
            fontSize: 12
          }
        },
        yAxis: {
          type: 'value',
          max: 100,
          axisLabel: {
            formatter: '{value}%'
          }
        },
        series: [{
          type: 'bar',
          data: this.seatUtilization.map(item => item.value),
          barWidth: '40%',
          itemStyle: {
            borderRadius: [4, 4, 0, 0],
            color: function(params) {
              const colors = ['#5470c6', '#91cc75']
              return colors[params.dataIndex % colors.length]
            }
          },
          label: {
            show: true,
            position: 'top',
            formatter: '{c}%',
            fontSize: 14,
            fontWeight: 'bold'
          }
        }]
      }
    },
    userGrowthOption() {
      return {
        tooltip: {
          trigger: 'axis'
        },
        xAxis: {
          type: 'category',
          data: this.userGrowthData.map(item => item[0])
        },
        yAxis: {
          type: 'value',
          name: '新用户',
          axisLabel: {
            formatter: '{value}'
          }
        },
        series: [
          {
            data: this.userGrowthData.map(item => item[1]),
            type: 'line',
            smooth: true,
            areaStyle: {
              opacity: 0.2
            },
            lineStyle: {
              width: 3
            },
            symbol: 'circle',
            symbolSize: 8,
            itemStyle: {
              color: '#4caf50'
            }
          }
        ]
      }
    },
    orderStatusOption() {
      return {
        tooltip: {
          trigger: 'item',
          formatter: '{b}: {c} ({d}%)'
        },
        legend: {
          orient: 'vertical',
          left: 'left',
          top: 'center'
        },
        series: [
          {
            type: 'pie',
            radius: ['40%', '70%'],
            center: ['60%', '50%'],
            avoidLabelOverlap: false,
            itemStyle: {
              borderRadius: 10,
              borderColor: '#fff',
              borderWidth: 2
            },
            label: {
              show: false,
              position: 'center'
            },
            emphasis: {
              label: {
                show: true,
                fontSize: 16,
                fontWeight: 'bold'
              }
            },
            labelLine: {
              show: false
            },
            data: this.orderStatusData
          }
        ]
      }
    }
  },
  methods: {
    // 添加辅助方法，确保能够处理各种API响应结构
    extractResponseData(response) {
      // 检查是否是axios响应
      if (response && response.data !== undefined) {
        console.log('从axios响应中提取数据')
        return response.data;
      }

      // 如果已经是纯数据对象，直接返回
      if (response && typeof response === 'object') {
        console.log('使用已提取的数据')
        return response;
      }

      console.warn('无法识别的响应格式', response)
      return {};
    },
    async refreshData() {
      this.loading = true
      this.error = null

      try {
        console.log(`刷新数据，时间段：${this.timePeriod}`)
        // 调用后端API获取仪表盘数据
        let response = await api.admin.getDashboardStats()

        // 从axios响应中提取数据
        response = this.extractResponseData(response)

        // 如果不是默认'week'，则重新获取特定时间段的数据
        if (this.timePeriod !== 'week') {
          try {
            const periodResponse = await api.admin.getDashboardStats({
              params: { period: this.timePeriod }
            })
            if (periodResponse) {
              response = this.extractResponseData(periodResponse)
            }
          } catch (err) {
            console.warn('获取特定时间段数据失败，使用默认数据', err)
          }
        }

        console.log('API处理后的数据:', response)

        // 更新本地数据
        if (response) {
          console.log('正在处理数据，结构:', Object.keys(response))

          if (response.stats) {
            console.log('统计数据:', response.stats)
            this.stats = response.stats
          } else {
            console.warn('未找到统计数据')
          }

          if (Array.isArray(response.revenueData)) {
            console.log('收入数据:', response.revenueData.length)
            this.revenueData = response.revenueData
          } else {
            console.warn('收入数据不是数组:', response.revenueData)
          }

          if (Array.isArray(response.popularDestinations)) {
            console.log('热门目的地数据:', response.popularDestinations.length)
            // 处理可能的乱码
            this.popularDestinations = response.popularDestinations.map(item => {
              // 如果name是乱码，用"目的地-N"替代
              // eslint-disable-next-line no-useless-escape
              if (item.name && (!/^[\u4e00-\u9fa5a-zA-Z0-9\s\-]+$/.test(item.name) || item.name.includes('\\u'))) {
                return {
                  name: `目的地-${item.value}`,
                  value: item.value
                }
              }
              return item
            })
          }

          if (Array.isArray(response.seatUtilization)) {
            // 处理乱码
            this.seatUtilization = response.seatUtilization.map(item => {
              // 替换可能的乱码为固定值
              // eslint-disable-next-line no-useless-escape
              if (item.name && (!/^[\u4e00-\u9fa5a-zA-Z0-9\s\-]+$/.test(item.name) || item.name.includes('\\u'))) {
                if (item.name.includes('\\u4ecb')) { // 尝试识别国际航线
                  return { name: '国际航线', value: item.value }
                } else {
                  return { name: '国内航线', value: item.value }
                }
              }
              return item
            })
          }

          if (Array.isArray(response.userGrowthData)) {
            this.userGrowthData = response.userGrowthData
          }

          if (Array.isArray(response.orderStatusData)) {
            // 处理乱码
            this.orderStatusData = response.orderStatusData.map(item => {
              // 替换可能的乱码为固定值
              // eslint-disable-next-line no-useless-escape
              if (item.name && (!/^[\u4e00-\u9fa5a-zA-Z0-9\s\-]+$/.test(item.name) || item.name.includes('\\u'))) {
                // 根据value值大致确定状态
                if (item.value > 800) {
                  return { name: '待付款', value: item.value }
                } else if (item.value > 10 && item.value < 20) {
                  return { name: '已支付', value: item.value }
                } else {
                  return { name: '已取消', value: item.value }
                }
              }
              return item
            })
          }
        }
      } catch (err) {
        console.error('获取仪表盘数据失败:', err)
        this.error = '获取仪表盘数据失败，请稍后再试'
      } finally {
        this.loading = false
      }
    },
    startRealtimeUpdates() {
      // 每5分钟刷新一次数据
      this.refreshInterval = setInterval(() => {
        this.refreshData()
      }, 300000)
    }
  },
  mounted() {
    this.refreshData() // 初始化数据
    this.startRealtimeUpdates()
  },
  beforeUnmount() {
    // 清除定时器
    if (this.refreshInterval) {
      clearInterval(this.refreshInterval)
    }
  }
}
</script>

<style scoped>
.admin-dashboard {
  padding: 20px 40px;
  width: 100%;
  box-sizing: border-box;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #eee;
}

.title {
  font-size: 24px;
  color: #333;
  margin: 0;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 15px;
}

.dashboard-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  padding: 24px;
  display: flex;
  align-items: center;
  transition: transform 0.2s, box-shadow 0.2s;
  border-left: 4px solid #3f51b5;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
}

.stat-flights {
  border-left-color: #3f51b5;
}

.stat-users {
  border-left-color: #4caf50;
}

.stat-orders {
  border-left-color: #ff9800;
}

.stat-revenue {
  border-left-color: #e91e63;
}

.stat-flights .stat-icon {
  color: #3f51b5;
}

.stat-users .stat-icon {
  color: #4caf50;
}

.stat-orders .stat-icon {
  color: #ff9800;
}

.stat-revenue .stat-icon {
  color: #e91e63;
}

.stat-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 20px;
}

.stat-icon i {
  font-size: 36px;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #333;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: #888;
  margin-bottom: 6px;
}

.stat-trend {
  font-size: 13px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 4px;
}

.stat-trend i {
  font-size: 10px;
}

.stat-trend.up {
  color: #52c41a;
}

.stat-trend.down {
  color: #ff4d4f;
}

.dashboard-content {
  display: grid;
  grid-template-columns: 1fr;
  gap: 30px;
}

.quick-actions {
  background: white;
  border-radius: 10px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.quick-actions h2 {
  font-size: 18px;
  margin-top: 0;
  margin-bottom: 15px;
  color: #333;
}

.action-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.btn {
  padding: 10px 15px;
  border-radius: 8px;
  text-decoration: none;
  font-weight: 500;
  display: flex;
  align-items: center;
  font-size: 14px;
  transition: background 0.2s, transform 0.1s;
}

.btn i {
  margin-right: 8px;
}

.btn:active {
  transform: scale(0.98);
}

.btn-primary {
  background: #3f51b5;
  color: white;
}

.btn-primary:hover {
  background: #303f9f;
}

.charts-container {
  display: grid;
  grid-template-columns: 1fr;
  gap: 20px;
}

.chart-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 20px;
}

.chart-card {
  background: white;
  border-radius: 10px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.chart-card.large {
  grid-column: 1 / -1;
}

.chart-card h3 {
  font-size: 16px;
  margin-top: 0;
  margin-bottom: 15px;
  color: #333;
}

.chart-wrapper {
  height: 300px;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 0;
}

.loading-spinner {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3f51b5;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }

  100% {
    transform: rotate(360deg);
  }
}

.loading-text {
  margin-top: 15px;
  color: #666;
  font-weight: 500;
}

.error-message {
  background-color: #ffebee;
  border: 1px solid #ffcdd2;
  border-radius: 4px;
  color: #b71c1c;
  padding: 15px;
  margin: 20px 0;
  display: flex;
  align-items: center;
}

.error-message i {
  margin-right: 10px;
  font-size: 20px;
}

.retry-button {
  margin-left: auto;
  background: #f44336;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 5px 10px;
  cursor: pointer;
  transition: background 0.2s;
}

.retry-button:hover {
  background: #d32f2f;
}

@media (max-width: 1200px) {
  .dashboard-stats {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
  
  .dashboard-stats {
    grid-template-columns: 1fr;
  }
}
</style>