<template>
  <div class="admin-revenue">
    <h1 class="title">收入管理</h1>
    
    <div class="summary-cards">
      <div class="summary-card">
        <div class="card-icon">
          <i class="fas fa-money-bill-wave"></i>
        </div>
        <div class="card-content">
          <div class="card-title">总收入</div>
          <div class="card-value">¥{{ formatNumber(totalRevenue) }}</div>
          <div class="card-trend positive">
            <i class="fas fa-arrow-up"></i> {{ revenueTrend }}% 较上月
          </div>
        </div>
      </div>
      
      <div class="summary-card">
        <div class="card-icon">
          <i class="fas fa-ticket-alt"></i>
        </div>
        <div class="card-content">
          <div class="card-title">机票销量</div>
          <div class="card-value">{{ formatNumber(ticketSales) }}</div>
          <div class="card-trend positive">
            <i class="fas fa-arrow-up"></i> {{ ticketSalesTrend }}% 较上月
          </div>
        </div>
      </div>
      
      <div class="summary-card">
        <div class="card-icon">
          <i class="fas fa-chart-line"></i>
        </div>
        <div class="card-content">
          <div class="card-title">平均票价</div>
          <div class="card-value">¥{{ averageTicketPrice }}</div>
          <div class="card-trend positive">
            <i class="fas fa-arrow-up"></i> {{ averagePriceTrend }}% 较上月
          </div>
        </div>
      </div>
      
      <div class="summary-card">
        <div class="card-icon">
          <i class="fas fa-percentage"></i>
        </div>
        <div class="card-content">
          <div class="card-title">毛利率</div>
          <div class="card-value">{{ grossMargin }}%</div>
          <div class="card-trend negative">
            <i class="fas fa-arrow-down"></i> {{ marginTrend }}% 较上月
          </div>
        </div>
      </div>
    </div>
    
    <div class="filter-section">
      <div class="date-filter">
        <select v-model="timeRange" @change="updateData">
          <option value="week">最近一周</option>
          <option value="month">本月</option>
          <option value="quarter">本季度</option>
          <option value="year">今年</option>
          <option value="custom">自定义</option>
        </select>
        
        <div v-if="timeRange === 'custom'" class="custom-date">
          <input type="date" v-model="customStartDate">
          <span>至</span>
          <input type="date" v-model="customEndDate">
          <button @click="updateData">应用</button>
        </div>
      </div>
      
      <div class="route-filter">
        <select v-model="routeFilter" @change="updateData">
          <option value="">所有航线</option>
          <option v-for="route in routes" :key="route.id" :value="route.id">
            {{ route.name }}
          </option>
        </select>
      </div>
      
      <div class="cabin-filter">
        <select v-model="cabinFilter" @change="updateData">
          <option value="">所有舱位</option>
          <option value="economy">经济舱</option>
          <option value="business">商务舱</option>
          <option value="first">头等舱</option>
        </select>
      </div>
      
      <div class="export-button">
        <button class="btn-export">
          <i class="fas fa-file-export"></i> 导出数据
        </button>
      </div>
    </div>
    
    <div class="chart-row">
      <div class="chart-card">
        <div class="card-header">
          <h2>收入趋势</h2>
          <div class="segmented-control">
            <button 
              v-for="option in chartViewOptions" 
              :key="option.value" 
              :class="['segment-button', { active: chartView === option.value }]"
              @click="chartView = option.value"
            >
              {{ option.label }}
            </button>
          </div>
        </div>
        <div class="chart-container revenue-chart">
          <!-- 在实际应用中这里应使用echarts或chart.js等图表库 -->
          <div class="mock-chart">
            <div class="mock-bars">
              <div 
                v-for="(item, index) in revenueData" 
                :key="index"
                class="mock-bar" 
                :style="{ height: (item.value / maxRevenue * 100) + '%' }"
              >
                <div class="bar-tooltip">¥{{ formatNumber(item.value) }}</div>
              </div>
            </div>
            <div class="chart-labels">
              <span v-for="(item, index) in revenueData" :key="'label-'+index">{{ item.label }}</span>
            </div>
          </div>
        </div>
      </div>
      
      <div class="chart-card">
        <div class="card-header">
          <h2>舱位收入分布</h2>
        </div>
        <div class="chart-container distribution-chart">
          <div class="pie-chart">
            <div class="pie-segments">
              <div 
                v-for="(segment, index) in cabinDistribution" 
                :key="index" 
                class="pie-segment"
                :style="getPieSegmentStyle(segment, index)"
              ></div>
            </div>
          </div>
          <div class="chart-legend">
            <div class="legend-item" v-for="(item, index) in cabinDistribution" :key="index">
              <div class="color-indicator" :style="{ backgroundColor: pieColors[index] }"></div>
              <div class="legend-label">{{ getCabinName(item.cabin) }}</div>
              <div class="legend-value">¥{{ formatNumber(item.value) }} ({{ item.percentage }}%)</div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div class="revenue-tables">
      <div class="table-header">
        <h2>航线收入详情</h2>
        <div class="table-actions">
          <div class="search-box">
            <input type="text" v-model="searchQuery" placeholder="搜索航线...">
            <i class="fas fa-search"></i>
          </div>
          <div class="sort-control">
            <label>排序：</label>
            <select v-model="sortBy">
              <option value="revenue">收入</option>
              <option value="tickets">票数</option>
              <option value="avgPrice">平均票价</option>
              <option value="growth">增长率</option>
            </select>
            <button class="sort-button" @click="toggleSortOrder">
              <i :class="sortOrder === 'asc' ? 'fas fa-sort-up' : 'fas fa-sort-down'"></i>
            </button>
          </div>
        </div>
      </div>
      
      <div class="table-container">
        <table class="revenue-table">
          <thead>
            <tr>
              <th>航线</th>
              <th>收入</th>
              <th>票数</th>
              <th>平均票价</th>
              <th>同期增长</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="route in sortedRouteRevenue" :key="route.id">
              <td>{{ route.name }}</td>
              <td class="value-cell">¥{{ formatNumber(route.revenue) }}</td>
              <td class="value-cell">{{ route.tickets }}</td>
              <td class="value-cell">¥{{ route.avgPrice }}</td>
              <td class="trend-cell" :class="getTrendClass(route.growth)">
                <i :class="route.growth >= 0 ? 'fas fa-arrow-up' : 'fas fa-arrow-down'"></i>
                {{ Math.abs(route.growth) }}%
              </td>
              <td class="action-cell">
                <button class="action-btn" @click="showRouteDetails(route.id)">
                  <i class="fas fa-chart-bar"></i> 详情
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <div class="pagination">
        <button class="page-btn" :disabled="currentPage === 1" @click="currentPage--">
          <i class="fas fa-chevron-left"></i>
        </button>
        <div class="page-info">{{ currentPage }} / {{ totalPages }}</div>
        <button class="page-btn" :disabled="currentPage === totalPages" @click="currentPage++">
          <i class="fas fa-chevron-right"></i>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AdminRevenueView',
  data() {
    return {
      totalRevenue: 3452980,
      revenueTrend: 8.5,
      ticketSales: 24856,
      ticketSalesTrend: 5.2,
      averageTicketPrice: 1389,
      averagePriceTrend: 3.1,
      grossMargin: 42.8,
      marginTrend: 1.2,
      
      timeRange: 'month',
      customStartDate: '',
      customEndDate: '',
      routeFilter: '',
      cabinFilter: '',
      
      chartView: 'monthly',
      chartViewOptions: [
        { label: '日视图', value: 'daily' },
        { label: '周视图', value: 'weekly' },
        { label: '月视图', value: 'monthly' }
      ],
      
      revenueData: [
        { label: '1月', value: 280000 },
        { label: '2月', value: 230000 },
        { label: '3月', value: 310000 },
        { label: '4月', value: 340000 },
        { label: '5月', value: 380000 },
        { label: '6月', value: 450000 },
        { label: '7月', value: 520000 },
        { label: '8月', value: 480000 }
      ],
      
      cabinDistribution: [
        { cabin: 'economy', value: 1960000, percentage: 56.8 },
        { cabin: 'business', value: 982000, percentage: 28.4 },
        { cabin: 'first', value: 510980, percentage: 14.8 }
      ],
      
      pieColors: ['#4CAF50', '#2196F3', '#FF9800'],
      
      routes: [
        { id: 1, name: '北京 - 上海' },
        { id: 2, name: '广州 - 北京' },
        { id: 3, name: '深圳 - 成都' },
        { id: 4, name: '上海 - 广州' },
        { id: 5, name: '成都 - 杭州' }
      ],
      
      routeRevenue: [
        { id: 1, name: '北京 - 上海', revenue: 980000, tickets: 7245, avgPrice: 1352, growth: 12.5 },
        { id: 2, name: '广州 - 北京', revenue: 750000, tickets: 5120, avgPrice: 1465, growth: 8.3 },
        { id: 3, name: '深圳 - 成都', revenue: 620000, tickets: 4560, avgPrice: 1360, growth: -2.1 },
        { id: 4, name: '上海 - 广州', revenue: 580000, tickets: 4210, avgPrice: 1378, growth: 5.7 },
        { id: 5, name: '成都 - 杭州', revenue: 522980, tickets: 3721, avgPrice: 1405, growth: 7.2 }
      ],
      
      searchQuery: '',
      sortBy: 'revenue',
      sortOrder: 'desc',
      currentPage: 1,
      itemsPerPage: 10
    }
  },
  computed: {
    maxRevenue() {
      return Math.max(...this.revenueData.map(item => item.value));
    },
    filteredRouteRevenue() {
      return this.routeRevenue.filter(route => {
        return route.name.toLowerCase().includes(this.searchQuery.toLowerCase());
      });
    },
    sortedRouteRevenue() {
      const sorted = [...this.filteredRouteRevenue].sort((a, b) => {
        let valA = a[this.sortBy];
        let valB = b[this.sortBy];
        
        if (this.sortOrder === 'asc') {
          return valA - valB;
        } else {
          return valB - valA;
        }
      });
      
      // 分页
      const start = (this.currentPage - 1) * this.itemsPerPage;
      const end = start + this.itemsPerPage;
      return sorted.slice(start, end);
    },
    totalPages() {
      return Math.ceil(this.filteredRouteRevenue.length / this.itemsPerPage);
    }
  },
  methods: {
    formatNumber(num) {
      return num.toLocaleString();
    },
    updateData() {
      console.log('更新数据：', {
        timeRange: this.timeRange,
        routeFilter: this.routeFilter,
        cabinFilter: this.cabinFilter
      });
      // 在实际应用中，这里应该调用API获取新的数据
    },
    getPieSegmentStyle(segment, index) {
      // 计算饼图分段的样式
      const color = this.pieColors[index % this.pieColors.length];
      
      // 计算分段的起始和结束角度
      let startPercent = 0;
      for (let i = 0; i < index; i++) {
        startPercent += this.cabinDistribution[i].percentage;
      }
      
      const startAngle = startPercent * 3.6; // 将百分比转换为角度
      const endAngle = startAngle + segment.percentage * 3.6;
      
      return {
        background: `conic-gradient(${color} ${startAngle}deg, ${color} ${endAngle}deg, transparent ${endAngle}deg)`
      };
    },
    getCabinName(cabinCode) {
      const names = {
        'economy': '经济舱',
        'business': '商务舱',
        'first': '头等舱'
      };
      return names[cabinCode] || cabinCode;
    },
    toggleSortOrder() {
      this.sortOrder = this.sortOrder === 'asc' ? 'desc' : 'asc';
    },
    getTrendClass(value) {
      return value >= 0 ? 'trend-up' : 'trend-down';
    },
    showRouteDetails(routeId) {
      console.log('查看航线详情:', routeId);
      // 在实际应用中，这里应该跳转到航线详情页或打开详情模态框
    }
  },
  mounted() {
    // 设置默认自定义日期为当前月份的第一天和最后一天
    const today = new Date();
    const firstDay = new Date(today.getFullYear(), today.getMonth(), 1);
    const lastDay = new Date(today.getFullYear(), today.getMonth() + 1, 0);
    
    this.customStartDate = firstDay.toISOString().split('T')[0];
    this.customEndDate = lastDay.toISOString().split('T')[0];
  }
}
</script>

<style scoped>
.admin-revenue {
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

.summary-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.summary-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 20px;
  display: flex;
  transition: transform 0.3s;
}

.summary-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.card-icon {
  background: rgba(63, 81, 181, 0.1);
  color: #3f51b5;
  width: 50px;
  height: 50px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  margin-right: 15px;
}

.summary-card:nth-child(2) .card-icon {
  background: rgba(76, 175, 80, 0.1);
  color: #4CAF50;
}

.summary-card:nth-child(3) .card-icon {
  background: rgba(33, 150, 243, 0.1);
  color: #2196F3;
}

.summary-card:nth-child(4) .card-icon {
  background: rgba(255, 152, 0, 0.1);
  color: #FF9800;
}

.card-content {
  flex: 1;
}

.card-title {
  color: #666;
  font-size: 14px;
  margin-bottom: 5px;
}

.card-value {
  font-size: 24px;
  font-weight: bold;
  color: #333;
  margin-bottom: 5px;
}

.card-trend {
  font-size: 14px;
  display: flex;
  align-items: center;
}

.card-trend.positive {
  color: #4CAF50;
}

.card-trend.negative {
  color: #F44336;
}

.card-trend i {
  margin-right: 5px;
}

.filter-section {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 15px;
  margin-bottom: 30px;
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  align-items: center;
}

.date-filter, .route-filter, .cabin-filter {
  display: flex;
  align-items: center;
  gap: 10px;
}

.date-filter select, .route-filter select, .cabin-filter select {
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background-color: white;
  min-width: 120px;
}

.custom-date {
  display: flex;
  align-items: center;
  gap: 10px;
}

.custom-date input {
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  width: 140px;
}

.custom-date button {
  padding: 8px 16px;
  background-color: #3f51b5;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.export-button {
  margin-left: auto;
}

.btn-export {
  padding: 8px 16px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
}

.chart-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 30px;
}

.chart-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.card-header h2 {
  font-size: 18px;
  color: #333;
  margin: 0;
}

.segmented-control {
  display: flex;
  border: 1px solid #ddd;
  border-radius: 4px;
  overflow: hidden;
}

.segment-button {
  padding: 6px 12px;
  background: #f5f5f5;
  border: none;
  cursor: pointer;
  font-size: 14px;
}

.segment-button:not(:last-child) {
  border-right: 1px solid #ddd;
}

.segment-button.active {
  background: #3f51b5;
  color: white;
}

.chart-container {
  height: 300px;
  position: relative;
}

.mock-chart {
  height: 250px;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
}

.mock-bars {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  height: 200px;
  width: 100%;
  padding-bottom: 20px;
}

.mock-bar {
  width: 40px;
  background-color: #3f51b5;
  border-radius: 4px 4px 0 0;
  position: relative;
  transition: height 0.3s;
}

.mock-bar:hover {
  background-color: #536dfe;
}

.mock-bar:hover .bar-tooltip {
  display: block;
}

.bar-tooltip {
  display: none;
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  white-space: nowrap;
  margin-bottom: 5px;
}

.chart-labels {
  display: flex;
  justify-content: space-between;
  margin-top: 10px;
}

.chart-labels span {
  width: 40px;
  text-align: center;
  font-size: 12px;
  color: #666;
}

.pie-chart {
  position: relative;
  width: 200px;
  height: 200px;
  margin: 0 auto;
}

.pie-segments {
  position: absolute;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  overflow: hidden;
}

.pie-segment {
  position: absolute;
  width: 100%;
  height: 100%;
}

.chart-legend {
  margin-top: 30px;
}

.legend-item {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}

.color-indicator {
  width: 16px;
  height: 16px;
  border-radius: 4px;
  margin-right: 10px;
}

.legend-label {
  flex: 1;
}

.legend-value {
  text-align: right;
  font-weight: 500;
}

.revenue-tables {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 20px;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.table-header h2 {
  font-size: 18px;
  color: #333;
  margin: 0;
}

.table-actions {
  display: flex;
  gap: 15px;
}

.search-box {
  position: relative;
}

.search-box input {
  padding: 8px 30px 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  min-width: 200px;
}

.search-box i {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  color: #666;
}

.sort-control {
  display: flex;
  align-items: center;
  gap: 8px;
}

.sort-control select {
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.sort-button {
  width: 32px;
  height: 32px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.table-container {
  overflow-x: auto;
}

.revenue-table {
  width: 100%;
  border-collapse: collapse;
}

.revenue-table th, .revenue-table td {
  padding: 12px 15px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.revenue-table th {
  font-weight: 600;
  color: #333;
  background-color: #f9f9f9;
}

.value-cell {
  text-align: right;
  font-weight: 500;
}

.trend-cell {
  display: flex;
  align-items: center;
  gap: 5px;
  font-weight: 500;
}

.trend-up {
  color: #4CAF50;
}

.trend-down {
  color: #F44336;
}

.action-cell {
  text-align: center;
}

.action-btn {
  padding: 6px 12px;
  background-color: #3f51b5;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 20px;
  gap: 15px;
}

.page-btn {
  width: 32px;
  height: 32px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.page-btn:disabled {
  color: #ccc;
  cursor: not-allowed;
}

.page-info {
  font-size: 14px;
  color: #666;
}

@media (max-width: 992px) {
  .chart-row {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .filter-section {
    flex-direction: column;
    align-items: stretch;
  }
  
  .export-button {
    margin-left: 0;
  }
  
  .table-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
  
  .table-actions {
    flex-direction: column;
    width: 100%;
  }
}
</style> 