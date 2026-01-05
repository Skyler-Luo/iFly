<template>
  <div class="reschedule-view">
    <div class="header-banner">
      <h1>机票改签</h1>
      <p class="subtitle">选择新航班完成改签</p>
    </div>

    <div class="reschedule-container">
      <!-- 步骤条 -->
      <el-steps :active="currentStep" finish-status="success" align-center class="steps-bar">
        <el-step title="选择航班" description="选择目标航班"></el-step>
        <el-step title="费用确认" description="确认改签费用"></el-step>
        <el-step title="改签完成" description="获取新机票"></el-step>
      </el-steps>

      <!-- 原机票信息 -->
      <div class="section-card original-ticket" v-if="originalTicket">
        <div class="section-title">
          <i class="el-icon-tickets"></i>
          <span>原机票信息</span>
        </div>
        <div class="ticket-info">
          <div class="info-row">
            <span class="label">航班号:</span>
            <span class="value">{{ originalTicket.flightNumber }}</span>
          </div>
          <div class="info-row">
            <span class="label">航线:</span>
            <span class="value">{{ originalTicket.departureCity }} → {{ originalTicket.arrivalCity }}</span>
          </div>
          <div class="info-row">
            <span class="label">出发时间:</span>
            <span class="value">{{ formatDateTime(originalTicket.departureTime) }}</span>
          </div>
          <div class="info-row">
            <span class="label">乘客:</span>
            <span class="value">{{ originalTicket.passengerName }}</span>
          </div>
          <div class="info-row">
            <span class="label">票价:</span>
            <span class="value price">¥{{ originalTicket.price.toFixed(2) }}</span>
          </div>
        </div>
      </div>

      <!-- 步骤1: 选择航班 -->
      <div class="step-content" v-if="currentStep === 0">
        <div class="section-card">
          <div class="section-title">
            <i class="el-icon-search"></i>
            <span>可改签航班</span>
          </div>
          
          <div v-if="isLoadingFlights" class="loading-container">
            <el-icon class="is-loading"><Loading /></el-icon>
            <span>正在加载可改签航班...</span>
          </div>

          <div v-else-if="availableFlights.length === 0" class="empty-container">
            <el-empty description="暂无可改签航班"></el-empty>
          </div>

          <div v-else class="flight-list">
            <div 
              v-for="flight in availableFlights" 
              :key="flight.id"
              class="flight-item"
              :class="{ selected: selectedFlight && selectedFlight.id === flight.id }"
              @click="selectFlight(flight)"
            >
              <div class="flight-header">
                <span class="flight-number">{{ flight.flightNumber }}</span>
                <span class="airline-name">{{ flight.airlineName }}</span>
              </div>
              <div class="flight-journey">
                <div class="departure">
                  <div class="time">{{ formatTime(flight.departureTime) }}</div>
                  <div class="city">{{ flight.departureCity }}</div>
                </div>
                <div class="direction">
                  <div class="line"></div>
                  <div class="duration">{{ formatDuration(flight.duration) }}</div>
                </div>
                <div class="arrival">
                  <div class="time">{{ formatTime(flight.arrivalTime) }}</div>
                  <div class="city">{{ flight.arrivalCity }}</div>
                </div>
              </div>
              <div class="flight-footer">
                <span class="date">{{ formatDate(flight.departureTime) }}</span>
                <span class="price">¥{{ flight.price.toFixed(2) }}</span>
                <span class="seats">余票: {{ flight.availableSeats }}</span>
              </div>
            </div>
          </div>

          <div class="step-actions">
            <el-button @click="goBack">返回</el-button>
            <el-button 
              type="primary" 
              :disabled="!selectedFlight"
              @click="goToPreview"
            >
              下一步
            </el-button>
          </div>
        </div>
      </div>

      <!-- 步骤2: 费用确认 -->
      <div class="step-content" v-if="currentStep === 1">
        <div class="section-card">
          <div class="section-title">
            <i class="el-icon-money"></i>
            <span>费用明细</span>
          </div>

          <div v-if="isLoadingPreview" class="loading-container">
            <el-icon class="is-loading"><Loading /></el-icon>
            <span>正在计算费用...</span>
          </div>

          <div v-else-if="feePreview" class="fee-preview">
            <div class="new-flight-info">
              <h4>新航班信息</h4>
              <div class="info-row">
                <span class="label">航班号:</span>
                <span class="value">{{ selectedFlight.flightNumber }}</span>
              </div>
              <div class="info-row">
                <span class="label">出发时间:</span>
                <span class="value">{{ formatDateTime(selectedFlight.departureTime) }}</span>
              </div>
            </div>

            <div class="fee-detail">
              <div class="fee-row">
                <span class="label">原票价:</span>
                <span class="value">¥{{ feePreview.originalPrice.toFixed(2) }}</span>
              </div>
              <div class="fee-row">
                <span class="label">新票价:</span>
                <span class="value">¥{{ feePreview.newPrice.toFixed(2) }}</span>
              </div>
              <div class="fee-row">
                <span class="label">改签手续费:</span>
                <span class="value">¥{{ feePreview.rescheduleFee.toFixed(2) }}</span>
              </div>
              <div class="fee-row highlight" v-if="feePreview.priceDifference > 0">
                <span class="label">需补差价:</span>
                <span class="value pay">¥{{ feePreview.totalToPay.toFixed(2) }}</span>
              </div>
              <div class="fee-row highlight" v-else-if="feePreview.priceDifference < 0">
                <span class="label">可退金额:</span>
                <span class="value refund">¥{{ feePreview.refundAmount.toFixed(2) }}</span>
              </div>
              <div class="fee-row highlight" v-else>
                <span class="label">费用变化:</span>
                <span class="value">无需补差价</span>
              </div>
            </div>
          </div>

          <div class="step-actions">
            <el-button @click="currentStep = 0">上一步</el-button>
            <el-button 
              type="primary" 
              :loading="isRescheduling"
              @click="executeReschedule"
            >
              确认改签
            </el-button>
          </div>
        </div>
      </div>

      <!-- 步骤3: 改签完成 -->
      <div class="step-content" v-if="currentStep === 2">
        <div class="section-card success-card">
          <div class="success-icon">
            <el-icon color="#67c23a" size="64"><CircleCheck /></el-icon>
          </div>
          <h2>改签成功</h2>
          <p class="success-message">您的机票已成功改签到新航班</p>

          <div class="new-ticket-info" v-if="newTicket">
            <div class="info-row">
              <span class="label">新票号:</span>
              <span class="value">{{ newTicket.ticketNumber }}</span>
            </div>
            <div class="info-row">
              <span class="label">航班号:</span>
              <span class="value">{{ newTicket.flightNumber }}</span>
            </div>
            <div class="info-row">
              <span class="label">座位号:</span>
              <span class="value">{{ newTicket.seatNumber }}</span>
            </div>
            <div class="info-row">
              <span class="label">乘客:</span>
              <span class="value">{{ newTicket.passengerName }}</span>
            </div>
          </div>

          <div class="step-actions">
            <el-button type="primary" @click="goToOrderDetail">
              查看订单详情
            </el-button>
            <el-button @click="goToOrderList">
              返回订单列表
            </el-button>
          </div>
        </div>
      </div>

      <!-- 错误状态 -->
      <div class="error-container" v-if="error">
        <el-alert :title="error" type="error" show-icon :closable="false"></el-alert>
        <el-button type="primary" @click="goBack" style="margin-top: 20px;">返回</el-button>
      </div>
    </div>
  </div>
</template>

<script>
import api from '@/services/api'
import { ElMessage } from 'element-plus'
import { Loading, CircleCheck } from '@element-plus/icons-vue'

export default {
  name: 'RescheduleView',
  components: {
    Loading,
    CircleCheck
  },
  data() {
    return {
      currentStep: 0,
      ticketId: null,
      orderId: null,
      originalTicket: null,
      availableFlights: [],
      selectedFlight: null,
      feePreview: null,
      newTicket: null,
      isLoadingFlights: false,
      isLoadingPreview: false,
      isRescheduling: false,
      error: null
    }
  },
  created() {
    this.ticketId = this.$route.params.ticketId
    this.orderId = this.$route.query.orderId
    this.fetchOriginalTicket()
    this.fetchAvailableFlights()
  },
  methods: {
    async fetchOriginalTicket() {
      try {
        const response = await api.tickets.getById(this.ticketId)
        const data = response.data || response
        this.originalTicket = {
          id: data.id,
          ticketNumber: data.ticket_number,
          flightNumber: data.flight_number,
          departureCity: data.departure_city,
          arrivalCity: data.arrival_city,
          departureTime: data.departure_time,
          passengerName: data.passenger_name,
          price: parseFloat(data.price) || 0
        }
      } catch (err) {
        console.error('获取原机票信息失败:', err)
        this.error = '获取机票信息失败'
      }
    },

    async fetchAvailableFlights() {
      this.isLoadingFlights = true
      this.error = null
      try {
        const response = await api.tickets.getAvailableFlights(this.ticketId)
        const data = response.data || response
        // 后端返回 { available_flights: [...], ticket_id, original_flight, count }
        const flights = data.available_flights || data.results || data || []
        this.availableFlights = flights.map(flight => ({
          id: flight.id,
          flightNumber: flight.flight_number,
          airlineName: flight.airline_name,
          departureCity: flight.departure_city,
          arrivalCity: flight.arrival_city,
          departureTime: flight.departure_time,
          arrivalTime: flight.arrival_time,
          duration: flight.duration,
          price: parseFloat(flight.economy_price || flight.price) || 0,
          availableSeats: flight.available_seats
        }))
      } catch (err) {
        console.error('获取可改签航班失败:', err)
        this.error = err.data?.detail || '获取可改签航班失败'
      } finally {
        this.isLoadingFlights = false
      }
    },

    selectFlight(flight) {
      this.selectedFlight = flight
    },

    async goToPreview() {
      if (!this.selectedFlight) return
      
      this.isLoadingPreview = true
      this.currentStep = 1
      this.error = null
      
      try {
        const response = await api.tickets.getReschedulePreview(this.ticketId, {
          new_flight_id: this.selectedFlight.id
        })
        const data = response.data || response
        // 后端返回 { fee_info: { original_price, new_price, ... }, ... }
        const feeInfo = data.fee_info || data
        this.feePreview = {
          originalPrice: parseFloat(feeInfo.original_price) || 0,
          newPrice: parseFloat(feeInfo.new_price) || 0,
          priceDifference: parseFloat(feeInfo.price_difference) || 0,
          rescheduleFee: parseFloat(feeInfo.reschedule_fee) || 0,
          totalToPay: parseFloat(feeInfo.total_to_pay) || 0,
          refundAmount: parseFloat(feeInfo.refund_amount) || 0
        }
      } catch (err) {
        console.error('获取费用预览失败:', err)
        this.error = err.data?.detail || '获取费用预览失败'
        this.currentStep = 0
      } finally {
        this.isLoadingPreview = false
      }
    },

    async executeReschedule() {
      this.isRescheduling = true
      this.error = null
      
      try {
        const response = await api.tickets.reschedule(this.ticketId, {
          new_flight_id: this.selectedFlight.id
        })
        const data = response.data || response
        
        this.newTicket = {
          id: data.new_ticket?.id || data.id,
          ticketNumber: data.new_ticket?.ticket_number || data.ticket_number,
          flightNumber: data.new_ticket?.flight_number || this.selectedFlight.flightNumber,
          seatNumber: data.new_ticket?.seat_number || data.seat_number || '--',
          passengerName: data.new_ticket?.passenger_name || this.originalTicket?.passengerName
        }
        
        this.currentStep = 2
        ElMessage.success('改签成功')
      } catch (err) {
        console.error('改签失败:', err)
        const errorMsg = err.data?.error || err.message || '改签失败，请稍后重试'
        ElMessage.error(errorMsg)
        this.error = errorMsg
      } finally {
        this.isRescheduling = false
      }
    },

    formatDate(dateStr) {
      if (!dateStr) return ''
      const d = new Date(dateStr)
      return `${d.getFullYear()}-${(d.getMonth() + 1).toString().padStart(2, '0')}-${d.getDate().toString().padStart(2, '0')}`
    },

    formatTime(dateStr) {
      if (!dateStr) return ''
      const d = new Date(dateStr)
      return `${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`
    },

    formatDateTime(dateStr) {
      return `${this.formatDate(dateStr)} ${this.formatTime(dateStr)}`
    },

    formatDuration(minutes) {
      if (!minutes) return ''
      const hours = Math.floor(minutes / 60)
      const mins = minutes % 60
      return `${hours}h${mins > 0 ? ` ${mins}m` : ''}`
    },

    goBack() {
      if (this.orderId) {
        this.$router.push(`/orders/${this.orderId}`)
      } else {
        this.$router.push('/orders')
      }
    },

    goToOrderDetail() {
      if (this.orderId) {
        this.$router.push(`/orders/${this.orderId}`)
      } else {
        this.$router.push('/orders')
      }
    },

    goToOrderList() {
      this.$router.push('/orders')
    }
  }
}
</script>


<style scoped>
.reschedule-view {
  min-height: 100vh;
  background-color: #f5f7fa;
}

.header-banner {
  background: linear-gradient(135deg, #1976d2 0%, #1565c0 100%);
  color: white;
  padding: 40px 20px;
  text-align: center;
}

.header-banner h1 {
  margin: 0 0 10px 0;
  font-size: 28px;
}

.header-banner .subtitle {
  margin: 0;
  opacity: 0.9;
}

.reschedule-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 20px;
}

.steps-bar {
  background: white;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.section-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #ebeef5;
}

.original-ticket .ticket-info {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
}

.info-row {
  display: flex;
  gap: 8px;
}

.info-row .label {
  color: #909399;
  min-width: 70px;
}

.info-row .value {
  color: #303133;
  font-weight: 500;
}

.info-row .value.price {
  color: #f56c6c;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  color: #909399;
}

.loading-container .is-loading {
  font-size: 32px;
  margin-bottom: 12px;
  animation: rotating 2s linear infinite;
}

@keyframes rotating {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.empty-container {
  padding: 40px;
}

.flight-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.flight-item {
  border: 2px solid #ebeef5;
  border-radius: 8px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.2s;
}

.flight-item:hover {
  border-color: #409eff;
  background-color: #f5f7fa;
}

.flight-item.selected {
  border-color: #409eff;
  background-color: #ecf5ff;
}

.flight-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 12px;
}

.flight-number {
  font-weight: 600;
  color: #303133;
}

.airline-name {
  color: #909399;
  font-size: 14px;
}

.flight-journey {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.departure, .arrival {
  text-align: center;
  min-width: 80px;
}

.departure .time, .arrival .time {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
}

.departure .city, .arrival .city {
  font-size: 14px;
  color: #606266;
}

.direction {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0 20px;
}

.direction .line {
  width: 100%;
  height: 2px;
  background: linear-gradient(90deg, #409eff 0%, #67c23a 100%);
  position: relative;
}

.direction .line::after {
  content: '→';
  position: absolute;
  right: -8px;
  top: -10px;
  color: #67c23a;
}

.direction .duration {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.flight-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 12px;
  border-top: 1px dashed #ebeef5;
}

.flight-footer .date {
  color: #909399;
  font-size: 14px;
}

.flight-footer .price {
  color: #f56c6c;
  font-size: 18px;
  font-weight: 600;
}

.flight-footer .seats {
  color: #67c23a;
  font-size: 14px;
}

.step-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}

.fee-preview {
  padding: 16px 0;
}

.new-flight-info {
  background: #f5f7fa;
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.new-flight-info h4 {
  margin: 0 0 12px 0;
  color: #303133;
}

.fee-detail {
  border: 1px solid #ebeef5;
  border-radius: 8px;
  overflow: hidden;
}

.fee-row {
  display: flex;
  justify-content: space-between;
  padding: 12px 16px;
  border-bottom: 1px solid #ebeef5;
}

.fee-row:last-child {
  border-bottom: none;
}

.fee-row.highlight {
  background: #fef0f0;
}

.fee-row .label {
  color: #606266;
}

.fee-row .value {
  font-weight: 500;
  color: #303133;
}

.fee-row .value.pay {
  color: #f56c6c;
  font-size: 18px;
}

.fee-row .value.refund {
  color: #67c23a;
  font-size: 18px;
}

.success-card {
  text-align: center;
  padding: 40px 20px;
}

.success-icon {
  margin-bottom: 20px;
}

.success-card h2 {
  margin: 0 0 12px 0;
  color: #303133;
}

.success-message {
  color: #909399;
  margin-bottom: 24px;
}

.new-ticket-info {
  background: #f0f9eb;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 24px;
  text-align: left;
  max-width: 400px;
  margin-left: auto;
  margin-right: auto;
}

.new-ticket-info .info-row {
  margin-bottom: 8px;
}

.new-ticket-info .info-row:last-child {
  margin-bottom: 0;
}

.error-container {
  text-align: center;
  padding: 20px;
}

@media (max-width: 768px) {
  .header-banner {
    padding: 30px 15px;
  }

  .header-banner h1 {
    font-size: 22px;
  }

  .reschedule-container {
    padding: 15px;
  }

  .original-ticket .ticket-info {
    grid-template-columns: 1fr;
  }

  .flight-journey {
    flex-direction: column;
    gap: 12px;
  }

  .direction {
    width: 100%;
    padding: 10px 0;
  }

  .direction .line {
    width: 60%;
  }
}
</style>
