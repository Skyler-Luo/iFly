<template>
    <div class="admin-orders">
        <h1 class="title">订单管理</h1>

        <div class="top-actions">
            <el-input
                v-model="searchQuery"
                placeholder="搜索订单号、用户..."
                clearable
                style="width: 300px"
                @keyup.enter="handleSearch"
            >
                <template #prefix>
                    <i class="fas fa-search"></i>
                </template>
            </el-input>

            <el-radio-group v-model="statusFilter" @change="handleSearch">
                <el-radio-button value="">全部</el-radio-button>
                <el-radio-button value="pending">待付款</el-radio-button>
                <el-radio-button value="paid">已付款</el-radio-button>
                <el-radio-button value="completed">已完成</el-radio-button>
                <el-radio-button value="canceled">已取消</el-radio-button>
            </el-radio-group>

            <button @click="exportOrders" class="btn btn-primary">
                <i class="fas fa-download"></i> 导出数据
            </button>
        </div>

        <div v-if="isLoading" class="loading-container">
            <div class="spinner"></div>
            <p>正在加载数据...</p>
        </div>

        <div v-else-if="error" class="error-container">
            <i class="fas fa-exclamation-triangle"></i>
            <p>{{ error }}</p>
            <button @click="fetchOrders" class="btn btn-primary">重新加载</button>
        </div>

        <div v-else class="data-table-container">
            <table class="data-table">
                <thead>
                    <tr>
                        <th @click="sortBy('id')">
                            订单号
                            <i class="fas" :class="getSortIconClass('id')"></i>
                        </th>
                        <th @click="sortBy('username')">
                            用户
                            <i class="fas" :class="getSortIconClass('username')"></i>
                        </th>
                        <th @click="sortBy('flightInfo')">
                            航班信息
                            <i class="fas" :class="getSortIconClass('flightInfo')"></i>
                        </th>
                        <th @click="sortBy('amount')">
                            金额
                            <i class="fas" :class="getSortIconClass('amount')"></i>
                        </th>
                        <th @click="sortBy('passengerCount')">
                            乘客数
                            <i class="fas" :class="getSortIconClass('passengerCount')"></i>
                        </th>
                        <th @click="sortBy('status')">
                            状态
                            <i class="fas" :class="getSortIconClass('status')"></i>
                        </th>
                        <th @click="sortBy('createdAt')">
                            创建时间
                            <i class="fas" :class="getSortIconClass('createdAt')"></i>
                        </th>
                        <th>操作</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="order in filteredOrders" :key="order.id">
                        <td>{{ order.id }}</td>
                        <td>{{ order.username }}</td>
                        <td>{{ order.flightInfo }}</td>
                        <td>¥{{ order.amount.toFixed(2) }}</td>
                        <td>{{ order.passengerCount }}</td>
                        <td>
                            <span class="status-badge" :class="'status-' + order.status">
                                {{ getStatusText(order.status) }}
                            </span>
                        </td>
                        <td>{{ formatDate(order.createdAt) }}</td>
                        <td class="actions-cell">
                            <button @click="viewOrderDetail(order.id)" class="btn-icon">
                                <i class="fas fa-eye"></i>
                            </button>
                            <div class="dropdown">
                                <button class="btn-icon dropdown-toggle">
                                    <i class="fas fa-ellipsis-v"></i>
                                </button>
                                <div class="dropdown-menu">
                                    <a @click="updateOrderStatus(order.id, 'completed')"
                                        v-if="order.status === 'paid'">标记为已完成</a>
                                    <a @click="updateOrderStatus(order.id, 'canceled')"
                                        v-if="order.status === 'pending'">取消订单</a>
                                    <a @click="viewPaymentDetails(order.id)">查看支付详情</a>
                                </div>
                            </div>
                        </td>
                    </tr>
                </tbody>
            </table>

            <div class="pagination">
                <el-pagination
                    v-model:current-page="currentPage"
                    :page-size="pageSize"
                    :total="processedOrders.length"
                    layout="total, prev, pager, next"
                    background
                />
            </div>
        </div>

        <!-- 退款处理弹窗 -->
        <div v-if="showRefundModal" class="modal">
            <div class="modal-content">
                <div class="modal-header">
                    <h2>处理退款</h2>
                    <button @click="showRefundModal = false" class="close-btn">&times;</button>
                </div>
                <div class="modal-body">
                    <p><strong>订单号:</strong> {{ selectedOrder?.id }}</p>
                    <p><strong>用户:</strong> {{ selectedOrder?.username }}</p>
                    <p><strong>金额:</strong> ¥{{ selectedOrder?.amount.toFixed(2) }}</p>

                    <div class="form-group">
                        <label>退款金额</label>
                        <input type="number" v-model="refundAmount" :max="selectedOrder?.amount" min="0" step="0.01" />
                    </div>

                    <div class="form-group">
                        <label>退款原因</label>
                        <select v-model="refundReason">
                            <option value="customer_request">客户要求</option>
                            <option value="flight_cancelled">航班取消</option>
                            <option value="flight_delayed">航班延误</option>
                            <option value="duplicate_booking">重复预订</option>
                            <option value="system_error">系统错误</option>
                            <option value="other">其他原因</option>
                        </select>
                    </div>

                    <div class="form-group" v-if="refundReason === 'other'">
                        <label>详细原因</label>
                        <textarea v-model="refundComment" rows="3"></textarea>
                    </div>

                    <div class="form-actions">
                        <button @click="showRefundModal = false" class="btn btn-secondary">取消</button>
                        <button @click="confirmRefund" class="btn btn-primary">确认退款</button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import api from '../services/api';

export default {
    name: 'AdminOrdersView',
    data() {
        return {
            orders: [],
            isLoading: false,
            error: null,
            searchQuery: '',
            statusFilter: '',
            dateFilter: '',
            sortKey: '',
            sortDirection: 'asc',
            currentPage: 1,
            pageSize: 8,
            showRefundModal: false,
            selectedOrder: null,
            refundAmount: 0,
            refundReason: 'customer_request',
            refundComment: ''
        }
    },
    computed: {
        processedOrders() {
            let result = [...this.orders];
            if (this.searchQuery) {
                const query = this.searchQuery.toLowerCase();
                result = result.filter(order =>
                    String(order.id).toLowerCase().includes(query) ||
                    order.username.toLowerCase().includes(query) ||
                    order.flightInfo.toLowerCase().includes(query)
                );
            }
            if (this.statusFilter) {
                result = result.filter(order => order.status === this.statusFilter);
            }
            if (this.dateFilter) {
                const filterDate = this.dateFilter;
                result = result.filter(order => {
                    const orderDate = new Date(order.createdAt).toISOString().split('T')[0];
                    return orderDate === filterDate;
                });
            }
            if (this.sortKey) {
                result.sort((a, b) => {
                    let aValue = a[this.sortKey];
                    let bValue = b[this.sortKey];
                    if (this.sortKey === 'createdAt') {
                        aValue = new Date(aValue).getTime();
                        bValue = new Date(bValue).getTime();
                    }
                    if (aValue < bValue) return this.sortDirection === 'asc' ? -1 : 1;
                    if (aValue > bValue) return this.sortDirection === 'asc' ? 1 : -1;
                    return 0;
                });
            }
            return result;
        },
        filteredOrders() {
            const start = (this.currentPage - 1) * this.pageSize;
            const end = start + this.pageSize;
            return this.processedOrders.slice(start, end);
        },
        totalPages() {
            return Math.ceil(this.processedOrders.length / this.pageSize) || 1;
        }
    },
    methods: {
        async fetchOrders() {
            this.isLoading = true;
            this.error = null;
            try {
                const params = {};
                if (this.searchQuery) params.search = this.searchQuery;
                if (this.statusFilter) params.status = this.statusFilter;
                if (this.dateFilter) params.date = this.dateFilter;
                const response = await api.admin.orders.getList(params);
                const data = Array.isArray(response) ? response : (response?.results || []);
                this.orders = data.map(order => {
                    const tickets = order.tickets || [];
                    const firstTicket = tickets[0] || {};
                    const flightInfo = firstTicket.flight_number 
                        ? `${firstTicket.flight_number} ${firstTicket.departure_city || ''}-${firstTicket.arrival_city || ''}`
                        : '无航班信息';
                    return {
                        id: order.order_number || order.id,
                        username: order.contact_name || '未知用户',
                        flightInfo: flightInfo,
                        amount: parseFloat(order.total_price) || 0,
                        passengerCount: tickets.length,
                        status: order.status,
                        createdAt: order.created_at,
                        paymentMethod: order.payment_method || '',
                        contactPhone: order.contact_phone || '',
                        contactEmail: order.contact_email || ''
                    };
                });
                console.log('获取到订单数据:', this.orders.length, '条');
            } catch (error) {
                console.error('获取订单数据失败:', error);
                this.error = '获取订单数据失败，请稍后再试';
                this.orders = [];
            } finally {
                this.isLoading = false;
            }
        },
        handleSearch() {
            this.currentPage = 1;
            this.fetchOrders();
        },
        sortBy(key) {
            if (this.sortKey === key) {
                this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
            } else {
                this.sortKey = key;
                this.sortDirection = 'asc';
            }
        },
        getSortIconClass(key) {
            if (this.sortKey !== key) return 'fa-sort';
            return this.sortDirection === 'asc' ? 'fa-sort-up' : 'fa-sort-down';
        },
        formatDate(dateStr) {
            if (!dateStr) return '';
            const date = new Date(dateStr);
            return date.toLocaleDateString('zh-CN') + ' ' + date.toLocaleTimeString('zh-CN');
        },
        getStatusText(status) {
            const statusMap = {
                pending: '待付款',
                paid: '已付款',
                completed: '已完成',
                canceled: '已取消'
            };
            return statusMap[status] || status;
        },
        viewOrderDetail(orderId) {
            this.$router.push(`/admin/orders/${orderId}`);
        },
        async updateOrderStatus(orderId, newStatus) {
            try {
                await api.admin.orders.updateStatus(orderId, newStatus);
                const order = this.orders.find(o => o.id === orderId);
                if (order) order.status = newStatus;
            } catch (error) {
                console.error('更新订单状态失败:', error);
                alert('更新订单状态失败，请稍后再试');
            }
        },
        processRefund(order) {
            this.selectedOrder = order;
            this.refundAmount = order.amount;
            this.refundReason = 'customer_request';
            this.refundComment = '';
            this.showRefundModal = true;
        },
        async confirmRefund() {
            if (!this.selectedOrder || this.refundAmount <= 0) return;
            try {
                const data = {
                    amount: this.refundAmount,
                    reason: this.refundReason,
                    comment: this.refundComment
                };
                await api.admin.orders.refund(this.selectedOrder.id, data);
                const order = this.orders.find(o => o.id === this.selectedOrder.id);
                if (order) {
                    order.status = 'refunded';
                    order.refundAmount = this.refundAmount;
                    order.refundReason = this.refundReason;
                }
                this.showRefundModal = false;
            } catch (error) {
                console.error('处理退款失败:', error);
                alert('处理退款失败，请稍后再试');
            }
        },
        async viewPaymentDetails(orderId) {
            try {
                const response = await api.admin.orders.getPaymentInfo(orderId);
                console.log('支付详情:', response.data);
                alert('支付详情已在控制台输出');
            } catch (error) {
                console.error('获取支付详情失败:', error);
                alert('获取支付详情失败，请稍后再试');
            }
        },
        async exportOrders() {
            try {
                const params = {};
                if (this.statusFilter) params.status = this.statusFilter;
                if (this.dateFilter) params.date = this.dateFilter;
                const response = await api.admin.reports.exportReport('orders', params);
                const url = window.URL.createObjectURL(new Blob([response]));
                const link = document.createElement('a');
                link.href = url;
                link.setAttribute('download', `orders-export-${new Date().toISOString().split('T')[0]}.csv`);
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            } catch (error) {
                console.error('导出订单数据失败:', error);
                alert('导出订单数据失败，请稍后再试');
            }
        }
    },
    mounted() {
        this.fetchOrders();
    }
}
</script>

<style scoped>
.admin-orders {
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

.top-actions {
    display: flex;
    justify-content: flex-start;
    align-items: center;
    margin-bottom: 20px;
    gap: 20px;
}

.btn {
    padding: 8px 16px;
    border-radius: 4px;
    border: none;
    font-weight: 500;
    cursor: pointer;
    display: flex;
    align-items: center;
    font-size: 14px;
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

.data-table-container {
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    overflow: hidden;
}

.data-table {
    width: 100%;
    border-collapse: collapse;
}

.data-table th,
.data-table td {
    padding: 12px 15px;
    text-align: left;
    border-bottom: 1px solid #eee;
}

.data-table th {
    background: #f9f9f9;
    color: #333;
    font-weight: 600;
    cursor: pointer;
    user-select: none;
}

.data-table th i {
    margin-left: 5px;
    font-size: 12px;
}

.data-table th:hover {
    background: #f0f0f0;
}

.data-table tbody tr:hover {
    background: #f9f9f9;
}

.status-badge {
    padding: 4px 8px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: 500;
    display: inline-block;
}

.status-pending {
    background: #fff8e1;
    color: #ff8f00;
}

.status-paid {
    background: #e3f2fd;
    color: #1976d2;
}

.status-completed {
    background: #e8f5e9;
    color: #2e7d32;
}

.status-canceled {
    background: #f5f5f5;
    color: #757575;
}

.actions-cell {
    white-space: nowrap;
    display: flex;
    gap: 5px;
}

.btn-icon {
    background: none;
    border: none;
    color: #666;
    cursor: pointer;
    padding: 5px;
    border-radius: 4px;
    transition: all 0.2s;
}

.btn-icon:hover {
    background: #f0f0f0;
    color: #333;
}

.dropdown {
    position: relative;
    display: inline-block;
}

.dropdown-toggle {
    background: none;
    border: none;
    cursor: pointer;
    padding: 5px 8px;
}

.dropdown-menu {
    position: absolute;
    right: 0;
    top: 100%;
    background: white;
    box-shadow: 0 3px 10px rgba(0, 0, 0, 0.2);
    border-radius: 4px;
    padding: 5px 0;
    min-width: 150px;
    z-index: 10;
    display: none;
}

.dropdown:hover .dropdown-menu {
    display: block;
}

.dropdown-menu a {
    display: block;
    padding: 8px 15px;
    color: #333;
    text-decoration: none;
    font-size: 14px;
    cursor: pointer;
}

.dropdown-menu a:hover {
    background: #f5f5f5;
}

.pagination {
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 15px;
    border-top: 1px solid #eee;
}

.modal {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
}

.modal-content {
    background: white;
    border-radius: 8px;
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
    width: 100%;
    max-width: 500px;
    max-height: 90vh;
    overflow-y: auto;
}

.modal-header {
    padding: 15px 20px;
    border-bottom: 1px solid #eee;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.modal-header h2 {
    font-size: 18px;
    color: #333;
    margin: 0;
}

.close-btn {
    background: none;
    border: none;
    font-size: 24px;
    color: #999;
    cursor: pointer;
}

.close-btn:hover {
    color: #333;
}

.modal-body {
    padding: 20px;
}

.form-group {
    margin-bottom: 15px;
}

.form-group label {
    display: block;
    margin-bottom: 5px;
    font-size: 14px;
    color: #555;
}

.form-group input,
.form-group select,
.form-group textarea {
    width: 100%;
    padding: 8px 12px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 14px;
    outline: none;
    box-sizing: border-box;
}

.form-actions {
    display: flex;
    justify-content: flex-end;
    gap: 10px;
    margin-top: 20px;
}

.loading-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 2rem;
    min-height: 200px;
}

.spinner {
    border: 4px solid rgba(0, 0, 0, 0.1);
    width: 36px;
    height: 36px;
    border-radius: 50%;
    border-left-color: #3498db;
    animation: spin 1s linear infinite;
    margin-bottom: 1rem;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

.error-container {
    text-align: center;
    padding: 2rem;
    color: #e74c3c;
}

.error-container i {
    font-size: 2rem;
    margin-bottom: 1rem;
}
</style>
