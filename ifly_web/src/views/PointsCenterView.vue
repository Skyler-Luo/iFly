<template>
    <div class="points-center">
        <div class="page-header">
            <h1>会员积分中心</h1>
        </div>

        <div class="points-overview">
            <el-row :gutter="20">
                <el-col :span="24" :lg="8">
                    <el-card class="points-card" shadow="hover">
                        <div class="points-summary">
                            <div class="points-value">
                                <span class="points-label">当前积分</span>
                                <span class="points-number">{{ userPoints.available }}</span>
                            </div>
                            <el-icon class="points-icon">
                                <Medal />
                            </el-icon>
                        </div>
                        <div class="points-actions">
                            <el-button type="primary" @click="goToExchange">积分兑换</el-button>
                            <el-button @click="goToDetail">积分明细</el-button>
                        </div>
                        <div class="points-expiring" v-if="userPoints.expiring > 0">
                            <el-alert title="积分到期提醒" type="warning" :closable="false" show-icon>
                                <div>您有 <strong>{{ userPoints.expiring }}</strong> 积分将于 {{ userPoints.expiryDate }}
                                    过期，请及时使用</div>
                            </el-alert>
                        </div>
                    </el-card>
                </el-col>

                <el-col :span="24" :lg="8">
                    <el-card class="member-card" shadow="hover">
                        <div class="member-info">
                            <div class="member-avatar">
                                <el-avatar :size="64" :src="userInfo.avatar">{{ userInfo.username?.substring(0, 1)
                                    }}</el-avatar>
                            </div>
                            <div class="member-details">
                                <h3>{{ userInfo.username }}</h3>
                                <div class="member-level">
                                    <el-tag :type="memberLevelType">{{ userInfo.memberLevel }}</el-tag>
                                    <div class="level-progress">
                                        <el-progress :percentage="memberLevelProgress" :color="memberLevelColor"
                                            :stroke-width="8" :show-text="false"></el-progress>
                                        <span class="progress-text">距离下一等级还需{{ userPoints.nextLevelPoints }}积分</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="member-benefits">
                            <h4>当前等级权益</h4>
                            <ul>
                                <li v-for="(benefit, index) in memberBenefits" :key="index">
                                    <el-icon>
                                        <Check />
                                    </el-icon>
                                    <span>{{ benefit }}</span>
                                </li>
                            </ul>
                        </div>
                    </el-card>
                </el-col>

                <el-col :span="24" :lg="8">
                    <el-card class="tasks-card" shadow="hover">
                        <div class="tasks-header">
                            <h3>积分获取任务</h3>
                            <router-link to="/points/tasks" class="view-all">查看全部</router-link>
                        </div>
                        <div class="tasks-list" v-loading="loadingTasks">
                            <div v-for="task in pointsTasks" :key="task.id" class="task-item">
                                <div class="task-info">
                                    <div class="task-name">
                                        <el-icon :class="{ 'task-done': task.completed }">
                                            <PriceTag />
                                        </el-icon>
                                        <span>{{ task.name }}</span>
                                    </div>
                                    <div class="task-points">+{{ task.points }}积分</div>
                                </div>
                                <el-button :type="task.completed ? 'success' : 'primary'" :disabled="task.completed"
                                    size="small" @click="completeTask(task)">
                                    {{ task.completed ? '已完成' : '去完成' }}
                                </el-button>
                            </div>
                        </div>
                    </el-card>
                </el-col>
            </el-row>
        </div>

        <div class="points-sections">
            <h2>积分兑换精选</h2>
            <el-row :gutter="20">
                <el-col :span="24" :md="8" :lg="6" v-for="item in exchangeItems" :key="item.id">
                    <el-card class="exchange-card" shadow="hover" @click="viewExchangeItem(item)">
                        <img :src="item.image" class="exchange-image" />
                        <div class="exchange-info">
                            <div class="exchange-title">{{ item.name }}</div>
                            <div class="exchange-points">{{ item.points }} 积分</div>
                            <div class="exchange-tag" v-if="item.isHot">热门</div>
                            <el-button type="primary" class="exchange-btn"
                                :disabled="userPoints.available < item.points">
                                立即兑换
                            </el-button>
                        </div>
                    </el-card>
                </el-col>
            </el-row>

            <div class="view-more-container">
                <router-link to="/points/exchange" class="view-more">
                    查看全部兑换商品
                    <el-icon>
                        <ArrowRight />
                    </el-icon>
                </router-link>
            </div>
        </div>

        <el-dialog v-model="exchangeDialogVisible" :title="selectedExchangeItem?.name" width="600px">
            <div v-if="selectedExchangeItem" class="exchange-dialog-content">
                <img :src="selectedExchangeItem.image" class="dialog-image" />
                <div class="dialog-details">
                    <div class="dialog-points">所需积分：{{ selectedExchangeItem.points }}</div>
                    <div class="dialog-description">{{ selectedExchangeItem.description }}</div>
                    <div class="dialog-rules" v-if="selectedExchangeItem.rules">
                        <h4>兑换规则</h4>
                        <ul>
                            <li v-for="(rule, index) in selectedExchangeItem.rules" :key="index">{{ rule }}</li>
                        </ul>
                    </div>
                    <div class="dialog-actions">
                        <el-button type="primary" size="large"
                            :disabled="userPoints.available < selectedExchangeItem.points" @click="exchangeItem">
                            立即兑换
                        </el-button>
                        <div class="points-check" v-if="userPoints.available < selectedExchangeItem.points">
                            <el-icon>
                                <Warning />
                            </el-icon>
                            积分不足，还差 {{ selectedExchangeItem.points - userPoints.available }} 积分
                        </div>
                    </div>
                </div>
            </div>
        </el-dialog>
    </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Medal, Check, PriceTag, ArrowRight, Warning } from '@element-plus/icons-vue'
// eslint-disable-next-line no-unused-vars
import api from '@/services/api'

export default {
    name: 'PointsCenterView',
    components: {
        Medal,
        Check,
        PriceTag,
        ArrowRight,
        Warning
    },
    setup() {
        const router = useRouter()
        const loadingTasks = ref(false)
        const exchangeDialogVisible = ref(false)
        const selectedExchangeItem = ref(null)

        const userInfo = reactive({
            username: '张三',
            avatar: '',
            memberLevel: '白银会员',
            joinDate: '2022-05-15'
        })

        const userPoints = reactive({
            available: 2350,
            expiring: 500,
            expiryDate: '2023-12-31',
            totalEarned: 3200,
            totalSpent: 850,
            nextLevelPoints: 1650
        })

        const pointsTasks = ref([
            {
                id: 1,
                name: '完善个人信息',
                points: 200,
                completed: true,
                route: '/profile'
            },
            {
                id: 2,
                name: '首次购票',
                points: 500,
                completed: true,
                route: '/'
            },
            {
                id: 3,
                name: '分享APP给好友',
                points: 300,
                completed: false,
                route: '/share'
            },
            {
                id: 4,
                name: '绑定手机号码',
                points: 100,
                completed: false,
                route: '/profile'
            },
            {
                id: 5,
                name: '评价已乘坐航班',
                points: 150,
                completed: false,
                route: '/orders'
            }
        ])

        const exchangeItems = ref([
            {
                id: 1,
                name: '经济舱升级商务舱',
                points: 2000,
                image: 'https://picsum.photos/id/250/600/400',
                description: '使用积分将您的经济舱机票升级为商务舱，享受更舒适的旅行体验。',
                isHot: true,
                rules: [
                    '仅适用于iFly航空运营的航班',
                    '升舱需提前至少24小时申请',
                    '升舱需视座位情况而定',
                    '每次升舱仅适用于单程航班'
                ]
            },
            {
                id: 2,
                name: '免费托运行李额',
                points: 1000,
                image: 'https://picsum.photos/id/46/600/400',
                description: '用积分兑换额外的托运行李额度，每次可增加10公斤。',
                isHot: false,
                rules: [
                    '需提前至少48小时申请',
                    '仅适用于iFly航空运营的航班',
                    '不可与其他行李额度优惠同时使用'
                ]
            },
            {
                id: 3,
                name: '机场贵宾休息室',
                points: 1500,
                image: 'https://picsum.photos/id/390/600/400',
                description: '兑换机场贵宾休息室使用权，享受候机时的优质服务与舒适环境。',
                isHot: true,
                rules: [
                    '可在指定机场的合作贵宾休息室使用',
                    '休息时间不超过3小时',
                    '需提前至少12小时预约'
                ]
            },
            {
                id: 4,
                name: '优惠券100元',
                points: 800,
                image: 'https://picsum.photos/id/36/600/400',
                description: '兑换100元机票优惠券，可直接抵扣机票金额。',
                isHot: false,
                rules: [
                    '单笔订单满500元可用',
                    '有效期为兑换后60天',
                    '不可与其他优惠券叠加使用'
                ]
            }
        ])

        const memberLevelType = computed(() => {
            const levels = {
                '普通会员': '',
                '白银会员': 'info',
                '黄金会员': 'warning',
                '白金会员': 'success',
                '钻石会员': 'danger'
            }
            return levels[userInfo.memberLevel] || ''
        })

        const memberLevelColor = computed(() => {
            const colors = {
                '普通会员': '#909399',
                '白银会员': '#A1A1AA',
                '黄金会员': '#F59E0B',
                '白金会员': '#10B981',
                '钻石会员': '#3B82F6'
            }
            return colors[userInfo.memberLevel] || '#909399'
        })

        const memberLevelProgress = computed(() => {
            const levelThresholds = {
                '普通会员': { min: 0, max: 1000 },
                '白银会员': { min: 1000, max: 5000 },
                '黄金会员': { min: 5000, max: 10000 },
                '白金会员': { min: 10000, max: 20000 },
                '钻石会员': { min: 20000, max: 50000 }
            }

            const currentLevel = levelThresholds[userInfo.memberLevel]
            if (!currentLevel) return 0

            const totalEarned = userPoints.available + userPoints.totalSpent
            const levelRange = currentLevel.max - currentLevel.min
            const userProgress = totalEarned - currentLevel.min
            return Math.min(Math.round((userProgress / levelRange) * 100), 100)
        })

        const memberBenefits = computed(() => {
            const benefits = {
                '普通会员': [
                    '正常积分累计',
                    '积分有效期24个月',
                    '生日积分礼遇'
                ],
                '白银会员': [
                    '正常积分累计',
                    '积分有效期24个月',
                    '生日积分礼遇',
                    '优先办理值机手续'
                ],
                '黄金会员': [
                    '积分1.2倍累计',
                    '积分有效期36个月',
                    '生日双倍积分礼遇',
                    '优先办理值机手续',
                    '免费选择座位'
                ],
                '白金会员': [
                    '积分1.5倍累计',
                    '积分不过期',
                    '生日三倍积分礼遇',
                    '贵宾休息室使用权',
                    '优先登机',
                    '免费选择座位',
                    '额外行李额度10kg'
                ],
                '钻石会员': [
                    '积分2倍累计',
                    '积分不过期',
                    '生日五倍积分礼遇',
                    '全球机场贵宾休息室',
                    '专属值机柜台',
                    '优先登机',
                    '免费选择座位',
                    '额外行李额度20kg',
                    '国内航班免费升舱机会2次/年'
                ]
            }

            return benefits[userInfo.memberLevel] || []
        })

        // 模拟获取用户积分数据
        const fetchUserPointsData = async () => {
            // 实际项目中应该从API获取数据
            // try {
            //   const result = await api.points.getUserPoints()
            //   userPoints.available = result.available
            //   userPoints.expiring = result.expiring
            //   userPoints.expiryDate = result.expiryDate
            //   userPoints.totalEarned = result.totalEarned
            //   userPoints.totalSpent = result.totalSpent
            //   userPoints.nextLevelPoints = result.nextLevelPoints
            //   
            //   userInfo.username = result.username
            //   userInfo.avatar = result.avatar
            //   userInfo.memberLevel = result.memberLevel
            //   userInfo.joinDate = result.joinDate
            // } catch (error) {
            //   console.error('获取用户积分数据失败:', error)
            //   ElMessage.error('获取积分数据失败')
            // }
        }

        // 模拟获取积分任务列表
        const fetchPointsTasks = async () => {
            loadingTasks.value = true

            // 使用setTimeout模拟API请求延迟
            setTimeout(() => {
                // 实际项目中应从API获取
                // try {
                //   const result = await api.points.getTasks()
                //   pointsTasks.value = result
                // } catch (error) {
                //   console.error('获取积分任务失败:', error)
                //   ElMessage.error('获取积分任务失败')
                // }

                loadingTasks.value = false
            }, 800)
        }

        // 完成积分任务
        const completeTask = (task) => {
            if (task.completed) return

            // 实际项目中应该调用API进行任务完成操作
            // try {
            //   await api.points.completeTask(task.id)
            //   
            //   // 任务完成后刷新任务列表和积分数据
            //   fetchPointsTasks()
            //   fetchUserPointsData()
            //   
            //   ElMessage.success(`恭喜您完成任务，获得${task.points}积分！`)
            // } catch (error) {
            //   console.error('完成任务失败:', error)
            //   ElMessage.error('无法完成任务，请稍后再试')
            // }

            // 跳转到相应页面完成任务
            router.push(task.route)
        }

        // 查看兑换商品详情
        const viewExchangeItem = (item) => {
            selectedExchangeItem.value = item
            exchangeDialogVisible.value = true
        }

        // 兑换商品
        const exchangeItem = () => {
            if (!selectedExchangeItem.value) return
            if (userPoints.available < selectedExchangeItem.value.points) {
                ElMessage.warning('积分不足，无法兑换')
                return
            }

            // 实际项目中应该调用API进行兑换操作
            // try {
            //   await api.points.exchange(selectedExchangeItem.value.id)
            //   userPoints.available -= selectedExchangeItem.value.points
            //   userPoints.totalSpent += selectedExchangeItem.value.points
            //   
            //   ElMessage.success('兑换成功！')
            //   exchangeDialogVisible.value = false
            // } catch (error) {
            //   console.error('兑换失败:', error)
            //   ElMessage.error('兑换失败，请稍后再试')
            // }

            // 模拟兑换成功
            userPoints.available -= selectedExchangeItem.value.points
            userPoints.totalSpent += selectedExchangeItem.value.points
            ElMessage.success('兑换成功！')
            exchangeDialogVisible.value = false
        }

        // 导航到其他积分中心页面
        const goToExchange = () => router.push('/points/exchange')
        const goToDetail = () => router.push('/points/history')

        onMounted(() => {
            fetchUserPointsData()
            fetchPointsTasks()
        })

        return {
            loadingTasks,
            userInfo,
            userPoints,
            pointsTasks,
            exchangeItems,
            exchangeDialogVisible,
            selectedExchangeItem,
            memberLevelType,
            memberLevelColor,
            memberLevelProgress,
            memberBenefits,
            completeTask,
            viewExchangeItem,
            exchangeItem,
            goToExchange,
            goToDetail
        }
    }
}
</script>

<style scoped>
.points-center {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

.page-header {
    text-align: center;
    margin-bottom: 30px;
}

.page-header h1 {
    font-size: 28px;
    color: #303133;
    margin-bottom: 10px;
}

.points-overview {
    margin-bottom: 40px;
}

.points-card,
.member-card,
.tasks-card {
    height: 100%;
    margin-bottom: 20px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    border-radius: 8px;
}

/* 积分卡片 */
.points-summary {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}

.points-value {
    display: flex;
    flex-direction: column;
}

.points-label {
    font-size: 16px;
    color: #606266;
    margin-bottom: 5px;
}

.points-number {
    font-size: 42px;
    font-weight: bold;
    color: #409EFF;
    line-height: 1;
}

.points-icon {
    font-size: 40px;
    color: #E6A23C;
}

.points-actions {
    display: flex;
    gap: 10px;
    margin-bottom: 15px;
}

.points-expiring {
    margin-top: 15px;
}

/* 会员卡片 */
.member-info {
    display: flex;
    align-items: center;
    margin-bottom: 20px;
}

.member-avatar {
    margin-right: 20px;
}

.member-details {
    flex-grow: 1;
}

.member-details h3 {
    margin: 0 0 10px;
    font-size: 20px;
    color: #303133;
}

.member-level {
    margin-top: 10px;
}

.level-progress {
    margin-top: 15px;
}

.progress-text {
    display: block;
    font-size: 12px;
    color: #909399;
    margin-top: 5px;
    text-align: right;
}

.member-benefits {
    margin-top: 20px;
    background-color: #f5f7fa;
    padding: 15px;
    border-radius: 8px;
}

.member-benefits h4 {
    margin: 0 0 15px;
    font-size: 16px;
    color: #303133;
}

.member-benefits ul {
    margin: 0;
    padding: 0;
    list-style: none;
}

.member-benefits li {
    display: flex;
    align-items: center;
    margin-bottom: 10px;
    color: #606266;
}

.member-benefits li .el-icon {
    color: #67C23A;
    margin-right: 8px;
}

/* 任务卡片 */
.tasks-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
}

.tasks-header h3 {
    margin: 0;
    font-size: 18px;
    color: #303133;
}

.view-all {
    color: #409EFF;
    font-size: 14px;
    text-decoration: none;
}

.task-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 15px 0;
    border-bottom: 1px solid #EBEEF5;
}

.task-item:last-child {
    border-bottom: none;
}

.task-info {
    flex-grow: 1;
    margin-right: 15px;
}

.task-name {
    display: flex;
    align-items: center;
    margin-bottom: 5px;
}

.task-name .el-icon {
    margin-right: 8px;
    color: #409EFF;
}

.task-name .task-done {
    color: #67C23A;
}

.task-points {
    font-size: 14px;
    color: #E6A23C;
    font-weight: bold;
}

/* 积分兑换部分 */
.points-sections {
    margin-top: 50px;
}

.points-sections h2 {
    font-size: 24px;
    color: #303133;
    margin-bottom: 20px;
}

.exchange-card {
    height: 100%;
    cursor: pointer;
    transition: transform 0.3s, box-shadow 0.3s;
    margin-bottom: 20px;
    overflow: hidden;
    position: relative;
}

.exchange-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
}

.exchange-image {
    width: 100%;
    height: 180px;
    object-fit: cover;
}

.exchange-info {
    padding: 15px;
}

.exchange-title {
    font-size: 16px;
    font-weight: bold;
    margin-bottom: 10px;
    color: #303133;
}

.exchange-points {
    font-size: 18px;
    color: #E6A23C;
    font-weight: bold;
    margin-bottom: 15px;
}

.exchange-tag {
    position: absolute;
    top: 10px;
    right: 10px;
    background-color: #F56C6C;
    color: white;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 12px;
    font-weight: bold;
}

.exchange-btn {
    width: 100%;
}

.view-more-container {
    text-align: center;
    margin-top: 30px;
}

.view-more {
    display: inline-flex;
    align-items: center;
    color: #409EFF;
    font-size: 16px;
    text-decoration: none;
    padding: 10px 20px;
    border: 1px solid #DCDFE6;
    border-radius: 20px;
    transition: all 0.3s;
}

.view-more:hover {
    color: #66b1ff;
    border-color: #c6e2ff;
    background-color: #ecf5ff;
}

.view-more .el-icon {
    margin-left: 5px;
}

/* 兑换详情对话框 */
.exchange-dialog-content {
    display: flex;
    flex-direction: column;
}

.dialog-image {
    width: 100%;
    max-height: 300px;
    object-fit: cover;
    border-radius: 8px;
    margin-bottom: 20px;
}

.dialog-points {
    font-size: 20px;
    color: #E6A23C;
    font-weight: bold;
    margin-bottom: 20px;
}

.dialog-description {
    color: #606266;
    line-height: 1.6;
    margin-bottom: 20px;
}

.dialog-rules {
    margin-bottom: 20px;
}

.dialog-rules h4 {
    margin: 0 0 10px;
    font-size: 16px;
    color: #303133;
}

.dialog-rules ul {
    padding-left: 20px;
    color: #606266;
}

.dialog-actions {
    margin-top: 20px;
}

.points-check {
    margin-top: 10px;
    color: #F56C6C;
    font-size: 14px;
    display: flex;
    align-items: center;
}

.points-check .el-icon {
    margin-right: 5px;
}

@media (min-width: 992px) {
    .exchange-dialog-content {
        flex-direction: row;
    }

    .dialog-image {
        width: 40%;
        margin-right: 20px;
        margin-bottom: 0;
        max-height: 400px;
    }

    .dialog-details {
        flex: 1;
    }
}
</style>