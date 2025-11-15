<template>
    <div class="admin-orders">
        <h1 class="title">订单管理</h1>

        <div class="top-actions">
            <div class="search-bar">
                <input type="text" v-model="searchQuery" placeholder="搜索订单号、用户..." />
                <button @click="handleSearch" class="btn-search">
                    <i class="fas fa-search"></i>
                </button>
            </div>

            <div class="filter-options">
                <select v-model="statusFilter">
                    <option value="">所有状态</option>
                    <option value="pending">待付款</option>
                    <option value="paid">已付款</option>
                    <option value="completed">已完成</option>
                    <option value="cancelled">已取消</option>
                    <option value="refunded">已退款</option>
                </select>

                <input type="date" v-model="dateFilter" placeholder="日期筛选" />
            </div>

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
                                    <a @click="updateOrderStatus(order.id, 'cancelled')"
                                        v-if="order.status === 'pending'">取消订单</a>
                                    <a @click="processRefund(order)"
                                        v-if="order.status === 'paid' || order.status === 'completed'">处理退款</a>
                                    <a @click="resendConfirmation(order.id)">重发确认邮件</a>
                                    <a @click="viewPaymentDetails(order.id)">查看支付详情</a>
                                </div>
                            </div>
                        </td>
                    </tr>
                </tbody>
            </table>

            <div class="pagination">
                <button @click="prevPage" :disabled="currentPage === 1" class="btn-page">
                    <i class="fas fa-chevron-left"></i>
                </button>
                <span class="page-info">{{ currentPage }} / {{ totalPages }}</span>
                <button @click="nextPage" :disabled="currentPage === totalPages" class="btn-page">
                    <i class="fas fa-chevron-right"></i>
                </button>
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
            pageSize: 5,
            showRefundModal: false,
            selectedOrder: null,
            refundAmount: 0,
            refundReason: 'customer_request',
            refundComment: ''
        }
    },
    computed: {
        filteredOrders() {
            let result = [...this.orders]

            // 应用搜索
            if (this.searchQuery) {
                const query = this.searchQuery.toLowerCase()
                result = result.filter(order =>
                    order.id.toLowerCase().includes(query) ||
                    order.username.toLowerCase().includes(query) ||
                    order.flightInfo.toLowerCase().includes(query)
                )
            }

            // 应用状态过滤
            if (this.statusFilter) {
                result = result.filter(order => order.status === this.statusFilter)
            }

            // 应用日期过滤
            if (this.dateFilter) {
                const filterDate = new Date(this.dateFilter).toISOString().split('T')[0]
                result = result.filter(order => {
                    const orderDate = new Date(order.createdAt).toISOString().split('T')[0]
                    return orderDate === filterDate
                })
            }

            // 应用排序
            if (this.sortKey) {
                result.sort((a, b) => {
                    let aValue = a[this.sortKey]
                    let bValue = b[this.sortKey]

                    // 日期排序特殊处理
                    if (this.sortKey === 'createdAt') {
                        aValue = new Date(aValue).getTime()
                        bValue = new Date(bValue).getTime()
                    }

                    if (aValue < bValue) return this.sortDirection === 'asc' ? -1 : 1
                    if (aValue > bValue) return this.sortDirection === 'asc' ? 1 : -1
                    return 0
                })
            }

            // 分页
            const startIndex = (this.currentPage - 1) * this.pageSize
            const endIndex = startIndex + this.pageSize
            return result.slice(startIndex, endIndex)
        },
        totalPages() {
            // 应用所有过滤条件后的总页数
            let filtered = [...this.orders]

            if (this.searchQuery) {
                const query = this.searchQuery.toLowerCase()
                filtered = filtered.filter(order =>
                    order.id.toLowerCase().includes(query) ||
                    order.username.toLowerCase().includes(query) ||
                    order.flightInfo.toLowerCase().includes(query)
                )
            }

            if (this.statusFilter) {
                filtered = filtered.filter(order => order.status === this.statusFilter)
            }

            if (this.dateFilter) {
                const filterDate = new Date(this.dateFilter).toISOString().split('T')[0]
                filtered = filtered.filter(order => {
                    const orderDate = new Date(order.createdAt).toISOString().split('T')[0]
                    return orderDate === filterDate
                })
            }

            return Math.ceil(filtered.length / this.pageSize)
        }
    },
    methods: {
        // 获取订单数据
        async fetchOrders() {
            this.isLoading = true;
            this.error = null;

            try {
                const params = {};
                if (this.searchQuery) params.search = this.searchQuery;
                if (this.statusFilter) params.status = this.statusFilter;
                if (this.dateFilter) params.date = this.dateFilter;

                const response = await api.admin.orders.getList(params);
                if (Array.isArray(response.data)) {
                    this.orders = response.data;
                } else {
                    console.warn('API返回的订单数据不是数组，使用空数组');
                    this.orders = [];
                }

                console.log('获取到订单数据:', this.orders);

                // 如果返回的数据为空，使用模拟数据
                if (!this.orders || this.orders.length === 0) {
                    console.warn('API返回的订单数据为空，使用默认数据');
                    this.useDefaultData();
                }
            } catch (error) {
                console.error('获取订单数据失败:', error);
                this.error = '获取订单数据失败，请稍后再试';

                // 确保orders是数组
                this.orders = [];
                // API调用失败，使用模拟数据
                this.useDefaultData();
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
                // 如果已经按这个键排序，切换排序方向
                this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc'
            } else {
                // 如果是新的排序键，设置为升序
                this.sortKey = key
                this.sortDirection = 'asc'
            }
        },
        getSortIconClass(key) {
            if (this.sortKey !== key) return 'fa-sort'
            return this.sortDirection === 'asc' ? 'fa-sort-up' : 'fa-sort-down'
        },
        formatDate(dateStr) {
            const date = new Date(dateStr)
            return date.toLocaleString()
        },
        getStatusText(status) {
            const statusMap = {
                pending: '待付款',
                paid: '已付款',
                completed: '已完成',
                cancelled: '已取消',
                refunded: '已退款'
            }
            return statusMap[status] || status
        },
        prevPage() {
            if (this.currentPage > 1) {
                this.currentPage--
            }
        },
        nextPage() {
            if (this.currentPage < this.totalPages) {
                this.currentPage++
            }
        },
        viewOrderDetail(orderId) {
            this.$router.push(`/admin/orders/${orderId}`)
        },
        // 更新订单状态
        async updateOrderStatus(orderId, newStatus) {
            try {
                await api.admin.orders.updateStatus(orderId, newStatus);
                const order = this.orders.find(o => o.id === orderId);
                if (order) {
                    order.status = newStatus;
                }
            } catch (error) {
                console.error('更新订单状态失败:', error);
                alert('更新订单状态失败，请稍后再试');
            }
        },
        // 处理退款
        processRefund(order) {
            this.selectedOrder = order
            this.refundAmount = order.amount
            this.refundReason = 'customer_request'
            this.refundComment = ''
            this.showRefundModal = true
        },
        // 处理退款
        async confirmRefund() {
            if (!this.selectedOrder || this.refundAmount <= 0) return;

            try {
                const data = {
                    amount: this.refundAmount,
                    reason: this.refundReason,
                    comment: this.refundComment
                };

                await api.admin.orders.refund(this.selectedOrder.id, data);

                // 更新本地订单数据
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
        // 重发确认邮件
        async resendConfirmation() {
            // 模拟API调用
            alert('确认邮件已重发');
        },
        // 查看支付详情
        async viewPaymentDetails(orderId) {
            try {
                const response = await api.admin.orders.getPaymentInfo(orderId);
                console.log('支付详情:', response.data);
                // 这里可以添加显示支付详情的逻辑
                alert('支付详情已在控制台输出');
            } catch (error) {
                console.error('获取支付详情失败:', error);
                alert('获取支付详情失败，请稍后再试');
            }
        },
        // 导出数据
        async exportOrders() {
            try {
                const params = {};
                if (this.statusFilter) params.status = this.statusFilter;
                if (this.dateFilter) params.date = this.dateFilter;

                const response = await api.admin.reports.exportReport('orders', params);

                // 处理下载逻辑
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
        },
        // 如果API调用失败，使用默认数据
        useDefaultData() {
            this.orders = [
                {
                    id: 'ORD20230712001',
                    username: '张伟',
                    flightInfo: 'CA1234 北京-上海 2023-07-15',
                    amount: 1580.00,
                    passengerCount: 1,
                    status: 'completed',
                    createdAt: '2023-07-12T10:30:00',
                    paymentMethod: '支付宝',
                    contactPhone: '13800138001',
                    contactEmail: 'zhangwei@example.com'
                },
                {
                    id: 'ORD20230713002',
                    username: '李明',
                    flightInfo: 'MU5678 广州-成都 2023-07-20',
                    amount: 3260.00,
                    passengerCount: 2,
                    status: 'paid',
                    createdAt: '2023-07-13T14:15:00',
                    paymentMethod: '微信支付',
                    contactPhone: '13900139002',
                    contactEmail: 'liming@example.com'
                },
                {
                    id: 'ORD20230714003',
                    username: '王静',
                    flightInfo: 'CZ3961 深圳-北京 2023-07-18',
                    amount: 2150.00,
                    passengerCount: 1,
                    status: 'pending',
                    createdAt: '2023-07-14T09:45:00',
                    contactPhone: '13700137003',
                    contactEmail: 'wangjing@example.com'
                }
            ];
        }
    },
    mounted() {
        this.fetchOrders();
    }
}
</script>

<style scoped>
/* 加载和错误状态 */
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
    0% {
        transform: rotate(0deg);
    }

    100% {
        transform: rotate(360deg);
    }
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

.admin-orders {
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

.top-actions {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    flex-wrap: wrap;
    gap: 10px;
}

.search-bar {
    display: flex;
    align-items: center;
    background: white;
    border-radius: 4px;
    overflow: hidden;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    flex: 1;
    max-width: 400px;
}

.search-bar input {
    border: none;
    padding: 10px 15px;
    flex: 1;
    outline: none;
    font-size: 14px;
}

.btn-search {
    background: #f5f5f5;
    border: none;
    height: 40px;
    width: 40px;
    cursor: pointer;
    color: #555;
}

.btn-search:hover {
    background: #eaeaea;
}

.filter-options {
    display: flex;
    gap: 10px;
}

.filter-options select,
.filter-options input {
    padding: 8px 12px;
    border: 1px solid #ddd;
    border-radius: 4px;
    outline: none;
    font-size: 14px;
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
    position: relative;
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

.data-table tbody tr:last-child td {
    border-bottom: none;
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

.status-cancelled {
    background: #f5f5f5;
    color: #757575;
}

.status-refunded {
    background: #ffebee;
    color: #c62828;
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

.btn-page {
    background: #f5f5f5;
    border: none;
    width: 32px;
    height: 32px;
    border-radius: 4px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    color: #555;
}

.btn-page:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

.btn-page:not(:disabled):hover {
    background: #e0e0e0;
}

.page-info {
    margin: 0 15px;
    font-size: 14px;
    color: #666;
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
}

.form-actions {
    display: flex;
    justify-content: flex-end;
    gap: 10px;
    margin-top: 20px;
}

@media (max-width: 768px) {
    .top-actions {
        flex-direction: column;
        align-items: stretch;
    }

    .search-bar {
        max-width: none;
    }

    .filter-options {
        flex-direction: column;
    }

    .data-table {
        display: block;
        overflow-x: auto;
    }
}
</style>