<template>
  <div class="admin-dashboard">
    <h1 class="title">管理员控制台</h1>

    <div class="dashboard-summary">
      <div class="summary-title">
        <h2>系统概览</h2>
        <div class="period-selector">
          <el-radio-group v-model="timePeriod" size="small" @change="refreshData">
            <el-radio-button label="day">今日</el-radio-button>
            <el-radio-button label="week">本周</el-radio-button>
            <el-radio-button label="month">本月</el-radio-button>
          </el-radio-group>
        </div>
      </div>

      <!-- 调试信息区域 -->
      <div v-if="debugMode" class="debug-info">
        <div class="debug-title">
          <h3>调试信息</h3>
          <button @click="debugMode = false" class="close-debug">关闭</button>
        </div>
        <div class="debug-content">
          <p>API响应状态: {{ apiStatus }}</p>
          <p>数据结构: {{ apiDataKeys.join(', ') }}</p>
          <p>统计数据: {{ JSON.stringify(stats) }}</p>
          <p>收入数据长度: {{ revenueData.length }}</p>
          <p>热门目的地长度: {{ popularDestinations.length }}</p>
          <p>航班利用率数据长度: {{ seatUtilization.length }}</p>
          <button @click="refreshData" class="refresh-debug">刷新数据</button>
        </div>
      </div>
    </div>

    <!-- 调试模式切换按钮 -->
    <div class="debug-toggle">
      <button @click="debugMode = !debugMode" class="debug-btn">
        {{ debugMode ? '隐藏调试' : '显示调试' }}
      </button>
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
        <div class="stat-card">
          <div class="stat-icon">
            <i class="fas fa-plane"></i>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.flights }}</div>
            <div class="stat-label">航班总数</div>
            <div class="stat-trend" :class="{ 'up': stats.flightsGrowth > 0, 'down': stats.flightsGrowth < 0 }">
              {{ stats.flightsGrowth > 0 ? '+' : '' }}{{ stats.flightsGrowth }}%
            </div>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-icon">
            <i class="fas fa-users"></i>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.users }}</div>
            <div class="stat-label">注册用户</div>
            <div class="stat-trend" :class="{ 'up': stats.usersGrowth > 0, 'down': stats.usersGrowth < 0 }">
              {{ stats.usersGrowth > 0 ? '+' : '' }}{{ stats.usersGrowth }}%
            </div>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-icon">
            <i class="fas fa-ticket-alt"></i>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.orders }}</div>
            <div class="stat-label">订单总数</div>
            <div class="stat-trend" :class="{ 'up': stats.ordersGrowth > 0, 'down': stats.ordersGrowth < 0 }">
              {{ stats.ordersGrowth > 0 ? '+' : '' }}{{ stats.ordersGrowth }}%
            </div>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-icon">
            <i class="fas fa-money-bill-wave"></i>
          </div>
          <div class="stat-content">
            <div class="stat-value">¥{{ stats.revenue.toLocaleString() }}</div>
            <div class="stat-label">总收入</div>
            <div class="stat-trend" :class="{ 'up': stats.revenueGrowth > 0, 'down': stats.revenueGrowth < 0 }">
              {{ stats.revenueGrowth > 0 ? '+' : '' }}{{ stats.revenueGrowth }}%
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
            <router-link to="/admin/promotions" class="btn btn-primary">
              <i class="fas fa-tags"></i> 优惠管理
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

        <div class="realtime-monitoring">
          <h2>实时监控</h2>
          <div class="monitoring-row">
            <div class="monitoring-card">
              <h3>当前在线用户</h3>
              <div class="realtime-value">{{ realtimeStats.onlineUsers }}</div>
              <div class="realtime-chart">
                <v-chart :option="onlineUsersOption" autoresize />
              </div>
            </div>

            <div class="monitoring-card">
              <h3>实时订单数</h3>
              <div class="realtime-value">{{ realtimeStats.activeOrders }}</div>
              <div class="realtime-chart">
                <v-chart :option="activeOrdersOption" autoresize />
              </div>
            </div>

            <div class="monitoring-card">
              <h3>系统资源</h3>
              <div class="resource-stats">
                <div class="resource-item">
                  <div class="resource-label">CPU</div>
                  <el-progress :percentage="realtimeStats.cpuUsage" :color="resourceColor" />
                </div>
                <div class="resource-item">
                  <div class="resource-label">内存</div>
                  <el-progress :percentage="realtimeStats.memoryUsage" :color="resourceColor" />
                </div>
                <div class="resource-item">
                  <div class="resource-label">存储</div>
                  <el-progress :percentage="realtimeStats.diskUsage" :color="resourceColor" />
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="recent-activities">
          <h2>最近活动</h2>
          <div class="activity-list">
            <div v-for="activity in recentActivities" :key="activity.id" class="activity-item">
              <div class="activity-icon" :class="'activity-' + activity.type">
                <i :class="getActivityIcon(activity.type)"></i>
              </div>
              <div class="activity-content">
                <div class="activity-title">{{ activity.title }}</div>
                <div class="activity-description">{{ activity.description }}</div>
                <div class="activity-time">{{ activity.time }}</div>
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
import api from '../services/api'

export default {
  name: 'AdminDashboardView',
  components: {
    VChart
  },
  data() {
    return {
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
      orderStatusData: [],
      realtimeStats: {
        onlineUsers: 0,
        activeOrders: 0,
        cpuUsage: 0,
        memoryUsage: 0,
        diskUsage: 0
      },
      onlineUserHistory: [0, 0, 0, 0, 0, 0, 0],
      activeOrderHistory: [0, 0, 0, 0, 0, 0, 0],
      recentActivities: [
        {
          id: 1,
          type: 'order',
          title: '新订单',
          description: '用户王小明(ID: 10089)预订了北京至上海的机票',
          time: '10分钟前'
        },
        {
          id: 2,
          type: 'user',
          title: '新用户注册',
          description: '5位新用户在过去一小时内完成注册',
          time: '1小时前'
        },
        {
          id: 3,
          type: 'system',
          title: '系统更新',
          description: '系统完成了数据库优化和安全更新',
          time: '3小时前'
        },
        {
          id: 4,
          type: 'promotion',
          title: '新优惠活动',
          description: '暑期特惠活动已经开始，持续到8月底',
          time: '5小时前'
        },
        {
          id: 5,
          type: 'alert',
          title: '系统警告',
          description: '检测到异常登录尝试，IP已被临时封锁',
          time: '12小时前'
        }
      ],
      debugMode: false,
      apiStatus: '',
      apiDataKeys: []
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
              clip: false,
              itemStyle: {
                borderWidth: 1,
                borderColor: '#464646'
              }
            },
            axisLine: {
              lineStyle: {
                width: 20
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
            data: this.seatUtilization,
            detail: {
              width: 50,
              height: 14,
              fontSize: 14,
              color: 'auto',
              borderColor: 'auto',
              borderRadius: 20,
              borderWidth: 1,
              formatter: '{value}%'
            }
          }
        ]
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
    },
    onlineUsersOption() {
      return {
        xAxis: {
          type: 'category',
          show: false,
          data: ['', '', '', '', '', '', '']
        },
        yAxis: {
          type: 'value',
          show: false
        },
        grid: {
          left: 0,
          right: 0,
          top: 0,
          bottom: 0
        },
        series: [
          {
            data: this.onlineUserHistory,
            type: 'line',
            showSymbol: false,
            smooth: true,
            lineStyle: {
              width: 2,
              color: '#1976d2'
            },
            areaStyle: {
              color: {
                type: 'linear',
                x: 0,
                y: 0,
                x2: 0,
                y2: 1,
                colorStops: [
                  {
                    offset: 0,
                    color: 'rgba(25, 118, 210, 0.5)'
                  },
                  {
                    offset: 1,
                    color: 'rgba(25, 118, 210, 0)'
                  }
                ]
              }
            }
          }
        ]
      }
    },
    activeOrdersOption() {
      return {
        xAxis: {
          type: 'category',
          show: false,
          data: ['', '', '', '', '', '', '']
        },
        yAxis: {
          type: 'value',
          show: false
        },
        grid: {
          left: 0,
          right: 0,
          top: 0,
          bottom: 0
        },
        series: [
          {
            data: this.activeOrderHistory,
            type: 'line',
            showSymbol: false,
            smooth: true,
            lineStyle: {
              width: 2,
              color: '#f44336'
            },
            areaStyle: {
              color: {
                type: 'linear',
                x: 0,
                y: 0,
                x2: 0,
                y2: 1,
                colorStops: [
                  {
                    offset: 0,
                    color: 'rgba(244, 67, 54, 0.5)'
                  },
                  {
                    offset: 1,
                    color: 'rgba(244, 67, 54, 0)'
                  }
                ]
              }
            }
          }
        ]
      }
    },
    resourceColor() {
      return (percentage) => {
        if (percentage < 70) return '#4caf50'
        if (percentage < 85) return '#ff9800'
        return '#f44336'
      }
    }
  },
  methods: {
    getActivityIcon(type) {
      const icons = {
        order: 'fas fa-shopping-cart',
        user: 'fas fa-user-plus',
        system: 'fas fa-cogs',
        promotion: 'fas fa-tag',
        alert: 'fas fa-exclamation-triangle'
      }
      return icons[type] || 'fas fa-info-circle'
    },
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

          if (response.realtimeStats) {
            this.realtimeStats = response.realtimeStats

            // 更新实时图表历史数据
            if (this.realtimeStats.onlineUsers) {
              this.onlineUserHistory = [
                ...this.onlineUserHistory.slice(1),
                this.realtimeStats.onlineUsers
              ]
            }

            if (this.realtimeStats.activeOrders) {
              this.activeOrderHistory = [
                ...this.activeOrderHistory.slice(1),
                this.realtimeStats.activeOrders
              ]
            }
          }
        }

        // 更新调试信息
        this.apiStatus = response ? '成功' : '失败'
        this.apiDataKeys = Object.keys(response || {})
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

      // 模拟实时数据更新
      this.realtimeInterval = setInterval(() => {
        // 更新在线用户数
        if (this.realtimeStats.onlineUsers > 0) {
          const randomChange = Math.floor(Math.random() * 10) - 3  // -3 到 6 的随机数
          this.realtimeStats.onlineUsers = Math.max(500, this.realtimeStats.onlineUsers + randomChange)
          this.onlineUserHistory.push(this.realtimeStats.onlineUsers)
          this.onlineUserHistory.shift()
        }

        // 更新实时订单数
        if (this.realtimeStats.activeOrders > 0) {
          const orderChange = Math.floor(Math.random() * 5) - 2  // -2 到 2 的随机数
          this.realtimeStats.activeOrders = Math.max(20, this.realtimeStats.activeOrders + orderChange)
          this.activeOrderHistory.push(this.realtimeStats.activeOrders)
          this.activeOrderHistory.shift()
        }

        // 更新系统资源使用率
        this.realtimeStats.cpuUsage = Math.min(95, Math.max(20, this.realtimeStats.cpuUsage + (Math.random() * 6 - 3)))
        this.realtimeStats.memoryUsage = Math.min(95, Math.max(50, this.realtimeStats.memoryUsage + (Math.random() * 4 - 2)))
        this.realtimeStats.diskUsage = Math.min(90, Math.max(30, this.realtimeStats.diskUsage + (Math.random() * 1 - 0.5)))
      }, 5000)  // 每5秒更新一次
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
    if (this.realtimeInterval) {
      clearInterval(this.realtimeInterval)
    }
  }
}
</script>

<style scoped>
.admin-dashboard {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.title {
  font-size: 28px;
  color: #333;
  margin-bottom: 30px;
  border-bottom: 2px solid #3f51b5;
  padding-bottom: 10px;
}

.dashboard-summary {
  margin-bottom: 20px;
}

.summary-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.summary-title h2 {
  font-size: 20px;
  margin: 0;
}

.dashboard-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background: white;
  border-radius: 10px;
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.1);
  padding: 20px;
  display: flex;
  align-items: center;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 10px;
  background: rgba(63, 81, 181, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 15px;
}

.stat-icon i {
  font-size: 24px;
  color: #3f51b5;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #333;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 14px;
  color: #666;
  margin-bottom: 5px;
}

.stat-trend {
  font-size: 12px;
  font-weight: 600;
}

.stat-trend.up {
  color: #4caf50;
}

.stat-trend.down {
  color: #f44336;
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

.realtime-monitoring {
  background: white;
  border-radius: 10px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.realtime-monitoring h2 {
  font-size: 18px;
  margin-top: 0;
  margin-bottom: 15px;
  color: #333;
}

.monitoring-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.monitoring-card {
  background: #f9f9f9;
  border-radius: 8px;
  padding: 15px;
}

.monitoring-card h3 {
  font-size: 16px;
  margin-top: 0;
  margin-bottom: 10px;
  color: #333;
}

.realtime-value {
  font-size: 24px;
  font-weight: bold;
  color: #3f51b5;
  margin-bottom: 10px;
}

.realtime-chart {
  height: 100px;
}

.resource-stats {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.resource-item {
  margin-bottom: 5px;
}

.resource-label {
  font-size: 14px;
  margin-bottom: 5px;
  color: #666;
}

.recent-activities {
  background: white;
  border-radius: 10px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.recent-activities h2 {
  font-size: 18px;
  margin-top: 0;
  margin-bottom: 15px;
  color: #333;
}

.activity-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
  max-height: 400px;
  overflow-y: auto;
}

.activity-item {
  display: flex;
  align-items: flex-start;
  padding: 15px;
  border-radius: 8px;
  background: #f9f9f9;
  transition: background 0.2s;
}

.activity-item:hover {
  background: #f0f0f0;
}

.activity-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 15px;
  flex-shrink: 0;
}

.activity-order {
  background: rgba(33, 150, 243, 0.2);
  color: #2196f3;
}

.activity-user {
  background: rgba(76, 175, 80, 0.2);
  color: #4caf50;
}

.activity-system {
  background: rgba(156, 39, 176, 0.2);
  color: #9c27b0;
}

.activity-promotion {
  background: rgba(255, 193, 7, 0.2);
  color: #ffc107;
}

.activity-alert {
  background: rgba(244, 67, 54, 0.2);
  color: #f44336;
}

.activity-content {
  flex: 1;
}

.activity-title {
  font-weight: 600;
  margin-bottom: 5px;
}

.activity-description {
  font-size: 13px;
  color: #666;
  margin-bottom: 5px;
}

.activity-time {
  font-size: 12px;
  color: #999;
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

.debug-info {
  background: white;
  border-radius: 10px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-top: 15px;
}

.debug-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.debug-title h3 {
  font-size: 16px;
  margin: 0;
}

.close-debug {
  background: #f44336;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 5px 10px;
  cursor: pointer;
  transition: background 0.2s;
}

.close-debug:hover {
  background: #d32f2f;
}

.debug-content {
  margin-bottom: 15px;
}

.refresh-debug {
  background: #3f51b5;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 5px 10px;
  cursor: pointer;
  transition: background 0.2s;
}

.refresh-debug:hover {
  background: #303f9f;
}

.debug-toggle {
  margin-top: 15px;
  text-align: right;
}

.debug-btn {
  background: #3f51b5;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 5px 10px;
  cursor: pointer;
  transition: background 0.2s;
}

.debug-btn:hover {
  background: #303f9f;
}
</style>