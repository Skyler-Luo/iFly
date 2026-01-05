<template>
    <div class="payment-view">
        <div class="header-banner">
            <h1>订单支付</h1>
            <div class="order-status" v-if="order" :class="statusClass">{{ orderStatusText }}</div>
        </div>

        <div class="payment-container">
            <div v-if="isLoading" class="loading-container">
                <div class="loading-spinner">
                    <i class="el-icon-loading"></i>
                </div>
                <p>正在加载订单信息...</p>
            </div>

            <div v-else-if="!order" class="error-container">
                <i class="el-icon-warning-outline"></i>
                <h2>未找到订单</h2>
                <p>抱歉，无法找到该订单信息或您没有权限查看。</p>
                <el-button type="primary" @click="goToOrderList">返回订单列表</el-button>
            </div>

            <div v-else class="payment-content">
                <div class="order-summary">
                    <h2>订单信息</h2>
                    <div class="order-info">
                        <div class="info-item">
                            <span class="label">订单号:</span>
                            <span class="value">{{ order.orderNumber }}</span>
                        </div>
                        <div class="info-item">
                            <span class="label">支付金额:</span>
                            <span class="value price">¥{{ order.totalAmount.toFixed(2) }}</span>
                        </div>
                    </div>
                </div>

                <div class="payment-methods">
                    <h3>选择支付方式</h3>
                    <el-radio-group v-model="paymentMethod">
                        <el-radio value="alipay">
                            <div class="payment-option">
                                <el-icon><Wallet /></el-icon>
                                <span>支付宝</span>
                            </div>
                        </el-radio>
                        <el-radio value="wechat">
                            <div class="payment-option">
                                <el-icon><ChatDotRound /></el-icon>
                                <span>微信支付</span>
                            </div>
                        </el-radio>
                        <el-radio value="creditcard">
                            <div class="payment-option">
                                <el-icon><CreditCard /></el-icon>
                                <span>信用卡</span>
                            </div>
                        </el-radio>
                    </el-radio-group>
                </div>

                <div v-if="paymentMethod && !paymentSuccess" class="qr-code-section">
                    <h3>请扫码完成支付</h3>
                    <div class="qr-code-container">
                        <img src="@/assets/qr.png" alt="支付二维码" class="qr-code" />
                    </div>
                    <div class="payment-tips">
                        <p>请使用{{ paymentMethodLabel }}扫描上方二维码</p>
                        <p>支付金额: <span class="price">¥{{ order.totalAmount.toFixed(2) }}</span></p>
                        <el-button type="primary" @click="simulatePayment" class="payment-button">
                            确认已支付
                        </el-button>
                    </div>
                </div>

                <div v-if="paymentSuccess" class="payment-success">
                    <i class="el-icon-success success-icon"></i>
                    <h2>支付成功</h2>
                    <p>您的订单已完成支付</p>
                    <div class="success-actions">
                        <el-button type="primary" @click="goToOrderDetail">查看订单详情</el-button>
                        <el-button @click="goToHome">返回首页</el-button>
                    </div>
                </div>

                <div v-if="!paymentMethod && !paymentSuccess" class="actions">
                    <el-button @click="goBack">返回</el-button>
                    <el-button type="primary" :disabled="!paymentMethod">
                        确认支付
                    </el-button>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import api from '@/services/api'
import { Wallet, ChatDotRound, CreditCard } from '@element-plus/icons-vue'

export default {
    name: 'PaymentView',
    components: {
        Wallet,
        ChatDotRound,
        CreditCard
    },
    data() {
        return {
            isLoading: true,
            order: null,
            paymentMethod: '',
            paymentSuccess: false
        };
    },
    computed: {
        paymentMethodLabel() {
            const methodMap = {
                'alipay': '支付宝',
                'wechat': '微信',
                'creditcard': '银联云闪付'
            };
            return methodMap[this.paymentMethod] || '';
        },
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
            const orderId = this.$route.params.orderId;

            // 使用真实API获取订单详情
            api.orders.getDetail(orderId)
                .then(response => {
                    console.log('订单详情:', response);
                    const data = response.data || response;

                    this.order = {
                        id: data.id,
                        orderNumber: data.order_number,
                        totalAmount: parseFloat(data.total_amount || data.total_price || 0),
                        status: data.status || 'pending'
                    };
                    this.isLoading = false;
                })
                .catch(error => {
                    console.error('获取订单失败:', error);
                    this.$message.error('获取订单信息失败');
                    this.isLoading = false;
                });
        },

        simulatePayment() {
            this.isLoading = true;
            console.log('尝试支付订单', this.order.id);

            // 尝试方法1：更新订单状态
            api.orders.updateStatus(this.order.id, { status: 'paid' })
                .then(response => {
                    console.log('支付成功 (方法1):', response);
                    // 更新本地订单状态
                    this.order.status = 'paid';
                    this.paymentSuccess = true;
                    this.$message.success('支付成功！');
                })
                .catch(error => {
                    console.error('支付失败 (方法1):', error);

                    // 尝试方法2：调用直接支付接口
                    console.log('尝试备选支付方法...');
                    return api.orders.pay(this.order.id, {
                        payment_method: this.paymentMethod,
                        amount: this.order.totalAmount
                    })
                        .then(response => {
                            console.log('支付成功 (方法2):', response);
                            // 更新本地订单状态
                            this.order.status = 'paid';
                            this.paymentSuccess = true;
                            this.$message.success('支付成功！');
                        })
                        .catch(secondError => {
                            console.error('备选支付方法也失败:', secondError);
                            this.$message.error('支付失败，请稍后重试');
                        });
                })
                .finally(() => {
                    this.isLoading = false;
                });
        },

        goToOrderDetail() {
            this.$router.push({
                name: 'orderDetail',
                params: { orderId: this.order.id }
            });
        },

        goBack() {
            this.$router.go(-1);
        },

        goToOrderList() {
            this.$router.push('/orders');
        },

        goToHome() {
            this.$router.push('/');
        }
    }
};
</script>

<style scoped>
.payment-view {
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

.payment-container {
    width: 100%;
    padding: 20px 40px;
    background-color: white;
    box-sizing: border-box;
    border-radius: 8px;
    padding: 30px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.loading-container,
.error-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 50px 0;
    text-align: center;
}

.loading-spinner {
    font-size: 40px;
    color: #0076c6;
    margin-bottom: 20px;
}

.error-container i {
    font-size: 60px;
    color: #f44336;
    margin-bottom: 20px;
}

.payment-content {
    padding: 20px 0;
}

.order-summary {
    margin-bottom: 30px;
}

.order-summary h2 {
    margin-top: 0;
    margin-bottom: 20px;
    font-size: 20px;
    color: #333;
}

.order-info {
    background-color: #f9f9f9;
    border-radius: 8px;
    padding: 20px;
}

.info-item {
    display: flex;
    justify-content: space-between;
    margin-bottom: 10px;
}

.info-item:last-child {
    margin-bottom: 0;
}

.label {
    color: #666;
}

.value {
    font-weight: 500;
    color: #333;
}

.price {
    color: #f44336;
    font-weight: 600;
}

.payment-methods {
    margin: 30px 0;
    padding: 20px;
    background-color: #f5f5f5;
    border-radius: 8px;
}

.payment-methods h3 {
    margin-top: 0;
    margin-bottom: 20px;
    font-size: 16px;
}

.payment-option {
    display: flex;
    align-items: center;
    gap: 8px;
}

.payment-option img {
    border-radius: 4px;
}

.qr-code-section {
    margin: 30px 0;
    text-align: center;
}

.qr-code-section h3 {
    margin-bottom: 20px;
}

.qr-code-container {
    display: flex;
    justify-content: center;
    margin-bottom: 20px;
}

.qr-code {
    width: 200px;
    height: 200px;
    border: 1px solid #eee;
    padding: 10px;
    border-radius: 8px;
    background-color: white;
}

.payment-tips {
    color: #666;
    margin-bottom: 20px;
}

.payment-button {
    margin-top: 20px;
}

.payment-success {
    text-align: center;
    padding: 40px 0;
}

.success-icon {
    font-size: 60px;
    color: #4caf50;
    margin-bottom: 20px;
}

.success-actions {
    margin-top: 30px;
    display: flex;
    justify-content: center;
    gap: 20px;
}

.actions {
    margin-top: 30px;
    display: flex;
    justify-content: center;
    gap: 20px;
}

@media (max-width: 768px) {
    .payment-container {
        padding: 20px;
    }

    .header-banner {
        flex-direction: column;
        align-items: flex-start;
    }

    .order-status {
        margin-top: 10px;
    }

    .success-actions {
        flex-direction: column;
        gap: 10px;
    }
}
</style>