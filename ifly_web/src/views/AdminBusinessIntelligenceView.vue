<template>
  <div class="business-intelligence">
    <div class="page-header">
      <h1>商务智能中心</h1>
      <div class="header-actions">
        <el-button type="primary" @click="exportReport">
          <i class="fas fa-file-export"></i> 导出报表
        </el-button>
      </div>
    </div>

    <!-- 航线收益分析 -->
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card class="bi-card">
          <div class="card-header">
            <h2>航线收益分析</h2>
            <div class="card-actions">
              <el-radio-group
                v-model="routeMetric"
                size="small"
                @change="fetchRouteAnalysis"
              >
                <el-radio-button value="revenue">收入</el-radio-button>
                <el-radio-button value="profit">利润</el-radio-button>
                <el-radio-button value="roi">ROI</el-radio-button>
              </el-radio-group>
            </div>
          </div>
          <div class="chart-container" style="height: 380px">
            <v-chart :option="routeProfitOption" autoresize />
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 多维度分析 - Requirements 7.1-7.6 -->
    <el-row :gutter="20" class="mt-20">
      <el-col :span="24">
        <el-card class="bi-card">
          <div class="card-header">
            <h2>多维度数据分析</h2>
          </div>

          <!-- 维度选择器 - Requirements 3.1-3.4, 7.1 -->
          <div class="dimension-selectors">
            <div class="selector-group">
              <span class="selector-label">分析维度：</span>
              <el-checkbox-group v-model="selectedDimensions" size="small">
                <el-checkbox-button value="time">时间</el-checkbox-button>
                <el-checkbox-button value="route">航线</el-checkbox-button>
                <el-checkbox-button value="cabin_class"
                  >舱位</el-checkbox-button
                >
                <el-checkbox-button value="user_segment"
                  >用户分群</el-checkbox-button
                >
              </el-checkbox-group>
            </div>

            <div class="selector-group">
              <span class="selector-label">时间粒度：</span>
              <el-select
                v-model="timeGranularity"
                size="small"
                style="width: 100px"
                :disabled="!selectedDimensions.includes('time')"
              >
                <el-option label="日" value="day" />
                <el-option label="周" value="week" />
                <el-option label="月" value="month" />
                <el-option label="季度" value="quarter" />
                <el-option label="年" value="year" />
              </el-select>
            </div>

            <div class="selector-group">
              <span class="selector-label">日期范围：</span>
              <el-date-picker
                v-model="dateRange"
                type="daterange"
                range-separator="至"
                start-placeholder="开始日期"
                end-placeholder="结束日期"
                size="small"
                value-format="YYYY-MM-DD"
                style="width: 260px"
              />
            </div>

            <div class="selector-group">
              <span class="selector-label">指标：</span>
              <el-checkbox-group v-model="selectedMetrics" size="small">
                <el-checkbox-button value="revenue">收入</el-checkbox-button>
                <el-checkbox-button value="order_count"
                  >订单数</el-checkbox-button
                >
                <el-checkbox-button value="avg_price">均价</el-checkbox-button>
              </el-checkbox-group>
            </div>

            <el-button
              type="primary"
              size="small"
              @click="fetchMultiDimensionAnalysis"
              :loading="analysisLoading"
            >
              <i class="el-icon-search"></i> 分析
            </el-button>
          </div>

          <!-- 图表类型切换 - Requirements 7.2, 7.4 -->
          <div class="chart-type-selector">
            <el-radio-group
              v-model="chartType"
              size="small"
              @change="updateAnalysisChart"
            >
              <el-radio-button value="bar">柱状图</el-radio-button>
              <el-radio-button value="line">折线图</el-radio-button>
              <el-radio-button value="pie">饼图</el-radio-button>
            </el-radio-group>
          </div>

          <!-- ECharts 图表 - Requirements 7.2 -->
          <div class="chart-container" style="height: 400px">
            <div v-if="analysisLoading" class="chart-loading">
              <el-icon class="is-loading"
                ><i class="el-icon-loading"></i
              ></el-icon>
              <span>加载中...</span>
            </div>
            <div v-else-if="analysisError" class="chart-no-data">
              <el-empty :description="analysisError" />
            </div>
            <div v-else-if="!hasAnalysisData" class="chart-no-data">
              <el-empty description="请选择维度和指标后点击分析" />
            </div>
            <v-chart
              v-else
              ref="analysisChart"
              :option="analysisChartOption"
              autoresize
            />
          </div>

          <!-- 数据表格 - Requirements 7.5 -->
          <div class="data-table-section" v-if="hasAnalysisData">
            <div class="table-header">
              <h3>分析结果明细</h3>
              <div class="table-actions">
                <!-- 导出功能 - Requirements 7.6 -->
                <el-button size="small" @click="exportCSV">
                  <i class="el-icon-download"></i> 导出 CSV
                </el-button>
                <el-button size="small" @click="exportChart">
                  <i class="el-icon-picture"></i> 导出图表
                </el-button>
              </div>
            </div>
            <el-table
              :data="analysisTableData"
              stripe
              border
              style="width: 100%"
              max-height="300"
            >
              <el-table-column
                v-for="col in analysisTableColumns"
                :key="col.prop"
                :prop="col.prop"
                :label="col.label"
                :width="col.width"
                :formatter="col.formatter"
              />
            </el-table>
            <div class="table-footer">
              <span>共 {{ analysisData.length }} 条记录</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 趋势分析 - Requirements 5.1-5.5 -->
    <el-row :gutter="20" class="mt-20">
      <el-col :span="24">
        <el-card class="bi-card">
          <div class="card-header">
            <h2>趋势分析与预测</h2>
            <div class="card-actions">
              <el-button
                size="small"
                @click="fetchTrends"
                :loading="trendsLoading"
              >
                <i class="el-icon-refresh"></i> 刷新
              </el-button>
            </div>
          </div>
          <div class="chart-container" style="height: 350px">
            <div v-if="trendsLoading" class="chart-loading">
              <el-icon class="is-loading"
                ><i class="el-icon-loading"></i
              ></el-icon>
              <span>加载中...</span>
            </div>
            <div v-else-if="!hasTrendsData" class="chart-no-data">
              <el-empty description="暂无趋势数据" />
            </div>
            <v-chart v-else :option="trendsChartOption" autoresize />
          </div>
          <!-- 季节性模式 -->
          <div
            v-if="seasonalPatterns && seasonalPatterns.peak_month"
            class="seasonal-info"
          >
            <el-alert type="info" :closable="false">
              <template #title>
                <span
                  >季节性分析：旺季为
                  {{ seasonalPatterns.peak_month }} 月，淡季为
                  {{ seasonalPatterns.low_month }} 月</span
                >
              </template>
            </el-alert>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
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
      // 航线分析
      routeMetric: 'revenue',
      routeData: {
        routes: [],
        revenue: [],
        profit: [],
        roi: []
      },

      // 多维度分析 - Requirements 3.1-3.7, 7.1-7.6
      selectedDimensions: ['time'],
      timeGranularity: 'month',
      dateRange: [],
      selectedMetrics: ['revenue', 'order_count'],
      chartType: 'bar',
      analysisData: [],
      analysisLoading: false,
      analysisError: null,

      // 趋势分析 - Requirements 5.1-5.5
      trendsData: [],
      seasonalPatterns: null,
      trendsLoading: false
    }
  },
  computed: {
    // 航线收益图表配置
    routeProfitOption() {
      const metricData = this.routeData[this.routeMetric] || []
      const metricName =
        this.routeMetric === 'revenue'
          ? '收入'
          : this.routeMetric === 'profit'
          ? '利润'
          : 'ROI'
      const formatter = this.routeMetric === 'roi' ? '{c}%' : '¥{c}'

      return {
        tooltip: {
          trigger: 'axis',
          axisPointer: { type: 'shadow' },
          formatter: this.routeMetric === 'roi' ? '{b}: {c}%' : '{b}: ¥{c}'
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: this.routeData.routes || [],
          axisLabel: { interval: 0, rotate: 30 }
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
              color: params => {
                const colorList = [
                  '#3f51b5',
                  '#4caf50',
                  '#ff9800',
                  '#9c27b0',
                  '#f44336'
                ]
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

    // 检查是否有分析数据
    hasAnalysisData() {
      return this.analysisData && this.analysisData.length > 0
    },

    // 多维度分析图表配置 - Requirements 7.2, 7.4
    analysisChartOption() {
      if (!this.hasAnalysisData) {
        return {
          title: {
            text: '暂无数据',
            left: 'center',
            top: 'center',
            textStyle: { color: '#999', fontSize: 14 }
          }
        }
      }

      const data = this.analysisData

      // 根据图表类型返回不同配置
      if (this.chartType === 'pie') {
        return this.buildPieChartOption(data)
      } else {
        return this.buildBarLineChartOption(data)
      }
    },

    // 分析结果表格列配置 - Requirements 7.5
    analysisTableColumns() {
      const columns = []

      // 根据选择的维度添加列
      if (this.selectedDimensions.includes('time')) {
        columns.push({ prop: 'time_period', label: '时间', width: 120 })
      }
      if (this.selectedDimensions.includes('route')) {
        columns.push({
          prop: 'tickets__flight__departure_city',
          label: '出发城市',
          width: 100
        })
        columns.push({
          prop: 'tickets__flight__arrival_city',
          label: '到达城市',
          width: 100
        })
      }
      if (this.selectedDimensions.includes('cabin_class')) {
        columns.push({
          prop: 'tickets__cabin_class',
          label: '舱位',
          width: 80,
          formatter: row => this.formatCabinClass(row.tickets__cabin_class)
        })
      }
      if (this.selectedDimensions.includes('user_segment')) {
        columns.push({
          prop: 'user_segment',
          label: '用户分群',
          width: 100,
          formatter: row => this.formatUserSegment(row.user_segment)
        })
      }

      // 根据选择的指标添加列
      if (this.selectedMetrics.includes('revenue')) {
        columns.push({
          prop: 'revenue',
          label: '收入',
          width: 120,
          formatter: row => this.formatCurrency(row.revenue)
        })
      }
      if (this.selectedMetrics.includes('order_count')) {
        columns.push({ prop: 'order_count', label: '订单数', width: 80 })
      }
      if (this.selectedMetrics.includes('avg_price')) {
        columns.push({
          prop: 'avg_price',
          label: '均价',
          width: 100,
          formatter: row => this.formatCurrency(row.avg_price)
        })
      }

      return columns
    },

    // 表格数据
    analysisTableData() {
      return this.analysisData || []
    },

    // 检查是否有趋势数据
    hasTrendsData() {
      return this.trendsData && this.trendsData.length > 0
    },

    // 趋势分析图表配置 - Requirements 5.1-5.5
    trendsChartOption() {
      if (!this.hasTrendsData) {
        return {}
      }

      const data = this.trendsData
      const periods = data.map(d => d.time_period || d.period || '')
      const revenues = data.map(d => d.revenue || 0)
      const movingAverages = data.map(d => d.moving_average || null)

      return {
        tooltip: {
          trigger: 'axis',
          formatter: params => {
            let result = params[0].axisValue + '<br/>'
            params.forEach(p => {
              if (p.value !== null && p.value !== undefined) {
                result += `${p.marker} ${
                  p.seriesName
                }: ¥${p.value.toLocaleString()}<br/>`
              }
            })
            const item = data[params[0].dataIndex]
            if (item && item.is_anomaly) {
              result += '<span style="color: #f56c6c">⚠ 异常数据点</span>'
            }
            return result
          }
        },
        legend: {
          data: ['收入', '移动平均']
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: periods,
          axisLabel: { rotate: 30 }
        },
        yAxis: {
          type: 'value',
          name: '收入 (¥)',
          axisLabel: {
            formatter: value => '¥' + (value / 10000).toFixed(0) + '万'
          }
        },
        series: [
          {
            name: '收入',
            type: 'bar',
            data: revenues,
            itemStyle: {
              color: params => {
                const item = data[params.dataIndex]
                return item && item.is_anomaly ? '#f56c6c' : '#409eff'
              }
            }
          },
          {
            name: '移动平均',
            type: 'line',
            data: movingAverages,
            smooth: true,
            lineStyle: { color: '#67c23a', width: 2 },
            itemStyle: { color: '#67c23a' }
          }
        ]
      }
    }
  },
  methods: {
    // 构建柱状图/折线图配置
    buildBarLineChartOption(data) {
      // 获取 X 轴数据
      let xAxisData = []
      if (this.selectedDimensions.includes('time')) {
        xAxisData = data.map(d => d.time_period || '')
      } else if (this.selectedDimensions.includes('route')) {
        xAxisData = data.map(
          d =>
            `${d.tickets__flight__departure_city || ''}-${
              d.tickets__flight__arrival_city || ''
            }`
        )
      } else if (this.selectedDimensions.includes('cabin_class')) {
        xAxisData = data.map(d => this.formatCabinClass(d.tickets__cabin_class))
      } else if (this.selectedDimensions.includes('user_segment')) {
        xAxisData = data.map(d => this.formatUserSegment(d.user_segment))
      }

      // 构建系列数据
      const series = []
      if (this.selectedMetrics.includes('revenue')) {
        series.push({
          name: '收入',
          type: this.chartType,
          data: data.map(d => d.revenue || 0),
          itemStyle: { color: '#409eff' }
        })
      }
      if (this.selectedMetrics.includes('order_count')) {
        series.push({
          name: '订单数',
          type: this.chartType,
          yAxisIndex: 1,
          data: data.map(d => d.order_count || 0),
          itemStyle: { color: '#67c23a' }
        })
      }
      if (this.selectedMetrics.includes('avg_price')) {
        series.push({
          name: '均价',
          type: this.chartType,
          data: data.map(d => d.avg_price || 0),
          itemStyle: { color: '#e6a23c' }
        })
      }

      return {
        tooltip: {
          trigger: 'axis',
          axisPointer: { type: 'shadow' }
        },
        legend: {
          data: series.map(s => s.name)
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: xAxisData,
          axisLabel: { rotate: 30 }
        },
        yAxis: [
          {
            type: 'value',
            name: '金额 (¥)',
            axisLabel: { formatter: '¥{value}' }
          },
          {
            type: 'value',
            name: '订单数',
            position: 'right',
            show: this.selectedMetrics.includes('order_count')
          }
        ],
        series: series
      }
    },

    // 构建饼图配置
    buildPieChartOption(data) {
      const metric = this.selectedMetrics[0] || 'revenue'
      const metricName =
        metric === 'revenue'
          ? '收入'
          : metric === 'order_count'
          ? '订单数'
          : '均价'

      let pieData = []
      if (this.selectedDimensions.includes('route')) {
        pieData = data.map(d => ({
          name: `${d.tickets__flight__departure_city || ''}-${
            d.tickets__flight__arrival_city || ''
          }`,
          value: d[metric] || 0
        }))
      } else if (this.selectedDimensions.includes('cabin_class')) {
        pieData = data.map(d => ({
          name: this.formatCabinClass(d.tickets__cabin_class),
          value: d[metric] || 0
        }))
      } else if (this.selectedDimensions.includes('user_segment')) {
        pieData = data.map(d => ({
          name: this.formatUserSegment(d.user_segment),
          value: d[metric] || 0
        }))
      } else {
        pieData = data.map((d, i) => ({
          name: d.time_period || `项目${i + 1}`,
          value: d[metric] || 0
        }))
      }

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
            name: metricName,
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
              formatter: '{b}: {d}%'
            },
            data: pieData
          }
        ]
      }
    },

    // 格式化舱位
    formatCabinClass(value) {
      const map = {
        economy: '经济舱',
        business: '商务舱',
        first: '头等舱'
      }
      return map[value] || value || '-'
    },

    // 格式化用户分群
    formatUserSegment(value) {
      const map = {
        new: '新用户',
        returning: '回头客',
        vip: 'VIP用户'
      }
      return map[value] || value || '-'
    },

    // 格式化货币
    formatCurrency(value) {
      if (value === null || value === undefined) return '-'
      return (
        '¥' +
        Number(value).toLocaleString('zh-CN', { minimumFractionDigits: 2 })
      )
    },

    // 获取航线分析数据
    async fetchRouteAnalysis() {
      try {
        // 获取所有三种指标的数据
        const [revenueRes, profitRes, roiRes] = await Promise.all([
          api.admin.analytics.getRouteAnalytics({ metric: 'revenue' }),
          api.admin.analytics.getRouteAnalytics({ metric: 'profit' }),
          api.admin.analytics.getRouteAnalytics({ metric: 'roi' })
        ])

        // 转换数据格式
        if (revenueRes && revenueRes.route_data) {
          this.routeData = {
            routes: revenueRes.route_data.map(item => item.route),
            revenue: revenueRes.route_data.map(item => item.value),
            profit: profitRes?.route_data?.map(item => item.value) || [],
            roi: roiRes?.route_data?.map(item => item.value) || []
          }
        }
      } catch (error) {
        /* error-handling */ console.error('获取航线分析数据失败:', error)
      }
    },

    // 获取多维度分析数据 - Requirements 3.1-3.7, 7.3
    async fetchMultiDimensionAnalysis() {
      if (this.selectedDimensions.length === 0) {
        ElMessage.warning('请至少选择一个分析维度')
        return
      }
      if (this.selectedMetrics.length === 0) {
        ElMessage.warning('请至少选择一个指标')
        return
      }

      this.analysisLoading = true
      this.analysisError = null

      try {
        const params = {
          dimensions: this.selectedDimensions,
          metrics: this.selectedMetrics,
          time_granularity: this.timeGranularity
        }

        if (this.dateRange && this.dateRange.length === 2) {
          params.start_date = this.dateRange[0]
          params.end_date = this.dateRange[1]
        }

        const response = await api.admin.analytics.getMultiDimensionAnalysis(
          params
        )

        if (response && response.data) {
          this.analysisData = response.data
          if (this.analysisData.length === 0) {
            this.analysisError = '没有符合条件的数据'
          }
        } else {
          this.analysisData = []
          this.analysisError = '数据暂无'
        }
      } catch (error) {
        /* error-handling */ console.error('获取多维度分析数据失败:', error)
        this.analysisError = '获取数据失败，请稍后重试'
        this.analysisData = []
      } finally {
        this.analysisLoading = false
      }
    },

    // 更新分析图表
    updateAnalysisChart() {
      // 图表会通过 computed 属性自动更新
    },

    // 获取趋势分析数据 - Requirements 5.1-5.5
    async fetchTrends() {
      this.trendsLoading = true

      try {
        const params = {}
        if (this.dateRange && this.dateRange.length === 2) {
          params.start_date = this.dateRange[0]
          params.end_date = this.dateRange[1]
        }

        const response = await api.admin.analytics.getTrends(params)

        if (response) {
          this.trendsData = response.trend_data || []
          this.seasonalPatterns = response.seasonal_patterns || null
        }
      } catch (error) {
        /* error-handling */ console.error('获取趋势分析数据失败:', error)
        this.trendsData = []
        this.seasonalPatterns = null
      } finally {
        this.trendsLoading = false
      }
    },

    // 导出 CSV - Requirements 7.6
    exportCSV() {
      if (!this.hasAnalysisData) {
        ElMessage.warning('没有可导出的数据')
        return
      }

      // 构建 CSV 内容
      const headers = this.analysisTableColumns.map(col => col.label)
      const rows = this.analysisData.map(row => {
        return this.analysisTableColumns.map(col => {
          const value = row[col.prop]
          if (col.prop === 'revenue' || col.prop === 'avg_price') {
            return value || 0
          }
          if (col.prop === 'tickets__cabin_class') {
            return this.formatCabinClass(value)
          }
          if (col.prop === 'user_segment') {
            return this.formatUserSegment(value)
          }
          return value || ''
        })
      })

      let csvContent = '\uFEFF' // BOM for UTF-8
      csvContent += headers.join(',') + '\n'
      rows.forEach(row => {
        csvContent += row.map(cell => `"${cell}"`).join(',') + '\n'
      })

      // 下载文件
      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
      const link = document.createElement('a')
      link.href = URL.createObjectURL(blob)
      link.download = `多维度分析_${new Date().toISOString().slice(0, 10)}.csv`
      link.click()
      URL.revokeObjectURL(link.href)

      ElMessage.success('CSV 导出成功')
    },

    // 导出图表 - Requirements 7.6
    exportChart() {
      const chartRef = this.$refs.analysisChart
      if (!chartRef) {
        ElMessage.warning('图表未加载')
        return
      }

      try {
        const url = chartRef.chart.getDataURL({
          type: 'png',
          pixelRatio: 2,
          backgroundColor: '#fff'
        })

        const link = document.createElement('a')
        link.href = url
        link.download = `多维度分析图表_${new Date()
          .toISOString()
          .slice(0, 10)}.png`
        link.click()

        ElMessage.success('图表导出成功')
      } catch (error) {
        /* error-handling */ console.error('导出图表失败:', error)
        ElMessage.error('导出图表失败')
      }
    },

    // 导出报表
    exportReport() {
      ElMessage.info('报表导出功能开发中')
    },

    // 初始化数据
    async initData() {
      await Promise.all([this.fetchRouteAnalysis(), this.fetchTrends()])
    }
  },
  mounted() {
    this.initData()
  }
}
</script>

<style scoped>
.business-intelligence {
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

.mt-20 {
  margin-top: 20px;
}

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

.card-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

/* 维度选择器样式 - Requirements 7.1 */
.dimension-selectors {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 15px;
  padding: 15px;
  background: #f5f7fa;
  border-radius: 6px;
  margin-bottom: 15px;
}

.selector-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.selector-label {
  font-size: 13px;
  color: #606266;
  white-space: nowrap;
}

/* 图表类型选择器 */
.chart-type-selector {
  margin-bottom: 15px;
  text-align: center;
}

.chart-container {
  width: 100%;
}

.chart-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #909399;
}

.chart-loading .is-loading {
  font-size: 32px;
  margin-bottom: 10px;
}

.chart-no-data {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
}

/* 数据表格区域 - Requirements 7.5 */
.data-table-section {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #eee;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.table-header h3 {
  font-size: 14px;
  margin: 0;
  color: #333;
}

.table-actions {
  display: flex;
  gap: 10px;
}

.table-footer {
  margin-top: 10px;
  text-align: right;
  font-size: 12px;
  color: #909399;
}

/* 季节性信息 */
.seasonal-info {
  margin-top: 15px;
}

/* 响应式调整 */
@media (max-width: 1200px) {
  .dimension-selectors {
    flex-direction: column;
    align-items: flex-start;
  }

  .selector-group {
    width: 100%;
  }
}
</style>
