<template>
    <div class="admin-promotion-usage">
        <h1 class="title">促销活动使用统计</h1>

        <div class="promotion-info">
            <div class="info-card">
                <div class="promo-header">
                    <div class="promo-badge" :class="getPromotionTypeClass(promotion.type)">
                        {{ getPromotionTypeName(promotion.type) }}
                    </div>
                    <h2>{{ promotion.name }}</h2>
                    <div class="promo-code">{{ promotion.code }}</div>
                </div>
                <div class="promo-details">
                    <div class="detail-row">
                        <div class="detail-item">
                            <div class="detail-label">有效期</div>
                            <div class="detail-value">
                                {{ formatDate(promotion.startDate) }} - {{ formatDate(promotion.endDate) }}
                                <span class="promo-status" :class="getStatusClass(promotion.status)">
                                    {{ getStatusText(promotion.status) }}
                                </span>
                            </div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">折扣类型</div>
                            <div class="detail-value">
                                {{ getDiscountTypeText(promotion.discountType) }}:
                                <strong>{{ formatDiscountValue(promotion) }}</strong>
                            </div>
                        </div>
                    </div>
                    <div class="detail-row">
                        <div class="detail-item">
                            <div class="detail-label">使用限制</div>
                            <div class="detail-value">
                                最低消费: {{ promotion.minSpend ? `¥${promotion.minSpend}` : '无限制' }} |
                                使用次数: {{ promotion.maxUses ? promotion.maxUses : '无限制' }}
                            </div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">适用产品</div>
                            <div class="detail-value">{{ getApplicableProducts(promotion) }}</div>
                        </div>
                    </div>
                    <div class="promo-description">
                        {{ promotion.description }}
                    </div>
                </div>
            </div>
        </div>

        <div class="usage-stats">
            <div class="stat-cards">
                <div class="stat-card">
                    <div class="stat-title">总使用次数</div>
                    <div class="stat-value">{{ usageStats.totalUses }}</div>
                    <div class="stat-compare" :class="getCompareClass(usageStats.usesChangePercent)">
                        <i class="fas" :class="usageStats.usesChangePercent >= 0 ? 'fa-arrow-up' : 'fa-arrow-down'"></i>
                        {{ Math.abs(usageStats.usesChangePercent) }}% 较上周
                    </div>
                </div>

                <div class="stat-card">
                    <div class="stat-title">总优惠金额</div>
                    <div class="stat-value">¥{{ usageStats.totalDiscountAmount.toFixed(2) }}</div>
                    <div class="stat-compare" :class="getCompareClass(usageStats.discountChangePercent)">
                        <i class="fas"
                            :class="usageStats.discountChangePercent >= 0 ? 'fa-arrow-up' : 'fa-arrow-down'"></i>
                        {{ Math.abs(usageStats.discountChangePercent) }}% 较上周
                    </div>
                </div>

                <div class="stat-card">
                    <div class="stat-title">带来订单数</div>
                    <div class="stat-value">{{ usageStats.totalOrders }}</div>
                    <div class="stat-compare" :class="getCompareClass(usageStats.ordersChangePercent)">
                        <i class="fas"
                            :class="usageStats.ordersChangePercent >= 0 ? 'fa-arrow-up' : 'fa-arrow-down'"></i>
                        {{ Math.abs(usageStats.ordersChangePercent) }}% 较上周
                    </div>
                </div>

                <div class="stat-card">
                    <div class="stat-title">总交易额</div>
                    <div class="stat-value">¥{{ usageStats.totalRevenue.toFixed(2) }}</div>
                    <div class="stat-compare" :class="getCompareClass(usageStats.revenueChangePercent)">
                        <i class="fas"
                            :class="usageStats.revenueChangePercent >= 0 ? 'fa-arrow-up' : 'fa-arrow-down'"></i>
                        {{ Math.abs(usageStats.revenueChangePercent) }}% 较上周
                    </div>
                </div>
            </div>

            <div class="chart-section">
                <div class="chart-header">
                    <h3>使用趋势</h3>
                    <div class="date-range-selector">
                        <button class="btn" :class="{ active: dateRange === 'week' }" @click="dateRange = 'week'">
                            周
                        </button>
                        <button class="btn" :class="{ active: dateRange === 'month' }" @click="dateRange = 'month'">
                            月
                        </button>
                        <button class="btn" :class="{ active: dateRange === 'quarter' }" @click="dateRange = 'quarter'">
                            季度
                        </button>
                        <button class="btn" :class="{ active: dateRange === 'year' }" @click="dateRange = 'year'">
                            年
                        </button>
                    </div>
                </div>
                <div class="chart-container">
                    <!-- 此处在实际应用中应该渲染图表 -->
                    <div class="chart-placeholder">
                        使用趋势图将在此显示（实际项目中可使用ECharts等图表库）
                    </div>
                </div>
            </div>

            <div class="usage-filters">
                <div class="search-box">
                    <input type="text" v-model="searchQuery" placeholder="搜索用户姓名/订单号">
                    <button><i class="fas fa-search"></i></button>
                </div>

                <div class="filter-group">
                    <select v-model="dateRangeFilter">
                        <option value="all">所有时间</option>
                        <option value="today">今天</option>
                        <option value="yesterday">昨天</option>
                        <option value="week">本周</option>
                        <option value="month">本月</option>
                    </select>
                </div>

                <div class="export-btn">
                    <button class="btn btn-secondary">
                        <i class="fas fa-download"></i> 导出数据
                    </button>
                </div>
            </div>

            <div class="usage-table">
                <table>
                    <thead>
                        <tr>
                            <th>使用时间</th>
                            <th>用户</th>
                            <th>订单号</th>
                            <th>原价金额</th>
                            <th>优惠金额</th>
                            <th>结算金额</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="(usage, index) in filteredUsages" :key="index">
                            <td>{{ formatDateTime(usage.usedAt) }}</td>
                            <td>
                                <div class="user-info">
                                    <div class="user-name">{{ usage.user.name }}</div>
                                    <div class="user-email">{{ usage.user.email }}</div>
                                </div>
                            </td>
                            <td>
                                <a class="order-link" @click="viewOrder(usage.order.id)">
                                    {{ usage.order.number }}
                                </a>
                            </td>
                            <td>¥{{ usage.originalAmount.toFixed(2) }}</td>
                            <td class="discount-amount">-¥{{ usage.discountAmount.toFixed(2) }}</td>
                            <td>¥{{ usage.finalAmount.toFixed(2) }}</td>
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
    </div>
</template>

<script>
export default {
    name: 'AdminPromotionUsageView',
    data() {
        return {
            dateRange: 'month',
            searchQuery: '',
            dateRangeFilter: 'all',
            currentPage: 1,
            perPage: 10,
            promotion: {
                id: 'PROMO-123',
                name: '暑期旅行特惠',
                code: 'SUMMER2023',
                type: 'seasonal',
                status: 'active',
                startDate: '2023-06-01',
                endDate: '2023-08-31',
                discountType: 'percentage',
                discountValue: 15,
                minSpend: 500,
                maxUses: 1000,
                applicableProducts: ['all_flights'],
                description: '暑期出行优惠活动，所有航班可享受票价85折优惠。每位用户限用一次，最低消费500元。'
            },
            usageStats: {
                totalUses: 358,
                usesChangePercent: 12.5,
                totalDiscountAmount: 42680.50,
                discountChangePercent: 8.3,
                totalOrders: 358,
                ordersChangePercent: 12.5,
                totalRevenue: 241345.75,
                revenueChangePercent: 15.2
            },
            usages: [
                {
                    usedAt: '2023-07-15T10:30:45',
                    user: {
                        id: 'USER-001',
                        name: '张三',
                        email: 'zhang.san@example.com'
                    },
                    order: {
                        id: 'ORD-001',
                        number: 'IF-20230715-001'
                    },
                    originalAmount: 1200,
                    discountAmount: 180,
                    finalAmount: 1020
                },
                {
                    usedAt: '2023-07-15T11:45:20',
                    user: {
                        id: 'USER-002',
                        name: '李四',
                        email: 'li.si@example.com'
                    },
                    order: {
                        id: 'ORD-002',
                        number: 'IF-20230715-002'
                    },
                    originalAmount: 850,
                    discountAmount: 127.50,
                    finalAmount: 722.50
                },
                {
                    usedAt: '2023-07-15T13:15:10',
                    user: {
                        id: 'USER-003',
                        name: '王五',
                        email: 'wang.wu@example.com'
                    },
                    order: {
                        id: 'ORD-003',
                        number: 'IF-20230715-003'
                    },
                    originalAmount: 1600,
                    discountAmount: 240,
                    finalAmount: 1360
                },
                {
                    usedAt: '2023-07-15T14:30:05',
                    user: {
                        id: 'USER-004',
                        name: '赵六',
                        email: 'zhao.liu@example.com'
                    },
                    order: {
                        id: 'ORD-004',
                        number: 'IF-20230715-004'
                    },
                    originalAmount: 2200,
                    discountAmount: 330,
                    finalAmount: 1870
                },
                {
                    usedAt: '2023-07-15T16:00:30',
                    user: {
                        id: 'USER-005',
                        name: '钱七',
                        email: 'qian.qi@example.com'
                    },
                    order: {
                        id: 'ORD-005',
                        number: 'IF-20230715-005'
                    },
                    originalAmount: 750,
                    discountAmount: 112.50,
                    finalAmount: 637.50
                }
            ]
        }
    },
    computed: {
        filteredUsages() {
            let result = [...this.usages];

            // 应用搜索过滤
            if (this.searchQuery) {
                const query = this.searchQuery.toLowerCase();
                result = result.filter(usage =>
                    usage.user.name.toLowerCase().includes(query) ||
                    usage.order.number.toLowerCase().includes(query)
                );
            }

            // 应用日期过滤
            if (this.dateRangeFilter !== 'all') {
                const now = new Date();
                let startOfRange = new Date();

                if (this.dateRangeFilter === 'today') {
                    startOfRange.setHours(0, 0, 0, 0);
                } else if (this.dateRangeFilter === 'yesterday') {
                    startOfRange.setDate(now.getDate() - 1);
                    startOfRange.setHours(0, 0, 0, 0);

                    const endOfYesterday = new Date();
                    endOfYesterday.setDate(now.getDate() - 1);
                    endOfYesterday.setHours(23, 59, 59, 999);

                    return result.filter(usage => {
                        const usageDate = new Date(usage.usedAt);
                        return usageDate >= startOfRange && usageDate <= endOfYesterday;
                    });
                } else if (this.dateRangeFilter === 'week') {
                    startOfRange.setDate(now.getDate() - now.getDay());
                    startOfRange.setHours(0, 0, 0, 0);
                } else if (this.dateRangeFilter === 'month') {
                    startOfRange.setDate(1);
                    startOfRange.setHours(0, 0, 0, 0);
                }

                result = result.filter(usage => {
                    const usageDate = new Date(usage.usedAt);
                    return usageDate >= startOfRange;
                });
            }

            return result;
        },
        totalPages() {
            return Math.ceil(this.filteredUsages.length / this.perPage);
        }
    },
    created() {
        // 从路由参数获取促销活动ID
        const promoId = this.$route.params.promoId;
        // 实际应用中应该从API获取促销活动详情和使用数据
        this.loadPromotionData(promoId);
    },
    methods: {
        formatDate(dateString) {
            const date = new Date(dateString);
            return date.toLocaleDateString('zh-CN');
        },
        formatDateTime(dateTimeString) {
            const date = new Date(dateTimeString);
            return date.toLocaleString('zh-CN');
        },
        getPromotionTypeClass(type) {
            const classes = {
                'seasonal': 'type-seasonal',
                'holiday': 'type-holiday',
                'flash': 'type-flash',
                'member': 'type-member',
                'first_purchase': 'type-first-purchase'
            };
            return classes[type] || '';
        },
        getPromotionTypeName(type) {
            const names = {
                'seasonal': '季节促销',
                'holiday': '节假日',
                'flash': '限时特惠',
                'member': '会员专享',
                'first_purchase': '首单优惠'
            };
            return names[type] || type;
        },
        getStatusClass(status) {
            return `status-${status}`;
        },
        getStatusText(status) {
            const statuses = {
                'active': '进行中',
                'upcoming': '即将开始',
                'expired': '已过期',
                'paused': '已暂停'
            };
            return statuses[status] || status;
        },
        getDiscountTypeText(type) {
            const types = {
                'percentage': '折扣',
                'fixed': '固定金额',
                'free_item': '赠品'
            };
            return types[type] || type;
        },
        formatDiscountValue(promotion) {
            if (promotion.discountType === 'percentage') {
                return `${100 - promotion.discountValue}折`;
            } else if (promotion.discountType === 'fixed') {
                return `减${promotion.discountValue}元`;
            } else if (promotion.discountType === 'free_item') {
                return promotion.discountValue;
            }
            return '';
        },
        getApplicableProducts(promotion) {
            if (promotion.applicableProducts.includes('all_flights')) {
                return '所有航班';
            } else if (promotion.applicableProducts.includes('domestic_flights')) {
                return '国内航班';
            } else if (promotion.applicableProducts.includes('international_flights')) {
                return '国际航班';
            }
            return '特定航班';
        },
        getCompareClass(percent) {
            return percent >= 0 ? 'change-up' : 'change-down';
        },
        loadPromotionData(promoId) {
            // 在实际应用中，这里应该调用API获取促销活动详情和使用数据
            console.log('正在加载促销活动ID:', promoId);
            // 模拟API加载
            this.promotion.id = promoId;
        },
        viewOrder(orderId) {
            console.log('查看订单详情:', orderId);
            // 实际应用中可能会导航到订单详情页
        }
    }
}
</script>

<style scoped>
.admin-promotion-usage {
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

.promotion-info {
    margin-bottom: 20px;
}

.info-card {
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    padding: 20px;
}

.promo-header {
    display: flex;
    align-items: center;
    margin-bottom: 15px;
}

.promo-badge {
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 12px;
    margin-right: 10px;
    white-space: nowrap;
}

.type-seasonal {
    background: #e3f2fd;
    color: #1565c0;
}

.type-holiday {
    background: #f3e5f5;
    color: #7b1fa2;
}

.type-flash {
    background: #fff8e1;
    color: #ff6f00;
}

.type-member {
    background: #e8f5e9;
    color: #2e7d32;
}

.type-first-purchase {
    background: #f1f8e9;
    color: #558b2f;
}

.promo-header h2 {
    margin: 0;
    font-size: 20px;
}

.promo-code {
    margin-left: auto;
    font-family: monospace;
    background: #f5f5f5;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 14px;
}

.promo-details {
    margin-top: 10px;
}

.detail-row {
    display: flex;
    margin-bottom: 10px;
}

.detail-item {
    flex: 1;
}

.detail-label {
    font-size: 12px;
    color: #666;
    margin-bottom: 3px;
}

.detail-value {
    font-size: 14px;
}

.promo-status {
    display: inline-block;
    margin-left: 10px;
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 12px;
}

.status-active {
    background: #e8f5e9;
    color: #2e7d32;
}

.status-upcoming {
    background: #e3f2fd;
    color: #1565c0;
}

.status-expired {
    background: #fafafa;
    color: #757575;
}

.status-paused {
    background: #fff8e1;
    color: #ff6f00;
}

.promo-description {
    margin-top: 10px;
    font-size: 14px;
    color: #555;
    line-height: 1.5;
}

.usage-stats {
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    padding: 20px;
}

.stat-cards {
    display: flex;
    flex-wrap: wrap;
    gap: 20px;
    margin-bottom: 20px;
}

.stat-card {
    background: #f9f9f9;
    border-radius: 8px;
    padding: 15px;
    flex: 1;
    min-width: 200px;
}

.stat-title {
    font-size: 14px;
    color: #666;
    margin-bottom: 5px;
}

.stat-value {
    font-size: 24px;
    font-weight: bold;
    color: #333;
    margin-bottom: 5px;
}

.stat-compare {
    font-size: 12px;
}

.change-up {
    color: #4caf50;
}

.change-down {
    color: #f44336;
}

.chart-section {
    margin: 20px 0;
    border-top: 1px solid #eee;
    padding-top: 20px;
}

.chart-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
}

.chart-header h3 {
    margin: 0;
    font-size: 16px;
}

.date-range-selector {
    display: flex;
    gap: 5px;
}

.date-range-selector .btn {
    padding: 5px 10px;
    background: #f5f5f5;
    border: 1px solid #ddd;
    border-radius: 4px;
    cursor: pointer;
}

.date-range-selector .btn.active {
    background: #3f51b5;
    color: white;
    border-color: #3f51b5;
}

.chart-container {
    height: 300px;
}

.chart-placeholder {
    height: 100%;
    background: #f9f9f9;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #999;
    border: 1px dashed #ddd;
    border-radius: 4px;
}

.usage-filters {
    display: flex;
    flex-wrap: wrap;
    gap: 15px;
    margin: 20px 0;
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

.usage-table {
    margin-top: 20px;
    margin-bottom: 20px;
    overflow-x: auto;
}

.usage-table table {
    width: 100%;
    border-collapse: collapse;
}

.usage-table th {
    background: #f9f9f9;
    padding: 12px 15px;
    text-align: left;
    font-weight: 600;
    color: #333;
    white-space: nowrap;
}

.usage-table td {
    padding: 12px 15px;
    border-top: 1px solid #eee;
    white-space: nowrap;
}

.user-info {
    line-height: 1.4;
}

.user-name {
    font-weight: bold;
}

.user-email {
    font-size: 12px;
    color: #666;
}

.order-link {
    color: #3f51b5;
    text-decoration: none;
    cursor: pointer;
}

.order-link:hover {
    text-decoration: underline;
}

.discount-amount {
    color: #f44336;
    font-weight: bold;
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
    .detail-row {
        flex-direction: column;
    }

    .detail-item {
        margin-bottom: 10px;
    }

    .promo-header {
        flex-wrap: wrap;
    }

    .promo-code {
        margin-left: 0;
        margin-top: 5px;
        width: 100%;
    }

    .stat-cards {
        flex-direction: column;
    }

    .chart-header {
        flex-direction: column;
        align-items: flex-start;
    }

    .date-range-selector {
        margin-top: 10px;
    }

    .usage-filters {
        flex-direction: column;
        align-items: stretch;
    }

    .export-btn {
        margin-left: 0;
    }
}
</style>