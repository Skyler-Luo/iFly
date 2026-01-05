import axios from 'axios'
import { ElMessage } from 'element-plus'
import tokenManager from '@/utils/tokenManager'

// 从环境变量获取API配置
const API_BASE_URL =
  process.env.VUE_APP_API_BASE_URL || 'http://127.0.0.1:8000/api'
const API_TIMEOUT = parseInt(process.env.VUE_APP_API_TIMEOUT) || 10000

// API基础配置
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
    Accept: 'application/json'
  }
})

// 创建一个用于文件上传的客户端实例
const uploadClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: API_TIMEOUT * 3, // 文件上传需要更长时间
  headers: {
    'Content-Type': 'multipart/form-data'
  }
})

// 通用请求拦截器配置
const setupRequestInterceptor = client => {
  return client.interceptors.request.use(
    config => {
      const token = tokenManager.getToken()
      if (token) {
        config.headers['Authorization'] = `Token ${token}`
        // 刷新token过期时间
        tokenManager.refreshToken()
      }
      return config
    },
    error => {
      return Promise.reject(error)
    }
  )
}

// 通用响应拦截器配置
const setupResponseInterceptor = client => {
  return client.interceptors.response.use(
    response => {
      // 成功响应直接返回数据
      return response.data || response
    },
    error => {
      // 统一错误处理
      const { response, request, message } = error

      if (response) {
        // 服务器响应了错误状态码
        const { status, data } = response

        switch (status) {
          case 401:
            // 未授权，清除token并跳转到登录页
            tokenManager.clearToken()
            ElMessage.error('登录已过期，请重新登录')
            if (window.location.pathname !== '/login') {
              window.location.href = '/#/login'
            }
            break
          case 403:
            ElMessage.error('权限不足，无法访问')
            break
          case 404:
            ElMessage.error('请求的资源不存在')
            break
          case 422: {
            // 表单验证错误
            const errorMsg = data?.detail || data?.message || '表单验证失败'
            ElMessage.error(errorMsg)
            break
          }
          case 429:
            ElMessage.error('请求过于频繁，请稍后再试')
            break
          case 500:
            ElMessage.error('服务器内部错误，请稍后再试')
            break
          default: {
            const defaultMsg =
              data?.error ||
              data?.detail ||
              data?.message ||
              `请求失败 (${status})`
            ElMessage.error(defaultMsg)
            break
          }
        }

        // 返回标准化的错误对象
        return Promise.reject({
          status,
          message: data?.error || data?.detail || data?.message || message,
          data: data
        })
      } else if (request) {
        // 网络错误
        ElMessage.error('网络连接异常，请检查网络设置')
        return Promise.reject({
          status: 0,
          message: '网络连接异常',
          data: null
        })
      } else {
        // 其他错误
        ElMessage.error('请求失败，请稍后再试')
        return Promise.reject({
          status: -1,
          message: message || '请求失败',
          data: null
        })
      }
    }
  )
}

// 为两个客户端设置拦截器
setupRequestInterceptor(apiClient)
setupResponseInterceptor(apiClient)
setupRequestInterceptor(uploadClient)
setupResponseInterceptor(uploadClient)

// API模块
const api = {
  // 用户认证相关
  auth: {
    login: credentials => apiClient.post('/accounts/login/', credentials),
    register: userData => apiClient.post('/accounts/register/', userData),
    logout: () => apiClient.post('/accounts/logout/'),
    getProfile: () => apiClient.get('/accounts/profile/'),
    updateProfile: data => apiClient.put('/accounts/profile/update/', data),
    uploadAvatar: formData =>
      uploadClient.put('/accounts/profile/update/', formData),
    changePassword: data =>
      apiClient.put('/accounts/profile/change-password/', data)
  },

  // 航班相关
  flights: {
    // 获取航班列表（支持筛选）
    getList: params => apiClient.get('/flights/', { params }),
    // 搜索航班
    search: params => apiClient.get('/flights/search/', { params }),
    // 获取航班详情
    getDetail: flightId => apiClient.get(`/flights/${flightId}/`),
    // 获取可用座位
    getAvailableSeats: (flightId, params) => {
      if (!flightId || flightId === 'undefined') {
        return Promise.reject({
          status: 400,
          message: '无效的航班ID',
          data: null
        })
      }
      return apiClient.get(`/flights/${flightId}/seats/`, { params })
    },
    // 获取票价信息
    getFare: (flightId, params) =>
      apiClient.get(`/flights/${flightId}/fare/`, { params }),
    // 获取预订信息
    getBookingInfo: (flightId, params) => {
      if (!flightId || flightId === 'undefined') {
        return Promise.reject({
          status: 400,
          message: '无效的航班ID',
          data: null
        })
      }
      return apiClient.get(`/flights/${flightId}/booking_info/`, { params })
    },
    // 更新航班价格（管理员）
    updatePrice: (flightId, data) =>
      apiClient.patch(`/flights/${flightId}/`, data)
  },

  // 乘客相关
  passengers: {
    getAll: () => apiClient.get('/accounts/passengers/'),
    create: data => apiClient.post('/accounts/passengers/', data),
    getById: id => apiClient.get(`/accounts/passengers/${id}/`),
    update: (id, data) => apiClient.put(`/accounts/passengers/${id}/`, data),
    delete: id => apiClient.delete(`/accounts/passengers/${id}/`)
  },

  // 订单相关
  orders: {
    create: orderData => apiClient.post('/bookings/orders/', orderData),
    getList: params => apiClient.get('/bookings/orders/', { params }),
    getDetail: orderId => {
      if (!orderId) {
        return Promise.reject({
          status: 400,
          message: '订单ID不能为空',
          data: null
        })
      }
      return apiClient.get(`/bookings/orders/${orderId}/`)
    },
    cancel: orderId => apiClient.post(`/bookings/orders/${orderId}/cancel/`),
    pay: (orderId, paymentData) =>
      apiClient.post(`/bookings/orders/${orderId}/pay/`, paymentData),
    updateStatus: (orderId, data) =>
      apiClient.patch(`/bookings/orders/${orderId}/status/`, data)
  },

  // 机票相关
  tickets: {
    getAll: params => apiClient.get('/bookings/tickets/', { params }),
    getById: id => apiClient.get(`/bookings/tickets/${id}/`),
    refund: id => apiClient.post(`/bookings/tickets/${id}/refund/`),
    // 值机搜索（通过票号和证件号）
    searchForCheckin: data =>
      apiClient.post('/bookings/tickets/search-for-checkin/', data),
    // 值机相关
    getCheckinInfo: id =>
      apiClient.get(`/bookings/tickets/${id}/checkin_info/`),
    checkin: (id, data) =>
      apiClient.post(`/bookings/tickets/${id}/checkin/`, data),
    getBoardingPass: id =>
      apiClient.get(`/bookings/tickets/${id}/boarding-pass/`),
    // 改签相关
    getAvailableFlights: id =>
      apiClient.get(`/bookings/tickets/${id}/available-flights/`),
    getReschedulePreview: (id, data) =>
      apiClient.post(`/bookings/tickets/${id}/reschedule/preview/`, data),
    reschedule: (id, data) =>
      apiClient.post(`/bookings/tickets/${id}/reschedule/`, data)
  },

  // 用户消息/通知相关 (notifications 应用)
  userMessages: {
    getMessages: params => apiClient.get('/notifications/', { params }),
    getDetail: messageId => apiClient.get(`/notifications/${messageId}/`),
    markAsRead: (messageId, isRead = true) =>
      apiClient.post(`/notifications/${messageId}/${isRead ? 'mark_read' : 'mark_unread'}/`),
    deleteMessage: messageId => apiClient.delete(`/notifications/${messageId}/`),
    markAllAsRead: () => apiClient.post('/notifications/read_all/'),
    deleteMultiple: messageIds =>
      apiClient.post('/notifications/delete_multiple/', { message_ids: messageIds }),
    getUnreadCount: () => apiClient.get('/notifications/unread_count/')
  },

  // 核心数据相关
  core: {
    getCities: () => apiClient.get('/core/cities/')
  },

  // 推荐相关
  recommendations: {
    getRouteRecommendations: params =>
      apiClient.get('/analytics/recommendations/routes/', { params })
  },

  // 管理员相关
  admin: {
    // 仪表盘数据
    getDashboardStats: params =>
      apiClient.get('/analytics/admin/dashboard/stats/', { params }),

    // 航班管理
    flights: {
      getList: params => apiClient.get('/admin/flights/', { params }),
      getDetail: flightId => apiClient.get(`/admin/flights/${flightId}/`),
      create: data => apiClient.post('/admin/flights/', data),
      update: (flightId, data) =>
        apiClient.put(`/admin/flights/${flightId}/`, data),
      delete: flightId => apiClient.delete(`/admin/flights/${flightId}/`),
      updateStatus: (flightId, status) =>
        apiClient.patch(`/admin/flights/${flightId}/status/`, { status }),
      getPassengers: (flightId, params) =>
        apiClient.get(`/admin/flights/${flightId}/passengers/`, { params }),
      getPricing: flightId =>
        apiClient.get(`/admin/flights/${flightId}/pricing/`),
      updatePricing: (flightId, data) =>
        apiClient.put(`/admin/flights/${flightId}/pricing/`, data)
    },

    // 用户管理
    users: {
      getList: params => apiClient.get('/admin/users/', { params }),
      getDetail: userId => apiClient.get(`/admin/users/${userId}/`),
      create: data => apiClient.post('/admin/users/', data),
      update: (userId, data) => apiClient.put(`/admin/users/${userId}/`, data),
      delete: userId => apiClient.delete(`/admin/users/${userId}/`),
      updateStatus: (userId, status) =>
        apiClient.patch(`/admin/users/${userId}/status/`, { status }),
      resetPassword: userId =>
        apiClient.post(`/admin/users/${userId}/reset_password/`),
      getUserOrders: (userId, params) =>
        apiClient.get(`/admin/users/${userId}/orders/`, { params }),
      sendNotification: (userId, data) =>
        apiClient.post(`/admin/users/${userId}/send_notification/`, data)
    },

    // 订单管理
    orders: {
      getList: params => apiClient.get('/admin/orders/', { params }),
      getDetail: orderId => apiClient.get(`/admin/orders/${orderId}/`),
      update: (orderId, data) =>
        apiClient.put(`/admin/orders/${orderId}/`, data),
      updateStatus: (orderId, status) =>
        apiClient.patch(`/admin/orders/${orderId}/status/`, { status }),
      refund: (orderId, data) =>
        apiClient.post(`/admin/orders/${orderId}/refund/`, data),
      getPaymentInfo: orderId =>
        apiClient.get(`/admin/orders/${orderId}/payment/`)
    },

    // 系统设置
    settings: {
      get: () => apiClient.get('/admin/settings/'),
      update: data => apiClient.put('/admin/settings/', data),
      getSiteInfo: () => apiClient.get('/admin/settings/site-info/'),
      updateSiteInfo: data => apiClient.put('/admin/settings/site-info/', data),
      getPaymentSettings: () => apiClient.get('/admin/settings/payment/'),
      updatePaymentSettings: data =>
        apiClient.put('/admin/settings/payment/', data),
      // 站点设置 - Requirements 6.2, 6.3
      getSiteSettings: () => apiClient.get('/admin/settings/site/'),
      updateSiteSettings: data => apiClient.put('/admin/settings/site/', data),
      // 业务规则设置 - Requirements 6.2, 6.3
      getBusinessRules: () => apiClient.get('/admin/settings/business/'),
      updateBusinessRules: data =>
        apiClient.put('/admin/settings/business/', data),
      // 设置变更历史 - Requirements 6.2, 6.3
      getSettingsHistory: params =>
        apiClient.get('/admin/settings/history/', { params })
    },

    // 报表和统计
    reports: {
      getSalesReport: params => apiClient.get('/analytics/sales/', { params }),
      getUserReport: params =>
        apiClient.get('/analytics/visualization/user-analytics/', { params }),
      getFlightReport: params =>
        apiClient.get('/analytics/flights/', { params }),
      exportReport: (type, params) =>
        apiClient.get(`/admin/reports/${type}/export/`, {
          params,
          responseType: 'blob'
        })
    },

    // 系统日志
    logs: {
      getSystemLogs: params => apiClient.get('/analytics/logs/', { params }),
      getUserActivityLogs: params =>
        apiClient.get('/analytics/logs/', { params }),
      getErrorLogs: params => apiClient.get('/analytics/logs/', { params })
    },

    // 数据分析相关
    analytics: {
      // 收入分析
      getRevenueAnalytics: params =>
        apiClient.get('/analytics/revenue/', { params }),
      // 航班分析
      getFlightStats: params =>
        apiClient.get('/analytics/flights/', { params }),
      // 数据可视化
      getVisualizationData: params =>
        apiClient.get('/analytics/visualization/', { params }),
      getSalesTrend: params =>
        apiClient.get('/analytics/visualization/sales-trend/', { params }),
      getUserAnalytics: params =>
        apiClient.get('/analytics/visualization/user-analytics/', { params }),
      getFlightAnalytics: params =>
        apiClient.get('/analytics/visualization/flight-analytics/', { params }),

      // 商业智能
      getBusinessIntelligence: params =>
        apiClient.get('/analytics/business-intelligence/', { params }),
      getRouteAnalytics: params =>
        apiClient.get('/analytics/business-intelligence/route-analytics/', {
          params
        }),
      // 多维度分析 - Requirements 7.3
      getMultiDimensionData: params =>
        apiClient.get('/analytics/business-intelligence/multi-dimension/', {
          params
        }),
      // 多维度分析 POST 接口 - Requirements 3.1-3.7, 7.3
      getMultiDimensionAnalysis: data =>
        apiClient.post('/analytics/business-intelligence/multi-dimension/', data),

      // 透视表 - Requirements 4.1-4.5, 7.3
      getPivotData: data =>
        apiClient.post('/analytics/pivot-data/', data),
      // 透视表导出 CSV - Requirements 4.5, 7.6
      exportPivotData: data =>
        apiClient.post('/analytics/pivot-data/export/', data, {
          responseType: 'blob'
        }),

      // 趋势分析 - Requirements 5.1-5.5, 7.3
      getTrends: params =>
        apiClient.get('/analytics/business-intelligence/trends/', { params }),

      // 综合分析
      getAnalyticsOverview: params =>
        apiClient.get('/analytics/overview/', { params }),
      getSalesAnalytics: params =>
        apiClient.get('/analytics/sales/', { params }),
      getCustomerSegments: params =>
        apiClient.get('/analytics/customers/segments/', { params }),
      getCustomerLoyalty: params =>
        apiClient.get('/analytics/customers/loyalty/', { params }),
      getRouteMap: params =>
        apiClient.get('/analytics/routes/map/', { params }),
      getPivotTableData: params =>
        apiClient.get('/analytics/pivot-data/', { params }),
      getRealtimeData: () => apiClient.get('/analytics/realtime/')
    }
  }
}

export default api
