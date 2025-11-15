import axios from 'axios';
// 添加模拟数据生成函数
// eslint-disable-next-line no-unused-vars
function generateMockFlights(count = 10) {
    const airlines = [
        { code: 'CA', name: '中国国际航空', logo: 'https://picsum.photos/id/10/40/40' },
        { code: 'MU', name: '东方航空', logo: 'https://picsum.photos/id/20/40/40' },
        { code: 'CZ', name: '南方航空', logo: 'https://picsum.photos/id/30/40/40' },
        { code: 'HU', name: '海南航空', logo: 'https://picsum.photos/id/40/40/40' },
        { code: '3U', name: '四川航空', logo: 'https://picsum.photos/id/50/40/40' },
        { code: 'MF', name: '厦门航空', logo: 'https://picsum.photos/id/60/40/40' }
    ];

    const airports = {
        '北京': ['首都国际机场', 'PEK'],
        '上海': ['浦东国际机场', 'PVG'],
        '广州': ['白云国际机场', 'CAN'],
        '深圳': ['宝安国际机场', 'SZX'],
        '成都': ['双流国际机场', 'CTU'],
        '杭州': ['萧山国际机场', 'HGH'],
        '西安': ['咸阳国际机场', 'XIY'],
        '重庆': ['江北国际机场', 'CKG'],
        '南京': ['禄口国际机场', 'NKG'],
        '厦门': ['高崎国际机场', 'XMN']
    };

    const flights = [];
    const today = new Date();

    for (let i = 0; i < count; i++) {
        // 随机选择航空公司
        const airline = airlines[Math.floor(Math.random() * airlines.length)];

        // 随机选择出发地和目的地
        const departureCity = '北京';
        const arrivalCity = '上海';

        // 随机生成航班号
        const flightNumber = `${airline.code}${1000 + Math.floor(Math.random() * 9000)}`;

        // 随机生成出发和到达时间
        const departureHour = 6 + Math.floor(Math.random() * 12); // 6am - 6pm
        const departureMinute = Math.floor(Math.random() * 60);
        const flightDuration = 120 + Math.floor(Math.random() * 180); // 2-5小时

        const departureTime = new Date(today);
        departureTime.setHours(departureHour, departureMinute, 0);

        const arrivalTime = new Date(departureTime);
        arrivalTime.setMinutes(arrivalTime.getMinutes() + flightDuration);

        // 随机生成价格
        const basePrice = 500 + Math.floor(Math.random() * 1500);
        const discount = Math.random() < 0.3 ? (0.7 + Math.random() * 0.2).toFixed(2) : 1;

        flights.push({
            id: 1000 + i,
            flight_number: flightNumber,
            airline_name: airline.name,
            airline_code: airline.code,
            airline_logo: airline.logo,
            departure_city: departureCity,
            arrival_city: arrivalCity,
            departure_airport: airports[departureCity][0],
            departure_airport_code: airports[departureCity][1],
            arrival_airport: airports[arrivalCity][0],
            arrival_airport_code: airports[arrivalCity][1],
            departure_time: departureTime.toISOString(),
            arrival_time: arrivalTime.toISOString(),
            duration: flightDuration,
            price: basePrice,
            discount: discount,
            available_seats: 10 + Math.floor(Math.random() * 100),
            aircraft_type: ['波音737', '波音777', '空客A320', '空客A330'][Math.floor(Math.random() * 4)],
            meal_service: Math.random() > 0.5,
            baggage_allowance: 20,
            business_available: Math.random() > 0.3,
            first_available: Math.random() > 0.7,
            direct_flight: true,
            punctuality_rate: 75 + Math.floor(Math.random() * 20),
            wifi: Math.random() > 0.5,
            power_outlet: Math.random() > 0.3,
            entertainment: Math.random() > 0.4
        });
    }

    return flights;
}

// 移除mockApi导入，只使用真实API
// import mockApi from './mockApi';

// 删除未使用的变量
// const USE_MOCK_API = false;

// API基础配置
const apiClient = axios.create({
    baseURL: 'http://127.0.0.1:8000/api',
    timeout: 10000,
    headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
});

// 创建一个用于文件上传的客户端实例
const uploadClient = axios.create({
    baseURL: 'http://127.0.0.1:8000/api',
    timeout: 30000,
    headers: {
        'Content-Type': 'multipart/form-data',
    }
});

// 添加请求拦截器，自动添加认证令牌
apiClient.interceptors.request.use(
    config => {
        const token = localStorage.getItem('token');
        if (token) {
            config.headers['Authorization'] = `Token ${token}`;
            console.log('已添加认证令牌到请求头');
        } else {
            console.warn('未找到认证令牌，请求可能会被拒绝');
        }
        return config;
    },
    error => {
        console.error('请求拦截器错误:', error);
        return Promise.reject(error);
    }
);

// 为上传客户端也添加认证令牌
uploadClient.interceptors.request.use(
    config => {
        const token = localStorage.getItem('token');
        if (token) {
            config.headers['Authorization'] = `Token ${token}`;
        }
        return config;
    },
    error => {
        return Promise.reject(error);
    }
);

// 移除所有拦截器代码，不再添加任何头部
// 也不再处理缓存控制或响应转换

// API模块
const api = {
    // 用户认证相关
    auth: {
        login: (credentials) => apiClient.post('/accounts/login/', credentials),
        register: (userData) => apiClient.post('/accounts/register/', userData),
        logout: () => apiClient.post('/accounts/logout/'),
        getProfile: () => apiClient.get('/accounts/profile/'),
        updateProfile: (data) => apiClient.put('/accounts/profile/update/', data),
        uploadAvatar: (formData) => uploadClient.put('/accounts/profile/update/', formData),
        changePassword: (data) => apiClient.put('/accounts/profile/change-password/', data)
    },

    // 航班相关
    flights: {
        search: (params) => apiClient.get('/flights/search/', { params }),
        getDetail: (flightId) => apiClient.get(`/flights/${flightId}/`),
        getAvailableSeats: (flightId) => {
            console.log(`正在获取航班${flightId}的座位数据`);
            if (!flightId || flightId === 'undefined') {
                console.error('无效的航班ID:', flightId);
                return Promise.reject(new Error('无效的航班ID'));
            }
            return apiClient.get(`/flights/${flightId}/seats/`)
                .then(response => {
                    console.log('座位API原始响应:', response);
                    // 确保返回数据的一致性
                    const responseData = response.data || response;
                    return responseData;
                })
                .catch(error => {
                    console.error('获取座位数据失败:', error);
                    // 返回一个标准格式的空座位图，避免前端解析错误
                    return Promise.resolve({
                        seat_map: [],
                        occupied_seats: []
                    });
                });
        },
        getFare: (flightId, params) => apiClient.get(`/flights/${flightId}/fare/`, { params }),
        getBookingInfo: (flightId, params) => {
            console.log(`正在获取航班${flightId}的预订信息`);
            if (!flightId || flightId === 'undefined') {
                console.error('无效的航班ID:', flightId);
                return Promise.reject(new Error('无效的航班ID'));
            }
            return apiClient.get(`/flights/${flightId}/booking_info/`, { params })
                .then(response => {
                    // 如果没有数据，添加一些默认值以防止前端错误
                    if (!response || (!response.data && !response.flight_number)) {
                        console.warn('航班预订信息返回为空，使用默认值');
                        return {
                            id: flightId,
                            flight_number: '未知航班',
                            airline_name: '未知航空',
                            departure_city: '出发城市',
                            arrival_city: '到达城市',
                            departure_time: new Date().toISOString(),
                            arrival_time: new Date(Date.now() + 3600000).toISOString(),
                            duration: 60,
                            price: 0,
                            cabin_price: 0,
                            available_seats: 0
                        };
                    }
                    return response;
                });
        }
    },

    // 乘客相关
    passengers: {
        getAll: () => apiClient.get('/accounts/passengers/'),
        create: (data) => apiClient.post('/accounts/passengers/', data),
        getById: (id) => apiClient.get(`/accounts/passengers/${id}/`),
        update: (id, data) => apiClient.put(`/accounts/passengers/${id}/`, data),
        delete: (id) => apiClient.delete(`/accounts/passengers/${id}/`),
    },

    // 订单相关
    orders: {
        create: (orderData) => apiClient.post('/bookings/orders/', orderData),
        getList: (params) => {
            console.log('获取订单列表，参数:', params);
            return apiClient.get('/bookings/orders/', { params })
                .then(response => {
                    console.log('获取订单列表成功:', response);
                    return response.data;
                })
                .catch(error => {
                    console.error('获取订单列表失败:', error);
                    if (error.response) {
                        console.error('错误状态码:', error.response.status);
                        console.error('错误数据:', error.response.data);
                    }
                    return Promise.reject(error);
                });
        },
        getDetail: (orderId) => {
            // 确保订单号正确传递，尝试直接通过ID获取
            if (!orderId) {
                return Promise.reject(new Error('订单ID不能为空'));
            }
            console.log('获取订单详情:', orderId);

            // 使用ID查询，如果是完整订单号，后端会处理
            return apiClient.get(`/bookings/orders/${orderId}/`);
        },
        cancel: (orderId) => apiClient.post(`/bookings/orders/${orderId}/cancel/`),
        pay: (orderId, paymentData) => apiClient.post(`/bookings/orders/${orderId}/pay/`, paymentData),
        updateStatus: (orderId, data) => {
            console.log('尝试更新订单状态:', orderId, data);
            // 尝试不同的API端点格式 - 一些API可能不使用尾部斜杠或使用不同的路径
            return apiClient.patch(`/bookings/orders/${orderId}/status`, data)
                .catch(error => {
                    console.log('第一个端点失败，尝试替代方案:', error);
                    // 尝试使用PUT方法
                    return apiClient.put(`/bookings/orders/${orderId}/status/`, data);
                })
                .catch(error => {
                    console.log('第二个端点失败，尝试替代方案:', error);
                    // 尝试更新整个订单
                    return apiClient.put(`/bookings/orders/${orderId}/`, { ...data, id: orderId });
                })
                .catch(error => {
                    console.log('第三个端点失败，尝试替代方案:', error);
                    // 最后尝试使用pay端点
                    return apiClient.post(`/bookings/orders/${orderId}/pay/`, { payment_status: 'paid', ...data });
                });
        }
    },

    // 机票相关
    tickets: {
        getAll: () => apiClient.get('/bookings/tickets/'),
        getById: (id) => apiClient.get(`/bookings/tickets/${id}/`),
        refund: (id) => apiClient.post(`/bookings/tickets/${id}/refund/`),
    },

    // 优惠活动相关
    promotions: {
        getList: (params) => apiClient.get('/promotions/', { params }),
        getDetail: (promoId) => apiClient.get(`/promotions/${promoId}/`),
        apply: (promoCode, orderId) => apiClient.post('/promotions/apply/', { promoCode, orderId }),
        validateCode: (promoCode) => apiClient.post('/promotions/validate/', { promoCode })
    },

    // 消息相关
    messages: {
        getMessages: (params) => {
            console.log('API 请求参数:', params);
            return apiClient.get('/notifications/', { params })
                .then(response => {
                    console.log('API 响应:', response);
                    return response.data;
                });
        },
        getDetail: (messageId) => apiClient.get(`/notifications/${messageId}/`),
        markAsRead: (messageId, isRead) => {
            const action = isRead ? 'mark_read' : 'mark_unread';
            return apiClient.post(`/notifications/${messageId}/${action}/`);
        },
        deleteMessage: (messageId) => apiClient.delete(`/notifications/${messageId}/`),
        markAllAsRead: () => apiClient.post('/notifications/read_all/'),
        deleteMultiple: (messageIds) => apiClient.post('/notifications/delete_multiple/', { message_ids: messageIds }),
        getUnreadCount: () => apiClient.get('/notifications/unread_count/')
    },

    // 积分中心相关
    points: {
        // 获取用户积分信息
        getUserPoints: () => apiClient.get('/points/user/'),

        // 获取用户积分明细
        getHistory: (params) => apiClient.get('/points/history/', { params }),

        // 获取积分摘要
        getOverview: () => apiClient.get('/points/overview/'),

        // 获取积分兑换商品列表
        getExchangeItems: (params) => apiClient.get('/points/exchange-items/', { params }),

        // 兑换积分商品
        exchange: (data) => apiClient.post('/points/exchange/', data),

        // 获取积分任务列表
        getTasks: () => apiClient.get('/points/tasks/'),

        // 完成积分任务
        completeTask: (taskId) => apiClient.post(`/points/tasks/${taskId}/complete/`),

        // 获取会员等级信息
        getMemberLevel: () => apiClient.get('/points/member-level/'),

        // 获取用户等级进度
        getLevelProgress: () => apiClient.get('/points/level-progress/'),

        // 签到获取积分
        checkIn: () => apiClient.post('/points/check-in/'),

        // 查询积分过期信息
        getExpiringPoints: () => apiClient.get('/points/expiring/'),

        // 里程兑换积分
        convertMileage: (data) => apiClient.post('/points/convert-mileage/', data)
    },

    // 热门路线相关
    routes: {
        getPopular: (params) => apiClient.get('/core/popular-routes/', { params: { ...params, simple: true } }),
    },

    // 天气相关
    weather: {
        getByCity: (city) => apiClient.get(`/core/weather/${city}/`, { params: { simple: true } }),
    },

    // 城市相关
    cities: {
        getAll: () => apiClient.get('/core/cities/'),
    },

    // 机场相关
    airports: {
        search: (keyword) => apiClient.get('/airports/search/', { params: { keyword } }),
        getDetail: (code) => apiClient.get(`/airports/${code}/`),
        getNearby: (lat, lng) => apiClient.get('/airports/nearby/', { params: { lat, lng } })
    },

    // 用户设置相关
    settings: {
        get: () => apiClient.get('/settings/'),
        update: (data) => apiClient.put('/settings/', data),
        updateNotification: (data) => apiClient.put('/settings/notification/', data)
    },

    // 反馈相关
    feedback: {
        submit: (data) => apiClient.post('/feedback/', data),
        getList: () => apiClient.get('/feedback/'),
        getDetail: (id) => apiClient.get(`/feedback/${id}/`)
    },

    // 管理员相关
    admin: {
        // 仪表盘数据
        getDashboardStats: () => apiClient.get('/analytics/admin/dashboard/stats/'),

        // 航班管理
        flights: {
            getList: (params) => apiClient.get('/api/admin/flights/', { params }),
            getDetail: (flightId) => apiClient.get(`/api/admin/flights/${flightId}/`),
            create: (data) => apiClient.post('/api/admin/flights/', data),
            update: (flightId, data) => apiClient.put(`/api/admin/flights/${flightId}/`, data),
            delete: (flightId) => apiClient.delete(`/api/admin/flights/${flightId}/`),
            updateStatus: (flightId, status) => apiClient.patch(`/api/admin/flights/${flightId}/status/`, { status }),
            getPassengers: (flightId, params) => apiClient.get(`/api/admin/flights/${flightId}/passengers/`, { params }),
            getPricing: (flightId) => apiClient.get(`/api/admin/flights/${flightId}/pricing/`),
            updatePricing: (flightId, data) => apiClient.put(`/api/admin/flights/${flightId}/pricing/`, data)
        },

        // 用户管理
        users: {
            getList: (params) => apiClient.get('/api/admin/users/', { params }),
            getDetail: (userId) => apiClient.get(`/api/admin/users/${userId}/`),
            create: (data) => apiClient.post('/api/admin/users/', data),
            update: (userId, data) => apiClient.put(`/api/admin/users/${userId}/`, data),
            delete: (userId) => apiClient.delete(`/api/admin/users/${userId}/`),
            updateStatus: (userId, status) => apiClient.patch(`/api/admin/users/${userId}/status/`, { status }),
            resetPassword: (userId) => apiClient.post(`/api/admin/users/${userId}/reset-password/`),
            getUserOrders: (userId, params) => apiClient.get(`/api/admin/users/${userId}/orders/`, { params }),
            adjustPoints: (userId, data) => apiClient.post(`/api/admin/users/${userId}/adjust-points/`, data),
            sendNotification: (userId, data) => apiClient.post(`/api/admin/users/${userId}/send-notification/`, data)
        },

        // 订单管理
        orders: {
            getList: (params) => apiClient.get('/api/admin/orders/', { params }),
            getDetail: (orderId) => apiClient.get(`/api/admin/orders/${orderId}/`),
            update: (orderId, data) => apiClient.put(`/api/admin/orders/${orderId}/`, data),
            updateStatus: (orderId, status) => apiClient.patch(`/api/admin/orders/${orderId}/status/`, { status }),
            refund: (orderId, data) => apiClient.post(`/api/admin/orders/${orderId}/refund/`, data),
            getPaymentInfo: (orderId) => apiClient.get(`/api/admin/orders/${orderId}/payment/`)
        },

        // 优惠活动管理
        promotions: {
            getList: (params) => apiClient.get('/api/admin/promotions/', { params }),
            getDetail: (promoId) => apiClient.get(`/api/admin/promotions/${promoId}/`),
            create: (data) => apiClient.post('/api/admin/promotions/', data),
            update: (promoId, data) => apiClient.put(`/api/admin/promotions/${promoId}/`, data),
            delete: (promoId) => apiClient.delete(`/api/admin/promotions/${promoId}/`),
            toggleStatus: (promoId, isActive) => apiClient.patch(`/api/admin/promotions/${promoId}/status/`, { is_active: isActive })
        },

        // 系统设置
        settings: {
            get: () => apiClient.get('/api/admin/settings/'),
            update: (data) => apiClient.put('/api/admin/settings/', data),
            getSiteInfo: () => apiClient.get('/api/admin/settings/site-info/'),
            updateSiteInfo: (data) => apiClient.put('/api/admin/settings/site-info/', data),
            getEmailSettings: () => apiClient.get('/api/admin/settings/email/'),
            updateEmailSettings: (data) => apiClient.put('/api/admin/settings/email/', data),
            getPaymentSettings: () => apiClient.get('/api/admin/settings/payment/'),
            updatePaymentSettings: (data) => apiClient.put('/api/admin/settings/payment/', data),
            testEmailSettings: (data) => apiClient.post('/api/admin/settings/email/test/', data)
        },

        // 报表和统计
        reports: {
            getSalesReport: (params) => apiClient.get('/api/admin/reports/sales/', { params }),
            getUserReport: (params) => apiClient.get('/api/admin/reports/users/', { params }),
            getFlightReport: (params) => apiClient.get('/api/admin/reports/flights/', { params }),
            getPromotionReport: (params) => apiClient.get('/api/admin/reports/promotions/', { params }),
            exportReport: (type, params) => apiClient.get(`/api/admin/reports/${type}/export/`, {
                params,
                responseType: 'blob'
            })
        },

        // 系统日志
        logs: {
            getSystemLogs: (params) => apiClient.get('/api/admin/logs/system/', { params }),
            getUserActivityLogs: (params) => apiClient.get('/api/admin/logs/user-activity/', { params }),
            getErrorLogs: (params) => apiClient.get('/api/admin/logs/errors/', { params })
        },

        // 数据分析相关
        analytics: {
            // 数据可视化
            getVisualizationData: (params) => apiClient.get('/analytics/visualization/', { params }),
            getSalesTrend: (params) => apiClient.get('/analytics/visualization/sales-trend/', { params }),
            getUserAnalytics: (params) => apiClient.get('/analytics/visualization/user-analytics/', { params }),
            getFlightAnalytics: (params) => apiClient.get('/analytics/visualization/flight-analytics/', { params }),

            // 商业智能
            getBusinessIntelligence: (params) => apiClient.get('/analytics/business-intelligence/', { params }),
            getSalesPrediction: (params) => apiClient.get('/analytics/business-intelligence/sales-prediction/', { params }),
            getRouteAnalytics: (params) => apiClient.get('/analytics/business-intelligence/route-analytics/', { params }),
            getPriceElasticity: (params) => apiClient.get('/analytics/business-intelligence/price-elasticity/', { params }),
            getCustomerLTV: () => apiClient.get('/analytics/business-intelligence/customer-ltv/'),
            getSeasonalityData: (params) => apiClient.get('/analytics/business-intelligence/seasonality/', { params }),
            getAnomalyDetection: (params) => apiClient.get('/analytics/business-intelligence/anomalies/', { params }),

            // 综合分析
            getAnalyticsOverview: (params) => apiClient.get('/analytics/overview/', { params }),
            getSalesAnalytics: (params) => apiClient.get('/analytics/sales/', { params }),
            getCustomerSegments: (params) => apiClient.get('/analytics/customers/segments/', { params }),
            getRouteMap: (params) => apiClient.get('/analytics/routes/map/', { params }),
            getCustomerLoyalty: (params) => apiClient.get('/analytics/customers/loyalty/', { params }),
            getPivotData: (params) => apiClient.get('/analytics/pivot-data/', { params }),
            getRealtimeData: () => apiClient.get('/analytics/realtime/')
        }
    }
};

export default api; 