<template>
  <div class="flight-results">
    <div class="results-header">
      <div class="route-info">
        <h1>{{ searchData.departureCity }} <span class="route-arrow">→</span> {{ searchData.arrivalCity }}</h1>
        <p class="date-info">{{ formatDate(searchData.departureDate) }} · {{ searchData.passengerCount || 1 }}位乘客</p>
      </div>
      <div class="actions">
        <el-button type="primary" @click="backToSearch" icon="el-icon-back">修改搜索</el-button>
      </div>
    </div>

    <div class="main-content">
      <!-- 筛选侧边栏 -->
      <transition name="slide-fade">
        <flight-filters v-show="!isMobile || showFilters" :filters="filters" :available-airlines="availableAirlines"
          :min-price="minPrice" :max-price="maxPrice" :is-mobile="isMobile" @filter-changed="updateFilters"
          @reset-filters="resetFilters" @close-filters="showFilters = false" />
      </transition>

      <!-- 航班列表 -->
      <div class="flights-list-container">
        <flight-list-header :flight-count="filteredFlights.length" :sort-option="sortOption" :is-mobile="isMobile"
          @sort-changed="handleSortChange" @show-filters="showFilters = true" />

        <transition-group name="flight-list" tag="div" class="flights-list"
          v-if="!isLoading && filteredFlights.length > 0">
          <flight-card v-for="flight in filteredFlights" :key="flight.id" :flight="flight" @select="selectFlight"
            @cabin-change="handleCabinChange" />
        </transition-group>

        <!-- 加载状态显示 -->
        <div v-else-if="isLoading" class="loading-state">
          <el-skeleton :rows="3" animated />
        </div>

        <!-- 无结果显示 -->
        <div v-else class="no-results">
          <div class="no-results-icon"></div>
          <h3>没有查询到航班</h3>
          <p>{{ error ? '获取航班数据失败，请稍后重试' : '请尝试调整搜索条件或选择其他日期' }}</p>
          <el-button v-if="error" type="primary" @click="fetchFlights">重试</el-button>
          <el-button v-else type="primary" @click="resetFilters">重置筛选条件</el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import FlightFilters from '@/components/flights/FlightFilters.vue'
import FlightCard from '@/components/flights/FlightCard.vue'
import FlightListHeader from '@/components/flights/FlightListHeader.vue'
import axios from 'axios'
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'

export default {
  name: 'FlightResults',
  components: {
    FlightFilters,
    FlightCard,
    FlightListHeader
  },
  setup() {
    const route = useRoute()
    const router = useRouter()

    const searchData = ref({
      departureCity: '',
      arrivalCity: '',
      departureDate: '',
      returnDate: null,
      passengerCount: 1,
      cabinClass: 'economy',
      adultCount: 1,
      childCount: 0,
      infantCount: 0
    })

    const flights = ref([])
    const filteredFlights = ref([])
    const isLoading = ref(true)
    const error = ref(false)
    const sortOption = ref('recommended')
    const filters = ref({
      departureTimeRange: [0, 24],
      priceRange: [0, 10000],
      airlines: [],
      directOnly: false,
      hasDiscount: false
    })
    const availableAirlines = ref([])
    const minPrice = ref(0)
    const maxPrice = ref(10000)
    const isMobile = ref(false)
    const showFilters = ref(false)
    const windowWidth = ref(window.innerWidth)

    // 从路由参数获取搜索数据
    if (route.query) {
      console.log('路由查询参数:', route.query);

      // 如果查询参数为空，提供默认值用于测试
      const hasValidParams = route.query.from && route.query.to;

      searchData.value = {
        departureCity: route.query.from || (hasValidParams ? '' : '北京'),
        arrivalCity: route.query.to || (hasValidParams ? '' : '上海'),
        departureDate: route.query.date || '2025-06-27',
        returnDate: route.query.returnDate || null,
        passengerCount: parseInt(route.query.passengers) || 1,
        cabinClass: route.query.cabin || 'economy',
        adultCount: parseInt(route.query.passengers) || 1,
        childCount: 0,
        infantCount: 0
      }
      console.log('设置搜索数据:', searchData.value);
    }

    // 检查是否为移动设备
    const checkDevice = () => {
      isMobile.value = window.innerWidth < 768
    }
    checkDevice()
    window.addEventListener('resize', checkDevice)

    // 加载航班数据
    const fetchFlights = async () => {
      isLoading.value = true
      error.value = null
      flights.value = []
      filteredFlights.value = []

      console.log('开始获取航班数据...')

      try {
        // 使用axios直接调用API
        const response = await axios.get('http://127.0.0.1:8000/api/flights/search/', {
          params: {
            departure_city: searchData.value.departureCity,
            arrival_city: searchData.value.arrivalCity,
            departure_date: formatDateForAPI(searchData.value.departureDate) || '2025-06-27'
          }
        })

        console.log('API调用成功，获取到航班数据')

        const responseData = response.data

        // 处理航班数据
        if (responseData && Array.isArray(responseData) && responseData.length > 0) {
          // 处理航班数据，确保格式一致
          flights.value = responseData.map(flight => {
            // 确保日期是Date对象
            const departureTime = new Date(flight.departure_time || flight.departureTime)
            const arrivalTime = new Date(flight.arrival_time || flight.arrivalTime)

            // 计算飞行时间（分钟）
            const timeDiff = Math.floor((arrivalTime - departureTime) / (1000 * 60))

            return {
              id: flight.id,
              flightNumber: flight.flight_number || flight.flightNumber,
              airlineName: flight.airline_name || flight.airlineName,
              airlineCode: flight.airline_code || flight.airlineCode,

              departureCity: flight.departure_city || flight.departureCity,
              arrivalCity: flight.arrival_city || flight.arrivalCity,
              departureAirport: flight.departure_airport || flight.departureAirport,
              departureAirportCode: flight.departure_airport_code || flight.departureAirportCode,
              arrivalAirport: flight.arrival_airport || flight.arrivalAirport,
              arrivalAirportCode: flight.arrival_airport_code || flight.arrivalAirportCode,
              departureTime: departureTime,
              arrivalTime: arrivalTime,
              duration: flight.duration || timeDiff,
              price: flight.price,
              discount: flight.discount || 1,
              availableSeats: flight.available_seats || flight.availableSeats || 0,
              aircraftType: flight.aircraft_type || flight.aircraftType,
              mealService: flight.meal_service ?? flight.mealService ?? false,
              baggageAllowance: flight.baggage_allowance ?? flight.baggageAllowance ?? 20,
              businessAvailable: flight.business_available || flight.businessAvailable || false,
              firstAvailable: flight.first_available || flight.firstAvailable || false,
              selectedClass: 'economy',
              showDetails: false,
              directFlight: flight.direct_flight || flight.directFlight || true,
              wifi: flight.wifi ?? false,
              powerOutlet: flight.power_outlet ?? flight.powerOutlet ?? false,
              entertainment: flight.entertainment ?? false
            }
          })

          // 设置价格筛选器范围
          if (flights.value.length > 0) {
            minPrice.value = Math.min(...flights.value.map(f => Math.round(f.price * f.discount)))
            maxPrice.value = Math.max(...flights.value.map(f => Math.round(f.price * f.discount)))
            filters.value.priceRange = [minPrice.value, maxPrice.value]
          }

          // 获取可用的航空公司
          const airlines = [...new Set(flights.value.map(f => f.airlineName).filter(Boolean))]
          availableAirlines.value = airlines.map(name => {
            return {
              name,
              code: name && typeof name === 'string' ? name.substring(0, 2).toUpperCase() : 'NA'
            }
          })
          filters.value.airlines = availableAirlines.value.map(a => a.code)

          applyFilters()
        } else {
          console.log('没有找到匹配的航班')
          flights.value = []
          filteredFlights.value = []
          error.value = '没有找到匹配的航班。请尝试不同的搜索条件。'
        }

      } catch (err) {
        console.error('获取航班数据失败', err)
        error.value = '获取航班数据失败，请稍后再试'
      } finally {
        isLoading.value = false
      }
    }

    // 其他方法保持不变
    const formatDate = (dateStr) => {
      if (!dateStr) return ''
      const date = new Date(dateStr)
      const options = { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' }
      return date.toLocaleDateString('zh-CN', options)
    }

    // 添加用于API的日期格式化方法
    const formatDateForAPI = (dateStr) => {
      if (!dateStr) return ''
      const date = new Date(dateStr)
      return date.toISOString().split('T')[0]  // 返回YYYY-MM-DD格式
    }

    const formatTime = (date) => {
      if (!date) return ''
      return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
    }

    const formatDuration = (minutes) => {
      const hours = Math.floor(minutes / 60)
      const mins = minutes % 60
      return `${hours}h ${mins}m`
    }

    const formatHour = (hour) => {
      return `${hour}:00`
    }

    const applyFilters = () => {
      const { departureTimeRange, priceRange, airlines, directOnly, hasDiscount } = filters.value

      filteredFlights.value = flights.value.filter(flight => {
        // 按起飞时间筛选
        const departureHour = flight.departureTime.getHours()
        const isTimeInRange = departureHour >= departureTimeRange[0] && departureHour <= departureTimeRange[1]

        // 按价格筛选
        const actualPrice = Math.round(flight.price * flight.discount)
        const isPriceInRange = actualPrice >= priceRange[0] && actualPrice <= priceRange[1]

        // 按航空公司筛选
        const airlineCode = flight.airlineName && typeof flight.airlineName === 'string' ?
          flight.airlineName.substring(0, 2).toUpperCase() : 'NA'
        const isAirlineSelected = airlines.includes(airlineCode)

        // 直飞筛选
        const isDirectMatch = !directOnly || flight.directFlight

        // 特价筛选
        const isDiscountMatch = !hasDiscount || flight.discount < 0.9

        return isTimeInRange && isPriceInRange && isAirlineSelected && isDirectMatch && isDiscountMatch
      })

      sortFlights()
    }

    const sortFlights = () => {
      console.log('正在排序，排序方式:', sortOption.value)
      switch (sortOption.value) {
        case 'recommended':
          // 推荐排序 - 结合多个因素
          filteredFlights.value.sort((a, b) => {
            // 计算推荐得分 (价格权重40% + 时间合理性30% + 折扣20% + 准点率10%)
            const aScore = calculateRecommendScore(a)
            const bScore = calculateRecommendScore(b)
            return bScore - aScore // 降序
          })
          break
        case 'price':
          filteredFlights.value.sort((a, b) =>
            (a.price * a.discount) - (b.price * b.discount)
          )
          break
        case 'departureTime':
          filteredFlights.value.sort((a, b) =>
            a.departureTime - b.departureTime
          )
          break
        case 'duration':
          filteredFlights.value.sort((a, b) =>
            a.duration - b.duration
          )
          break
      }
      // 强制视图更新
      filteredFlights.value = [...filteredFlights.value]
    }

    const calculateRecommendScore = (flight) => {
      // 价格得分 (越低越好)
      const priceRange = maxPrice.value - minPrice.value
      const priceScore = priceRange > 0
        ? 1 - ((flight.price * flight.discount - minPrice.value) / priceRange)
        : 0.5

      // 起飞时间合理性 (早上8-10点和下午3-5点最合理)
      const hour = flight.departureTime.getHours()
      let timeScore = 0
      if (hour >= 8 && hour <= 10) {
        timeScore = 1
      } else if (hour >= 15 && hour <= 17) {
        timeScore = 0.9
      } else if (hour >= 6 && hour <= 12) {
        timeScore = 0.8
      } else if (hour >= 13 && hour <= 19) {
        timeScore = 0.7
      } else {
        timeScore = 0.3 // 夜间航班
      }

      // 折扣得分
      const discountScore = 1 - flight.discount

      // 综合得分 (权重可调整)
      return priceScore * 0.5 + timeScore * 0.3 + discountScore * 0.2
    }

    const resetFilters = () => {
      filters.value = {
        departureTimeRange: [0, 24],
        priceRange: [minPrice.value, maxPrice.value],
        airlines: availableAirlines.value.map(a => a.code),
        directOnly: false,
        hasDiscount: false
      }
      applyFilters()

      // 如果是移动设备，隐藏筛选面板
      if (isMobile.value) {
        showFilters.value = false
      }
    }

    const selectFlight = (flight) => {
      // 跳转到预订页面，传递选中的航班信息
      console.log('选择航班，ID:', flight.id);
      router.push({
        name: 'booking',
        params: { flightId: flight.id },
        query: {
          class: flight.selectedClass || 'economy',
          passengers: searchData.value.passengerCount || 1
        }
      })
    }

    const backToSearch = () => {
      router.push('/')
    }

    const handleResize = () => {
      windowWidth.value = window.innerWidth
      checkDevice()
    }

    const updateFilters = (newFilters) => {
      filters.value = { ...newFilters };
      applyFilters();
    }

    const handleCabinChange = (flight, newClass) => {
      flight.selectedClass = newClass;
      applyFilters();
    }

    // 新增处理排序选项变化的方法
    const handleSortChange = (value) => {
      sortOption.value = value;
      sortFlights();
    }

    // 在组件挂载时加载航班数据
    onMounted(() => {
      fetchFlights();
    });

    return {
      searchData,
      flights,
      filteredFlights,
      isLoading,
      error,
      sortOption,
      filters,
      availableAirlines,
      minPrice,
      maxPrice,
      isMobile,
      showFilters,
      windowWidth,
      formatDate,
      formatDateForAPI,
      formatTime,
      formatDuration,
      formatHour,
      applyFilters,
      sortFlights,
      resetFilters,
      selectFlight,
      backToSearch,
      checkDevice,
      handleResize,
      updateFilters,
      handleCabinChange,
      handleSortChange,
      fetchFlights
    }
  }
}
</script>

<style scoped>
.flight-results {
  background-color: #f5f9fc;
  min-height: 100vh;
  padding-bottom: 40px;
  width: 100%;
  overflow-x: hidden;
}

.results-header {
  background: linear-gradient(135deg, #00468c, #0076c6);
  color: white;
  padding: 30px 40px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 4px 12px rgba(0, 70, 140, 0.15);
  position: relative;
  overflow: hidden;
  width: 100%;
  box-sizing: border-box;
}

.results-header::after {
  content: '';
  position: absolute;
  width: 100%;
  height: 10px;
  bottom: 0;
  left: 0;
  background: linear-gradient(90deg,
      rgba(255, 255, 255, 0.1) 0%,
      rgba(255, 255, 255, 0.3) 50%,
      rgba(255, 255, 255, 0.1) 100%);
  animation: shimmer 3s infinite linear;
}

@keyframes shimmer {
  0% {
    transform: translateX(-100%);
  }

  100% {
    transform: translateX(100%);
  }
}

.route-info h1 {
  font-size: 2.2em;
  margin: 0 0 10px 0;
  font-weight: 700;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  animation: fadeIn 0.8s ease-out;
}

.route-arrow {
  margin: 0 10px;
  font-weight: normal;
  position: relative;
  display: inline-block;
  transition: transform 0.3s;
}

.route-arrow:hover {
  transform: translateX(5px);
}

.date-info {
  margin: 0;
  font-size: 1.1em;
  opacity: 0.9;
  animation: fadeIn 1s ease-out;
}

.main-content {
  display: flex;
  width: 100%;
  max-width: 100%;
  margin: 0;
  padding: 20px 40px;
  gap: 24px;
  position: relative;
  align-items: flex-start;
  box-sizing: border-box;
}

/* 筛选面板样式 */
.filters-panel {
  width: 280px;
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
  align-self: flex-start;
  position: sticky;
  top: 20px;
  transition: all 0.3s ease;
  border: 1px solid rgba(0, 70, 140, 0.1);
  animation: slideInLeft 0.5s ease-out;
}

.filters-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.filters-panel h3 {
  margin: 0;
  color: #00468c;
  font-size: 1.3em;
  font-weight: 600;
}

.filter-group {
  margin-bottom: 25px;
  border-bottom: 1px solid #f0f0f0;
  padding-bottom: 20px;
}

.filter-group:last-of-type {
  border-bottom: none;
  padding-bottom: 0;
}

.filter-group h4 {
  margin-bottom: 15px;
  color: #333;
  font-size: 1.1em;
  font-weight: 500;
}

.time-range-display,
.price-range-display {
  display: flex;
  justify-content: space-between;
  margin-top: 8px;
  color: #666;
  font-size: 0.9em;
}

.reset-btn {
  width: 100%;
  margin-top: 10px;
  transition: all 0.2s;
}

.reset-btn:hover {
  background-color: #f5f5f5;
  color: #00468c;
}

/* 航班列表样式 */
.flights-list-container {
  flex: 1;
  min-width: 0;
  max-width: calc(100% - 304px);
  animation: fadeIn 0.8s ease-out;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  background: white;
  padding: 15px 20px;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
}

.found-count {
  font-weight: 500;
  color: #00468c;
  font-size: 1.1em;
}

.count-highlight {
  font-weight: 700;
  font-size: 1.2em;
  color: #0076c6;
}

.sort-options span {
  margin-right: 10px;
  color: #666;
}

.flight-card {
  background: white;
  border-radius: 12px;
  margin-bottom: 20px;
  overflow: hidden;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
  transition: all 0.3s;
  border: 1px solid rgba(0, 70, 140, 0.05);
  transform-origin: center;
  animation: cardAppear 0.4s ease-out;
}

.flight-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0, 70, 140, 0.15);
  border-color: rgba(0, 118, 198, 0.2);
}

.flight-card.low-seats {
  border-left: 4px solid #ff6b6b;
}

.flight-card.special-discount {
  border-left: 4px solid #4caf50;
}

.flight-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  background-color: #f8f9fa;
  border-bottom: 1px solid #eee;
}

.airline-info {
  display: flex;
  align-items: center;
}



.airline-name {
  font-weight: 600;
  color: #333;
  font-size: 1.1em;
}

.flight-number {
  color: #666;
  font-size: 0.9em;
  margin-top: 3px;
}

.tags {
  display: flex;
  gap: 10px;
}

.tag-warning,
.tag-success {
  padding: 5px 12px;
  border-radius: 100px;
  font-size: 0.85em;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.tag-warning {
  background-color: rgba(255, 107, 107, 0.1);
  color: #ff6b6b;
  border: 1px solid rgba(255, 107, 107, 0.3);
}

.tag-success {
  background-color: rgba(76, 175, 80, 0.1);
  color: #4caf50;
  border: 1px solid rgba(76, 175, 80, 0.3);
}

.flight-main {
  padding: 25px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.time-info {
  display: flex;
  align-items: center;
  gap: 25px;
}

.departure,
.arrival {
  text-align: center;
}

.time {
  font-size: 1.8em;
  font-weight: 700;
  color: #333;
  letter-spacing: -0.5px;
}

.airport {
  color: #666;
  margin-top: 5px;
  font-size: 0.95em;
}

.flight-path {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 150px;
}

.duration {
  color: #666;
  font-size: 0.9em;
  margin-bottom: 8px;
  background-color: #f5f9fc;
  padding: 4px 12px;
  border-radius: 100px;
  border: 1px solid #e0e0e0;
}

.path-line {
  position: relative;
  width: 120px;
  height: 2px;
  background-color: #ddd;
  margin: 10px 0;
}

.path-line::before,
.path-line::after {
  content: '';
  position: absolute;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  top: -2px;
  background-color: #0076c6;
}

.path-line::before {
  left: 0;
}

.path-line::after {
  right: 0;
}

.airplane-icon {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 22px;
  height: 22px;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 576 512'%3E%3Cpath fill='%230076c6' d='M482.3 192C516.5 192 576 221 576 256C576 292 516.5 320 482.3 320H365.7L265.2 495.9C259.5 505.8 248.9 512 237.4 512H181.2C170.6 512 162.9 501.8 165.8 491.6L214.9 320H112L68.8 377.6C65.78 381.6 61.04 384 56 384H14.03C6.284 384 0 377.7 0 369.1C0 368.7 .1818 367.4 .5398 366.1L32 256L.5398 145.9C.1818 144.6 0 143.3 0 142C0 134.3 6.284 128 14.03 128H56C61.04 128 65.78 130.4 68.8 134.4L112 192H214.9L165.8 20.4C162.9 10.17 170.6 0 181.2 0H237.4C248.9 0 259.5 6.153 265.2 16.12L365.7 192H482.3z'/%3E%3C/svg%3E");
  background-size: contain;
  background-repeat: no-repeat;
  animation: flyPlane 3s infinite linear;
}

@keyframes flyPlane {
  0% {
    transform: translate(-50%, -50%) rotate(0);
  }

  25% {
    transform: translate(-55%, -45%) rotate(-5deg);
  }

  50% {
    transform: translate(-50%, -50%) rotate(0);
  }

  75% {
    transform: translate(-45%, -55%) rotate(5deg);
  }

  100% {
    transform: translate(-50%, -50%) rotate(0);
  }
}

.flight-type {
  color: #666;
  font-size: 0.85em;
  margin-top: 8px;
}

.booking-info {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 12px;
}

.price-container {
  text-align: right;
}

.current-price {
  font-size: 2em;
  font-weight: 700;
  color: #00468c;
  letter-spacing: -0.5px;
}

.original-price {
  color: #999;
  text-decoration: line-through;
  font-size: 0.9em;
  margin-top: 2px;
}

.discount {
  background-color: #ffd166;
  color: #333;
  padding: 3px 10px;
  border-radius: 100px;
  font-size: 0.85em;
  font-weight: 600;
  display: inline-block;
  margin-top: 5px;
}

.flight-details {
  padding: 0 20px 20px;
  border-top: 1px solid #eee;
  display: flex;
  flex-wrap: wrap;
  gap: 30px;
  background-color: #f8f9fa;
  animation: slideDown 0.3s ease-out;
}

.details-section {
  flex: 1;
  min-width: 250px;
}

.details-section h4 {
  color: #00468c;
  margin-bottom: 15px;
  font-size: 1.1em;
  font-weight: 600;
  padding-top: 20px;
}

.detail-item {
  margin-bottom: 10px;
  display: flex;
}

.detail-item .label {
  color: #666;
  width: 100px;
  font-weight: 500;
}

.cabin-options {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.cabin-price {
  color: #00468c;
  font-weight: 600;
  margin-left: 10px;
}

.amenities .amenity-icons {
  display: flex;
  gap: 20px;
  margin-top: 10px;
}

.amenity-item {
  text-align: center;
  transition: all 0.3s;
}

.amenity-icon {
  width: 40px;
  height: 40px;
  margin: 0 auto 5px;
  background-size: contain;
  background-position: center;
  background-repeat: no-repeat;
  opacity: 1;
}

.wifi-icon {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 640 512'%3E%3Cpath fill='%230076c6' d='M54.2 202.9C123.2 136.7 216.8 96 320 96s196.8 40.7 265.8 106.9c12.8 12.2 33 11.8 45.2-.9s11.8-33-.9-45.2C549.7 79.5 440.4 32 320 32S90.3 79.5 9.8 156.7C-2.9 169-3.3 189.2 8.9 202s32.5 13.2 45.2 .9zM320 256c56.8 0 108.6 21.1 148.2 56c13.3 11.7 33.5 10.4 45.2-2.8s10.4-33.5-2.8-45.2C459.8 219.2 393 192 320 192s-139.8 27.2-190.5 72c-13.3 11.7-14.5 31.9-2.8 45.2s31.9 14.5 45.2 2.8c39.5-34.9 91.3-56 148.2-56zm64 160c0-35.3-28.7-64-64-64s-64 28.7-64 64s28.7 64 64 64s64-28.7 64-64z'/%3E%3C/svg%3E");
}

.power-icon {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 576 512'%3E%3Cpath fill='%230076c6' d='M64 64C28.7 64 0 92.7 0 128V384c0 35.3 28.7 64 64 64H512c35.3 0 64-28.7 64-64V128c0-35.3-28.7-64-64-64H64zm16 64h32c8.8 0 16 7.2 16 16v32c0 8.8-7.2 16-16 16H80c-8.8 0-16-7.2-16-16V144c0-8.8 7.2-16 16-16zM64 240c0-8.8 7.2-16 16-16h32c8.8 0 16 7.2 16 16v32c0 8.8-7.2 16-16 16H80c-8.8 0-16-7.2-16-16V240zm16 80h32c8.8 0 16 7.2 16 16v32c0 8.8-7.2 16-16 16H80c-8.8 0-16-7.2-16-16V336c0-8.8 7.2-16 16-16zm80-176c0-8.8 7.2-16 16-16h32c8.8 0 16 7.2 16 16v32c0 8.8-7.2 16-16 16H176c-8.8 0-16-7.2-16-16V144zm16 80h32c8.8 0 16 7.2 16 16v32c0 8.8-7.2 16-16 16H176c-8.8 0-16-7.2-16-16V240c0-8.8 7.2-16 16-16zM160 336c0-8.8 7.2-16 16-16h32c8.8 0 16 7.2 16 16v32c0 8.8-7.2 16-16 16H176c-8.8 0-16-7.2-16-16V336zM272 128h32c8.8 0 16 7.2 16 16v32c0 8.8-7.2 16-16 16H272c-8.8 0-16-7.2-16-16V144c0-8.8 7.2-16 16-16zM256 240c0-8.8 7.2-16 16-16h32c8.8 0 16 7.2 16 16v32c0 8.8-7.2 16-16 16H272c-8.8 0-16-7.2-16-16V240zm16 80h32c8.8 0 16 7.2 16 16v32c0 8.8-7.2 16-16 16H272c-8.8 0-16-7.2-16-16V336c0-8.8 7.2-16 16-16z'/%3E%3C/svg%3E");
}

.entertainment-icon {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 640 512'%3E%3Cpath fill='%230076c6' d='M64 64V352H576V64H64zM0 64C0 28.7 28.7 0 64 0H576c35.3 0 64 28.7 64 64V352c0 35.3-28.7 64-64 64H64c-35.3 0-64-28.7-64-64V64zM128 448H512c17.7 0 32 14.3 32 32s-14.3 32-32 32H128c-17.7 0-32-14.3-32-32s14.3-32 32-32z'/%3E%3C/svg%3E");
}

.amenity-name {
  font-size: 0.9em;
  color: #333;
}

.amenity-item.inactive {
  opacity: 0.4;
}

.flight-footer {
  padding: 12px 20px;
  background-color: #f8f9fa;
  border-top: 1px solid #eee;
  text-align: center;
}

.flight-footer .el-button {
  transition: all 0.2s;
}

.flight-footer .el-button:hover {
  color: #0076c6;
  transform: translateY(-2px);
}

.no-results {
  text-align: center;
  padding: 60px 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
  animation: fadeIn 1s ease-out;
}

.no-results-icon {
  width: 120px;
  height: 120px;
  margin: 0 auto 20px;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 512 512'%3E%3Cpath fill='%23cccccc' d='M505 41c9.4-9.4 9.4-24.6 0-33.9s-24.6-9.4-33.9 0L396.5 81.5C358.1 50.6 309.2 32 256 32C132.3 32 32 132.3 32 256c0 53.2 18.6 102.1 49.5 140.5L7 471c-9.4 9.4-9.4 24.6 0 33.9s24.6 9.4 33.9 0l74.5-74.5c38.4 31 87.3 49.5 140.5 49.5c123.7 0 224-100.3 224-224c0-53.2-18.6-102.1-49.5-140.5L505 41zM362.3 115.7L115.7 362.3C93.3 332.8 80 295.9 80 256c0-97.2 78.8-176 176-176c39.9 0 76.8 13.3 106.3 35.7zM149.7 396.3L396.3 149.7C418.7 179.2 432 216.1 432 256c0 97.2-78.8 176-176 176c-39.9 0-76.8-13.3-106.3-35.7z'/%3E%3C/svg%3E");
  background-size: contain;
  background-position: center;
  background-repeat: no-repeat;
  opacity: 0.6;
}

.no-results h3 {
  color: #00468c;
  margin-bottom: 10px;
  font-size: 1.5em;
}

.no-results p {
  color: #666;
  margin-bottom: 25px;
  font-size: 1.1em;
}

/* 移动设备样式 */
@media (max-width: 992px) {
  .main-content {
    flex-direction: column;
    padding: 20px;
  }

  .flights-list-container {
    max-width: 100%;
  }

  .flight-main {
    flex-direction: column;
    gap: 25px;
  }

  .booking-info {
    align-items: center;
    margin-top: 15px;
  }

  .flight-details {
    flex-direction: column;
    gap: 10px;
  }
}

@media (max-width: 768px) {
  .results-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
    padding: 20px;
  }

  .route-info h1 {
    font-size: 1.6em;
  }

  .time-info {
    flex-direction: column;
    gap: 15px;
  }

  .path-line {
    transform: rotate(90deg);
    margin: 20px 0;
  }

  .list-header {
    flex-direction: column;
    gap: 15px;
    align-items: flex-start;
  }

  .mobile-filter-toggle {
    margin-bottom: 10px;
  }
}

/* 动画定义 */
@keyframes fadeIn {
  from {
    opacity: 0;
  }

  to {
    opacity: 1;
  }
}

@keyframes slideInLeft {
  from {
    opacity: 0;
    transform: translateX(-30px);
  }

  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes slideDown {
  from {
    opacity: 0;
    max-height: 0;
    transform: translateY(-10px);
  }

  to {
    opacity: 1;
    max-height: 1000px;
    transform: translateY(0);
  }
}

@keyframes cardAppear {
  from {
    opacity: 0;
    transform: scale(0.95);
  }

  to {
    opacity: 1;
    transform: scale(1);
  }
}

/* 列表动画 */
.flight-list-enter-active,
.flight-list-leave-active {
  transition: all 0.5s;
}

.flight-list-enter,
.flight-list-leave-to {
  opacity: 0;
  transform: translateY(30px);
}

/* 侧边栏过渡动画 */
.slide-fade-enter-active {
  transition: all 0.3s ease-out;
}

.slide-fade-leave-active {
  transition: all 0.3s cubic-bezier(1.0, 0.5, 0.8, 1.0);
}

.slide-fade-enter,
.slide-fade-leave-to {
  transform: translateX(-20px);
  opacity: 0;
}

.loading-state {
  padding: 40px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
}
</style>
