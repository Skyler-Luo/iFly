<template>
  <div class="admin-flight-pricing">
    <h1 class="title">航班票价管理</h1>

    <!-- 加载状态 -->
    <div v-if="isLoading" class="loading-container">
      <i class="el-icon-loading"></i>
      <span>正在加载航班数据...</span>
    </div>

    <!-- 错误提示 -->
    <div v-else-if="error" class="error-container">
      <i class="el-icon-warning"></i>
      <span>{{ error }}</span>
      <el-button type="primary" size="small" @click="retryLoad">
        重新加载
      </el-button>
    </div>

    <!-- 航班不存在提示 -->
    <div v-else-if="!flight" class="empty-container">
      <i class="el-icon-info"></i>
      <span>航班信息不存在</span>
      <el-button type="primary" size="small" @click="goBack">
        返回列表
      </el-button>
    </div>

    <!-- 航班信息 -->
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
        </div>
      </div>

      <div class="pricing-container">
        <div class="pricing-header">
          <h2>舱位价格设置</h2>
          <div class="currency-select">
            <label>货币单位:</label>
            <select v-model="selectedCurrency">
              <option value="CNY">人民币 (¥)</option>
              <option value="USD">美元 ($)</option>
              <option value="EUR">欧元 (€)</option>
            </select>
          </div>
        </div>

        <div class="cabin-pricing">
          <div
            v-for="(cabin, index) in cabinPricing"
            :key="index"
            class="cabin-class"
          >
            <div class="cabin-header">
              <h3>{{ getCabinName(cabin.type) }}</h3>
              <span class="seat-count">
                可售座位数: {{ cabin.availableSeats }}/{{ cabin.totalSeats }}
              </span>
            </div>

            <div class="price-settings">
              <div class="price-group">
                <label>基础票价</label>
                <div class="price-input">
                  <span class="currency-symbol">{{ getCurrencySymbol() }}</span>
                  <input
                    v-model="cabin.basePrice"
                    type="number"
                    min="0"
                    step="10"
                  />
                </div>
              </div>

              <div class="price-group">
                <label>当前售价</label>
                <div class="price-input">
                  <span class="currency-symbol">{{ getCurrencySymbol() }}</span>
                  <input
                    v-model="cabin.currentPrice"
                    type="number"
                    min="0"
                    step="10"
                  />
                </div>
              </div>

              <div class="price-group">
                <div class="slider-header">
                  <label>折扣率</label>
                  <span class="discount-value">
                    {{ calculateDiscount(cabin) }}%
                  </span>
                </div>
                <input
                  v-model="cabin.discountPct"
                  type="range"
                  min="0"
                  max="100"
                  step="5"
                  class="discount-slider"
                  @input="updateCurrentPrice(cabin)"
                />
              </div>
            </div>

            <div class="pricing-options">
              <div class="option">
                <label class="checkbox">
                  <input v-model="cabin.specialMeal" type="checkbox" />
                  <span></span>
                  特殊餐食 (+¥{{ cabin.specialMealPrice }})
                </label>
              </div>

              <div class="option">
                <label class="checkbox">
                  <input v-model="cabin.extraLegroom" type="checkbox" />
                  <span></span>
                  加大腿部空间 (+¥{{ cabin.extraLegroomPrice }})
                </label>
              </div>

              <div class="option">
                <label class="checkbox">
                  <input v-model="cabin.priorityBoarding" type="checkbox" />
                  <span></span>
                  优先登机 (+¥{{ cabin.priorityBoardingPrice }})
                </label>
              </div>
            </div>

            <div class="baggage-allowance">
              <h4>行李额度设置</h4>
              <div class="baggage-inputs">
                <div class="baggage-group">
                  <label>随身行李 (kg)</label>
                  <input
                    v-model="cabin.carryOnAllowance"
                    type="number"
                    min="0"
                    step="1"
                  />
                </div>
                <div class="baggage-group">
                  <label>托运行李 (kg)</label>
                  <input
                    v-model="cabin.checkedBaggageAllowance"
                    type="number"
                    min="0"
                    step="5"
                  />
                </div>
                <div class="baggage-group">
                  <label>额外行李费率 (¥/kg)</label>
                  <input
                    v-model="cabin.extraBaggagePrice"
                    type="number"
                    min="0"
                    step="10"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="pricing-rules">
          <h3>动态定价规则</h3>

          <div class="rule-group">
            <label>高峰期调价比例</label>
            <div class="price-input">
              <input
                v-model="pricingRules.peakSeasonFactor"
                type="number"
                min="1"
                max="3"
                step="0.05"
              />
              <span>倍</span>
            </div>
          </div>

          <div class="rule-group">
            <label>靠近起飞日期调价策略</label>
            <div
              v-for="(strategy, index) in pricingRules.departureDateStrategies"
              :key="index"
              class="strategy-item"
            >
              <span>起飞前 {{ strategy.days }} 天内</span>
              <div class="price-input">
                <input
                  v-model="strategy.factor"
                  type="number"
                  min="1"
                  max="3"
                  step="0.05"
                />
                <span>倍</span>
              </div>
            </div>
          </div>

          <div class="rule-group">
            <label>剩余座位数调价策略</label>
            <div
              v-for="(strategy, index) in pricingRules.remainingSeatStrategies"
              :key="index"
              class="strategy-item"
            >
              <span>剩余座位 {{ strategy.percentage }}% 以下</span>
              <div class="price-input">
                <input
                  v-model="strategy.factor"
                  type="number"
                  min="1"
                  max="3"
                  step="0.05"
                />
                <span>倍</span>
              </div>
            </div>
          </div>
        </div>

        <div class="pricing-actions">
          <button class="btn btn-secondary" @click="resetPricing">
            <i class="fas fa-undo"></i> 重置价格
          </button>
          <button class="btn btn-secondary" @click="applyDynamicPricing">
            <i class="fas fa-bolt"></i> 应用动态定价
          </button>
          <button class="btn btn-primary" @click="savePricing">
            <i class="fas fa-save"></i> 保存设置
          </button>
        </div>
      </div>

      <div v-if="showHistoryChart" class="price-history">
        <h3>价格历史走势</h3>
        <div class="chart-container">
          <!-- 此处在实际应用中应该渲染图表 -->
          <div class="chart-placeholder">
            价格历史图表将在此显示（实际项目中可使用ECharts等图表库）
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script>
import api from '@/services/api'
import { ElMessage } from 'element-plus'

export default {
  name: 'AdminFlightPricingView',
  data() {
    return {
      flight: null,
      isLoading: false,
      error: null,
      isSaving: false,
      selectedCurrency: 'CNY',
      cabinPricing: [],
      pricingRules: {
        peakSeasonFactor: 1.2,
        departureDateStrategies: [
          { days: 3, factor: 1.5 },
          { days: 7, factor: 1.3 },
          { days: 14, factor: 1.1 }
        ],
        remainingSeatStrategies: [
          { percentage: 10, factor: 1.5 },
          { percentage: 30, factor: 1.2 },
          { percentage: 50, factor: 1.1 }
        ]
      },
      showHistoryChart: false,
      originalPricing: null
    }
  },
  created() {
    const flightId = this.$route.params.flightId
    if (flightId) {
      this.loadFlightData(flightId)
    } else {
      this.error = '缺少航班ID参数'
    }
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
    getCabinName(type) {
      const names = {
        economy: '经济舱',
        business: '商务舱',
        first: '头等舱'
      }
      return names[type] || type
    },
    getCurrencySymbol() {
      const symbols = {
        CNY: '¥',
        USD: '$',
        EUR: '€'
      }
      return symbols[this.selectedCurrency] || '¥'
    },
    calculateDiscount(cabin) {
      if (cabin.basePrice === 0) return 0
      const discount =
        100 - Math.round((cabin.currentPrice / cabin.basePrice) * 100)
      return discount > 0 ? discount : 0
    },
    updateCurrentPrice(cabin) {
      cabin.currentPrice = Math.round(
        cabin.basePrice * (1 - cabin.discountPct / 100)
      )
    },
    calculateDuration(departureTime, arrivalTime) {
      if (!departureTime || !arrivalTime) return '-'
      const departure = new Date(departureTime)
      const arrival = new Date(arrivalTime)
      const diffMs = arrival - departure
      const hours = Math.floor(diffMs / (1000 * 60 * 60))
      const minutes = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60))
      return `${hours}小时${minutes}分钟`
    },
    transformFlightData(flightData) {
      return {
        id: flightData.id,
        flightNumber: flightData.flight_number,
        departureCity: flightData.departure_city,
        departureAirport: flightData.departure_airport || '',
        arrivalCity: flightData.arrival_city,
        arrivalAirport: flightData.arrival_airport || '',
        departureTime: flightData.departure_time,
        arrivalTime: flightData.arrival_time,
        duration: this.calculateDuration(
          flightData.departure_time,
          flightData.arrival_time
        ),
        aircraft: flightData.aircraft_type || '-',
        economyPrice: flightData.economy_price,
        businessPrice: flightData.business_price,
        firstClassPrice: flightData.first_class_price,
        availableSeats: flightData.available_seats,
        totalSeats: flightData.total_seats
      }
    },
    buildCabinPricing(flightData, fareData) {
      const cabinClasses = [
        { type: 'economy', priceField: 'economy_price', defaultPrice: 800 },
        { type: 'business', priceField: 'business_price', defaultPrice: 2000 },
        { type: 'first', priceField: 'first_class_price', defaultPrice: 5000 }
      ]

      return cabinClasses.map(cabin => {
        const basePrice = flightData[cabin.priceField] || cabin.defaultPrice
        const currentPrice = fareData?.fare_per_person || basePrice

        const totalSeats = Math.floor((flightData.total_seats || 180) / 3)
        const availableSeats = Math.floor(
          (flightData.available_seats || totalSeats) / 3
        )

        return {
          type: cabin.type,
          basePrice: parseFloat(basePrice) || cabin.defaultPrice,
          currentPrice:
            parseFloat(currentPrice) ||
            parseFloat(basePrice) ||
            cabin.defaultPrice,
          discountPct: 0,
          availableSeats: availableSeats,
          totalSeats: totalSeats,
          specialMeal: cabin.type !== 'economy',
          specialMealPrice: cabin.type === 'economy' ? 50 : 0,
          extraLegroom: cabin.type !== 'economy',
          extraLegroomPrice: cabin.type === 'economy' ? 100 : 0,
          priorityBoarding: cabin.type !== 'economy',
          priorityBoardingPrice: cabin.type === 'economy' ? 30 : 0,
          carryOnAllowance:
            cabin.type === 'first' ? 15 : cabin.type === 'business' ? 10 : 5,
          checkedBaggageAllowance:
            cabin.type === 'first' ? 40 : cabin.type === 'business' ? 30 : 20,
          extraBaggagePrice: cabin.type === 'first' ? 30 : 50
        }
      })
    },
    async loadFlightData(flightId) {
      this.isLoading = true
      this.error = null

      try {
        const flightResponse = await api.flights.getDetail(flightId)
        const flightData = flightResponse.results
          ? flightResponse.results[0]
          : flightResponse

        if (!flightData) {
          this.error = '航班信息不存在'
          this.flight = null
          return
        }

        this.flight = this.transformFlightData(flightData)

        let fareData = null
        try {
          const fareResponse = await api.flights.getFare(flightId, {
            cabin_class: 'economy'
          })
          fareData = fareResponse
        } catch {
          /* debug */ console.log('获取票价信息失败，使用航班基础价格')
        }

        this.cabinPricing = this.buildCabinPricing(flightData, fareData)
        this.originalPricing = JSON.parse(JSON.stringify(this.cabinPricing))
      } catch (error) {
        /* debug */ console.error('加载航班数据失败:', error)
        this.error = error.message || '加载航班数据失败，请稍后重试'
        this.flight = null
      } finally {
        this.isLoading = false
      }
    },
    retryLoad() {
      const flightId = this.$route.params.flightId
      if (flightId) {
        this.loadFlightData(flightId)
      }
    },
    goBack() {
      this.$router.push('/admin/flights')
    },
    resetPricing() {
      if (this.originalPricing) {
        this.cabinPricing = JSON.parse(JSON.stringify(this.originalPricing))
        ElMessage.success('价格已重置')
      }
    },
    applyDynamicPricing() {
      this.cabinPricing.forEach(cabin => {
        let dynamicFactor = 1

        const seatPercentage = (cabin.availableSeats / cabin.totalSeats) * 100
        for (const strategy of this.pricingRules.remainingSeatStrategies) {
          if (seatPercentage <= strategy.percentage) {
            dynamicFactor = Math.max(dynamicFactor, strategy.factor)
            break
          }
        }

        cabin.currentPrice = Math.round(cabin.basePrice * dynamicFactor)

        if (cabin.basePrice > 0) {
          cabin.discountPct = Math.max(
            0,
            100 - Math.round((cabin.currentPrice / cabin.basePrice) * 100)
          )
        }
      })

      ElMessage.success('已应用动态定价规则')
    },
    async savePricing() {
      if (!this.flight || !this.flight.id) {
        ElMessage.error('航班信息不存在')
        return
      }

      this.isSaving = true

      try {
        const updateData = {}

        this.cabinPricing.forEach(cabin => {
          if (cabin.type === 'economy') {
            updateData.economy_price = cabin.currentPrice
          } else if (cabin.type === 'business') {
            updateData.business_price = cabin.currentPrice
          } else if (cabin.type === 'first') {
            updateData.first_class_price = cabin.currentPrice
          }
        })

        await api.flights.updatePrice(this.flight.id, updateData)

        ElMessage.success('价格设置已保存')
        this.originalPricing = JSON.parse(JSON.stringify(this.cabinPricing))
      } catch (error) {
        /* debug */ console.error('保存价格失败:', error)
        ElMessage.error(error.message || '保存价格失败，请稍后重试')
      } finally {
        this.isSaving = false
      }
    }
  }
}
</script>

<style scoped>
.admin-flight-pricing {
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

/* 加载状态样式 */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.loading-container i {
  font-size: 32px;
  color: #3f51b5;
  margin-bottom: 15px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.loading-container span {
  color: #666;
  font-size: 14px;
}

/* 错误状态样式 */
.error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.error-container i {
  font-size: 48px;
  color: #f56c6c;
  margin-bottom: 15px;
}

.error-container span {
  color: #666;
  font-size: 14px;
  margin-bottom: 15px;
}

/* 空数据状态样式 */
.empty-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.empty-container i {
  font-size: 48px;
  color: #909399;
  margin-bottom: 15px;
}

.empty-container span {
  color: #666;
  font-size: 14px;
  margin-bottom: 15px;
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
  flex: 1 1 25%;
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

.pricing-container {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 20px;
  margin-bottom: 20px;
}

.pricing-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.pricing-header h2 {
  font-size: 18px;
  margin: 0;
}

.currency-select {
  display: flex;
  align-items: center;
}

.currency-select label {
  margin-right: 10px;
}

.currency-select select {
  padding: 5px 10px;
  border-radius: 4px;
  border: 1px solid #ddd;
}

.cabin-pricing {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  margin-bottom: 20px;
}

.cabin-class {
  flex: 1;
  min-width: 300px;
  border: 1px solid #eee;
  border-radius: 8px;
  padding: 15px;
  background: #f9f9f9;
}

.cabin-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.cabin-header h3 {
  margin: 0;
  font-size: 16px;
}

.seat-count {
  font-size: 13px;
  color: #666;
}

.price-settings {
  margin-bottom: 20px;
}

.price-group {
  margin-bottom: 10px;
}

.price-group label {
  display: block;
  margin-bottom: 5px;
  font-size: 14px;
  color: #555;
}

.price-input {
  position: relative;
  display: flex;
  align-items: center;
}

.price-input input {
  width: 100%;
  padding: 8px 12px 8px 25px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.currency-symbol {
  position: absolute;
  left: 10px;
  font-weight: bold;
}

.slider-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.discount-value {
  font-weight: bold;
  color: #3f51b5;
}

.discount-slider {
  width: 100%;
  margin-top: 5px;
}

.pricing-options {
  margin-bottom: 20px;
}

.option {
  margin-bottom: 8px;
}

.checkbox {
  display: inline-flex;
  align-items: center;
  cursor: pointer;
}

.checkbox input {
  position: absolute;
  opacity: 0;
  cursor: pointer;
}

.checkbox span {
  height: 18px;
  width: 18px;
  background-color: #eee;
  border-radius: 4px;
  margin-right: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
}

.checkbox span::after {
  content: '';
  width: 5px;
  height: 10px;
  border: solid white;
  border-width: 0 2px 2px 0;
  transform: rotate(45deg);
  display: none;
}

.checkbox input:checked ~ span {
  background-color: #3f51b5;
}

.checkbox input:checked ~ span::after {
  display: block;
}

.baggage-allowance h4 {
  margin-top: 0;
  margin-bottom: 10px;
  font-size: 14px;
  color: #333;
}

.baggage-inputs {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.baggage-group {
  flex: 1;
  min-width: 100px;
}

.baggage-group label {
  display: block;
  font-size: 12px;
  margin-bottom: 5px;
  color: #666;
}

.baggage-group input {
  width: 100%;
  padding: 6px 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.pricing-rules {
  background: #f5f5f5;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 20px;
}

.pricing-rules h3 {
  margin-top: 0;
  margin-bottom: 15px;
  font-size: 16px;
}

.rule-group {
  margin-bottom: 15px;
}

.rule-group label {
  display: block;
  font-weight: 600;
  margin-bottom: 10px;
}

.strategy-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  padding: 8px;
  background: white;
  border-radius: 4px;
  border: 1px solid #eee;
}

.strategy-item .price-input {
  width: 100px;
}

.pricing-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

.btn {
  padding: 8px 16px;
  border-radius: 4px;
  border: none;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  transition: all 0.3s;
}

.btn i {
  margin-right: 8px;
}

.btn-primary {
  background: #3f51b5;
  color: white;
}

.btn-primary:hover {
  background: #303f9f;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
}

.btn-secondary {
  background: #f5f5f5;
  color: #333;
}

.btn-secondary:hover {
  background: #e0e0e0;
}

.price-history {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 20px;
}

.price-history h3 {
  margin-top: 0;
  margin-bottom: 15px;
  font-size: 16px;
}

.chart-container {
  height: 300px;
}

.chart-placeholder {
  height: 100%;
  background: #f9f9f9;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #999;
  border: 1px dashed #ddd;
  border-radius: 4px;
}

@media (max-width: 768px) {
  .flight-header {
    flex-direction: column;
    gap: 10px;
  }

  .cabin-pricing {
    flex-direction: column;
  }

  .baggage-inputs {
    flex-direction: column;
  }

  .strategy-item {
    flex-direction: column;
    align-items: stretch;
  }

  .strategy-item .price-input {
    width: 100%;
    margin-top: 5px;
  }
}
</style>
