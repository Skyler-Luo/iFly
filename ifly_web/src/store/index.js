import { createStore } from 'vuex'
import tokenManager from '@/utils/tokenManager'
import api from '@/services/api'

export default createStore({
  state: {
    // 用户认证状态
    isAuthenticated: false,
    user: null,
    
    // 应用状态
    loading: false,
    
    // 搜索和预订状态
    searchParams: {
      departureCity: '',
      arrivalCity: '',
      departureDate: null,
      returnDate: null,
      passengers: 1
    },
    
    // 航班搜索结果
    flights: [],
    selectedFlight: null,
    
    // 预订信息
    bookingInfo: {
      passengers: [],
      contactInfo: {}
    },
    
    // 消息提示
    messages: []
  },
  
  getters: {
    // 用户相关
    isLoggedIn: state => state.isAuthenticated,
    currentUser: state => state.user,
    isAdmin: state => state.user && state.user.role === 'admin',
    
    // 搜索相关
    hasSearchParams: state => state.searchParams.departureCity && state.searchParams.arrivalCity,
    searchResultsCount: state => state.flights.length,
    
    // 预订相关
    hasSelectedFlight: state => !!state.selectedFlight,
    passengerCount: state => state.bookingInfo.passengers.length,
    
    // 应用状态
    isLoading: state => state.loading
  },
  
  mutations: {
    // 用户认证
    SET_AUTHENTICATED(state, isAuth) {
      state.isAuthenticated = isAuth
    },
    
    SET_USER(state, user) {
      state.user = user
      state.isAuthenticated = !!user
    },
    
    CLEAR_USER(state) {
      state.user = null
      state.isAuthenticated = false
    },
    
    // 应用状态
    SET_LOADING(state, loading) {
      state.loading = loading
    },
    
    // 搜索参数
    SET_SEARCH_PARAMS(state, params) {
      state.searchParams = { ...state.searchParams, ...params }
    },
    
    CLEAR_SEARCH_PARAMS(state) {
      state.searchParams = {
        departureCity: '',
        arrivalCity: '',
        departureDate: null,
        returnDate: null,
        passengers: 1
      }
    },
    
    // 航班结果
    SET_FLIGHTS(state, flights) {
      state.flights = flights
    },
    
    SET_SELECTED_FLIGHT(state, flight) {
      state.selectedFlight = flight
    },
    
    CLEAR_FLIGHTS(state) {
      state.flights = []
      state.selectedFlight = null
    },
    
    // 预订信息
    SET_BOOKING_INFO(state, bookingInfo) {
      state.bookingInfo = { ...state.bookingInfo, ...bookingInfo }
    },
    
    ADD_PASSENGER(state, passenger) {
      state.bookingInfo.passengers.push(passenger)
    },
    
    REMOVE_PASSENGER(state, index) {
      state.bookingInfo.passengers.splice(index, 1)
    },
    
    UPDATE_PASSENGER(state, { index, passenger }) {
      state.bookingInfo.passengers.splice(index, 1, passenger)
    },
    
    SET_CONTACT_INFO(state, contactInfo) {
      state.bookingInfo.contactInfo = contactInfo
    },
    
    CLEAR_BOOKING_INFO(state) {
      state.bookingInfo = {
        passengers: [],
        contactInfo: {}
      }
    },
    
    // 消息系统
    ADD_MESSAGE(state, message) {
      const msg = {
        id: Date.now(),
        type: 'info',
        ...message,
        timestamp: new Date()
      }
      state.messages.push(msg)
    },
    
    REMOVE_MESSAGE(state, messageId) {
      const index = state.messages.findIndex(msg => msg.id === messageId)
      if (index > -1) {
        state.messages.splice(index, 1)
      }
    },
    
    CLEAR_MESSAGES(state) {
      state.messages = []
    }
  },
  
  actions: {
    // 用户认证相关
    async login({ commit }, { token, user }) {
      try {
        // 使用安全的token管理器存储token
        tokenManager.setToken(token, user)
        
        commit('SET_USER', user)
        commit('SET_AUTHENTICATED', true)
        
        return { success: true }
      } catch (error) {
        console.error('登录状态保存失败:', error)
        return { success: false, error: error.message }
      }
    },
    
    async logout({ commit }) {
      try {
        // 清除token
        tokenManager.clearToken()
        
        // 清除状态
        commit('CLEAR_USER')
        commit('CLEAR_SEARCH_PARAMS')
        commit('CLEAR_FLIGHTS')
        commit('CLEAR_BOOKING_INFO')
        commit('CLEAR_MESSAGES')
        
        return { success: true }
      } catch (error) {
        console.error('登出失败:', error)
        return { success: false, error: error.message }
      }
    },
    
    // 检查认证状态
    checkAuth({ commit }) {
      const user = tokenManager.getUser()
      const isAuthenticated = tokenManager.isAuthenticated()
      
      if (isAuthenticated && user) {
        commit('SET_USER', user)
        commit('SET_AUTHENTICATED', true)
      } else {
        commit('CLEAR_USER')
      }
      
      return isAuthenticated
    },
    
    // 搜索相关
    updateSearchParams({ commit }, params) {
      commit('SET_SEARCH_PARAMS', params)
    },
    
    async searchFlights({ commit, state }, searchParams = null) {
      commit('SET_LOADING', true)
      
      try {
        const params = searchParams || state.searchParams
        
        // 调用真实API搜索航班
        const response = await api.flights.search({
          departure_city: params.departureCity || params.from,
          arrival_city: params.arrivalCity || params.to,
          departure_date: params.departureDate || params.date,
          min_price: params.minPrice,
          max_price: params.maxPrice,
          available_seats: params.passengerCount || 1
        })
        
        // 格式化API返回的数据以适配前端
        const flights = response.map(flight => ({
          id: flight.id,
          flightNumber: flight.flight_number,
          airline: flight.airline_name,
          airlineLogo: flight.airline_logo,
          departureCity: flight.departure_city,
          arrivalCity: flight.arrival_city,
          departureTime: flight.departure_time,
          arrivalTime: flight.arrival_time,
          price: parseFloat(flight.price),
          discount: parseFloat(flight.discount || 1),
          availableSeats: flight.available_seats,
          aircraftType: flight.aircraft_type,
          status: flight.status,
          duration: flight.duration
        }))
        
        commit('SET_FLIGHTS', flights)
        return { success: true, flights }
        
      } catch (error) {
        console.error('航班搜索失败:', error)
        commit('ADD_MESSAGE', {
          type: 'error',
          content: '航班搜索失败，请稍后重试'
        })
        return { success: false, error: error.message }
      } finally {
        commit('SET_LOADING', false)
      }
    },
    
    // 预订相关
    selectFlight({ commit }, flight) {
      commit('SET_SELECTED_FLIGHT', flight)
    },
    
    addPassenger({ commit }, passenger) {
      commit('ADD_PASSENGER', passenger)
    },
    
    updateContactInfo({ commit }, contactInfo) {
      commit('SET_CONTACT_INFO', contactInfo)
    },
    
    // 消息系统
    showMessage({ commit }, message) {
      commit('ADD_MESSAGE', message)
      
      // 自动清除消息（可选）
      if (message.autoClose !== false) {
        setTimeout(() => {
          commit('REMOVE_MESSAGE', message.id)
        }, message.duration || 5000)
      }
    },
    
    hideMessage({ commit }, messageId) {
      commit('REMOVE_MESSAGE', messageId)
    }
  },
  
  modules: {
    // 可以添加模块化的状态管理
  }
})
