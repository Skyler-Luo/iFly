<template>
  <div class="checkin-page">
    <!-- 加载状态 -->
    <div v-if="isLoading" class="loading-state">
      <el-icon class="is-loading"><Loading /></el-icon>
      <span>正在加载...</span>
    </div>

    <!-- 错误状态 -->
    <div v-else-if="error" class="error-state">
      <el-icon><CircleClose /></el-icon>
      <p>{{ error }}</p>
      <el-button @click="goBack">返回订单列表</el-button>
    </div>

    <!-- 主内容 -->
    <div v-else-if="ticket.ticket_id" class="main-content">
      <!-- 顶部：航班信息条 -->
      <div class="flight-bar">
        <div class="flight-info">
          <div class="route">
            <span class="city">{{ ticket.departure_city }}</span>
            <span class="code">{{ getCityCode(ticket.departure_city) }}</span>
            <span class="time">{{ formatTime(ticket.departure_time) }}</span>
          </div>
          <div class="arrow">
            <span class="flight-no">{{ ticket.flight_number }}</span>
            <el-icon><Right /></el-icon>
          </div>
          <div class="route">
            <span class="city">{{ ticket.arrival_city }}</span>
            <span class="code">{{ getCityCode(ticket.arrival_city) }}</span>
            <span class="time">{{ formatTime(ticket.arrival_time) }}</span>
          </div>
        </div>
        <div class="passenger-info">
          <div class="info-item">
            <span class="label">乘客</span>
            <span class="value">{{ ticket.passenger_name }}</span>
          </div>
          <div class="info-item">
            <span class="label">舱位</span>
            <span class="value">{{ getCabinLabel(ticket.cabin_class) }}</span>
          </div>
          <div class="info-item seat-display">
            <span class="label">座位</span>
            <span class="value">{{ selectedSeat || ticket.current_seat || '未选' }}</span>
          </div>
        </div>
        <div class="status-tag">
          <el-tag :type="ticket.checked_in ? 'success' : 'warning'" size="large">
            {{ ticket.checked_in ? '已值机' : '待值机' }}
          </el-tag>
        </div>
      </div>

      <!-- 座位选择区域 -->
      <div v-if="!ticket.checked_in && !showBoardingPass" class="seat-section">
        <div class="seat-header">
          <span class="title">选择座位</span>
          <div class="legend">
            <span class="item"><i class="dot available"></i>可选</span>
            <span class="item"><i class="dot selected"></i>已选</span>
            <span class="item"><i class="dot current"></i>当前</span>
            <span class="item"><i class="dot occupied"></i>已售</span>
          </div>
        </div>
        <div class="seat-area">
          <checkin-seat-map
            :flight-id="ticket.flight_id"
            :current-seat="ticket.current_seat"
            :cabin-class="ticket.cabin_class"
            :selected-seat="selectedSeat"
            @select-seat="onSeatSelect"
          />
        </div>
        <div class="action-bar">
          <el-button type="primary" size="large" @click="confirmCheckin" :loading="submitting" :disabled="!selectedSeat && !ticket.current_seat">
            确认值机
          </el-button>
        </div>
      </div>

      <!-- 登机牌 -->
      <div v-if="showBoardingPass && boardingPass.boarding_pass_number" class="pass-section">
        <div class="success-banner">
          <el-icon><CircleCheck /></el-icon>
          <span>值机成功</span>
        </div>

        <div class="boarding-pass">
          <div class="pass-header">
            <span class="airline">iFly航空</span>
            <span class="title">BOARDING PASS</span>
          </div>
          
          <div class="pass-route">
            <div class="from">
              <span class="code">{{ getCityCode(boardingPass.departure_city) }}</span>
              <span class="name">{{ boardingPass.departure_city }}</span>
            </div>
            <el-icon class="arrow"><Right /></el-icon>
            <div class="to">
              <span class="code">{{ getCityCode(boardingPass.arrival_city) }}</span>
              <span class="name">{{ boardingPass.arrival_city }}</span>
            </div>
          </div>

          <div class="pass-details">
            <div class="detail-row">
              <div class="field">
                <span class="label">PASSENGER</span>
                <span class="value">{{ boardingPass.passenger_name }}</span>
              </div>
              <div class="field">
                <span class="label">FLIGHT</span>
                <span class="value">{{ boardingPass.flight_number }}</span>
              </div>
              <div class="field">
                <span class="label">DATE</span>
                <span class="value">{{ formatDate(boardingPass.departure_time) }}</span>
              </div>
            </div>
            <div class="detail-row highlight">
              <div class="field large">
                <span class="label">SEAT</span>
                <span class="value">{{ boardingPass.seat_number }}</span>
              </div>
              <div class="field large">
                <span class="label">GATE</span>
                <span class="value">{{ boardingPass.gate }}</span>
              </div>
              <div class="field">
                <span class="label">BOARDING</span>
                <span class="value">{{ formatTime(boardingPass.boarding_time) }}</span>
              </div>
            </div>
          </div>

          <div class="pass-footer">
            <div class="barcode"></div>
            <span class="number">{{ boardingPass.boarding_pass_number }}</span>
          </div>
        </div>

        <div class="action-bar">
          <el-button type="primary" @click="printPass"><el-icon><Download /></el-icon>打印</el-button>
          <el-button @click="goBack">返回订单</el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { CircleCheck, CircleClose, Download, Loading, Right } from '@element-plus/icons-vue'
import api from '@/services/api'
import CheckinSeatMap from '@/components/CheckinSeatMap.vue'

export default {
  name: 'CheckinView',
  components: { Loading, CircleClose, CircleCheck, Right, Download, CheckinSeatMap },
  data() {
    return {
      isLoading: true,
      error: null,
      ticket: {},
      selectedSeat: null,
      submitting: false,
      showBoardingPass: false,
      boardingPass: {},
      currentTicketId: null  // 存储当前机票ID
    }
  },
  created() {
    this.initCheckin()
  },
  methods: {
    async initCheckin() {
      const ticketId = this.$route.params.ticketId
      const query = this.$route.query
      
      if (ticketId) {
        // 直接通过 ticketId 加载（从订单页面跳转）
        this.currentTicketId = ticketId
        await this.loadCheckinInfo(ticketId)
      } else if (query.ticketNo && query.idNumber) {
        // 通过票号和证件号搜索（从首页搜索跳转）
        await this.searchTicket(query)
      } else {
        this.isLoading = false
        this.error = '未找到机票信息，请检查输入的票号和证件号'
      }
    },

    async searchTicket(query) {
      try {
        this.isLoading = true
        this.error = null
        
        const response = await api.tickets.searchForCheckin({
          ticket_number: query.ticketNo,
          id_number: query.idNumber,
          passenger_name: query.name || undefined,
          flight_number: query.flightNo || undefined
        })
        
        // 搜索成功，获取 ticketId 并加载值机信息
        this.currentTicketId = response.ticket_id
        
        if (response.checked_in) {
          // 已值机，加载登机牌
          await this.loadBoardingPass(response.ticket_id)
        } else {
          // 未值机，加载值机信息
          await this.loadCheckinInfo(response.ticket_id)
        }
      } catch (err) {
        this.isLoading = false
        this.error = err.data?.detail || err.message || '搜索机票失败，请检查票号和证件号'
      }
    },

    async loadCheckinInfo(ticketId) {
      try {
        this.isLoading = true
        this.error = null
        const response = await api.tickets.getCheckinInfo(ticketId)
        this.ticket = {
          ticket_id: response.ticket_id,
          ticket_number: response.ticket_number,
          passenger_name: response.passenger_name,
          flight_id: response.flight_id,
          flight_number: response.flight_number,
          departure_city: response.departure_city,
          arrival_city: response.arrival_city,
          departure_time: response.departure_time,
          arrival_time: response.arrival_time,
          current_seat: response.current_seat,
          cabin_class: response.cabin_class,
          checked_in: response.checked_in
        }
        this.selectedSeat = response.current_seat
      } catch (err) {
        if (err.data?.checked_in) {
          await this.loadBoardingPass(ticketId)
        } else {
          this.error = err.data?.detail || '加载值机信息失败'
        }
      } finally {
        this.isLoading = false
      }
    },

    async loadBoardingPass(ticketId) {
      try {
        const response = await api.tickets.getBoardingPass(ticketId)
        if (response.boarding_pass) {
          this.boardingPass = response.boarding_pass
          this.showBoardingPass = true
        }
      } catch (err) {
        this.error = '加载登机牌失败'
      }
    },

    onSeatSelect(seat) {
      this.selectedSeat = seat
    },

    async confirmCheckin() {
      try {
        this.submitting = true
        const ticketId = this.currentTicketId || this.$route.params.ticketId
        const seatToUse = this.selectedSeat || this.ticket.current_seat
        const response = await api.tickets.checkin(ticketId, { seat_number: seatToUse })
        if (response.success) {
          this.boardingPass = response.boarding_pass
          this.showBoardingPass = true
          this.$message.success('值机成功！')
        }
      } catch (err) {
        this.$message.error(err.data?.detail || '值机失败')
      } finally {
        this.submitting = false
      }
    },

    printPass() { window.print() },
    goBack() { this.$router.push('/orders') },

    formatTime(dateStr) {
      if (!dateStr) return '--:--'
      return new Date(dateStr).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
    },
    formatDate(dateStr) {
      if (!dateStr) return ''
      return new Date(dateStr).toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit' })
    },
    getCabinLabel(c) {
      return { economy: '经济舱', business: '商务舱', first: '头等舱' }[c] || c
    },
    getCityCode(city) {
      const codes = { 北京: 'PEK', 上海: 'SHA', 广州: 'CAN', 深圳: 'SZX', 成都: 'CTU', 杭州: 'HGH', 武汉: 'WUH', 西安: 'XIY', 重庆: 'CKG', 南京: 'NKG' }
      return codes[city] || city?.substring(0, 3).toUpperCase() || 'XXX'
    }
  }
}
</script>

<style scoped>
.checkin-page {
  width: 100%;
  flex: 1;
  background: #f0f2f5;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
}

/* 加载/错误状态 */
.loading-state, .error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex: 1;
  padding: 60px 20px;
  color: #909399;
}
.loading-state .el-icon, .error-state .el-icon { font-size: 48px; margin-bottom: 16px; }
.error-state .el-icon { color: #f56c6c; }
.error-state p { margin: 0 0 16px; color: #606266; }

/* 主内容 */
.main-content {
  display: flex;
  flex-direction: column;
  flex: 1;
}

/* 顶部航班信息条 */
.flight-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 24px;
  background: linear-gradient(135deg, #409eff 0%, #337ecc 100%);
  color: #fff;
  gap: 24px;
}

.flight-info {
  display: flex;
  align-items: center;
  gap: 16px;
}

.flight-info .route {
  text-align: center;
}
.flight-info .route .city {
  display: block;
  font-size: 14px;
  opacity: 0.9;
}
.flight-info .route .code {
  display: block;
  font-size: 24px;
  font-weight: 700;
}
.flight-info .route .time {
  display: block;
  font-size: 13px;
  opacity: 0.85;
}

.flight-info .arrow {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0 8px;
}
.flight-info .arrow .flight-no {
  font-size: 11px;
  opacity: 0.8;
  margin-bottom: 2px;
}
.flight-info .arrow .el-icon {
  font-size: 18px;
}

.passenger-info {
  display: flex;
  gap: 24px;
}
.passenger-info .info-item {
  text-align: center;
}
.passenger-info .label {
  display: block;
  font-size: 11px;
  opacity: 0.7;
  margin-bottom: 2px;
}
.passenger-info .value {
  font-size: 15px;
  font-weight: 500;
}
.passenger-info .seat-display .value {
  font-size: 20px;
  font-weight: 700;
  color: #ffd700;
}

.status-tag {
  flex-shrink: 0;
}

/* 座位选择区域 */
.seat-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
  background: #fff;
}

.seat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 24px;
  border-bottom: 1px solid #ebeef5;
}
.seat-header .title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}
.seat-header .legend {
  display: flex;
  gap: 16px;
}
.seat-header .legend .item {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  color: #606266;
}
.seat-header .legend .dot {
  width: 14px;
  height: 14px;
  border-radius: 3px;
}
.dot.available { background: linear-gradient(180deg, #7ed56f 0%, #55c149 100%); }
.dot.selected { background: linear-gradient(180deg, #66b1ff 0%, #409eff 100%); }
.dot.current { background: linear-gradient(180deg, #f5c06d 0%, #e6a23c 100%); }
.dot.occupied { background: linear-gradient(180deg, #e8e8e8 0%, #d5d5d5 100%); }

.seat-area {
  flex: 1;
  overflow: auto;
  padding: 16px;
}

.action-bar {
  padding: 12px 24px;
  border-top: 1px solid #ebeef5;
  text-align: center;
  background: #fafafa;
}

/* 登机牌区域 */
.pass-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 24px;
  background: #fff;
}

.success-banner {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: linear-gradient(135deg, #f0f9eb 0%, #e1f3d8 100%);
  border-radius: 8px;
  color: #67c23a;
  font-weight: 500;
  margin-bottom: 20px;
}
.success-banner .el-icon { font-size: 20px; }

.boarding-pass {
  width: 100%;
  max-width: 420px;
  border: 1px solid #e4e7ed;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
  margin-bottom: 20px;
}
.pass-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 16px;
  background: linear-gradient(135deg, #409eff 0%, #337ecc 100%);
  color: #fff;
}
.pass-header .airline { font-weight: 600; font-size: 14px; }
.pass-header .title { font-size: 11px; opacity: 0.9; }

.pass-route {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 24px;
  padding: 16px;
  border-bottom: 1px dashed #e4e7ed;
}
.pass-route .from, .pass-route .to { text-align: center; }
.pass-route .code { display: block; font-size: 24px; font-weight: 700; color: #409eff; }
.pass-route .name { font-size: 11px; color: #909399; }
.pass-route .arrow { color: #c0c4cc; font-size: 18px; }

.pass-details { padding: 12px 16px; }
.detail-row { display: flex; gap: 12px; margin-bottom: 10px; }
.detail-row:last-child { margin-bottom: 0; }
.detail-row .field { flex: 1; }
.detail-row .field .label { display: block; font-size: 9px; color: #909399; margin-bottom: 2px; text-transform: uppercase; }
.detail-row .field .value { font-size: 13px; color: #303133; font-weight: 500; }
.detail-row.highlight { background: #f0f9ff; margin: 0 -16px; padding: 10px 16px; }
.detail-row .field.large .value { font-size: 22px; font-weight: 700; color: #409eff; }

.pass-footer {
  padding: 10px 16px;
  background: #fafafa;
  border-top: 1px dashed #e4e7ed;
  text-align: center;
}
.pass-footer .barcode {
  height: 32px;
  background: repeating-linear-gradient(90deg, #303133 0 2px, transparent 2px 4px);
  max-width: 180px;
  margin: 0 auto 6px;
}
.pass-footer .number { font-size: 10px; color: #909399; font-family: monospace; }

/* 响应式 */
@media (max-width: 768px) {
  .flight-bar {
    flex-direction: column;
    gap: 12px;
    padding: 12px 16px;
  }
  .passenger-info { gap: 16px; }
  .seat-header { flex-direction: column; gap: 8px; }
}

/* 打印样式 */
@media print {
  .checkin-page { background: #fff; }
  .flight-bar, .seat-section, .success-banner, .action-bar { display: none !important; }
  .pass-section { padding: 0; }
  .boarding-pass { box-shadow: none; border: 2px solid #000; max-width: 100%; }
}
</style>
