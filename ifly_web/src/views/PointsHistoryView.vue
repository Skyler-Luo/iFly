<template>
    <div class="points-history">
        <div class="page-header">
            <el-page-header @back="goBack" content="积分明细"></el-page-header>
        </div>

        <div class="points-summary-panel">
            <el-row :gutter="20">
                <el-col :xs="24" :sm="8">
                    <div class="summary-card">
                        <div class="summary-title">可用积分</div>
                        <div class="summary-value">{{ pointsOverview.available }}</div>
                    </div>
                </el-col>
                <el-col :xs="24" :sm="8">
                    <div class="summary-card">
                        <div class="summary-title">总收入积分</div>
                        <div class="summary-value green">+{{ pointsOverview.totalEarned }}</div>
                    </div>
                </el-col>
                <el-col :xs="24" :sm="8">
                    <div class="summary-card">
                        <div class="summary-title">总支出积分</div>
                        <div class="summary-value orange">-{{ pointsOverview.totalSpent }}</div>
                    </div>
                </el-col>
            </el-row>
        </div>

        <div class="points-filter">
            <el-form :inline="true" class="filter-form">
                <el-form-item label="时间范围">
                    <el-date-picker v-model="dateRange" type="daterange" range-separator="至" start-placeholder="开始日期"
                        end-placeholder="结束日期" format="YYYY-MM-DD" value-format="YYYY-MM-DD"
                        :shortcuts="dateShortcuts" />
                </el-form-item>
                <el-form-item label="交易类型">
                    <el-select v-model="transactionType" placeholder="全部类型">
                        <el-option label="全部类型" value="all" />
                        <el-option label="积分获取" value="earn" />
                        <el-option label="积分消费" value="spend" />
                        <el-option label="积分过期" value="expire" />
                        <el-option label="积分调整" value="adjust" />
                    </el-select>
                </el-form-item>
                <el-form-item>
                    <el-button type="primary" @click="searchHistory">搜索</el-button>
                    <el-button @click="resetFilter">重置</el-button>
                </el-form-item>
            </el-form>
        </div>

        <div class="points-table">
            <el-table v-loading="loading" :data="pointsHistory" style="width: 100%" :empty-text="emptyText" border>
                <el-table-column prop="date" label="交易日期" min-width="120">
                    <template #default="scope">
                        <div>{{ formatDate(scope.row.date) }}</div>
                    </template>
                </el-table-column>

                <el-table-column prop="description" label="交易描述" min-width="200" />

                <el-table-column prop="points" label="积分变动" width="120">
                    <template #default="scope">
                        <span :class="getPointsClass(scope.row.points)">
                            {{ getPointsDisplay(scope.row.points) }}
                        </span>
                    </template>
                </el-table-column>

                <el-table-column prop="type" label="交易类型" width="120">
                    <template #default="scope">
                        <el-tag :type="getTransactionTypeTag(scope.row.type)">
                            {{ getTransactionTypeText(scope.row.type) }}
                        </el-tag>
                    </template>
                </el-table-column>

                <el-table-column prop="balance" label="积分余额" width="120" />

                <el-table-column label="操作" width="100" fixed="right">
                    <template #default="scope">
                        <el-button v-if="scope.row.hasDetails" link type="primary" @click="showDetails(scope.row)">
                            详情
                        </el-button>
                    </template>
                </el-table-column>
            </el-table>
        </div>

        <div class="pagination-container">
            <el-pagination v-model:current-page="currentPage" v-model:page-size="pageSize"
                :page-sizes="[10, 20, 50, 100]" layout="total, sizes, prev, pager, next, jumper" :total="totalRecords"
                @size-change="handleSizeChange" @current-change="handleCurrentChange" />
        </div>

        <!-- 交易详情对话框 -->
        <el-dialog v-model="detailsVisible" :title="`交易详情 - ${currentTransaction?.id || ''}`" width="500px">
            <div v-if="currentTransaction" class="transaction-details">
                <div class="detail-item">
                    <span class="detail-label">交易时间:</span>
                    <span class="detail-value">{{ formatDateTime(currentTransaction.date) }}</span>
                </div>

                <div class="detail-item">
                    <span class="detail-label">交易类型:</span>
                    <span class="detail-value">
                        <el-tag :type="getTransactionTypeTag(currentTransaction.type)">
                            {{ getTransactionTypeText(currentTransaction.type) }}
                        </el-tag>
                    </span>
                </div>

                <div class="detail-item">
                    <span class="detail-label">积分变动:</span>
                    <span :class="['detail-value', getPointsClass(currentTransaction.points)]">
                        {{ getPointsDisplay(currentTransaction.points) }}
                    </span>
                </div>

                <div class="detail-item">
                    <span class="detail-label">交易描述:</span>
                    <span class="detail-value">{{ currentTransaction.description }}</span>
                </div>

                <div class="detail-item">
                    <span class="detail-label">积分余额:</span>
                    <span class="detail-value">{{ currentTransaction.balance }}</span>
                </div>

                <div class="detail-item" v-if="currentTransaction.orderNumber">
                    <span class="detail-label">订单编号:</span>
                    <span class="detail-value">
                        <router-link :to="`/orders/${currentTransaction.orderId}`">
                            {{ currentTransaction.orderNumber }}
                        </router-link>
                    </span>
                </div>

                <div class="detail-item" v-if="currentTransaction.expireDate">
                    <span class="detail-label">有效期至:</span>
                    <span class="detail-value">{{ formatDate(currentTransaction.expireDate) }}</span>
                </div>

                <div class="detail-item" v-if="currentTransaction.remark">
                    <span class="detail-label">备注:</span>
                    <span class="detail-value">{{ currentTransaction.remark }}</span>
                </div>
            </div>
        </el-dialog>
    </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { format, parseISO } from 'date-fns'
// eslint-disable-next-line no-unused-vars
import api from '@/services/api'

export default {
    name: 'PointsHistoryView',
    setup() {
        const router = useRouter()
        const loading = ref(false)
        const dateRange = ref([])
        const transactionType = ref('all')
        const currentPage = ref(1)
        const pageSize = ref(10)
        const totalRecords = ref(0)
        const detailsVisible = ref(false)
        const currentTransaction = ref(null)
        const emptyText = ref('暂无积分交易记录')

        // 积分概览
        const pointsOverview = reactive({
            available: 2350,
            totalEarned: 3200,
            totalSpent: 850
        })

        // 积分交易历史
        const pointsHistory = ref([
            {
                id: 'TX20230501001',
                date: '2023-05-01T14:23:45',
                description: '购买机票 PEK-SHA 获得积分',
                points: 500,
                type: 'earn',
                balance: 500,
                hasDetails: true,
                orderNumber: 'ORD2023050100123',
                orderId: '100123',
                expireDate: '2025-05-01',
                remark: '首次购票额外奖励'
            },
            {
                id: 'TX20230510002',
                date: '2023-05-10T10:15:30',
                description: '完善个人信息获得积分',
                points: 200,
                type: 'earn',
                balance: 700,
                hasDetails: true,
                remark: '新用户任务奖励'
            },
            {
                id: 'TX20230615003',
                date: '2023-06-15T16:42:10',
                description: '购买机票 SHA-CAN 获得积分',
                points: 350,
                type: 'earn',
                balance: 1050,
                hasDetails: true,
                orderNumber: 'ORD2023061500456',
                orderId: '100456',
                expireDate: '2025-06-15'
            },
            {
                id: 'TX20230620004',
                date: '2023-06-20T09:35:12',
                description: '兑换机场贵宾休息室服务',
                points: -1500,
                type: 'spend',
                balance: -450,
                hasDetails: true,
                remark: '贵宾休息室使用3小时'
            },
            {
                id: 'TX20230621005',
                date: '2023-06-21T11:25:33',
                description: '服务投诉补偿积分',
                points: 1000,
                type: 'adjust',
                balance: 550,
                hasDetails: true,
                remark: '航班延误补偿'
            },
            {
                id: 'TX20230725006',
                date: '2023-07-25T15:10:50',
                description: '购买机票 CAN-PEK 获得积分',
                points: 450,
                type: 'earn',
                balance: 1000,
                hasDetails: true,
                orderNumber: 'ORD2023072500789',
                orderId: '100789',
                expireDate: '2025-07-25'
            },
            {
                id: 'TX20230805007',
                date: '2023-08-05T18:23:05',
                description: '兑换优惠券',
                points: -200,
                type: 'spend',
                balance: 800,
                hasDetails: true,
                remark: '100元机票优惠券'
            },
            {
                id: 'TX20230920008',
                date: '2023-09-20T20:15:40',
                description: '会员等级升级奖励积分',
                points: 1000,
                type: 'earn',
                balance: 1800,
                hasDetails: true,
                remark: '晋升白银会员奖励'
            },
            {
                id: 'TX20231015009',
                date: '2023-10-15T14:30:22',
                description: '积分过期',
                points: -150,
                type: 'expire',
                balance: 1650,
                hasDetails: true,
                remark: '2021年10月积分到期'
            },
            {
                id: 'TX20231105010',
                date: '2023-11-05T09:45:18',
                description: '购买机票 PEK-CTU 获得积分',
                points: 700,
                type: 'earn',
                balance: 2350,
                hasDetails: true,
                orderNumber: 'ORD2023110500567',
                orderId: '100567',
                expireDate: '2025-11-05'
            }
        ])

        const dateShortcuts = [
            {
                text: '最近一周',
                value: () => {
                    const end = new Date()
                    const start = new Date()
                    start.setTime(start.getTime() - 3600 * 1000 * 24 * 7)
                    return [start, end]
                }
            },
            {
                text: '最近一个月',
                value: () => {
                    const end = new Date()
                    const start = new Date()
                    start.setTime(start.getTime() - 3600 * 1000 * 24 * 30)
                    return [start, end]
                }
            },
            {
                text: '最近三个月',
                value: () => {
                    const end = new Date()
                    const start = new Date()
                    start.setTime(start.getTime() - 3600 * 1000 * 24 * 90)
                    return [start, end]
                }
            }
        ]

        // 格式化日期时间
        const formatDate = (dateString) => {
            try {
                return format(parseISO(dateString), 'yyyy-MM-dd')
            } catch (e) {
                return dateString
            }
        }

        // 格式化日期时间（包含时间）
        const formatDateTime = (dateString) => {
            try {
                return format(parseISO(dateString), 'yyyy-MM-dd HH:mm:ss')
            } catch (e) {
                return dateString
            }
        }

        // 获取积分变动的显示文本
        const getPointsDisplay = (points) => {
            if (points > 0) {
                return `+${points}`
            }
            return points.toString()
        }

        // 获取积分变动的CSS类
        const getPointsClass = (points) => {
            if (points > 0) {
                return 'points-positive'
            } else if (points < 0) {
                return 'points-negative'
            }
            return ''
        }

        // 获取交易类型的标签类型
        const getTransactionTypeTag = (type) => {
            const types = {
                'earn': 'success',
                'spend': 'info',
                'expire': 'danger',
                'adjust': 'warning'
            }
            return types[type] || ''
        }

        // 获取交易类型的显示文本
        const getTransactionTypeText = (type) => {
            const texts = {
                'earn': '积分获取',
                'spend': '积分消费',
                'expire': '积分过期',
                'adjust': '积分调整'
            }
            return texts[type] || '未知类型'
        }

        // 显示交易详情
        const showDetails = (transaction) => {
            currentTransaction.value = transaction
            detailsVisible.value = true
        }

        // 搜索历史记录
        const searchHistory = () => {
            loading.value = true
            currentPage.value = 1

            // 模拟API请求
            setTimeout(() => {
                // 实际项目中应该调用API获取过滤后的数据
                // try {
                //   const params = {
                //     page: currentPage.value,
                //     pageSize: pageSize.value,
                //     startDate: dateRange.value?.[0] || null,
                //     endDate: dateRange.value?.[1] || null,
                //     type: transactionType.value !== 'all' ? transactionType.value : null
                //   }
                //   const result = await api.points.getHistory(params)
                //   pointsHistory.value = result.records
                //   totalRecords.value = result.total
                // } catch (error) {
                //   console.error('获取积分历史失败:', error)
                //   ElMessage.error('获取积分历史失败')
                // }

                // 模拟筛选逻辑
                let filteredData = [...getAllHistory()]

                // 按日期范围筛选
                if (dateRange.value && dateRange.value.length === 2) {
                    const startDate = new Date(dateRange.value[0])
                    const endDate = new Date(dateRange.value[1])
                    endDate.setHours(23, 59, 59, 999) // 设置为当天结束时间

                    filteredData = filteredData.filter(item => {
                        const itemDate = new Date(item.date)
                        return itemDate >= startDate && itemDate <= endDate
                    })
                }

                // 按类型筛选
                if (transactionType.value !== 'all') {
                    filteredData = filteredData.filter(item => item.type === transactionType.value)
                }

                totalRecords.value = filteredData.length

                // 分页
                const start = (currentPage.value - 1) * pageSize.value
                const end = start + pageSize.value
                pointsHistory.value = filteredData.slice(start, end)

                loading.value = false
            }, 800)
        }

        // 重置筛选条件
        const resetFilter = () => {
            dateRange.value = []
            transactionType.value = 'all'
            searchHistory()
        }

        // 处理每页显示数量变化
        const handleSizeChange = (size) => {
            pageSize.value = size
            searchHistory()
        }

        // 处理页码变化
        const handleCurrentChange = (page) => {
            currentPage.value = page
            searchHistory()
        }

        // 返回上一页
        const goBack = () => {
            router.push('/points')
        }

        // 获取所有历史记录（模拟）
        const getAllHistory = () => {
            return [
                {
                    id: 'TX20230501001',
                    date: '2023-05-01T14:23:45',
                    description: '购买机票 PEK-SHA 获得积分',
                    points: 500,
                    type: 'earn',
                    balance: 500,
                    hasDetails: true,
                    orderNumber: 'ORD2023050100123',
                    orderId: '100123',
                    expireDate: '2025-05-01',
                    remark: '首次购票额外奖励'
                },
                {
                    id: 'TX20230510002',
                    date: '2023-05-10T10:15:30',
                    description: '完善个人信息获得积分',
                    points: 200,
                    type: 'earn',
                    balance: 700,
                    hasDetails: true,
                    remark: '新用户任务奖励'
                },
                {
                    id: 'TX20230615003',
                    date: '2023-06-15T16:42:10',
                    description: '购买机票 SHA-CAN 获得积分',
                    points: 350,
                    type: 'earn',
                    balance: 1050,
                    hasDetails: true,
                    orderNumber: 'ORD2023061500456',
                    orderId: '100456',
                    expireDate: '2025-06-15'
                },
                {
                    id: 'TX20230620004',
                    date: '2023-06-20T09:35:12',
                    description: '兑换机场贵宾休息室服务',
                    points: -1500,
                    type: 'spend',
                    balance: -450,
                    hasDetails: true,
                    remark: '贵宾休息室使用3小时'
                },
                {
                    id: 'TX20230621005',
                    date: '2023-06-21T11:25:33',
                    description: '服务投诉补偿积分',
                    points: 1000,
                    type: 'adjust',
                    balance: 550,
                    hasDetails: true,
                    remark: '航班延误补偿'
                },
                {
                    id: 'TX20230725006',
                    date: '2023-07-25T15:10:50',
                    description: '购买机票 CAN-PEK 获得积分',
                    points: 450,
                    type: 'earn',
                    balance: 1000,
                    hasDetails: true,
                    orderNumber: 'ORD2023072500789',
                    orderId: '100789',
                    expireDate: '2025-07-25'
                },
                {
                    id: 'TX20230805007',
                    date: '2023-08-05T18:23:05',
                    description: '兑换优惠券',
                    points: -200,
                    type: 'spend',
                    balance: 800,
                    hasDetails: true,
                    remark: '100元机票优惠券'
                },
                {
                    id: 'TX20230920008',
                    date: '2023-09-20T20:15:40',
                    description: '会员等级升级奖励积分',
                    points: 1000,
                    type: 'earn',
                    balance: 1800,
                    hasDetails: true,
                    remark: '晋升白银会员奖励'
                },
                {
                    id: 'TX20231015009',
                    date: '2023-10-15T14:30:22',
                    description: '积分过期',
                    points: -150,
                    type: 'expire',
                    balance: 1650,
                    hasDetails: true,
                    remark: '2021年10月积分到期'
                },
                {
                    id: 'TX20231105010',
                    date: '2023-11-05T09:45:18',
                    description: '购买机票 PEK-CTU 获得积分',
                    points: 700,
                    type: 'earn',
                    balance: 2350,
                    hasDetails: true,
                    orderNumber: 'ORD2023110500567',
                    orderId: '100567',
                    expireDate: '2025-11-05'
                },
                {
                    id: 'TX20230502011',
                    date: '2023-05-02T08:30:00',
                    description: '参与调查问卷获得积分',
                    points: 100,
                    type: 'earn',
                    balance: 600,
                    hasDetails: true,
                    remark: '用户体验调查'
                },
                {
                    id: 'TX20230620012',
                    date: '2023-06-20T11:45:20',
                    description: '兑换免费托运行李额',
                    points: -1000,
                    type: 'spend',
                    balance: 50,
                    hasDetails: true,
                    remark: '额外10kg行李额度'
                }
            ]
        }

        // 初始化加载积分历史
        onMounted(() => {
            // 模拟获取用户积分概览
            // async function fetchPointsOverview() {
            //   try {
            //     const result = await api.points.getOverview()
            //     pointsOverview.available = result.available
            //     pointsOverview.totalEarned = result.totalEarned
            //     pointsOverview.totalSpent = result.totalSpent
            //   } catch (error) {
            //     console.error('获取积分概览失败:', error)
            //     ElMessage.error('获取积分概览失败')
            //   }
            // }

            // fetchPointsOverview()
            searchHistory()
        })

        return {
            loading,
            dateRange,
            transactionType,
            currentPage,
            pageSize,
            totalRecords,
            pointsHistory,
            pointsOverview,
            detailsVisible,
            currentTransaction,
            emptyText,
            dateShortcuts,
            formatDate,
            formatDateTime,
            getPointsDisplay,
            getPointsClass,
            getTransactionTypeTag,
            getTransactionTypeText,
            showDetails,
            searchHistory,
            resetFilter,
            handleSizeChange,
            handleCurrentChange,
            goBack
        }
    }
}
</script>

<style scoped>
.points-history {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

.page-header {
    margin-bottom: 30px;
}

.points-summary-panel {
    margin-bottom: 30px;
}

.summary-card {
    background: #f5f7fa;
    border-radius: 8px;
    padding: 20px;
    text-align: center;
    margin-bottom: 20px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
}

.summary-title {
    font-size: 16px;
    color: #606266;
    margin-bottom: 10px;
}

.summary-value {
    font-size: 28px;
    font-weight: bold;
    color: #303133;
}

.summary-value.green {
    color: #67C23A;
}

.summary-value.orange {
    color: #E6A23C;
}

.points-filter {
    margin-bottom: 20px;
}

.filter-form {
    background: #fff;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
}

.points-table {
    margin-bottom: 20px;
}

.points-positive {
    color: #67C23A;
    font-weight: bold;
}

.points-negative {
    color: #F56C6C;
    font-weight: bold;
}

.pagination-container {
    display: flex;
    justify-content: flex-end;
    margin-top: 20px;
}

/* 交易详情样式 */
.transaction-details {
    padding: 10px 0;
}

.detail-item {
    display: flex;
    margin-bottom: 15px;
}

.detail-label {
    width: 100px;
    color: #909399;
    flex-shrink: 0;
}

.detail-value {
    flex-grow: 1;
    color: #303133;
}

@media (max-width: 768px) {
    .filter-form {
        padding: 15px;
    }

    .summary-value {
        font-size: 24px;
    }

    .detail-item {
        flex-direction: column;
    }

    .detail-label {
        width: 100%;
        margin-bottom: 5px;
    }
}
</style>