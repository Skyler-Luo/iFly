<template>
    <div class="order-detail-view">
        <div class="header-banner">
            <h1>订单详情</h1>
            <div class="order-status" :class="statusClass">{{ orderStatusText }}</div>
        </div>

        <div class="order-container" v-if="order">
            <div class="order-header">
                <div class="order-id">
                    <span class="label">订单编号:</span>
                    <span class="value">{{ order.orderNumber }}</span>
                </div>
                <div class="order-time">
                    <span class="label">下单时间:</span>
                    <span class="value">{{ formatDate(order.createdAt) }}</span>
                </div>
                <div class="actions">
                    <el-button type="primary" size="small" @click="printOrder">
                        <i class="el-icon-printer"></i> 打印订单
                    </el-button>
                    <el-button v-if="order.status === 'pending'" type="danger" plain size="small"
                        @click="showCancelDialog">
                        取消订单
                    </el-button>
                </div>
            </div>

            <div class="section-card">
                <div class="section-title">
                    <i class="el-icon-info"></i>
                    <span>订单状态</span>
                </div>
                <div class="status-timeline">
                    <el-steps :active="getStatusStep()" finish-status="success" align-center>
                        <el-step title="订单提交" :description="formatDateTime(order.createdAt)"></el-step>
                        <el-step title="支付完成"
                            :description="order.paidAt ? formatDateTime(order.paidAt) : '等待支付'"></el-step>
                        <el-step title="出票完成"
                            :description="order.ticketedAt ? formatDateTime(order.ticketedAt) : '等待出票'"></el-step>
                        <el-step title="行程完成"
                            :description="order.completedAt ? formatDateTime(order.completedAt) : '等待出行'"></el-step>
                    </el-steps>
                </div>
            </div>

            <div class="section-card">
                <div class="section-title">
                    <i class="el-icon-tickets"></i>
                    <span>航班信息</span>
                </div>
                <div class="flight-cards">
                    <div class="flight-card" v-for="(ticket, index) in order.tickets" :key="index">
                        <div class="flight-header">
                            <div class="airline">
                                <div class="airline-icon">
                                    <span class="plane-svg"></span>
                                </div>
                                <div class="airline-info">
                                    <div class="airline-name">{{ ticket.flight?.airlineName || '未知航空' }}</div>
                                    <div class="flight-number">{{ ticket.flight?.flightNumber || '未知航班' }}</div>
                                </div>
                            </div>
                            <div class="flight-status"
                                :class="getFlightStatusClass(ticket.flight?.status || 'scheduled')">
                                {{ getFlightStatusText(ticket.flight?.status || 'scheduled') }}
                            </div>
                        </div>

                        <div class="flight-journey">
                            <div class="departure">
                                <div class="time">{{ formatTime(ticket.flight?.departureTime) || '--:--' }}</div>
                                <div class="date">{{ formatDate(ticket.flight?.departureTime) || '未知日期' }}</div>
                                <div class="city">{{ ticket.flight?.departureCity || '未知城市' }}</div>
                                <div class="airport">{{ ticket.flight?.departureAirport || '未知机场' }}</div>
                            </div>

                            <div class="flight-direction">
                                <div class="direction-line"></div>
                                <div class="duration">{{ formatDuration(ticket.flight?.duration) }}</div>
                                <div class="cabin-class">{{ getCabinLabel(ticket.cabinClass) }}</div>
                            </div>

                            <div class="arrival">
                                <div class="time">{{ formatTime(ticket.flight?.arrivalTime) || '--:--' }}</div>
                                <div class="date">{{ formatDate(ticket.flight?.arrivalTime) || '未知日期' }}</div>
                                <div class="city">{{ ticket.flight?.arrivalCity || '未知城市' }}</div>
                                <div class="airport">{{ ticket.flight?.arrivalAirport || '未知机场' }}</div>
                            </div>
                        </div>

                        <div class="ticket-info">
                            <div class="seat">
                                <span class="label">座位:</span>
                                <span class="value">{{ ticket.seatNumber || '--' }}</span>
                            </div>
                            <div class="passenger">
                                <span class="label">乘客:</span>
                                <span class="value">{{ ticket.passenger?.name || '未知乘客' }}</span>
                            </div>
                            <div class="ticket-number">
                                <span class="label">票号:</span>
                                <span class="value">{{ ticket.ticketNumber || '--' }}</span>
                            </div>
                        </div>

                        <!-- 值机状态展示 -->
                        <div class="checkin-status" v-if="ticket.checkedIn">
                            <div class="checkin-badge">
                                <el-tag type="success" size="small">
                                    <i class="el-icon-check"></i> 已值机
                                </el-tag>
                                <span class="checkin-time" v-if="ticket.checkedInAt">
                                    {{ formatDateTime(ticket.checkedInAt) }}
                                </span>
                            </div>
                            <div class="boarding-info">
                                <div class="boarding-item" v-if="ticket.gate">
                                    <span class="label">登机口:</span>
                                    <span class="value highlight">{{ ticket.gate }}</span>
                                </div>
                                <div class="boarding-item" v-if="ticket.boardingPassNumber">
                                    <span class="label">登机牌号:</span>
                                    <span class="value">{{ ticket.boardingPassNumber }}</span>
                                </div>
                            </div>
                        </div>

                        <div class="ticket-actions">
                            <el-button v-if="canReschedule(ticket)" type="warning" size="small" plain
                                @click="goToReschedule(ticket)">
                                改签
                            </el-button>
                            <el-button v-if="canRefund(ticket)" type="danger" size="small" plain
                                @click="showRefundDialog(ticket)">
                                申请退票
                            </el-button>
                            <el-button v-if="canCheckIn(ticket)" type="primary" size="small"
                                @click="goToCheckIn(ticket)">
                                在线值机
                            </el-button>
                            <el-button v-if="ticket.checkedIn" type="success" size="small"
                                @click="viewBoardingPass(ticket)">
                                查看登机牌
                            </el-button>
                            <el-button type="info" size="small" plain @click="showTicketDetail(ticket)">
                                查看详情
                            </el-button>
                        </div>
                    </div>

                    <!-- 如果没有机票数据，显示提示 -->
                    <div v-if="!order.tickets || order.tickets.length === 0" class="no-tickets-message">
                        <i class="el-icon-warning-outline"></i>
                        <p>未找到航班信息</p>
                    </div>
                </div>
            </div>

            <div class="section-card">
                <div class="section-title">
                    <i class="el-icon-user"></i>
                    <span>乘客信息</span>
                </div>
                <div class="passenger-list">
                    <el-table :data="order.passengers" stripe style="width: 100%">
                        <el-table-column prop="name" label="姓名"></el-table-column>
                        <el-table-column prop="idType" label="证件类型">
                            <template #default="scope">
                                {{ getIdTypeLabel(scope.row.idType) }}
                            </template>
                        </el-table-column>
                        <el-table-column prop="idNumber" label="证件号码"></el-table-column>
                        <el-table-column prop="phone" label="联系电话"></el-table-column>
                        <template #empty>
                            <div class="empty-text">
                                <i class="el-icon-info"></i>
                                <p>暂无乘客信息</p>
                            </div>
                        </template>
                    </el-table>
                </div>
            </div>

            <div class="section-card">
                <div class="section-title">
                    <i class="el-icon-wallet"></i>
                    <span>支付信息</span>
                </div>
                <div class="payment-info">
                    <div class="payment-row">
                        <span class="label">支付状态:</span>
                        <span class="value" :class="order.paidAt ? 'success-text' : 'warning-text'">
                            {{ order.paidAt ? '已支付' : '待支付' }}
                        </span>
                    </div>
                    <div class="payment-row" v-if="order.status === 'pending' && remainingPaymentSeconds > 0">
                        <span class="label">剩余支付时间:</span>
                        <span class="value">
                            <CountdownTimer 
                                :remaining-seconds="remainingPaymentSeconds"
                                :warning-threshold="300"
                                @timeout="handlePaymentTimeout"
                            />
                        </span>
                    </div>
                    <div class="payment-row" v-if="order.paidAt">
                        <span class="label">支付时间:</span>
                        <span class="value">{{ formatDateTime(order.paidAt) }}</span>
                    </div>
                    <div class="payment-row">
                        <span class="label">支付方式:</span>
                        <span class="value">{{ getPaymentMethodLabel(order.paymentMethod) }}</span>
                    </div>
                    <div class="payment-row">
                        <span class="label">订单金额:</span>
                        <span class="value price">¥ {{ order.totalAmount.toFixed(2) }}</span>
                    </div>

                    <div class="price-detail">
                        <div class="price-item" v-for="(item, index) in order.priceDetail" :key="index">
                            <span class="item-name">{{ item.name }}</span>
                            <span class="item-value">¥ {{ item.amount.toFixed(2) }}</span>
                        </div>
                        <div class="price-total">
                            <span class="total-label">总计</span>
                            <span class="total-value">¥ {{ order.totalAmount.toFixed(2) }}</span>
                        </div>
                    </div>
                </div>

                <div class="payment-action" v-if="order.status === 'pending'">
                    <el-button type="primary" @click="goToPay">
                        立即支付 ¥{{ order.totalAmount.toFixed(2) }}
                    </el-button>
                </div>
            </div>

            <div class="section-card">
                <div class="section-title">
                    <i class="el-icon-document"></i>
                    <span>订单备注</span>
                </div>
                <div class="remarks">
                    <p v-if="order.remarks">{{ order.remarks }}</p>
                    <p v-else class="no-remarks">暂无备注</p>

                    <div class="add-remark" v-if="!isEditingRemark">
                        <el-button type="text" @click="startEditRemark">
                            {{ order.remarks ? '修改备注' : '添加备注' }}
                        </el-button>
                    </div>

                    <div v-else class="edit-remark">
                        <el-input type="textarea" v-model="remarkContent" :rows="3" placeholder="请输入备注内容"></el-input>
                        <div class="remark-actions">
                            <el-button size="small" @click="cancelEditRemark">取消</el-button>
                            <el-button type="primary" size="small" @click="saveRemark">保存</el-button>
                        </div>
                    </div>
                </div>
            </div>

            <div class="related-actions">
                <el-button plain @click="goToOrderList">
                    <i class="el-icon-back"></i> 返回订单列表
                </el-button>
                <el-button plain @click="goToHomePage">
                    <i class="el-icon-s-home"></i> 返回首页
                </el-button>
            </div>
        </div>

        <div v-else-if="isLoading" class="loading-container">
            <div class="loading-spinner">
                <i class="el-icon-loading"></i>
            </div>
            <p>正在加载订单信息...</p>
        </div>

        <div v-else class="error-container">
            <i class="el-icon-warning-outline"></i>
            <h2>未找到订单</h2>
            <p>抱歉，无法找到该订单信息或您没有权限查看。</p>
            <el-button type="primary" @click="goToOrderList">返回订单列表</el-button>
        </div>

        <!-- 退票对话框 -->
        <el-dialog title="申请退票" v-model="refundDialogVisible" width="500px">
            <div class="refund-dialog-content">
                <div class="refund-info">
                    <p class="refund-notice">请确认是否要退票，退票可能会收取手续费。</p>

                    <div class="refund-ticket-info" v-if="selectedTicket">
                        <div class="info-row">
                            <span class="label">航班:</span>
                            <span class="value">{{ selectedTicket.flight.flightNumber }}</span>
                        </div>
                        <div class="info-row">
                            <span class="label">路线:</span>
                            <span class="value">{{ selectedTicket.flight.departureCity }} - {{
                                selectedTicket.flight.arrivalCity
                                }}</span>
                        </div>
                        <div class="info-row">
                            <span class="label">日期:</span>
                            <span class="value">{{ formatDate(selectedTicket.flight.departureTime) }}</span>
                        </div>
                        <div class="info-row">
                            <span class="label">乘客:</span>
                            <span class="value">{{ selectedTicket.passenger.name }}</span>
                        </div>
                        <div class="info-row">
                            <span class="label">座位:</span>
                            <span class="value">{{ selectedTicket.seatNumber }}</span>
                        </div>
                    </div>

                    <div class="refund-fee">
                        <div class="fee-row">
                            <span class="label">票价:</span>
                            <span class="value">¥ {{ selectedTicket ? selectedTicket.price.toFixed(2) : '0.00' }}</span>
                        </div>
                        <div class="fee-row">
                            <span class="label">退票手续费:</span>
                            <span class="value">¥ {{ calculateRefundFee().toFixed(2) }}</span>
                        </div>
                        <div class="fee-row total">
                            <span class="label">预计退款金额:</span>
                            <span class="value">¥ {{ calculateRefundAmount().toFixed(2) }}</span>
                        </div>
                    </div>

                    <div class="refund-reason">
                        <el-form :model="refundForm" label-width="100px">
                            <el-form-item label="退票原因:">
                                <el-select v-model="refundForm.reason" placeholder="请选择退票原因" style="width: 100%">
                                    <el-option label="行程变更" value="schedule_change"></el-option>
                                    <el-option label="个人原因" value="personal_reason"></el-option>
                                    <el-option label="航班延误/取消" value="flight_issue"></el-option>
                                    <el-option label="其他原因" value="other"></el-option>
                                </el-select>
                            </el-form-item>
                            <el-form-item label="备注:" v-if="refundForm.reason === 'other'">
                                <el-input type="textarea" v-model="refundForm.remark" :rows="2"
                                    placeholder="请简述退票原因"></el-input>
                            </el-form-item>
                        </el-form>
                    </div>
                </div>
            </div>
            <template #footer>
                <span class="dialog-footer">
                    <el-button @click="refundDialogVisible = false">取消</el-button>
                    <el-button type="primary" @click="submitRefund" :loading="isRefunding">确认退票</el-button>
                </span>
            </template>
        </el-dialog>

        <!-- 取消订单对话框 -->
        <el-dialog title="取消订单" v-model="cancelOrderDialogVisible" width="500px">
            <div class="cancel-dialog-content">
                <p class="cancel-warning">
                    <i class="el-icon-warning"></i>
                    请确认是否要取消整个订单？订单取消后将不可恢复。
                </p>

                <div class="cancel-info">
                    <div class="info-row">
                        <span class="label">订单编号:</span>
                        <span class="value">{{ order ? order.orderNumber : '' }}</span>
                    </div>
                    <div class="info-row">
                        <span class="label">包含机票:</span>
                        <span class="value">{{ order ? order.tickets.length : 0 }}张</span>
                    </div>
                    <div class="info-row">
                        <span class="label">订单金额:</span>
                        <span class="value">¥ {{ order ? order.totalAmount.toFixed(2) : '0.00' }}</span>
                    </div>
                </div>

                <div class="cancel-reason">
                    <el-form :model="cancelForm" label-width="100px">
                        <el-form-item label="取消原因:">
                            <el-select v-model="cancelForm.reason" placeholder="请选择取消原因" style="width: 100%">
                                <el-option label="计划变更" value="plan_change"></el-option>
                                <el-option label="重新预订" value="rebook"></el-option>
                                <el-option label="价格原因" value="price_issue"></el-option>
                                <el-option label="其他原因" value="other"></el-option>
                            </el-select>
                        </el-form-item>
                        <el-form-item label="备注:" v-if="cancelForm.reason === 'other'">
                            <el-input type="textarea" v-model="cancelForm.remark" :rows="2"
                                placeholder="请简述取消原因"></el-input>
                        </el-form-item>
                    </el-form>
                </div>
            </div>
            <template #footer>
                <span class="dialog-footer">
                    <el-button @click="cancelOrderDialogVisible = false">返回</el-button>
                    <el-button type="danger" @click="confirmCancelOrder" :loading="isCancelling">确认取消订单</el-button>
                </span>
            </template>
        </el-dialog>
    </div>
</template>

<script>
import api from '@/services/api'
import { ElMessage } from 'element-plus'
import CountdownTimer from '@/components/CountdownTimer.vue'

export default {
    name: 'OrderDetail',
    components: {
        CountdownTimer
    },
    data() {
        return {
            isLoading: true,
            order: null,
            error: null,
            isEditingRemark: false,
            remarkContent: '',
            refundDialogVisible: false,
            cancelOrderDialogVisible: false,
            selectedTicket: null,
            isRefunding: false,
            isCancelling: false,
            remainingPaymentSeconds: 0,
            refundForm: {
                reason: 'personal_reason',
                remark: ''
            },
            cancelForm: {
                reason: 'plan_change',
                remark: ''
            }
        };
    },
    computed: {
        orderStatusText() {
            if (!this.order) return '';

            const statusMap = {
                'pending': '待支付',
                'paid': '已支付',
                'ticketed': '已出票',
                'completed': '已完成',
                'cancelled': '已取消',
                'refunded': '已退款'
            };

            return statusMap[this.order.status] || '未知状态';
        },
        statusClass() {
            if (!this.order) return '';

            const classMap = {
                'pending': 'status-pending',
                'paid': 'status-paid',
                'ticketed': 'status-ticketed',
                'completed': 'status-completed',
                'cancelled': 'status-cancelled',
                'refunded': 'status-refunded'
            };

            return classMap[this.order.status] || '';
        }
    },
    created() {
        this.fetchOrderDetail();
    },
    methods: {
        fetchOrderDetail() {
            this.isLoading = true;

            // 获取订单ID
            const orderId = this.$route.params.orderId;
            console.log('获取订单详情，ID:', orderId);

            // 调用API获取订单详情
            api.orders.getDetail(orderId)
                .then(response => {
                    console.log('订单详情原始响应:', response);
                    const data = response.data || response;

                    try {
                        // 处理API返回的数据
                        const order = {
                            id: data.id,
                            orderNumber: data.order_number,
                            status: data.status,
                            createdAt: new Date(data.created_at),
                            paidAt: data.paid_at ? new Date(data.paid_at) : null,
                            ticketedAt: data.ticketed_at ? new Date(data.ticketed_at) : null,
                            completedAt: data.completed_at ? new Date(data.completed_at) : null,
                            paymentMethod: data.payment_method,
                            totalAmount: parseFloat(data.total_amount || data.total_price || 0),
                            priceDetail: data.price_details || [],
                            remarks: data.remarks || '',
                            passengers: [],
                            tickets: []
                        };

                        // 处理乘客信息
                        if (data.passengers && Array.isArray(data.passengers)) {
                            console.log('乘客信息原始数据:', data.passengers);
                            order.passengers = data.passengers.map(passenger => ({
                                id: passenger.id,
                                name: passenger.name,
                                idType: passenger.id_type,
                                idNumber: passenger.id_number,
                                phone: passenger.phone
                            }));
                            console.log('处理后的乘客数据:', order.passengers);
                        } else if (data.passenger_info && Array.isArray(data.passenger_info)) {
                            // 兼容另一种API格式，从passenger_info字段获取乘客信息
                            console.log('从passenger_info获取乘客信息:', data.passenger_info);
                            order.passengers = data.passenger_info.map(passenger => ({
                                id: passenger.id,
                                name: passenger.name,
                                idType: passenger.id_type || passenger.idType,
                                idNumber: passenger.id_number || passenger.idNumber,
                                phone: passenger.phone
                            }));
                            console.log('处理后的乘客数据:', order.passengers);
                        } else {
                            // 如果没有直接的乘客信息，从机票中提取
                            if (data.tickets && Array.isArray(data.tickets) && data.tickets.length > 0) {
                                console.log('从机票信息中提取乘客信息');
                                const passengers = [];

                                try {
                                    // 直接尝试通过控制台日志中的结构来提取乘客信息
                                    const firstTicket = data.tickets[0];
                                    console.log('检查第一张机票数据结构:', firstTicket);

                                    // 特别处理我们在控制台看到的结构
                                    if (firstTicket &&
                                        typeof firstTicket.passenger_name === 'string' &&
                                        typeof firstTicket.passenger_id_number === 'string') {

                                        console.log('检测到特定机票数据结构，直接创建乘客信息');

                                        data.tickets.forEach(ticket => {
                                            if (ticket.passenger_name && ticket.passenger_id_number) {
                                                const passenger = {
                                                    id: ticket.id || 0,
                                                    name: ticket.passenger_name,
                                                    idType: ticket.passenger_id_type || 'idcard',
                                                    idNumber: ticket.passenger_id_number,
                                                    phone: ticket.passenger_phone || ticket.phone || '--'
                                                };

                                                // 检查该乘客是否已存在
                                                const exists = passengers.some(p =>
                                                    p.name === passenger.name &&
                                                    p.idNumber === passenger.idNumber
                                                );

                                                if (!exists) {
                                                    console.log('添加乘客:', passenger);
                                                    passengers.push(passenger);
                                                }
                                            }
                                        });

                                        if (passengers.length > 0) {
                                            order.passengers = passengers;
                                            console.log('直接创建的乘客信息:', order.passengers);
                                        }
                                    }
                                } catch (extractError) {
                                    console.error('提取乘客信息时出错:', extractError);
                                }

                                // 如果上面的提取方式没有成功，使用原有逻辑
                                if (order.passengers.length === 0) {
                                    // 原有的乘客信息提取逻辑
                                    data.tickets.forEach(ticket => {
                                        // 提取乘客信息的代码...
                                        try {
                                            if (ticket.passenger) {
                                                const passenger = {
                                                    id: ticket.passenger.id || ticket.passenger_id,
                                                    name: ticket.passenger.name || '未知乘客',
                                                    idType: ticket.passenger.id_type || ticket.passenger.idType || 'idcard',
                                                    idNumber: ticket.passenger.id_number || ticket.passenger.idNumber || '--',
                                                    phone: ticket.passenger.phone || ticket.phone || '--'
                                                };
                                                // 避免添加重复乘客
                                                if (!passengers.some(p => p.id === passenger.id)) {
                                                    passengers.push(passenger);
                                                }
                                            } else if (ticket.passenger_id) {
                                                // 如果只有passenger_id，创建一个基本的乘客信息
                                                const passenger = {
                                                    id: ticket.passenger_id,
                                                    name: ticket.passenger_name || '乘客' + (passengers.length + 1),
                                                    idType: 'idcard',
                                                    idNumber: '--',
                                                    phone: ticket.phone || '--'
                                                };
                                                // 避免添加重复乘客
                                                if (!passengers.some(p => p.id === passenger.id)) {
                                                    passengers.push(passenger);
                                                }
                                            } else if (ticket.passenger_name || ticket.passenger_id_number) {
                                                // 处理扁平结构的乘客信息字段
                                                console.log('发现扁平结构的乘客字段:', ticket);
                                                console.log('乘客姓名:', ticket.passenger_name);
                                                console.log('证件号:', ticket.passenger_id_number);
                                                const passenger = {
                                                    id: ticket.id || 0,
                                                    name: (ticket.passenger_name && ticket.passenger_name !== '') ? ticket.passenger_name : '未知乘客',
                                                    idType: (ticket.passenger_id_type && ticket.passenger_id_type !== '') ? ticket.passenger_id_type : 'idcard',
                                                    idNumber: (ticket.passenger_id_number && ticket.passenger_id_number !== '') ? ticket.passenger_id_number : '--',
                                                    phone: (ticket.passenger_phone && ticket.passenger_phone !== '') ? ticket.passenger_phone : ticket.phone || '--'
                                                };
                                                console.log('创建的乘客对象:', passenger);
                                                // 避免添加重复乘客
                                                passengers.push(passenger);
                                            }
                                        } catch (innerError) {
                                            console.error('处理单个乘客时出错:', innerError);
                                        }
                                    });

                                    order.passengers = passengers;
                                    console.log('提取的乘客数据:', order.passengers);
                                }
                            } else {
                                console.warn('没有找到乘客数据或格式不正确:', data.passengers);
                                // 创建一个空的乘客数组，避免在模板中使用时出错
                                order.passengers = [];
                            }
                        }

                        // 处理机票信息
                        try {
                            if (data.tickets && Array.isArray(data.tickets)) {
                                console.log('解析机票数据:', data.tickets);
                                order.tickets = data.tickets.map(ticket => {
                                    // 记录原始数据用于调试
                                    console.log('单张机票数据:', ticket);

                                    try {
                                        // 创建默认航班信息，防止缺失字段导致的错误
                                        const defaultFlight = {
                                            id: ticket.flight_id || ticket.flight?.id || 0,
                                            flightNumber: ticket.flight_number || ticket.flight?.flight_number || '未知航班',
                                            airlineName: ticket.airline_name || ticket.flight?.airline_name || '未知航空',
                                            airlineLogo: ticket.airline_logo || ticket.flight?.airline_logo || '',
                                            departureCity: ticket.departure_city || ticket.flight?.departure_city || '未知城市',
                                            arrivalCity: ticket.arrival_city || ticket.flight?.arrival_city || '未知城市',
                                            departureAirport: ticket.departure_airport || ticket.flight?.departure_airport || '未知机场',
                                            arrivalAirport: ticket.arrival_airport || ticket.flight?.arrival_airport || '未知机场',
                                            departureTime: ticket.departure_time ? new Date(ticket.departure_time) :
                                                ticket.flight?.departure_time ? new Date(ticket.flight.departure_time) : new Date(),
                                            arrivalTime: ticket.arrival_time ? new Date(ticket.arrival_time) :
                                                ticket.flight?.arrival_time ? new Date(ticket.flight.arrival_time) : new Date(),
                                            duration: ticket.duration ||
                                                (ticket.arrival_time && ticket.departure_time) ?
                                                Math.floor((new Date(ticket.arrival_time) - new Date(ticket.departure_time)) / (1000 * 60)) : 120,
                                            status: ticket.flight_status || ticket.flight?.status || 'scheduled'
                                        };

                                        // 尝试计算持续时间（如果不存在）
                                        if (!defaultFlight.duration && defaultFlight.arrivalTime && defaultFlight.departureTime) {
                                            defaultFlight.duration = Math.floor((defaultFlight.arrivalTime - defaultFlight.departureTime) / (1000 * 60));
                                        }

                                        return {
                                            id: ticket.id,
                                            ticketNumber: ticket.ticket_number,
                                            passenger: order.passengers.find(p => p.id === ticket.passenger_id) ||
                                                // 针对扁平结构的机票数据，通过姓名和证件号匹配乘客
                                                (ticket.passenger_name ?
                                                    order.passengers.find(p =>
                                                        p.name === ticket.passenger_name &&
                                                        (p.idNumber === ticket.passenger_id_number || !ticket.passenger_id_number)
                                                    ) : {}) ||
                                                // 如果无法关联到乘客，直接使用机票上的乘客信息
                                                (ticket.passenger_name ? {
                                                    name: ticket.passenger_name,
                                                    idType: ticket.passenger_id_type || 'idcard',
                                                    idNumber: ticket.passenger_id_number || '--',
                                                    phone: ticket.passenger_phone || ticket.phone || '--'
                                                } : {}),
                                            flight: defaultFlight,
                                            seatNumber: ticket.seat_number || '--',
                                            cabinClass: ticket.cabin_class || 'economy',
                                            price: parseFloat(ticket.price) || 0,
                                            status: ticket.status || 'valid',
                                            // 值机相关字段
                                            checkedIn: ticket.checked_in || false,
                                            checkedInAt: ticket.checked_in_at ? new Date(ticket.checked_in_at) : null,
                                            boardingPassNumber: ticket.boarding_pass_number || null,
                                            gate: ticket.gate || null
                                        };
                                    } catch (ticketError) {
                                        console.error('处理单张机票时出错:', ticketError);
                                        return {
                                            id: ticket.id || 0,
                                            ticketNumber: ticket.ticket_number || '未知票号',
                                            passenger: {},
                                            flight: {
                                                flightNumber: ticket.flight_number || '未知航班',
                                                departureCity: ticket.departure_city || '未知城市',
                                                arrivalCity: ticket.arrival_city || '未知城市',
                                                departureTime: new Date(),
                                                arrivalTime: new Date(),
                                                status: 'unknown'
                                            },
                                            seatNumber: '--',
                                            cabinClass: 'economy',
                                            price: 0,
                                            status: 'unknown',
                                            // 值机相关字段
                                            checkedIn: false,
                                            checkedInAt: null,
                                            boardingPassNumber: null,
                                            gate: null
                                        };
                                    }
                                });
                                console.log('处理后的机票数据:', order.tickets);
                            } else {
                                console.warn('没有找到机票数据或格式不正确');
                                order.tickets = [];
                            }
                        } catch (ticketsError) {
                            console.error('处理机票信息时出错:', ticketsError);
                            order.tickets = [];
                        }

                        this.order = order;
                        this.remarkContent = this.order.remarks || '';
                    } catch (error) {
                        console.error('处理订单数据时出错:', error);
                        // 创建一个最小化的订单对象，以便页面能够渲染
                        this.order = {
                            id: data.id || 0,
                            orderNumber: data.order_number || '未知订单',
                            status: data.status || 'unknown',
                            createdAt: new Date(),
                            totalAmount: parseFloat(data.total_amount || 0),
                            passengers: [],
                            tickets: []
                        };
                    }

                    this.isLoading = false;
                    
                    // 如果是待支付订单，获取剩余支付时间
                    if (this.order && this.order.status === 'pending') {
                        this.fetchRemainingPaymentTime();
                    }
                })
                .catch(error => {
                    console.error('获取订单详情失败:', error);
                    if (error.response) {
                        console.error('错误状态码:', error.response.status);
                        console.error('错误数据:', error.response.data);
                    }
                    ElMessage.error('获取订单详情失败，请稍后重试');
                    this.isLoading = false;
                });
        },

        formatDate(date) {
            if (!date) return '';
            try {
                const d = new Date(date);
                if (isNaN(d.getTime())) {
                    console.warn('无效的日期格式:', date);
                    return '';
                }
                return `${d.getFullYear()}-${(d.getMonth() + 1).toString().padStart(2, '0')}-${d.getDate().toString().padStart(2, '0')}`;
            } catch (e) {
                console.error('日期格式化错误:', e);
                return '';
            }
        },

        formatTime(date) {
            if (!date) return '';
            try {
                const d = new Date(date);
                if (isNaN(d.getTime())) {
                    console.warn('无效的时间格式:', date);
                    return '';
                }
                return `${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`;
            } catch (e) {
                console.error('时间格式化错误:', e);
                return '';
            }
        },

        formatDateTime(date) {
            if (!date) return '';
            const formattedDate = this.formatDate(date);
            const formattedTime = this.formatTime(date);
            if (!formattedDate || !formattedTime) return '';
            return `${formattedDate} ${formattedTime}`;
        },

        formatDuration(minutes) {
            if (!minutes || isNaN(minutes)) {
                return '未知';
            }
            const hours = Math.floor(minutes / 60);
            const mins = minutes % 60;
            return `${hours}小时${mins > 0 ? ` ${mins}分钟` : ''}`;
        },

        getIdTypeLabel(idType) {
            const idTypeMap = {
                'idcard': '身份证',
                'passport': '护照',
                'military': '军官证'
            };
            return idTypeMap[idType] || '身份证';
        },

        getCabinLabel(cabinClass) {
            const cabinMap = {
                'economy': '经济舱',
                'business': '商务舱',
                'first': '头等舱'
            };
            return cabinMap[cabinClass] || '经济舱';
        },

        getPaymentMethodLabel(method) {
            const methodMap = {
                'alipay': '支付宝',
                'wechat': '微信支付',
                'creditcard': '信用卡'
            };
            return methodMap[method] || '未知方式';
        },

        getFlightStatusText(status) {
            const statusMap = {
                'scheduled': '计划起飞',
                'boarding': '正在登机',
                'departed': '已起飞',
                'arrived': '已到达',
                'delayed': '延误',
                'cancelled': '已取消'
            };
            return statusMap[status] || '未知状态';
        },

        getFlightStatusClass(status) {
            const classMap = {
                'scheduled': 'status-normal',
                'boarding': 'status-normal',
                'departed': 'status-success',
                'arrived': 'status-success',
                'delayed': 'status-warning',
                'cancelled': 'status-danger'
            };
            return classMap[status] || '';
        },

        getStatusStep() {
            if (!this.order) return 0;

            if (this.order.completedAt) return 4;
            if (this.order.ticketedAt) return 3;
            if (this.order.paidAt) return 2;
            return 1;
        },

        canRefund(ticket) {
            if (!this.order || !ticket) return false;

            // 已支付、已出票且未退票的机票可以退票
            return (this.order.status === 'paid' || this.order.status === 'ticketed') &&
                ticket.status === 'valid';
        },

        canCheckIn(ticket) {
            if (!this.order || !ticket) return false;

            // 已值机的机票不显示值机按钮
            if (ticket.checkedIn) return false;

            // 已支付且机票有效的可以值机
            return this.order.status === 'paid' &&
                ticket.status === 'valid';
        },

        canReschedule(ticket) {
            if (!this.order || !ticket) return false;

            // 机票状态必须为有效
            if (ticket.status !== 'valid') return false;

            // 订单状态必须为已支付或已出票
            if (this.order.status !== 'paid' && this.order.status !== 'ticketed') return false;

            // 航班起飞时间必须距当前超过2小时
            const departureTime = new Date(ticket.flight?.departureTime);
            const now = new Date();
            const diffHours = (departureTime - now) / (1000 * 60 * 60);

            return diffHours > 2;
        },

        goToReschedule(ticket) {
            this.$router.push({
                path: `/reschedule/${ticket.id}`,
                query: { orderId: this.order.id }
            });
        },

        async fetchRemainingPaymentTime() {
            try {
                // 计算剩余支付时间（订单创建后30分钟内需支付）
                const createdAt = new Date(this.order.createdAt);
                const now = new Date();
                const paymentDeadline = new Date(createdAt.getTime() + 30 * 60 * 1000); // 30分钟
                const remainingMs = paymentDeadline - now;
                
                if (remainingMs > 0) {
                    this.remainingPaymentSeconds = Math.floor(remainingMs / 1000);
                } else {
                    this.remainingPaymentSeconds = 0;
                }
            } catch (err) {
                console.error('获取剩余支付时间失败:', err);
                this.remainingPaymentSeconds = 0;
            }
        },

        handlePaymentTimeout() {
            ElMessage.warning('支付时间已过期，订单将自动取消');
            // 刷新订单详情
            this.fetchOrderDetail();
        },

        showRefundDialog(ticket) {
            this.selectedTicket = ticket;
            this.refundDialogVisible = true;
        },

        calculateRefundFee() {
            if (!this.selectedTicket) return 0;

            // 模拟退票手续费计算逻辑
            const departureTime = new Date(this.selectedTicket.flight.departureTime);
            const now = new Date();
            const diffHours = (departureTime - now) / (1000 * 60 * 60);

            if (diffHours > 24 * 7) { // 提前7天，手续费5%
                return this.selectedTicket.price * 0.05;
            } else if (diffHours > 24 * 2) { // 提前2-7天，手续费20%
                return this.selectedTicket.price * 0.2;
            } else if (diffHours > 24) { // 提前1-2天，手续费30%
                return this.selectedTicket.price * 0.3;
            } else { // 起飞前24小时内，手续费50%
                return this.selectedTicket.price * 0.5;
            }
        },

        calculateRefundAmount() {
            if (!this.selectedTicket) return 0;
            return this.selectedTicket.price - this.calculateRefundFee();
        },

        submitRefund() {
            this.isRefunding = true;

            api.tickets.refund(this.selectedTicket.id)
                .then(() => {
                    this.isRefunding = false;
                    this.refundDialogVisible = false;
                    this.$message.success('退票申请已提交，退款将在1-7个工作日内退回原支付账户');
                    // 重新加载订单详情
                    this.fetchOrderDetail();
                })
                .catch(error => {
                    this.isRefunding = false;
                    console.error('退票失败:', error);
                    this.$message.error(error.message || '退票失败，请稍后重试');
                });
        },

        showCancelDialog() {
            this.cancelOrderDialogVisible = true;
        },

        confirmCancelOrder() {
            this.isCancelling = true;

            api.orders.cancel(this.order.id)
                .then(() => {
                    this.isCancelling = false;
                    this.cancelOrderDialogVisible = false;
                    this.$message.success('订单已取消');
                    // 重新加载订单详情
                    this.fetchOrderDetail();
                })
                .catch(error => {
                    this.isCancelling = false;
                    console.error('取消订单失败:', error);
                    this.$message.error(error.message || '取消订单失败，请稍后重试');
                });
        },

        startEditRemark() {
            this.remarkContent = this.order.remarks || '';
            this.isEditingRemark = true;
        },

        cancelEditRemark() {
            this.remarkContent = this.order.remarks || '';
            this.isEditingRemark = false;
        },

        saveRemark() {
            // 备注功能暂不支持API，仅本地保存
            this.order.remarks = this.remarkContent;
            this.isEditingRemark = false;
            this.$message.success('备注已保存');
        },

        showTicketDetail(ticket) {
            // 实际应用中可能会打开一个详情弹窗或导航到票面详情页
            this.$message.info(`查看机票: ${ticket.ticketNumber}`);
        },

        goToCheckIn(ticket) {
            // 导航到值机页面
            this.$router.push({
                name: 'checkin',
                params: { ticketId: ticket.id }
            });
        },

        viewBoardingPass(ticket) {
            // 导航到值机页面查看登机牌（已值机状态会直接显示登机牌）
            this.$router.push({
                name: 'checkin',
                params: { ticketId: ticket.id }
            });
        },

        goToPay() {
            // 导航到支付页面
            this.$router.push({
                name: 'payment',
                params: { orderId: this.order.id }
            });
        },

        printOrder() {
            window.print();
        },

        goToOrderList() {
            this.$router.push('/orders');
        },

        goToHomePage() {
            this.$router.push('/');
        }
    }
};
</script>

<style scoped>
.order-detail-view {
    padding: 20px 40px;
    background-color: #f5f7fa;
    width: 100%;
    box-sizing: border-box;
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

.order-container {
    width: 100%;
    padding: 20px 40px;
    box-sizing: border-box;
}

.order-header {
    background-color: white;
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
}

.order-id,
.order-time {
    display: flex;
    align-items: center;
}

.label {
    color: #666;
    margin-right: 8px;
    font-size: 14px;
}

.value {
    font-weight: 500;
    color: #333;
}

.actions {
    display: flex;
    gap: 10px;
}

.section-card {
    background-color: white;
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 20px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
}

.section-title {
    display: flex;
    align-items: center;
    margin-bottom: 20px;
    padding-bottom: 10px;
    border-bottom: 1px solid #eee;
}

.section-title i {
    color: #0076c6;
    margin-right: 8px;
    font-size: 18px;
}

.section-title span {
    font-size: 18px;
    font-weight: 600;
    color: #333;
}

.status-timeline {
    padding: 20px 0;
}

.flight-cards {
    display: flex;
    flex-direction: column;
    gap: 20px;
}

.flight-card {
    border: 1px solid #eee;
    border-radius: 8px;
    padding: 20px;
    background-color: #fafafa;
    transition: all 0.3s ease;
}

.flight-card:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    transform: translateY(-2px);
}

.flight-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}

.airline {
    display: flex;
    align-items: center;
}

.airline-icon {
    width: 44px;
    height: 44px;
    border-radius: 50%;
    margin-right: 12px;
    background: linear-gradient(135deg, #409eff 0%, #337ecc 100%);
    display: flex;
    align-items: center;
    justify-content: center;
}

.plane-svg {
    width: 24px;
    height: 24px;
    display: block;
    background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="%23ffffff" d="M21 16v-2l-8-5V3.5c0-.83-.67-1.5-1.5-1.5S10 2.67 10 3.5V9l-8 5v2l8-2.5V19l-2 1.5V22l3.5-1 3.5 1v-1.5L13 19v-5.5l8 2.5z"/></svg>');
    background-size: contain;
    background-repeat: no-repeat;
    background-position: center;
}

.airline-info {
    display: flex;
    flex-direction: column;
}

.airline-name {
    font-weight: 600;
    color: #333;
}

.flight-number {
    font-size: 14px;
    color: #666;
}

.flight-status {
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 12px;
    font-weight: 500;
}

.status-normal {
    background-color: #e3f2fd;
    color: #1976d2;
}

.status-success {
    background-color: #e8f5e9;
    color: #2e7d32;
}

.status-warning {
    background-color: #fff8e1;
    color: #f57c00;
}

.status-danger {
    background-color: #ffebee;
    color: #c62828;
}

.flight-journey {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    padding: 15px;
    background-color: white;
    border-radius: 8px;
}

.departure,
.arrival {
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 30%;
}

.time {
    font-size: 22px;
    font-weight: 700;
    color: #0076c6;
    margin-bottom: 5px;
}

.date {
    font-size: 14px;
    color: #666;
    margin-bottom: 10px;
}

.city {
    font-size: 16px;
    font-weight: 600;
    margin-bottom: 5px;
}

.airport {
    font-size: 12px;
    color: #666;
}

.flight-direction {
    display: flex;
    flex-direction: column;
    align-items: center;
    flex: 1;
    position: relative;
}

.direction-line {
    height: 2px;
    width: 100%;
    background-color: #e0e0e0;
    position: relative;
}

.direction-line::before {
    content: '';
    position: absolute;
    right: 0;
    top: 50%;
    transform: translateY(-50%);
    width: 0;
    height: 0;
    border-top: 5px solid transparent;
    border-bottom: 5px solid transparent;
    border-left: 8px solid #e0e0e0;
}

.duration {
    font-size: 14px;
    color: #666;
    margin-top: 8px;
}

.cabin-class {
    font-size: 12px;
    color: #0076c6;
    padding: 2px 8px;
    background-color: #e3f2fd;
    border-radius: 10px;
    margin-top: 5px;
}

.ticket-info {
    display: flex;
    justify-content: space-between;
    padding: 15px 0;
    border-top: 1px dashed #eee;
    border-bottom: 1px dashed #eee;
    margin-bottom: 15px;
}

.seat,
.passenger,
.ticket-number {
    display: flex;
    align-items: center;
}

/* 值机状态展示样式 */
.checkin-status {
    background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
    border: 1px solid #a5d6a7;
    border-radius: 8px;
    padding: 12px 16px;
    margin: 12px 0;
}

.checkin-badge {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 8px;
}

.checkin-badge .el-tag {
    font-weight: 500;
}

.checkin-time {
    font-size: 12px;
    color: #666;
}

.boarding-info {
    display: flex;
    gap: 24px;
    flex-wrap: wrap;
}

.boarding-item {
    display: flex;
    align-items: center;
    gap: 6px;
}

.boarding-item .label {
    font-size: 13px;
    color: #666;
}

.boarding-item .value {
    font-size: 14px;
    font-weight: 500;
    color: #333;
}

.boarding-item .value.highlight {
    font-size: 18px;
    font-weight: 700;
    color: #1976d2;
}

.ticket-actions {
    display: flex;
    justify-content: flex-end;
    gap: 10px;
}

.passenger-list {
    margin-top: 10px;
}

.payment-info {
    padding: 10px 0;
}

.payment-row {
    display: flex;
    padding: 10px 0;
}

.payment-row .label {
    width: 100px;
}

.success-text {
    color: #2e7d32;
}

.warning-text {
    color: #f57c00;
}

.price {
    font-size: 18px;
    font-weight: 600;
    color: #f44336;
}

.price-detail {
    margin-top: 20px;
    border-top: 1px dashed #eee;
    padding-top: 15px;
}

.price-item {
    display: flex;
    justify-content: space-between;
    padding: 8px 0;
}

.price-total {
    display: flex;
    justify-content: space-between;
    padding: 12px 0;
    margin-top: 10px;
    border-top: 1px solid #eee;
    font-weight: 600;
}

.total-value {
    font-size: 18px;
    color: #f44336;
}

.payment-action {
    margin-top: 20px;
    text-align: center;
}

.remarks {
    padding: 10px 0;
}

.no-remarks {
    color: #999;
    font-style: italic;
}

.add-remark {
    margin-top: 10px;
}

.edit-remark {
    margin-top: 15px;
}

.remark-actions {
    display: flex;
    justify-content: flex-end;
    margin-top: 10px;
    gap: 10px;
}

.related-actions {
    display: flex;
    justify-content: center;
    gap: 20px;
    margin-top: 30px;
    margin-bottom: 40px;
}

.loading-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 100px 0;
}

.loading-spinner {
    font-size: 40px;
    color: #0076c6;
    margin-bottom: 20px;
}

.error-container {
    text-align: center;
    padding: 100px 0;
}

.error-container i {
    font-size: 60px;
    color: #f44336;
    margin-bottom: 20px;
}

.refund-dialog-content,
.cancel-dialog-content {
    padding: 10px 0;
}

.refund-notice,
.cancel-warning {
    margin-bottom: 20px;
    padding: 10px;
    background-color: #fff8e1;
    border-radius: 4px;
    color: #f57c00;
}

.cancel-warning i {
    margin-right: 5px;
}

.refund-ticket-info,
.cancel-info {
    margin-bottom: 20px;
    padding: 15px;
    background-color: #f5f5f5;
    border-radius: 4px;
}

.info-row {
    display: flex;
    margin-bottom: 8px;
}

.info-row .label {
    width: 60px;
}

.refund-fee,
.fee-row {
    margin-bottom: 15px;
}

.fee-row {
    display: flex;
    justify-content: space-between;
    padding: 5px 0;
}

.fee-row.total {
    font-weight: 600;
    border-top: 1px solid #eee;
    padding-top: 10px;
    margin-top: 10px;
}

.refund-reason,
.cancel-reason {
    margin-top: 20px;
}

/* 响应式调整 */
@media screen and (max-width: 768px) {
    .order-header {
        flex-direction: column;
        align-items: flex-start;
    }

    .order-id,
    .order-time {
        margin-bottom: 10px;
    }

    .actions {
        margin-top: 10px;
        width: 100%;
        justify-content: space-between;
    }

    .flight-journey {
        flex-direction: column;
        gap: 15px;
    }

    .departure,
    .arrival {
        width: 100%;
    }

    .flight-direction {
        margin: 10px 0;
    }

    .direction-line {
        transform: rotate(90deg);
        width: 100px;
    }

    .ticket-info {
        flex-direction: column;
        gap: 10px;
    }

    .related-actions {
        flex-direction: column;
        gap: 10px;
    }
}

/* 打印样式 */
@media print {

    .header-banner,
    .actions,
    .ticket-actions,
    .add-remark,
    .edit-remark,
    .remark-actions,
    .related-actions {
        display: none;
    }

    .order-detail-view {
        background-color: white;
        padding: 0;
    }

    .section-card {
        box-shadow: none;
        border: 1px solid #eee;
        page-break-inside: avoid;
    }
}

.no-tickets-message {
    text-align: center;
    padding: 30px;
    background-color: #f8f9fa;
    border-radius: 8px;
    margin: 20px 0;
}

.no-tickets-message i {
    font-size: 40px;
    color: #909399;
    margin-bottom: 10px;
}

.no-tickets-message p {
    color: #606266;
    font-size: 16px;
}

.empty-text {
    text-align: center;
    padding: 20px 0;
    color: #909399;
}

.empty-text i {
    font-size: 24px;
    margin-bottom: 10px;
}

.empty-text p {
    margin: 5px 0 0;
}
</style>