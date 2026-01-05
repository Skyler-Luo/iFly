<template>
  <div class="seat-map">
    <!-- 加载状态 -->
    <div v-if="loading" class="loading">
      <el-icon class="is-loading"><Loading /></el-icon>
      <span>加载座位...</span>
    </div>

    <!-- 座位图 -->
    <div v-else class="cabin">
      <!-- 错误提示 -->
      <div v-if="loadError" class="error-tip">
        <el-icon><WarningFilled /></el-icon>
        <span>座位加载失败，显示默认布局</span>
      </div>

      <!-- 座位区域 -->
      <div class="seat-grid">
        <!-- 列标签 -->
        <div class="grid-row header">
          <span class="row-label"></span>
          <template v-for="(col, idx) in columns" :key="'h-' + col">
            <span v-if="isAislePosition(idx)" class="aisle"></span>
            <span class="col-label">{{ col }}</span>
          </template>
          <span class="row-label"></span>
        </div>

        <!-- 座位行 -->
        <div v-for="row in rows" :key="row" class="grid-row">
          <span class="row-label">{{ row }}</span>
          <template v-for="(col, idx) in columns" :key="row + col">
            <span v-if="isAislePosition(idx)" class="aisle"></span>
            <button
              class="seat"
              :class="getSeatClass(row, col)"
              :disabled="isSeatOccupied(row, col)"
              @click="selectSeat(row, col)"
              :title="getSeatTooltip(row, col)"
            >
              {{ col }}
            </button>
          </template>
          <span class="row-label">{{ row }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { Loading, WarningFilled } from '@element-plus/icons-vue'
import api from '@/services/api'
import { isAislePosition as calculateAislePosition } from '@/utils/aislePosition'

export default {
  name: 'CheckinSeatMap',
  components: { Loading, WarningFilled },
  props: {
    flightId: { type: [Number, String], required: true },
    currentSeat: { type: String, default: '' },
    cabinClass: { type: String, default: 'economy' },
    selectedSeat: { type: String, default: null }
  },
  emits: ['select-seat'],
  data() {
    return {
      loading: true,
      loadError: false,
      rows: [],
      columns: ['A', 'B', 'C', 'D', 'E', 'F'],
      occupiedSeats: [],
      defaultConfig: {
        economy: { start: 10, end: 30, cols: 6 },
        business: { start: 4, end: 9, cols: 4 },
        first: { start: 1, end: 3, cols: 4 }
      }
    }
  },
  created() { this.loadSeatMap() },
  watch: {
    flightId() { this.loadSeatMap() },
    cabinClass() { this.loadSeatMap() }
  },
  methods: {
    async loadSeatMap() {
      if (!this.flightId || this.flightId === 'undefined') {
        this.setupDefaultSeats()
        this.loading = false
        return
      }
      try {
        this.loading = true
        this.loadError = false
        const res = await api.flights.getAvailableSeats(this.flightId, { cabin_class: this.cabinClass })
        if (res?.seat_map && Array.isArray(res.seat_map)) {
          this.parseSeatMap(res)
        } else {
          this.setupDefaultSeats()
        }
        this.occupiedSeats = res?.occupied_seats || []
      } catch (err) {
        this.loadError = true
        this.setupDefaultSeats()
        this.occupiedSeats = []
      } finally {
        this.loading = false
      }
    },

    parseSeatMap(res) {
      const start = res.start_row || 1
      const end = res.end_row || res.rows || 30
      const colCount = res.columns || 6
      this.rows = Array.from({ length: end - start + 1 }, (_, i) => start + i)
      this.columns = Array.from({ length: colCount }, (_, i) => String.fromCharCode(65 + i))
    },

    setupDefaultSeats() {
      const cfg = this.defaultConfig[this.cabinClass] || this.defaultConfig.economy
      this.rows = Array.from({ length: cfg.end - cfg.start + 1 }, (_, i) => cfg.start + i)
      this.columns = cfg.cols === 6 ? ['A', 'B', 'C', 'D', 'E', 'F'] : ['A', 'B', 'D', 'E']
    },

    isAislePosition(index) { return calculateAislePosition(index, this.columns.length) },

    isSeatOccupied(row, col) {
      const seat = `${row}${col}`
      return seat !== this.currentSeat && this.occupiedSeats.includes(seat)
    },

    getSeatClass(row, col) {
      const seat = `${row}${col}`
      if (this.isSeatOccupied(row, col)) return 'occupied'
      if (this.selectedSeat === seat) return 'selected'
      if (this.currentSeat === seat && this.selectedSeat !== seat) return 'current'
      return 'available'
    },

    getSeatTooltip(row, col) {
      const seat = `${row}${col}`
      if (this.isSeatOccupied(row, col)) return `${seat} 已售`
      const pos = (col === 'A' || col === 'F') ? '靠窗' : (col === 'C' || col === 'D') ? '过道' : '中间'
      return `${seat} ${pos}`
    },

    selectSeat(row, col) {
      if (this.isSeatOccupied(row, col)) {
        this.$message.warning('该座位已被占用')
        return
      }
      this.$emit('select-seat', `${row}${col}`)
    }
  }
}
</script>

<style scoped>
.seat-map {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding: 12px;
  box-sizing: border-box;
}

.loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 40px 20px;
  color: #909399;
  width: 100%;
}

.cabin {
  width: 100%;
}

.error-tip {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 6px 10px;
  margin-bottom: 8px;
  background: #fef0f0;
  border-radius: 4px;
  font-size: 11px;
  color: #f56c6c;
}

/* 座位网格 */
.seat-grid {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
}

.grid-row {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 4px;
  width: 100%;
}
.grid-row.header {
  margin-bottom: 8px;
}

.row-label {
  width: 28px;
  font-size: 11px;
  color: #909399;
  text-align: center;
  flex-shrink: 0;
}

.col-label {
  width: 44px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  color: #606266;
  margin: 0 3px;
}

.aisle {
  width: 24px;
  flex-shrink: 0;
}

/* 座位按钮 - 真实座位样式 */
.seat {
  width: 44px;
  height: 48px;
  margin: 0 3px;
  border: none;
  border-radius: 8px 8px 4px 4px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s;
  position: relative;
  display: flex;
  align-items: flex-end;
  justify-content: center;
  padding-bottom: 4px;
  box-sizing: border-box;
  flex-shrink: 0;
}

/* 座椅靠背 */
.seat::before {
  content: '';
  position: absolute;
  top: 3px;
  left: 3px;
  right: 3px;
  height: 20px;
  border-radius: 6px 6px 2px 2px;
  background: inherit;
  filter: brightness(0.85);
}

/* 座椅扶手 */
.seat::after {
  content: '';
  position: absolute;
  bottom: 3px;
  left: 0;
  right: 0;
  height: 4px;
  background: rgba(0,0,0,0.1);
  border-radius: 0 0 4px 4px;
}

.seat.available {
  background: linear-gradient(180deg, #7ed56f 0%, #55c149 100%);
  color: #fff;
  box-shadow: 0 2px 4px rgba(85, 193, 73, 0.3);
}
.seat.available:hover {
  background: linear-gradient(180deg, #95e085 0%, #67d45a 100%);
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(85, 193, 73, 0.4);
}

.seat.selected {
  background: linear-gradient(180deg, #66b1ff 0%, #409eff 100%);
  color: #fff;
  transform: translateY(-2px);
  box-shadow: 0 4px 10px rgba(64, 158, 255, 0.5);
}

.seat.current {
  background: linear-gradient(180deg, #f5c06d 0%, #e6a23c 100%);
  color: #fff;
  box-shadow: 0 2px 4px rgba(230, 162, 60, 0.3);
}

.seat.occupied {
  background: linear-gradient(180deg, #e8e8e8 0%, #d5d5d5 100%);
  color: #b0b0b0;
  cursor: not-allowed;
  box-shadow: none;
}

/* 响应式 - 小屏幕 */
@media (max-width: 500px) {
  .seat { width: 32px; height: 36px; font-size: 10px; margin: 0 2px; }
  .seat::before { height: 14px; }
  .col-label { width: 32px; font-size: 10px; margin: 0 2px; }
  .aisle { width: 14px; }
  .row-label { width: 20px; font-size: 10px; }
}

/* 大屏幕 - 座位更大 */
@media (min-width: 800px) {
  .seat { width: 50px; height: 54px; font-size: 13px; margin: 0 4px; }
  .seat::before { height: 22px; }
  .col-label { width: 50px; font-size: 13px; margin: 0 4px; }
  .aisle { width: 28px; }
  .row-label { width: 32px; font-size: 12px; }
  .grid-row { margin-bottom: 5px; }
}

@media (min-width: 1200px) {
  .seat { width: 56px; height: 60px; font-size: 14px; margin: 0 5px; }
  .seat::before { height: 24px; }
  .col-label { width: 56px; font-size: 14px; margin: 0 5px; }
  .aisle { width: 32px; }
  .row-label { width: 36px; font-size: 13px; }
  .grid-row { margin-bottom: 6px; }
}
</style>
