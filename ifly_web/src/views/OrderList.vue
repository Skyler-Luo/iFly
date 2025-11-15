<template>
    <div class="order-list-view">
        <div class="header-banner">
            <h1>我的订单</h1>
            <div class="filter-options">
                <el-select v-model="statusFilter" placeholder="订单状态" size="small" clearable>
                    <el-option v-for="item in statusOptions" :key="item.value" :label="item.label"
                        :value="item.value"></el-option>
                </el-select>
                <el-date-picker v-model="dateRange" type="daterange" range-separator="至" start-placeholder="开始日期"
                    end-placeholder="结束日期" size="small"></el-date-picker>
                <el-button type="primary" size="small" @click="searchOrders">查询</el-button>
            </div>
        </div>

        <div class="order-list-container">
            <div v-if="isLoading" class="loading-container">
                <div class="loading-spinner">
                    <i class="el-icon-loading"></i>
                </div>
                <p>正在加载订单数据...</p>
            </div>

            <div v-else-if="orders.length === 0" class="empty-container">
                <i class="el-icon-tickets"></i>
                <h3>暂无订单</h3>
                <p>您还没有预订任何航班</p>
                <el-button type="primary" @click="goToHome">立即预订</el-button>
            </div>

            <div v-else class="order-list">
                <div v-for="order in orders" :key="order.id" class="order-card" @click="goToOrderDetail(order.id)">
                    <div class="order-header">
                        <div class="order-info">
                            <div class="order-number">订单号: {{ order.orderNumber }}</div>
                            <div class="order-time">下单时间: {{ formatDateTime(order.createdAt) }}</div>
                        </div>
                        <div class="order-status" :class="getStatusClass(order.status)">
                            {{ getStatusText(order.status) }}
                        </div>
                    </div>

                    <div class="flight-info">
                        <div v-for="(ticket, index) in order.tickets.slice(0, 1)" :key="index" class="flight-route">
                            <div class="cities">
                                <span class="departure-city">{{ ticket.flight.departureCity }}</span>
                                <span class="route-arrow">→</span>
                                <span class="arrival-city">{{ ticket.flight.arrivalCity }}</span>
                            </div>
                            <div class="flight-time">
                                <span class="date">{{ formatDate(ticket.flight.departureTime) }}</span>
                                <span class="time">{{ formatTime(ticket.flight.departureTime) }}</span>
                            </div>
                            <div class="flight-number">{{ ticket.flight.flightNumber }}</div>
                        </div>
                        <div v-if="order.tickets.length > 1" class="more-flights">
                            还有 {{ order.tickets.length - 1 }} 个航班
                        </div>
                    </div>

                    <div class="order-footer">
                        <div class="passenger-count">
                            <i class="el-icon-user"></i>
                            <span>{{ order.passengers.length }}位乘客</span>
                        </div>
                        <div class="order-price">
                            <span class="price-label">总价:</span>
                            <span class="price-amount">¥{{ order.totalAmount.toFixed(2) }}</span>
                        </div>
                        <div class="order-actions">
                            <el-button v-if="order.status === 'pending'" type="primary" size="mini"
                                @click.stop="goToPayment(order.id)">
                                继续支付
                            </el-button>
                            <el-button type="primary" plain size="mini" @click.stop="goToOrderDetail(order.id)">
                                查看详情
                            </el-button>
                        </div>
                    </div>
                </div>

                <div class="pagination-container">
                    <el-pagination background layout="prev, pager, next" :total="total" :page-size="pageSize"
                        v-model:current-page="currentPage" @current-change="handlePageChange"></el-pagination>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import api from '@/services/api'
import { ElMessage } from 'element-plus'

export default {
    name: 'OrderList',
    data() {
        return {
            isLoading: true,
            orders: [],
            total: 0,
            currentPage: 1,
            pageSize: 10,
            statusFilter: '',
            dateRange: null,
            statusOptions: [
                { value: 'pending', label: '待支付' },
                { value: 'paid', label: '已支付' },
                { value: 'ticketed', label: '已出票' },
                { value: 'completed', label: '已完成' },
                { value: 'cancelled', label: '已取消' },
                { value: 'refunded', label: '已退款' }
            ]
        };
    },
    created() {
        this.fetchOrders();
    },
    methods: {
        fetchOrders() {
            this.isLoading = true;

            // 构建API查询参数
            const params = {
                page: this.currentPage,
                page_size: this.pageSize
            };

            // 添加状态过滤
            if (this.statusFilter) {
                params.status = this.statusFilter;
            }

            // 添加日期范围过滤
            if (this.dateRange && this.dateRange[0] && this.dateRange[1]) {
                params.start_date = this.formatDate(this.dateRange[0]);
                params.end_date = this.formatDate(this.dateRange[1]);
            }

            console.log('开始获取订单列表');
            // 调用API获取订单数据
            api.orders.getList(params)
                .then(response => {
                    console.log('API返回数据:', response);
                    // 如果API返回了完整的分页数据
                    if (response && response.results && response.count !== undefined) {
                        console.log('处理分页数据，共', response.count, '条');
                        this.orders = this.transformOrders(response.results);
                        this.total = response.count;
                    }
                    // 如果API只返回了订单数组
                    else if (Array.isArray(response)) {
                        console.log('处理数组数据，共', response.length, '条');
                        this.orders = this.transformOrders(response);
                        this.total = response.length;
                    }
                    // 处理其他情况
                    else if (response) {
                        console.log('处理未知格式数据');
                        const data = Array.isArray(response.data) ? response.data :
                            (response.data && response.data.results) ? response.data.results :
                                [response];
                        this.orders = this.transformOrders(data);
                        this.total = data.length;
                    }
                    else {
                        console.warn('API返回空数据');
                        this.orders = [];
                        this.total = 0;
                    }
                    this.isLoading = false;
                })
                .catch(error => {
                    console.error('获取订单数据失败:', error);
                    this.isLoading = false;
                    this.orders = [];
                    this.total = 0;
                    ElMessage.error('获取订单数据失败，请稍后重试');
                });
        },

        // 将API返回的订单数据转换为前端所需格式
        transformOrders(apiOrders) {
            return apiOrders.map(order => {
                // 构建订单数据结构
                const transformedOrder = {
                    id: order.id,
                    orderNumber: order.order_number || `ORD${Math.random().toString().substring(2, 10).toUpperCase()}`,
                    status: order.status,
                    createdAt: new Date(order.created_at),
                    paidAt: order.paid_at ? new Date(order.paid_at) : null,
                    ticketedAt: order.ticketed_at ? new Date(order.ticketed_at) : null,
                    completedAt: order.completed_at ? new Date(order.completed_at) : null,
                    totalAmount: parseFloat(order.total_amount),
                    passengers: [],
                    tickets: []
                };

                // 处理乘客信息
                if (order.passengers && Array.isArray(order.passengers)) {
                    transformedOrder.passengers = order.passengers.map(passenger => ({
                        id: passenger.id,
                        name: passenger.name,
                        idType: passenger.id_type,
                        idNumber: passenger.id_number
                    }));
                }

                // 处理机票信息
                if (order.tickets && Array.isArray(order.tickets)) {
                    transformedOrder.tickets = order.tickets.map(ticket => ({
                        id: ticket.id,
                        ticketNumber: ticket.ticket_number,
                        passenger: transformedOrder.passengers.find(p => p.id === ticket.passenger_id) || {},
                        flight: {
                            id: ticket.flight_id,
                            flightNumber: ticket.flight_number || 'N/A',
                            airlineName: ticket.airline_name || '未知航空',
                            departureCity: ticket.departure_city || '',
                            arrivalCity: ticket.arrival_city || '',
                            departureTime: ticket.departure_time ? new Date(ticket.departure_time) : null,
                            arrivalTime: ticket.arrival_time ? new Date(ticket.arrival_time) : null,
                            status: ticket.flight_status || 'scheduled'
                        },
                        seatNumber: ticket.seat_number,
                        cabinClass: ticket.cabin_class || 'economy',
                        price: parseFloat(ticket.price)
                    }));
                }

                return transformedOrder;
            });
        },

        handlePageChange(page) {
            this.currentPage = page;
            this.fetchOrders();
        },

        searchOrders() {
            this.currentPage = 1;
            this.fetchOrders();
        },

        formatDate(date) {
            if (!date) return '';
            const d = new Date(date);
            return `${d.getFullYear()}-${(d.getMonth() + 1).toString().padStart(2, '0')}-${d.getDate().toString().padStart(2, '0')}`;
        },

        formatTime(date) {
            if (!date) return '';
            const d = new Date(date);
            return `${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`;
        },

        formatDateTime(date) {
            if (!date) return '';
            return this.formatDate(date) + ' ' + this.formatTime(date);
        },

        getStatusText(status) {
            const statusMap = {
                'pending': '待支付',
                'paid': '已支付',
                'ticketed': '已出票',
                'completed': '已完成',
                'cancelled': '已取消',
                'refunded': '已退款'
            };
            return statusMap[status] || '未知状态';
        },

        getStatusClass(status) {
            const classMap = {
                'pending': 'status-pending',
                'paid': 'status-paid',
                'ticketed': 'status-ticketed',
                'completed': 'status-completed',
                'cancelled': 'status-cancelled',
                'refunded': 'status-refunded'
            };
            return classMap[status] || '';
        },

        goToOrderDetail(orderId) {
            this.$router.push({
                name: 'orderDetail',
                params: { orderId }
            });
        },

        goToPayment(orderId) {
            this.$router.push({
                name: 'payment',
                params: { orderId }
            });
        },

        goToHome() {
            this.$router.push('/');
        }
    }
};
</script>

<style scoped>
.order-list-view {
    padding: 20px;
    background-color: #f5f7fa;
    min-height: 100vh;
}

.header-banner {
    background: linear-gradient(135deg, #00468c, #0076c6);
    color: white;
    padding: 25px;
    border-radius: 8px;
    margin-bottom: 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 4px 12px rgba(0, 71, 140, 0.15);
}

.header-banner h1 {
    margin: 0;
    font-size: 24px;
    font-weight: 600;
}

.filter-options {
    display: flex;
    gap: 10px;
}

.order-list-container {
    max-width: 1000px;
    margin: 0 auto;
}

.loading-container,
.empty-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 100px 0;
    text-align: center;
}

.loading-spinner {
    font-size: 40px;
    color: #0076c6;
    margin-bottom: 20px;
}

.empty-container i {
    font-size: 60px;
    color: #ccc;
    margin-bottom: 20px;
}

.order-list {
    display: flex;
    flex-direction: column;
    gap: 15px;
}

.order-card {
    background-color: white;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
    cursor: pointer;
    transition: all 0.3s ease;
}

.order-card:hover {
    box-shadow: 0 4px 16px 0 rgba(0, 0, 0, 0.1);
    transform: translateY(-2px);
}

.order-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 15px;
    padding-bottom: 15px;
    border-bottom: 1px solid #eee;
}

.order-number {
    font-weight: 600;
    color: #333;
    margin-bottom: 5px;
}

.order-time {
    font-size: 14px;
    color: #666;
}

.order-status {
    padding: 6px 12px;
    border-radius: 20px;
    font-size: 14px;
    font-weight: 500;
}

.status-pending {
    background-color: #fff8e1;
    color: #f57c00;
}

.status-paid {
    background-color: #e3f2fd;
    color: #1976d2;
}

.status-ticketed {
    background-color: #e8f5e9;
    color: #2e7d32;
}

.status-completed {
    background-color: #e8f5e9;
    color: #2e7d32;
}

.status-cancelled {
    background-color: #fafafa;
    color: #757575;
}

.status-refunded {
    background-color: #ffebee;
    color: #c62828;
}

.flight-info {
    margin-bottom: 15px;
    padding-bottom: 15px;
    border-bottom: 1px solid #eee;
}

.flight-route {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
}

.cities {
    display: flex;
    align-items: center;
    font-size: 18px;
    font-weight: 600;
}

.route-arrow {
    margin: 0 10px;
    color: #0076c6;
}

.flight-time {
    display: flex;
    flex-direction: column;
    align-items: center;
}

.date {
    font-size: 14px;
    color: #666;
    margin-bottom: 5px;
}

.time {
    font-weight: 600;
    color: #0076c6;
}

.flight-number {
    font-size: 14px;
    color: #666;
}

.more-flights {
    text-align: center;
    font-size: 14px;
    color: #0076c6;
    margin-top: 10px;
}

.order-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.passenger-count {
    display: flex;
    align-items: center;
    color: #666;
    font-size: 14px;
}

.passenger-count i {
    margin-right: 5px;
}

.order-price {
    display: flex;
    align-items: baseline;
}

.price-label {
    font-size: 14px;
    color: #666;
    margin-right: 5px;
}

.price-amount {
    font-size: 18px;
    font-weight: 600;
    color: #f44336;
}

.order-actions {
    display: flex;
    gap: 10px;
}

.pagination-container {
    margin-top: 30px;
    display: flex;
    justify-content: center;
}

/* 响应式调整 */
@media screen and (max-width: 768px) {
    .header-banner {
        flex-direction: column;
        align-items: flex-start;
    }

    .filter-options {
        margin-top: 15px;
        width: 100%;
        flex-wrap: wrap;
    }

    .filter-options .el-select,
    .filter-options .el-date-picker {
        margin-bottom: 10px;
    }

    .order-header {
        flex-direction: column;
    }

    .order-status {
        margin-top: 10px;
    }

    .flight-route {
        flex-direction: column;
        align-items: flex-start;
        gap: 10px;
    }

    .order-footer {
        flex-direction: column;
        align-items: flex-start;
        gap: 10px;
    }

    .order-actions {
        width: 100%;
        justify-content: flex-end;
    }
}
</style>