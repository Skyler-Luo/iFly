<template>
    <div class="order-history-tab">
        <div class="order-header">
            <h3>我的订单</h3>
            <el-select v-model="orderStatus" placeholder="订单状态" style="width: 150px" @change="handleFilterChange">
                <el-option label="全部订单" value="" />
                <el-option label="待支付" value="PENDING" />
                <el-option label="已支付" value="PAID" />
                <el-option label="已取消" value="CANCELLED" />
                <el-option label="已退款" value="REFUNDED" />
            </el-select>
        </div>

        <div v-if="loading" class="loading-container">
            <el-skeleton :rows="3" animated />
            <el-divider />
            <el-skeleton :rows="3" animated />
        </div>

        <div v-else-if="orders.length === 0" class="empty-container">
            <el-empty description="暂无订单记录" />
        </div>

        <div v-else class="order-list">
            <el-card v-for="order in orders" :key="order.id" class="order-card" shadow="hover">
                <div class="order-card-header">
                    <div class="order-info">
                        <span class="order-number">订单号: {{ order.order_number }}</span>
                        <span class="order-date">下单时间: {{ formatDate(order.created_at) }}</span>
                    </div>
                    <el-tag :type="getStatusType(order.status)">{{ getStatusText(order.status) }}</el-tag>
                </div>

                <div class="flight-info">
                    <div class="route-info">
                        <div class="departure">
                            <div class="city">{{ order.flight_info.departure_city }}</div>
                            <div class="airport">{{ order.flight_info.departure_airport }}</div>
                            <div class="time">{{ formatTime(order.flight_info.departure_time) }}</div>
                        </div>

                        <div class="flight-arrow">
                            <el-icon>
                                <ArrowRight />
                            </el-icon>
                        </div>

                        <div class="arrival">
                            <div class="city">{{ order.flight_info.arrival_city }}</div>
                            <div class="airport">{{ order.flight_info.arrival_airport }}</div>
                            <div class="time">{{ formatTime(order.flight_info.arrival_time) }}</div>
                        </div>
                    </div>

                    <div class="flight-detail">
                        <div>{{ order.flight_info.airline }} {{ order.flight_info.flight_number }}</div>
                        <div>{{ formatDate(order.flight_info.departure_time, 'YYYY-MM-DD') }}</div>
                    </div>
                </div>

                <div class="passenger-info">
                    <div class="passenger-count">
                        <el-icon>
                            <User />
                        </el-icon>
                        <span>{{ order.passengers.length }}位乘客</span>
                    </div>
                    <div class="passenger-list">
                        <span v-for="(passenger, index) in order.passengers" :key="index" class="passenger-item">
                            {{ passenger.name }}
                            <span v-if="index < order.passengers.length - 1">,</span>
                        </span>
                    </div>
                </div>

                <div class="order-footer">
                    <div class="price">
                        <span class="price-label">总价:</span>
                        <span class="price-value">¥{{ order.total_amount.toFixed(2) }}</span>
                    </div>

                    <div class="actions">
                        <el-button v-if="order.status === 'PENDING'" type="primary" size="small"
                            @click="goToPayment(order.id)">
                            去支付
                        </el-button>

                        <el-button type="primary" size="small" @click="viewOrderDetail(order.id)" plain>
                            查看详情
                        </el-button>

                        <el-button v-if="order.status === 'PENDING'" type="danger" size="small"
                            @click="cancelOrder(order)" plain>
                            取消订单
                        </el-button>
                    </div>
                </div>
            </el-card>
        </div>

        <!-- 分页 -->
        <div class="pagination-container">
            <el-pagination v-model:current-page="currentPage" v-model:page-size="pageSize" :page-sizes="[5, 10, 20]"
                layout="total, sizes, prev, pager, next" :total="totalOrders" @size-change="handleSizeChange"
                @current-change="handleCurrentChange" />
        </div>

        <!-- 取消订单确认对话框 -->
        <el-dialog v-model="cancelDialogVisible" title="取消订单" width="400px">
            <div>确定要取消订单 "{{ currentOrder?.order_number || '' }}" 吗？</div>
            <template #footer>
                <span class="dialog-footer">
                    <el-button @click="cancelDialogVisible = false">取消</el-button>
                    <el-button type="danger" @click="confirmCancelOrder" :loading="cancelling">
                        确认取消
                    </el-button>
                </span>
            </template>
        </el-dialog>
    </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowRight, User } from '@element-plus/icons-vue'
// import api from '@/services/api' // 暂时不使用API

export default {
    name: 'OrderHistoryTab',
    components: {
        ArrowRight,
        User
    },
    setup() {
        const router = useRouter()
        const loading = ref(false)
        const cancelling = ref(false)
        const orders = ref([])
        const totalOrders = ref(0)
        const currentPage = ref(1)
        const pageSize = ref(5)
        const orderStatus = ref('')
        const cancelDialogVisible = ref(false)
        const currentOrder = ref(null)

        // 获取订单列表
        const fetchOrders = () => {
            loading.value = true

            // 使用模拟数据（因为API尚未接入）
            setTimeout(() => {
                orders.value = [
                    {
                        id: 1,
                        order_number: 'ORD202406200001',
                        created_at: '2024-06-20 10:30:00',
                        status: 'PAID',
                        total_amount: 2580,
                        flight_info: {
                            departure_city: '上海',
                            departure_airport: '虹桥国际机场',
                            departure_time: '2024-07-10 08:30:00',
                            arrival_city: '北京',
                            arrival_airport: '首都国际机场',
                            arrival_time: '2024-07-10 10:40:00',
                            airline: '东方航空',
                            flight_number: 'MU5137'
                        },
                        passengers: [
                            { name: '张三' },
                            { name: '李四' }
                        ]
                    },
                    {
                        id: 2,
                        order_number: 'ORD202406190002',
                        created_at: '2024-06-19 15:20:00',
                        status: 'PENDING',
                        total_amount: 1290,
                        flight_info: {
                            departure_city: '广州',
                            departure_airport: '白云国际机场',
                            departure_time: '2024-07-15 14:20:00',
                            arrival_city: '成都',
                            arrival_airport: '双流国际机场',
                            arrival_time: '2024-07-15 16:45:00',
                            airline: '南方航空',
                            flight_number: 'CZ3456'
                        },
                        passengers: [
                            { name: '张三' }
                        ]
                    },
                    {
                        id: 3,
                        order_number: 'ORD202406150003',
                        created_at: '2024-06-15 09:15:00',
                        status: 'CANCELLED',
                        total_amount: 3260,
                        flight_info: {
                            departure_city: '上海',
                            departure_airport: '浦东国际机场',
                            departure_time: '2024-06-30 21:10:00',
                            arrival_city: '深圳',
                            arrival_airport: '宝安国际机场',
                            arrival_time: '2024-06-30 23:30:00',
                            airline: '中国国际航空',
                            flight_number: 'CA1234'
                        },
                        passengers: [
                            { name: '张三' },
                            { name: '李四' },
                            { name: '王五' }
                        ]
                    }
                ]

                totalOrders.value = orders.value.length
                loading.value = false
            }, 500)

            /* 实际API调用代码（暂时注释掉）
            try {
              const params = {
                page: currentPage.value,
                page_size: pageSize.value
              }
              
              if (orderStatus.value) {
                params.status = orderStatus.value
              }
              
              const response = await api.orders.getAll(params)
              orders.value = response.results
              totalOrders.value = response.count
            } catch (error) {
              console.error('获取订单列表失败:', error)
              ElMessage.error('获取订单列表失败，请稍后重试')
            } finally {
              loading.value = false
            }
            */
        }

        // 格式化日期
        const formatDate = (dateString, format = 'YYYY-MM-DD HH:mm') => {
            if (!dateString) return ''
            const date = new Date(dateString)
            const year = date.getFullYear()
            const month = String(date.getMonth() + 1).padStart(2, '0')
            const day = String(date.getDate()).padStart(2, '0')
            const hours = String(date.getHours()).padStart(2, '0')
            const minutes = String(date.getMinutes()).padStart(2, '0')

            if (format === 'YYYY-MM-DD') {
                return `${year}-${month}-${day}`
            }

            return `${year}-${month}-${day} ${hours}:${minutes}`
        }

        // 格式化时间
        const formatTime = (dateString) => {
            if (!dateString) return ''
            const date = new Date(dateString)
            const hours = String(date.getHours()).padStart(2, '0')
            const minutes = String(date.getMinutes()).padStart(2, '0')
            return `${hours}:${minutes}`
        }

        // 获取状态显示文本
        const getStatusText = (status) => {
            const statusMap = {
                'PENDING': '待支付',
                'PAID': '已支付',
                'CANCELLED': '已取消',
                'REFUNDED': '已退款'
            }
            return statusMap[status] || status
        }

        // 获取状态标签类型
        const getStatusType = (status) => {
            const typeMap = {
                'PENDING': 'warning',
                'PAID': 'success',
                'CANCELLED': 'info',
                'REFUNDED': 'info'
            }
            return typeMap[status] || ''
        }

        // 处理页码变化
        const handleCurrentChange = (page) => {
            currentPage.value = page
            fetchOrders()
        }

        // 处理每页数量变化
        const handleSizeChange = (size) => {
            pageSize.value = size
            currentPage.value = 1
            fetchOrders()
        }

        // 处理筛选变化
        const handleFilterChange = () => {
            currentPage.value = 1
            fetchOrders()
        }

        // 查看订单详情
        const viewOrderDetail = (orderId) => {
            router.push(`/orders/${orderId}`)
        }

        // 前往支付
        const goToPayment = (orderId) => {
            router.push(`/payment/${orderId}`)
        }

        // 取消订单
        const cancelOrder = (order) => {
            currentOrder.value = order
            cancelDialogVisible.value = true
        }

        // 确认取消订单
        const confirmCancelOrder = () => {
            if (!currentOrder.value || !currentOrder.value.id) return

            cancelling.value = true

            // 模拟取消订单（因为API尚未接入）
            setTimeout(() => {
                const orderIndex = orders.value.findIndex(order => order.id === currentOrder.value.id)
                if (orderIndex !== -1) {
                    orders.value[orderIndex].status = 'CANCELLED'
                }
                ElMessage.success('订单取消成功')
                cancelDialogVisible.value = false
                cancelling.value = false
            }, 500)

            /* 实际API调用代码（暂时注释掉）
            try {
                await api.orders.cancel(currentOrder.value.id)
                ElMessage.success('订单取消成功')
                cancelDialogVisible.value = false
                fetchOrders()
            } catch (error) {
                console.error('取消订单失败:', error)
                ElMessage.error('取消订单失败，请稍后重试')
            } finally {
                cancelling.value = false
            }
            */
        }

        onMounted(() => {
            fetchOrders()
        })

        return {
            loading,
            orders,
            totalOrders,
            currentPage,
            pageSize,
            orderStatus,
            cancelDialogVisible,
            cancelling,
            currentOrder,
            formatDate,
            formatTime,
            getStatusText,
            getStatusType,
            handleCurrentChange,
            handleSizeChange,
            handleFilterChange,
            viewOrderDetail,
            goToPayment,
            cancelOrder,
            confirmCancelOrder
        }
    }
}
</script>

<style scoped>
.order-history-tab {
    padding: 10px;
}

.order-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}

.order-header h3 {
    margin: 0;
}

.loading-container,
.empty-container {
    padding: 20px;
}

.order-list {
    margin-bottom: 20px;
}

.order-card {
    margin-bottom: 15px;
}

.order-card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
}

.order-number {
    font-weight: bold;
    margin-right: 15px;
}

.flight-info {
    display: flex;
    justify-content: space-between;
    margin-bottom: 15px;
    padding: 10px;
    background-color: #f8f9fa;
    border-radius: 4px;
}

.route-info {
    display: flex;
    align-items: center;
}

.departure,
.arrival {
    text-align: center;
}

.city {
    font-size: 18px;
    font-weight: bold;
}

.airport {
    font-size: 12px;
    color: #909399;
}

.time {
    font-size: 16px;
    margin-top: 5px;
}

.flight-arrow {
    margin: 0 20px;
    color: #909399;
}

.flight-detail {
    display: flex;
    flex-direction: column;
    justify-content: center;
    text-align: right;
}

.passenger-info {
    display: flex;
    align-items: center;
    margin-bottom: 15px;
}

.passenger-count {
    display: flex;
    align-items: center;
    margin-right: 15px;
}

.passenger-count .el-icon {
    margin-right: 5px;
}

.order-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-top: 1px solid #ebeef5;
    padding-top: 15px;
}

.price-label {
    margin-right: 5px;
}

.price-value {
    font-size: 18px;
    font-weight: bold;
    color: #f56c6c;
}

.actions {
    display: flex;
    gap: 10px;
}

.pagination-container {
    display: flex;
    justify-content: center;
    margin-top: 20px;
}
</style>