<template>
    <div class="ticket-list-tab">
        <div class="ticket-header">
            <h3>我的机票</h3>
            <el-select v-model="ticketStatus" placeholder="机票状态" style="width: 150px" @change="handleFilterChange">
                <el-option label="全部机票" value="" />
                <el-option label="未使用" value="UNUSED" />
                <el-option label="已使用" value="USED" />
                <el-option label="已退票" value="REFUNDED" />
                <el-option label="已过期" value="EXPIRED" />
            </el-select>
        </div>

        <div v-if="loading" class="loading-container">
            <el-skeleton :rows="3" animated />
            <el-divider />
            <el-skeleton :rows="3" animated />
        </div>

        <div v-else-if="tickets.length === 0" class="empty-container">
            <el-empty description="暂无机票记录" />
        </div>

        <div v-else class="ticket-list">
            <el-card v-for="ticket in tickets" :key="ticket.id" class="ticket-card" shadow="hover">
                <div class="ticket-card-header">
                    <div class="ticket-info">
                        <span class="ticket-number">票号: {{ ticket.ticket_number }}</span>
                        <span class="order-date">订单号: {{ ticket.order_number }}</span>
                    </div>
                    <el-tag :type="getStatusType(ticket.status)">{{ getStatusText(ticket.status) }}</el-tag>
                </div>

                <div class="flight-info">
                    <div class="route-info">
                        <div class="departure">
                            <div class="city">{{ ticket.flight_info.departure_city }}</div>
                            <div class="airport">{{ ticket.flight_info.departure_airport }}</div>
                            <div class="time">{{ formatTime(ticket.flight_info.departure_time) }}</div>
                            <div class="date">{{ formatDate(ticket.flight_info.departure_time, 'YYYY-MM-DD') }}</div>
                        </div>

                        <div class="flight-arrow">
                            <el-icon>
                                <ArrowRight />
                            </el-icon>
                        </div>

                        <div class="arrival">
                            <div class="city">{{ ticket.flight_info.arrival_city }}</div>
                            <div class="airport">{{ ticket.flight_info.arrival_airport }}</div>
                            <div class="time">{{ formatTime(ticket.flight_info.arrival_time) }}</div>
                            <div class="date">{{ formatDate(ticket.flight_info.arrival_time, 'YYYY-MM-DD') }}</div>
                        </div>
                    </div>
                </div>

                <div class="ticket-detail">
                    <div class="flight-detail">
                        <div class="detail-item">
                            <span class="detail-label">航班:</span>
                            <span class="detail-value">{{ ticket.flight_info.airline }} {{
                                ticket.flight_info.flight_number }}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">座位:</span>
                            <span class="detail-value">{{ ticket.seat_info.cabin_class }} {{
                                ticket.seat_info.seat_number }}</span>
                        </div>
                    </div>

                    <div class="passenger-detail">
                        <div class="detail-item">
                            <span class="detail-label">乘客:</span>
                            <span class="detail-value">{{ ticket.passenger_info.name }}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">证件:</span>
                            <span class="detail-value">{{ ticket.passenger_info.id_card }}</span>
                        </div>
                    </div>
                </div>

                <div class="barcode-section">
                    <img :src="ticket.barcode_url || 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAASwAAABkCAYAAAA8AQ3AAAAACXBIWXMAAA7EAAAOxAGVKw4bAAABYklEQVR4nO3VMQ0AMAzAsJU/6YHoMS2yEeTJ7O4AEzj+AcAisIBMYAGZwAIygQVkAgvIBBaQCSwgE1hAJrCATGABmcACMoEFZAILyAQWkAksIBNYQCawgExgAZnAAjKBBWQCC8gEFpAJLCATWEAmsIBMYAGZwAIygQVkAgvIBBaQCSwgE1hAJrCATGABmcACMoEFZAILyAQWkAksIBNYQCawgExgAZnAAjKBBWQCC8gEFpAJLCATWEAmsIBMYAGZwAIygQVkAgvIBBaQCSwgE1hAJrCATGABmcACMoEFZAILyAQWkAksIBNYQCawgExgAZnAAjKBBWQCC8gEFpAJLCATWEAmsIBMYAGZwAIygQVkAgvIBBaQCSwgE1hAJrCATGABmcACMoEFZAILyAQWkAksIBNYQCawgExgAZnAAjKBBWQCC8gEFpAJLCATWEAmsIBMYAGZwAIygQVkAgvIBBaQCSzg8gCHzQN3JA6KqQAAAABJRU5ErkJggg=='"
                        class="barcode-image" />
                </div>

                <div class="ticket-footer">
                    <div class="flight-status" v-if="ticket.status === 'UNUSED'">
                        <div class="countdown" v-if="getFlightCountdown(ticket.flight_info.departure_time)">
                            距离起飞还有: {{ getFlightCountdown(ticket.flight_info.departure_time) }}
                        </div>
                    </div>

                    <div class="actions">
                        <el-button v-if="ticket.status === 'UNUSED' && canCheckin(ticket.flight_info.departure_time)"
                            type="primary" size="small" @click="goToCheckin(ticket.id)">
                            在线值机
                        </el-button>

                        <el-button v-if="ticket.status === 'UNUSED'" type="danger" size="small"
                            @click="handleRefund(ticket)" plain>
                            申请退票
                        </el-button>

                        <el-button type="primary" size="small" @click="viewOrderDetail(ticket.order_id)" plain>
                            查看订单
                        </el-button>
                    </div>
                </div>
            </el-card>
        </div>

        <!-- 分页 -->
        <div class="pagination-container">
            <el-pagination v-model:current-page="currentPage" v-model:page-size="pageSize" :page-sizes="[5, 10, 20]"
                layout="total, sizes, prev, pager, next" :total="totalTickets" @size-change="handleSizeChange"
                @current-change="handleCurrentChange" />
        </div>

        <!-- 退票确认对话框 -->
        <el-dialog v-model="refundDialogVisible" title="申请退票" width="400px">
            <div>
                <p>确定要申请退票吗？</p>
                <p class="refund-info">票号: {{ currentTicket?.ticket_number || '' }}</p>
                <p class="refund-info">航班: {{ currentTicket?.flight_info?.airline || '' }} {{
                    currentTicket?.flight_info?.flight_number || '' }}</p>
                <p class="refund-info">
                    航线: {{ currentTicket?.flight_info?.departure_city || '' }} - {{
                        currentTicket?.flight_info?.arrival_city || '' }}
                </p>
                <p class="refund-warning">注意: 退票可能会收取手续费，具体以航空公司规定为准。</p>
            </div>
            <template #footer>
                <span class="dialog-footer">
                    <el-button @click="refundDialogVisible = false">取消</el-button>
                    <el-button type="danger" @click="confirmRefund" :loading="refunding">
                        确认退票
                    </el-button>
                </span>
            </template>
        </el-dialog>
    </div>
</template>

<script>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowRight } from '@element-plus/icons-vue'
// import api from '@/services/api' // 暂时不使用API

export default {
    name: 'TicketListTab',
    components: {
        ArrowRight
    },
    setup() {
        const router = useRouter()
        const loading = ref(false)
        const refunding = ref(false)
        const tickets = ref([])
        const totalTickets = ref(0)
        const currentPage = ref(1)
        const pageSize = ref(5)
        const ticketStatus = ref('')
        const refundDialogVisible = ref(false)
        const currentTicket = ref(null)
        const updateInterval = ref(null)

        // 获取机票列表
        const fetchTickets = () => {
            loading.value = true

            // 使用模拟数据（因为API尚未接入）
            setTimeout(() => {
                const mockTickets = [
                    {
                        id: 1,
                        ticket_number: 'TK20240610001',
                        order_number: 'ORD202406200001',
                        status: 'UNUSED',
                        flight_info: {
                            airline: '东方航空',
                            flight_number: 'MU5137',
                            departure_city: '上海',
                            departure_airport: '虹桥国际机场',
                            departure_terminal: 'T2',
                            departure_time: '2024-07-10 08:30:00',
                            arrival_city: '北京',
                            arrival_airport: '首都国际机场',
                            arrival_terminal: 'T3',
                            arrival_time: '2024-07-10 10:40:00'
                        },
                        seat_info: {
                            cabin_class: '经济舱',
                            seat_number: '14A'
                        },
                        passenger_info: {
                            name: '张三',
                            id_card: '310000********0000'
                        },
                        barcode_url: 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAASwAAABkCAYAAAA8AQ3AAAAACXBIWXMAAA7EAAAOxAGVKw4bAAABYklEQVR4nO3VMQ0AMAzAsJU/6YHoMS2yEeTJ7O4AEzj+AcAisIBMYAGZwAIygQVkAgvIBBaQCSwgE1hAJrCATGABmcACMoEFZAILyAQWkAksIBNYQCawgExgAZnAAjKBBWQCC8gEFpAJLCATWEAmsIBMYAGZwAIygQVkAgvIBBaQCSwgE1hAJrCATGABmcACMoEFZAILyAQWkAksIBNYQCawgExgAZnAAjKBBWQCC8gEFpAJLCATWEAmsIBMYAGZwAIygQVkAgvIBBaQCSwgE1hAJrCATGABmcACMoEFZAILyAQWkAksIBNYQCawgExgAZnAAjKBBWQCC8gEFpAJLCATWEAmsIBMYAGZwAIygQVkAgvIBBaQCSwgE1hAJrCATGABmcACMoEFZAILyAQWkAksIBNYQCawgExgAZnAAjKBBWQCC8gEFpAJLCATWEAmsIBMYAGZwAIygQVkAgvIBBaQCSzg8gCHzQN3JA6KqQAAAABJRU5ErkJggg==',
                        order_id: 1
                    },
                    {
                        id: 2,
                        ticket_number: 'TK20240610002',
                        order_number: 'ORD202406200001',
                        status: 'UNUSED',
                        flight_info: {
                            airline: '东方航空',
                            flight_number: 'MU5137',
                            departure_city: '上海',
                            departure_airport: '虹桥国际机场',
                            departure_terminal: 'T2',
                            departure_time: '2024-07-10 08:30:00',
                            arrival_city: '北京',
                            arrival_airport: '首都国际机场',
                            arrival_terminal: 'T3',
                            arrival_time: '2024-07-10 10:40:00'
                        },
                        seat_info: {
                            cabin_class: '经济舱',
                            seat_number: '14B'
                        },
                        passenger_info: {
                            name: '李四',
                            id_card: 'P12345678'
                        },
                        barcode_url: 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAASwAAABkCAYAAAA8AQ3AAAAACXBIWXMAAA7EAAAOxAGVKw4bAAABYklEQVR4nO3VMQ0AMAzAsJU/6YHoMS2yEeTJ7O4AEzj+AcAisIBMYAGZwAIygQVkAgvIBBaQCSwgE1hAJrCATGABmcACMoEFZAILyAQWkAksIBNYQCawgExgAZnAAjKBBWQCC8gEFpAJLCATWEAmsIBMYAGZwAIygQVkAgvIBBaQCSwgE1hAJrCATGABmcACMoEFZAILyAQWkAksIBNYQCawgExgAZnAAjKBBWQCC8gEFpAJLCATWEAmsIBMYAGZwAIygQVkAgvIBBaQCSwgE1hAJrCATGABmcACMoEFZAILyAQWkAksIBNYQCawgExgAZnAAjKBBWQCC8gEFpAJLCATWEAmsIBMYAGZwAIygQVkAgvIBBaQCSwgE1hAJrCATGABmcACMoEFZAILyAQWkAksIBNYQCawgExgAZnAAjKBBWQCC8gEFpAJLCATWEAmsIBMYAGZwAIygQVkAgvIBBaQCSzg8gCHzQN3JA6KqQAAAABJRU5ErkJggg==',
                        order_id: 1
                    },
                    {
                        id: 3,
                        ticket_number: 'TK20240615001',
                        order_number: 'ORD202406190002',
                        status: 'UNUSED',
                        flight_info: {
                            airline: '南方航空',
                            flight_number: 'CZ3456',
                            departure_city: '广州',
                            departure_airport: '白云国际机场',
                            departure_terminal: 'T1',
                            departure_time: '2024-07-15 14:20:00',
                            arrival_city: '成都',
                            arrival_airport: '双流国际机场',
                            arrival_terminal: 'T2',
                            arrival_time: '2024-07-15 16:45:00'
                        },
                        seat_info: {
                            cabin_class: '经济舱',
                            seat_number: '23C'
                        },
                        passenger_info: {
                            name: '张三',
                            id_card: '310000********0000'
                        },
                        barcode_url: 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAASwAAABkCAYAAAA8AQ3AAAAACXBIWXMAAA7EAAAOxAGVKw4bAAABYklEQVR4nO3VMQ0AMAzAsJU/6YHoMS2yEeTJ7O4AEzj+AcAisIBMYAGZwAIygQVkAgvIBBaQCSwgE1hAJrCATGABmcACMoEFZAILyAQWkAksIBNYQCawgExgAZnAAjKBBWQCC8gEFpAJLCATWEAmsIBMYAGZwAIygQVkAgvIBBaQCSwgE1hAJrCATGABmcACMoEFZAILyAQWkAksIBNYQCawgExgAZnAAjKBBWQCC8gEFpAJLCATWEAmsIBMYAGZwAIygQVkAgvIBBaQCSwgE1hAJrCATGABmcACMoEFZAILyAQWkAksIBNYQCawgExgAZnAAjKBBWQCC8gEFpAJLCATWEAmsIBMYAGZwAIygQVkAgvIBBaQCSzg8gCHzQN3JA6KqQAAAABJRU5ErkJggg==',
                        order_id: 2
                    }
                ]

                // 根据筛选条件过滤
                if (ticketStatus.value) {
                    tickets.value = mockTickets.filter(ticket => ticket.status === ticketStatus.value)
                } else {
                    tickets.value = mockTickets
                }

                totalTickets.value = tickets.value.length
                loading.value = false
            }, 500)

            /* 实际API调用代码（暂时注释掉）
            try {
                const params = {
                    page: currentPage.value,
                    page_size: pageSize.value
                }

                if (ticketStatus.value) {
                    params.status = ticketStatus.value
                }

                const response = await api.tickets.getAll(params)
                tickets.value = response.results
                totalTickets.value = response.count
            } catch (error) {
                console.error('获取机票列表失败:', error)
                ElMessage.error('获取机票列表失败，请稍后重试')
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
                'UNUSED': '未使用',
                'USED': '已使用',
                'REFUNDED': '已退票',
                'EXPIRED': '已过期'
            }
            return statusMap[status] || status
        }

        // 获取状态标签类型
        const getStatusType = (status) => {
            const typeMap = {
                'UNUSED': 'success',
                'USED': 'info',
                'REFUNDED': 'warning',
                'EXPIRED': 'danger'
            }
            return typeMap[status] || ''
        }

        // 获取航班倒计时
        const getFlightCountdown = (departureTime) => {
            if (!departureTime) return null

            const departure = new Date(departureTime)
            const now = new Date()
            const diffTime = departure - now

            // 如果已经过了起飞时间
            if (diffTime <= 0) return null

            const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24))
            const diffHours = Math.floor((diffTime % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60))
            const diffMinutes = Math.floor((diffTime % (1000 * 60 * 60)) / (1000 * 60))

            if (diffDays > 0) {
                return `${diffDays}天 ${diffHours}小时`
            } else {
                return `${diffHours}小时 ${diffMinutes}分钟`
            }
        }

        // 判断是否可以在线值机
        const canCheckin = (departureTime) => {
            if (!departureTime) return false

            const departure = new Date(departureTime)
            const now = new Date()
            const diffTime = departure - now

            // 起飞前24小时到起飞前2小时可以值机
            const hours24 = 24 * 60 * 60 * 1000
            const hours2 = 2 * 60 * 60 * 1000

            return diffTime > hours2 && diffTime < hours24
        }

        // 处理页码变化
        const handleCurrentChange = (page) => {
            currentPage.value = page
            fetchTickets()
        }

        // 处理每页数量变化
        const handleSizeChange = (size) => {
            pageSize.value = size
            currentPage.value = 1
            fetchTickets()
        }

        // 处理筛选变化
        const handleFilterChange = () => {
            currentPage.value = 1
            fetchTickets()
        }

        // 查看订单详情
        const viewOrderDetail = (orderId) => {
            router.push(`/orders/${orderId}`)
        }

        // 前往值机页面
        const goToCheckin = (ticketId) => {
            router.push(`/checkin/${ticketId}`)
        }

        // 处理退票
        const handleRefund = (ticket) => {
            currentTicket.value = ticket
            refundDialogVisible.value = true
        }

        // 确认退票
        const confirmRefund = () => {
            if (!currentTicket.value || !currentTicket.value.id) return

            refunding.value = true

            // 模拟退票（因为API尚未接入）
            setTimeout(() => {
                // 找到对应机票并修改状态
                const index = tickets.value.findIndex(ticket => ticket.id === currentTicket.value.id)
                if (index !== -1) {
                    tickets.value[index].status = 'REFUNDED'
                }

                ElMessage.success('退票申请已提交，请等待处理')
                refundDialogVisible.value = false
                refunding.value = false
            }, 500)

            /* 实际API调用代码（暂时注释掉）
            try {
                await api.tickets.refund(currentTicket.value.id)
                ElMessage.success('退票申请已提交，请等待处理')
                refundDialogVisible.value = false
                fetchTickets()
            } catch (error) {
                console.error('退票申请失败:', error)
                ElMessage.error('退票申请失败，请稍后重试')
            } finally {
                refunding.value = false
            }
            */
        }

        // 定时刷新倒计时
        onMounted(() => {
            fetchTickets()

            // 每分钟更新一次倒计时
            updateInterval.value = setInterval(() => {
                // 强制组件重新渲染
                tickets.value = [...tickets.value]
            }, 60000)
        })

        onBeforeUnmount(() => {
            // 清除定时器
            if (updateInterval.value) {
                clearInterval(updateInterval.value)
            }
        })

        return {
            loading,
            tickets,
            totalTickets,
            currentPage,
            pageSize,
            ticketStatus,
            refundDialogVisible,
            refunding,
            currentTicket,
            formatDate,
            formatTime,
            getStatusText,
            getStatusType,
            getFlightCountdown,
            canCheckin,
            handleCurrentChange,
            handleSizeChange,
            handleFilterChange,
            viewOrderDetail,
            goToCheckin,
            handleRefund,
            confirmRefund
        }
    }
}
</script>

<style scoped>
.ticket-list-tab {
    padding: 10px;
}

.ticket-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}

.ticket-header h3 {
    margin: 0;
}

.loading-container,
.empty-container {
    padding: 20px;
}

.ticket-list {
    margin-bottom: 20px;
}

.ticket-card {
    margin-bottom: 15px;
    border-radius: 8px;
    overflow: hidden;
}

.ticket-card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
}

.ticket-number {
    font-weight: bold;
    margin-right: 15px;
}

.flight-info {
    margin-bottom: 15px;
    padding: 15px;
    background-color: #f8f9fa;
    border-radius: 8px;
}

.route-info {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.departure,
.arrival {
    text-align: center;
}

.city {
    font-size: 20px;
    font-weight: bold;
}

.airport {
    font-size: 12px;
    color: #909399;
}

.time {
    font-size: 18px;
    font-weight: bold;
    margin-top: 5px;
}

.date {
    font-size: 12px;
    color: #606266;
}

.flight-arrow {
    margin: 0 30px;
    color: #909399;
}

.ticket-detail {
    display: flex;
    justify-content: space-between;
    margin-bottom: 15px;
}

.detail-item {
    margin-bottom: 5px;
}

.detail-label {
    color: #909399;
    margin-right: 5px;
}

.barcode-section {
    text-align: center;
    margin-bottom: 15px;
    padding: 10px 0;
    border-top: 1px dashed #dcdfe6;
    border-bottom: 1px dashed #dcdfe6;
}

.barcode-image {
    max-width: 100%;
    height: auto;
}

.ticket-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.countdown {
    font-weight: bold;
    color: #409eff;
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

.refund-info {
    margin: 5px 0;
}

.refund-warning {
    margin-top: 10px;
    color: #f56c6c;
    font-size: 12px;
}
</style>