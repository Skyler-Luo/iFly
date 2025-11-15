<template>
    <div class="admin-user-orders">
        <h1 class="title">用户订单管理</h1>

        <div class="user-info">
            <div class="info-card">
                <div class="avatar">
                    <img v-if="user.avatar" :src="user.avatar" alt="用户头像">
                    <div v-else class="avatar-placeholder">
                        {{ getAvatarPlaceholder(user.name) }}
                    </div>
                </div>
                <div class="user-details">
                    <h2>{{ user.name }}</h2>
                    <div class="user-id">ID: {{ user.id }}</div>
                    <div class="user-meta">
                        <div class="meta-item">
                            <i class="fas fa-envelope"></i>
                            {{ user.email }}
                        </div>
                        <div class="meta-item">
                            <i class="fas fa-phone"></i>
                            {{ user.phone }}
                        </div>
                        <div class="meta-item">
                            <i class="fas fa-calendar"></i>
                            注册时间: {{ formatDate(user.registerDate) }}
                        </div>
                    </div>
                    <div class="user-stats">
                        <div class="stat-item">
                            <div class="stat-value">{{ user.orderCount }}</div>
                            <div class="stat-label">总订单数</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value">{{ formatCurrency(user.totalSpent) }}</div>
                            <div class="stat-label">消费总额</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value">{{ user.points }}</div>
                            <div class="stat-label">积分</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="order-filters">
            <div class="search-box">
                <input type="text" v-model="searchQuery" placeholder="搜索订单号/航班号">
                <button><i class="fas fa-search"></i></button>
            </div>

            <div class="filter-group">
                <select v-model="statusFilter">
                    <option value="">所有状态</option>
                    <option value="pending">待支付</option>
                    <option value="paid">已支付</option>
                    <option value="completed">已完成</option>
                    <option value="cancelled">已取消</option>
                    <option value="refunded">已退款</option>
                </select>
            </div>

            <div class="filter-group">
                <select v-model="dateRangeFilter">
                    <option value="all">所有时间</option>
                    <option value="today">今天</option>
                    <option value="week">本周</option>
                    <option value="month">本月</option>
                    <option value="year">今年</option>
                    <option value="custom">自定义</option>
                </select>
            </div>

            <div class="date-range" v-if="dateRangeFilter === 'custom'">
                <input type="date" v-model="startDate">
                <span>至</span>
                <input type="date" v-model="endDate">
            </div>

            <div class="export-btn">
                <button class="btn btn-secondary">
                    <i class="fas fa-download"></i> 导出订单
                </button>
            </div>
        </div>

        <div class="orders-table">
            <table>
                <thead>
                    <tr>
                        <th>订单号</th>
                        <th>创建时间</th>
                        <th>航班信息</th>
                        <th>乘客信息</th>
                        <th>支付金额</th>
                        <th>支付方式</th>
                        <th>订单状态</th>
                        <th>操作</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="order in filteredOrders" :key="order.id">
                        <td>
                            <div class="order-id">{{ order.orderNumber }}</div>
                            <div class="order-code">{{ order.id }}</div>
                        </td>
                        <td>{{ formatDate(order.createdAt) }}</td>
                        <td>
                            <div class="flight-info">
                                <div class="flight-number">{{ order.flight.flightNumber }}</div>
                                <div class="flight-route">
                                    {{ order.flight.departureCity }} → {{ order.flight.arrivalCity }}
                                </div>
                                <div class="flight-date">{{ formatDate(order.flight.departureTime) }}</div>
                            </div>
                        </td>
                        <td>
                            <div class="passenger-count">{{ order.passengerCount }}名乘客</div>
                            <div class="passenger-list">
                                {{ getPassengerList(order.passengers) }}
                            </div>
                        </td>
                        <td>
                            <div class="order-amount">{{ formatCurrency(order.amount) }}</div>
                        </td>
                        <td>{{ getPaymentMethod(order.paymentMethod) }}</td>
                        <td>
                            <span :class="getOrderStatusClass(order.status)">
                                {{ getOrderStatusText(order.status) }}
                            </span>
                        </td>
                        <td>
                            <button class="action-btn view-btn" @click="viewOrderDetails(order)">
                                <i class="fas fa-eye"></i>
                            </button>
                            <button class="action-btn edit-btn" @click="editOrder(order)">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button class="action-btn" v-if="order.status === 'paid' || order.status === 'pending'"
                                @click="cancelOrder(order)" title="取消订单">
                                <i class="fas fa-ban"></i>
                            </button>
                            <button class="action-btn" v-if="order.status === 'completed'" @click="issueRefund(order)"
                                title="申请退款">
                                <i class="fas fa-undo"></i>
                            </button>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>

        <div class="pagination">
            <button class="prev-btn" :disabled="currentPage === 1" @click="currentPage--">
                <i class="fas fa-chevron-left"></i>
            </button>
            <div class="page-info">
                {{ currentPage }} / {{ totalPages }}
            </div>
            <button class="next-btn" :disabled="currentPage === totalPages" @click="currentPage++">
                <i class="fas fa-chevron-right"></i>
            </button>
        </div>
    </div>
</template>

<script>
export default {
    name: 'AdminUserOrdersView',
    data() {
        return {
            searchQuery: '',
            statusFilter: '',
            dateRangeFilter: 'all',
            startDate: '',
            endDate: '',
            currentPage: 1,
            perPage: 10,
            user: {
                id: '123456',
                name: '张文杰',
                email: 'zhang.wj@example.com',
                phone: '13812345678',
                registerDate: '2022-03-15T10:30:00',
                orderCount: 12,
                totalSpent: 15680.50,
                points: 3500,
                avatar: null
            },
            orders: [
                {
                    id: 'ORD12345678',
                    orderNumber: 'IF-20230510-001',
                    createdAt: '2023-05-10T14:30:00',
                    amount: 1580,
                    paymentMethod: 'alipay',
                    status: 'completed',
                    flight: {
                        flightNumber: 'CA1234',
                        departureCity: '北京',
                        arrivalCity: '上海',
                        departureTime: '2023-05-15T09:30:00'
                    },
                    passengerCount: 1,
                    passengers: [
                        { name: '张文杰', idNumber: '110101199001011234' }
                    ]
                },
                {
                    id: 'ORD23456789',
                    orderNumber: 'IF-20230615-002',
                    createdAt: '2023-06-15T10:15:00',
                    amount: 3560,
                    paymentMethod: 'wechat',
                    status: 'paid',
                    flight: {
                        flightNumber: 'CA5678',
                        departureCity: '北京',
                        arrivalCity: '广州',
                        departureTime: '2023-06-20T14:20:00'
                    },
                    passengerCount: 2,
                    passengers: [
                        { name: '张文杰', idNumber: '110101199001011234' },
                        { name: '李小红', idNumber: '110101199203033456' }
                    ]
                },
                {
                    id: 'ORD34567890',
                    orderNumber: 'IF-20230720-003',
                    createdAt: '2023-07-20T16:45:00',
                    amount: 2100,
                    paymentMethod: 'credit_card',
                    status: 'pending',
                    flight: {
                        flightNumber: 'CA9012',
                        departureCity: '上海',
                        arrivalCity: '成都',
                        departureTime: '2023-07-25T11:00:00'
                    },
                    passengerCount: 1,
                    passengers: [
                        { name: '张文杰', idNumber: '110101199001011234' }
                    ]
                },
                {
                    id: 'ORD45678901',
                    orderNumber: 'IF-20230805-004',
                    createdAt: '2023-08-05T09:20:00',
                    amount: 5200,
                    paymentMethod: 'alipay',
                    status: 'cancelled',
                    flight: {
                        flightNumber: 'CA3456',
                        departureCity: '广州',
                        arrivalCity: '北京',
                        departureTime: '2023-08-10T17:30:00'
                    },
                    passengerCount: 2,
                    passengers: [
                        { name: '张文杰', idNumber: '110101199001011234' },
                        { name: '王小明', idNumber: '110101199505055678' }
                    ]
                },
                {
                    id: 'ORD56789012',
                    orderNumber: 'IF-20230912-005',
                    createdAt: '2023-09-12T13:10:00',
                    amount: 3240,
                    paymentMethod: 'wechat',
                    status: 'refunded',
                    flight: {
                        flightNumber: 'CA7890',
                        departureCity: '成都',
                        arrivalCity: '深圳',
                        departureTime: '2023-09-18T08:45:00'
                    },
                    passengerCount: 1,
                    passengers: [
                        { name: '张文杰', idNumber: '110101199001011234' }
                    ]
                }
            ]
        }
    },
    computed: {
        filteredOrders() {
            let result = [...this.orders];

            // 应用搜索过滤
            if (this.searchQuery) {
                const query = this.searchQuery.toLowerCase();
                result = result.filter(order =>
                    order.orderNumber.toLowerCase().includes(query) ||
                    order.flight.flightNumber.toLowerCase().includes(query)
                );
            }

            // 应用状态过滤
            if (this.statusFilter) {
                result = result.filter(order => order.status === this.statusFilter);
            }

            // 应用日期过滤
            if (this.dateRangeFilter !== 'all') {
                const now = new Date();
                let startOfRange = new Date();

                if (this.dateRangeFilter === 'today') {
                    startOfRange.setHours(0, 0, 0, 0);
                } else if (this.dateRangeFilter === 'week') {
                    startOfRange.setDate(now.getDate() - now.getDay());
                    startOfRange.setHours(0, 0, 0, 0);
                } else if (this.dateRangeFilter === 'month') {
                    startOfRange.setDate(1);
                    startOfRange.setHours(0, 0, 0, 0);
                } else if (this.dateRangeFilter === 'year') {
                    startOfRange.setMonth(0, 1);
                    startOfRange.setHours(0, 0, 0, 0);
                } else if (this.dateRangeFilter === 'custom' && this.startDate && this.endDate) {
                    startOfRange = new Date(this.startDate);
                    const endOfRange = new Date(this.endDate);
                    endOfRange.setHours(23, 59, 59, 999);

                    result = result.filter(order => {
                        const orderDate = new Date(order.createdAt);
                        return orderDate >= startOfRange && orderDate <= endOfRange;
                    });
                    return result;
                }

                result = result.filter(order => {
                    const orderDate = new Date(order.createdAt);
                    return orderDate >= startOfRange;
                });
            }

            return result;
        },
        totalPages() {
            return Math.ceil(this.filteredOrders.length / this.perPage);
        }
    },
    created() {
        // 从路由参数获取用户ID
        const userId = this.$route.params.userId;
        // 实际应用中应该从API获取用户和订单数据
        this.loadUserData(userId);
    },
    methods: {
        formatDate(dateString) {
            const date = new Date(dateString);
            return date.toLocaleDateString('zh-CN');
        },
        formatCurrency(amount) {
            return `¥${amount.toFixed(2)}`;
        },
        getAvatarPlaceholder(name) {
            return name ? name.charAt(0).toUpperCase() : 'U';
        },
        getPaymentMethod(method) {
            const methods = {
                'alipay': '支付宝',
                'wechat': '微信支付',
                'credit_card': '信用卡',
                'points': '积分兑换'
            };
            return methods[method] || method;
        },
        getOrderStatusText(status) {
            const statuses = {
                'pending': '待支付',
                'paid': '已支付',
                'completed': '已完成',
                'cancelled': '已取消',
                'refunded': '已退款'
            };
            return statuses[status] || status;
        },
        getOrderStatusClass(status) {
            return `status-${status}`;
        },
        getPassengerList(passengers) {
            if (!passengers || passengers.length === 0) return '无乘客信息';
            if (passengers.length <= 2) {
                return passengers.map(p => p.name).join(', ');
            }
            return `${passengers[0].name}, ${passengers[1].name} 等${passengers.length}人`;
        },
        loadUserData(userId) {
            // 在实际应用中，这里应该调用API获取用户详情和订单列表
            console.log('正在加载用户ID:', userId);
            // 模拟API加载
            this.user.id = userId;
        },
        viewOrderDetails(order) {
            console.log('查看订单详情:', order);
            // 实际应用中可能会导航到订单详情页或弹出详情模态框
        },
        editOrder(order) {
            console.log('编辑订单:', order);
            // 实际应用中可能会导航到订单编辑页或弹出编辑模态框
        },
        cancelOrder(order) {
            if (confirm(`确定要取消订单 ${order.orderNumber} 吗？`)) {
                console.log('取消订单:', order);
                order.status = 'cancelled';
            }
        },
        issueRefund(order) {
            if (confirm(`确定要为订单 ${order.orderNumber} 申请退款吗？`)) {
                console.log('申请退款:', order);
                order.status = 'refunded';
            }
        }
    }
}
</script>

<style scoped>
.admin-user-orders {
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

.user-info {
    margin-bottom: 20px;
}

.info-card {
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    padding: 15px;
    display: flex;
    align-items: center;
}

.avatar {
    width: 80px;
    height: 80px;
    border-radius: 50%;
    margin-right: 20px;
    overflow: hidden;
}

.avatar img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.avatar-placeholder {
    width: 100%;
    height: 100%;
    background: #3f51b5;
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 32px;
    font-weight: bold;
}

.user-details {
    flex: 1;
}

.user-details h2 {
    margin: 0 0 5px 0;
    font-size: 20px;
}

.user-id {
    font-size: 14px;
    color: #666;
    margin-bottom: 10px;
}

.user-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 15px;
    margin-bottom: 15px;
}

.meta-item {
    font-size: 14px;
    color: #555;
    display: flex;
    align-items: center;
}

.meta-item i {
    margin-right: 5px;
    color: #3f51b5;
}

.user-stats {
    display: flex;
    gap: 20px;
}

.stat-item {
    text-align: center;
    min-width: 80px;
}

.stat-value {
    font-size: 18px;
    font-weight: bold;
    color: #3f51b5;
}

.stat-label {
    font-size: 12px;
    color: #666;
}

.order-filters {
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

.date-range {
    display: flex;
    align-items: center;
    gap: 10px;
}

.date-range input {
    padding: 8px 12px;
    border: 1px solid #ddd;
    border-radius: 4px;
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

.orders-table {
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    overflow: hidden;
    margin-bottom: 20px;
}

.orders-table table {
    width: 100%;
    border-collapse: collapse;
}

.orders-table th {
    background: #f9f9f9;
    padding: 12px 15px;
    text-align: left;
    font-weight: 600;
    color: #333;
}

.orders-table td {
    padding: 12px 15px;
    border-top: 1px solid #eee;
}

.order-id {
    font-weight: bold;
    color: #3f51b5;
}

.order-code {
    font-size: 12px;
    color: #999;
    margin-top: 3px;
}

.flight-info {
    line-height: 1.4;
}

.flight-number {
    font-weight: bold;
}

.flight-route {
    font-size: 13px;
}

.flight-date {
    font-size: 12px;
    color: #666;
}

.passenger-count {
    margin-bottom: 3px;
}

.passenger-list {
    font-size: 12px;
    color: #666;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 200px;
}

.order-amount {
    font-weight: bold;
    color: #3f51b5;
}

.status-pending {
    background: #fff8e1;
    color: #ff6f00;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 12px;
}

.status-paid {
    background: #e8f5e9;
    color: #2e7d32;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 12px;
}

.status-completed {
    background: #e3f2fd;
    color: #1565c0;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 12px;
}

.status-cancelled {
    background: #fafafa;
    color: #757575;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 12px;
}

.status-refunded {
    background: #f3e5f5;
    color: #7b1fa2;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 12px;
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

.view-btn {
    background: #e3f2fd;
    color: #1565c0;
}

.view-btn:hover {
    background: #bbdefb;
}

.edit-btn {
    background: #e8f5e9;
    color: #2e7d32;
}

.edit-btn:hover {
    background: #c8e6c9;
}

.action-btn:nth-child(3) {
    background: #ffebee;
    color: #c62828;
}

.action-btn:nth-child(3):hover {
    background: #ffcdd2;
}

.action-btn:nth-child(4) {
    background: #f3e5f5;
    color: #7b1fa2;
}

.action-btn:nth-child(4):hover {
    background: #e1bee7;
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
    .info-card {
        flex-direction: column;
        text-align: center;
    }

    .avatar {
        margin-right: 0;
        margin-bottom: 15px;
    }

    .user-meta {
        justify-content: center;
    }

    .user-stats {
        justify-content: center;
    }

    .order-filters {
        flex-direction: column;
        align-items: stretch;
    }

    .export-btn {
        margin-left: 0;
    }

    .date-range {
        flex-direction: column;
    }

    .orders-table {
        overflow-x: auto;
    }
}
</style>