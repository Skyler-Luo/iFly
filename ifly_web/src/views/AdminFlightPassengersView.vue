<template>
  <div class="admin-flight-passengers">
    <h1 class="title">航班乘客管理</h1>

    <!-- 加载状态 -->
    <div v-if="isLoading" class="loading-container">
      <i class="fas fa-spinner fa-spin"></i>
      <span>加载中...</span>
    </div>

    <!-- 错误提示 -->
    <div v-else-if="error" class="error-container">
      <i class="fas fa-exclamation-circle"></i>
      <span>{{ error }}</span>
      <button class="btn btn-primary" @click="retryLoad">重新加载</button>
    </div>

    <!-- 航班不存在提示 -->
    <div v-else-if="!flight" class="empty-container">
      <i class="fas fa-plane-slash"></i>
      <span>航班信息不存在</span>
    </div>

    <!-- 正常内容 -->
    <template v-else>
      <div class="flight-info">
        <div class="flight-header">
          <div class="flight-number">
            <strong>航班号：</strong> {{ flight.flightNumber }}
          </div>
          <div class="flight-route">
            <span>{{ flight.departureCity }}</span>
            <i class="fas fa-arrow-right"></i>
            <span>{{ flight.arrivalCity }}</span>
          </div>
          <div class="flight-date">
            <strong>日期：</strong> {{ formatDate(flight.departureTime) }}
          </div>
        </div>
        <div class="flight-details">
          <div class="detail-item">
            <div class="label">起飞时间</div>
            <div class="value">{{ formatTime(flight.departureTime) }}</div>
          </div>
          <div class="detail-item">
            <div class="label">到达时间</div>
            <div class="value">{{ formatTime(flight.arrivalTime) }}</div>
          </div>
          <div class="detail-item">
            <div class="label">飞行时间</div>
            <div class="value">{{ flight.duration }}</div>
          </div>
          <div class="detail-item">
            <div class="label">飞机型号</div>
            <div class="value">{{ flight.aircraft }}</div>
          </div>
          <div class="detail-item">
            <div class="label">机票总数</div>
            <div class="value">{{ flight.totalSeats }}</div>
          </div>
          <div class="detail-item">
            <div class="label">已售票数</div>
            <div class="value">{{ flight.soldSeats }}</div>
          </div>
        </div>
      </div>

      <div class="passenger-filters">
        <div class="search-box">
          <input
            type="text"
            v-model="searchQuery"
            placeholder="搜索乘客姓名/身份证号/手机号"
          />
          <button><i class="fas fa-search"></i></button>
        </div>

        <div class="filter-group">
          <select v-model="cabinFilter">
            <option value="">所有舱位</option>
            <option value="economy">经济舱</option>
            <option value="business">商务舱</option>
            <option value="first">头等舱</option>
          </select>
        </div>

        <div class="filter-group">
          <select v-model="checkinFilter">
            <option value="">所有状态</option>
            <option value="checked">已值机</option>
            <option value="not_checked">未值机</option>
          </select>
        </div>

        <div class="export-btn">
          <button class="btn btn-secondary">
            <i class="fas fa-download"></i> 导出乘客名单
          </button>
        </div>
      </div>

      <!-- 暂无乘客提示 -->
      <div v-if="passengers.length === 0" class="empty-passengers">
        <i class="fas fa-users-slash"></i>
        <span>暂无乘客</span>
      </div>

      <template v-else>
        <div class="passenger-table">
          <table>
            <thead>
              <tr>
                <th>座位号</th>
                <th>姓名</th>
                <th>身份证号</th>
                <th>手机号码</th>
                <th>舱位等级</th>
                <th>值机状态</th>
                <th>特殊服务</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="passenger in filteredPassengers" :key="passenger.id">
                <td>{{ passenger.seatNumber || '-' }}</td>
                <td>{{ passenger.name }}</td>
                <td>{{ passenger.idNumber }}</td>
                <td>{{ passenger.phone }}</td>
                <td>
                  <span :class="getCabinClass(passenger.cabinClass)">
                    {{ getCabinName(passenger.cabinClass) }}
                  </span>
                </td>
                <td>
                  <span :class="getCheckinStatus(passenger.checkedIn)">
                    {{ passenger.checkedIn ? '已值机' : '未值机' }}
                  </span>
                </td>
                <td>{{ passenger.specialService || '无' }}</td>
                <td>
                  <button
                    class="action-btn edit-btn"
                    @click="editPassenger(passenger)"
                  >
                    <i class="fas fa-edit"></i>
                  </button>
                  <button
                    class="action-btn checkin-btn"
                    @click="toggleCheckin(passenger)"
                    :disabled="passenger.checkedIn"
                  >
                    <i class="fas fa-check-square"></i>
                  </button>
                  <button
                    class="action-btn remove-btn"
                    @click="removePassenger(passenger)"
                  >
                    <i class="fas fa-trash"></i>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="pagination">
          <button
            class="prev-btn"
            :disabled="currentPage === 1"
            @click="currentPage--"
          >
            <i class="fas fa-chevron-left"></i>
          </button>
          <div class="page-info">{{ currentPage }} / {{ totalPages }}</div>
          <button
            class="next-btn"
            :disabled="currentPage === totalPages"
            @click="currentPage++"
          >
            <i class="fas fa-chevron-right"></i>
          </button>
        </div>
      </template>
    </template>
  </div>
</template>

<script>
import api from '@/services/api'
import { ElMessage } from 'element-plus'

export default {
  name: 'AdminFlightPassengersView',
  data() {
    return {
      searchQuery: '',
      cabinFilter: '',
      checkinFilter: '',
      currentPage: 1,
      perPage: 10,
      isLoading: false,
      error: null,
      flight: null,
      passengers: []
    }
  },
  computed: {
    filteredPassengers() {
      let result = [...this.passengers]

      // 应用搜索过滤
      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase()
        result = result.filter(
          p =>
            p.name.toLowerCase().includes(query) ||
            p.idNumber.includes(query) ||
            p.phone.includes(query)
        )
      }

      // 应用舱位过滤
      if (this.cabinFilter) {
        result = result.filter(p => p.cabinClass === this.cabinFilter)
      }

      // 应用值机状态过滤
      if (this.checkinFilter === 'checked') {
        result = result.filter(p => p.checkedIn)
      } else if (this.checkinFilter === 'not_checked') {
        result = result.filter(p => !p.checkedIn)
      }

      return result
    },
    totalPages() {
      return Math.max(
        1,
        Math.ceil(this.filteredPassengers.length / this.perPage)
      )
    }
  },
  created() {
    // 从路由参数获取航班ID
    const flightId = this.$route.params.flightId
    this.loadFlightData(flightId)
  },
  methods: {
    formatDate(dateString) {
      if (!dateString) return '-'
      const date = new Date(dateString)
      return date.toLocaleDateString('zh-CN')
    },
    formatTime(dateString) {
      if (!dateString) return '-'
      const date = new Date(dateString)
      return date.toLocaleTimeString('zh-CN', {
        hour: '2-digit',
        minute: '2-digit'
      })
    },
    getCabinClass(cabin) {
      const classes = {
        economy: 'cabin-economy',
        business: 'cabin-business',
        first: 'cabin-first'
      }
      return classes[cabin] || ''
    },
    getCabinName(cabin) {
      const names = {
        economy: '经济舱',
        business: '商务舱',
        first: '头等舱'
      }
      return names[cabin] || cabin
    },
    getCheckinStatus(isCheckedIn) {
      return isCheckedIn ? 'status-checked' : 'status-not-checked'
    },
    // 计算飞行时长
    calculateDuration(departureTime, arrivalTime) {
      if (!departureTime || !arrivalTime) return '-'
      const dep = new Date(departureTime)
      const arr = new Date(arrivalTime)
      const diffMs = arr - dep
      const hours = Math.floor(diffMs / (1000 * 60 * 60))
      const minutes = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60))
      return `${hours}小时${minutes}分钟`
    },
    // 转换航班数据为页面显示格式
    transformFlightData(flightData) {
      return {
        id: flightData.id,
        flightNumber: flightData.flight_number,
        departureCity: flightData.departure_city,
        departureAirport: flightData.departure_airport,
        arrivalCity: flightData.arrival_city,
        arrivalAirport: flightData.arrival_airport,
        departureTime: flightData.departure_time,
        arrivalTime: flightData.arrival_time,
        duration: this.calculateDuration(
          flightData.departure_time,
          flightData.arrival_time
        ),
        aircraft: flightData.aircraft_type,
        totalSeats:
          flightData.total_seats ||
          flightData.seat_rows * flightData.seats_per_row ||
          0,
        soldSeats: flightData.booked_seats || 0
      }
    },
    // 转换机票数据为乘客显示格式
    transformTicketsToPassengers(tickets) {
      return tickets.map(ticket => {
        // 从 passenger_info 嵌套对象或直接字段获取乘客信息
        const passengerInfo = ticket.passenger_info || {}

        // 获取乘客姓名：优先从 passenger_info，其次从直接字段
        const name = passengerInfo.name || ticket.passenger_name || '-'

        // 获取证件号码：优先从 passenger_info.id_card，其次从 passenger_id_number
        const idNumber =
          passengerInfo.id_card || ticket.passenger_id_number || '-'

        // 获取联系电话：从订单联系人信息获取（机票本身不存储手机号）
        const phone = ticket.contact_phone || '-'

        return {
          id: ticket.id,
          name: name,
          idNumber: idNumber,
          phone: phone,
          cabinClass: ticket.cabin_class || 'economy',
          checkedIn: ticket.checked_in || false,
          seatNumber: ticket.seat_number || null,
          specialService: ticket.special_service || null,
          ticketId: ticket.id,
          // 保留额外信息供后续使用
          ticketNumber: ticket.ticket_number || null,
          ticketStatus: ticket.status || 'valid',
          orderId: ticket.order_id || ticket.order || null,
          orderNumber: ticket.order_number || null
        }
      })
    },
    async loadFlightData(flightId) {
      if (!flightId) {
        this.error = '航班ID无效'
        return
      }

      this.isLoading = true
      this.error = null

      try {
        // 获取航班信息
        const flightResponse = await api.flights.getDetail(flightId)
        this.flight = this.transformFlightData(flightResponse)

        // 获取该航班的机票（乘客）列表
        const ticketsResponse = await api.tickets.getAll({ flight: flightId })
        const ticketsData = ticketsResponse.results || ticketsResponse || []
        this.passengers = this.transformTicketsToPassengers(ticketsData)
      } catch (err) {
        console.error('加载航班乘客数据失败:', err)
        this.error = err.message || '加载数据失败，请稍后重试'
        this.flight = null
        this.passengers = []
      } finally {
        this.isLoading = false
      }
    },
    retryLoad() {
      const flightId = this.$route.params.flightId
      this.loadFlightData(flightId)
    },
    editPassenger(passenger) {
      // 编辑乘客信息的逻辑
      console.log('编辑乘客:', passenger)
      ElMessage.info('编辑功能开发中')
    },
    async toggleCheckin(passenger) {
      // 切换值机状态的逻辑
      try {
        await api.tickets.checkin(passenger.ticketId, {})
        passenger.checkedIn = true
        ElMessage.success('值机成功')
      } catch (err) {
        console.error('值机失败:', err)
        ElMessage.error(err.message || '值机失败，请稍后重试')
      }
    },
    removePassenger(passenger) {
      // 删除乘客的逻辑
      if (confirm(`确定要移除乘客 ${passenger.name} 吗？`)) {
        console.log('移除乘客:', passenger)
        const index = this.passengers.findIndex(p => p.id === passenger.id)
        if (index !== -1) {
          this.passengers.splice(index, 1)
        }
        ElMessage.success('乘客已移除')
      }
    }
  }
}
</script>

<style scoped>
.admin-flight-passengers {
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
.error-container,
.empty-container,
.empty-passengers {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  color: #666;
}

.loading-container i,
.error-container i,
.empty-container i,
.empty-passengers i {
  font-size: 48px;
  margin-bottom: 16px;
  color: #999;
}

.error-container i {
  color: #f44336;
}

.error-container .btn {
  margin-top: 16px;
}

.btn-primary {
  background: #3f51b5;
  color: white;
}

.btn-primary:hover {
  background: #303f9f;
}

.flight-info {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 15px;
  margin-bottom: 20px;
}

.flight-header {
  display: flex;
  justify-content: space-between;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
}

.flight-route {
  display: flex;
  align-items: center;
  font-size: 18px;
  font-weight: bold;
}

.flight-route i {
  margin: 0 10px;
  color: #3f51b5;
}

.flight-details {
  display: flex;
  flex-wrap: wrap;
  margin-top: 10px;
}

.detail-item {
  flex: 1 1 30%;
  min-width: 150px;
  margin: 5px 0;
}

.detail-item .label {
  font-size: 12px;
  color: #666;
}

.detail-item .value {
  font-weight: bold;
}

.passenger-filters {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  margin-bottom: 20px;
  align-items: center;
}

.search-box {
  flex: 1;
  min-width: 250px;
  position: relative;
}

.search-box input {
  width: 100%;
  padding: 8px 30px 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.search-box button {
  position: absolute;
  right: 0;
  top: 0;
  height: 100%;
  width: 30px;
  background: transparent;
  border: none;
  cursor: pointer;
}

.filter-group select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: white;
}

.export-btn {
  margin-left: auto;
}

.btn {
  padding: 8px 16px;
  border-radius: 4px;
  border: none;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
}

.btn i {
  margin-right: 8px;
}

.btn-secondary {
  background: #f5f5f5;
  color: #333;
}

.btn-secondary:hover {
  background: #e0e0e0;
}

.passenger-table {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.passenger-table table {
  width: 100%;
  border-collapse: collapse;
}

.passenger-table th {
  background: #f9f9f9;
  padding: 12px 15px;
  text-align: left;
  font-weight: 600;
  color: #333;
}

.passenger-table td {
  padding: 12px 15px;
  border-top: 1px solid #eee;
}

.cabin-economy {
  background: #e3f2fd;
  color: #1565c0;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.cabin-business {
  background: #e8f5e9;
  color: #2e7d32;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.cabin-first {
  background: #fff8e1;
  color: #ff6f00;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.status-checked {
  color: #4caf50;
  font-weight: bold;
}

.status-not-checked {
  color: #f44336;
}

.action-btn {
  width: 28px;
  height: 28px;
  border-radius: 4px;
  border: none;
  margin-right: 5px;
  cursor: pointer;
  transition: all 0.2s;
}

.edit-btn {
  background: #e3f2fd;
  color: #1565c0;
}

.edit-btn:hover {
  background: #bbdefb;
}

.checkin-btn {
  background: #e8f5e9;
  color: #2e7d32;
}

.checkin-btn:hover {
  background: #c8e6c9;
}

.checkin-btn:disabled {
  background: #f5f5f5;
  color: #999;
  cursor: not-allowed;
}

.remove-btn {
  background: #ffebee;
  color: #c62828;
}

.remove-btn:hover {
  background: #ffcdd2;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 20px;
}

.pagination button {
  width: 32px;
  height: 32px;
  border-radius: 4px;
  background: white;
  border: 1px solid #ddd;
  color: #333;
  cursor: pointer;
}

.pagination button:disabled {
  color: #ccc;
  cursor: not-allowed;
}

.pagination .page-info {
  margin: 0 10px;
}

@media (max-width: 768px) {
  .flight-header {
    flex-direction: column;
    gap: 10px;
  }

  .passenger-filters {
    flex-direction: column;
    align-items: stretch;
  }

  .export-btn {
    margin-left: 0;
  }
}
</style>
