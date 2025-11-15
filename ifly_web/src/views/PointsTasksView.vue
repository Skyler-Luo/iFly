<template>
    <div class="points-tasks">
        <div class="page-header">
            <el-page-header @back="goBack" content="积分任务中心"></el-page-header>
        </div>

        <div class="points-balance">
            <div class="balance-info">
                <span>当前可用积分：</span>
                <span class="balance-value">{{ userPoints }}</span>
            </div>
            <el-button @click="goToHistory" size="small">查看积分明细</el-button>
        </div>

        <div class="tasks-container">
            <el-tabs v-model="activeTab" class="task-tabs">
                <el-tab-pane label="日常任务" name="daily">
                    <div class="tasks-group">
                        <h3 class="tasks-group-title">
                            <span>每日任务</span>
                            <span class="tasks-desc">每天重置，次日凌晨更新</span>
                        </h3>
                        <el-card v-for="task in dailyTasks" :key="task.id" class="task-card" shadow="hover">
                            <task-item :task="task" @complete="completeTask" @view-details="viewTaskDetails" />
                        </el-card>
                    </div>

                    <div class="tasks-group">
                        <h3 class="tasks-group-title">
                            <span>旅行任务</span>
                            <span class="tasks-desc">与旅行相关的积分任务</span>
                        </h3>
                        <el-card v-for="task in travelTasks" :key="task.id" class="task-card" shadow="hover">
                            <task-item :task="task" @complete="completeTask" @view-details="viewTaskDetails" />
                        </el-card>
                    </div>
                </el-tab-pane>

                <el-tab-pane label="新手任务" name="rookie">
                    <div class="tasks-group">
                        <h3 class="tasks-group-title">
                            <span>账户任务</span>
                            <span class="tasks-desc">完成账户相关设置获取积分</span>
                        </h3>
                        <el-card v-for="task in accountTasks" :key="task.id" class="task-card" shadow="hover">
                            <task-item :task="task" @complete="completeTask" @view-details="viewTaskDetails" />
                        </el-card>
                    </div>

                    <div class="tasks-group">
                        <h3 class="tasks-group-title">
                            <span>首次体验</span>
                            <span class="tasks-desc">首次使用相关服务获取积分奖励</span>
                        </h3>
                        <el-card v-for="task in firstTimeTasks" :key="task.id" class="task-card" shadow="hover">
                            <task-item :task="task" @complete="completeTask" @view-details="viewTaskDetails" />
                        </el-card>
                    </div>
                </el-tab-pane>

                <el-tab-pane label="积分奖励" name="rewards">
                    <div class="tasks-group">
                        <h3 class="tasks-group-title">
                            <span>积分倍增</span>
                            <span class="tasks-desc">会员等级积分倍率</span>
                        </h3>
                        <el-card class="info-card">
                            <div class="multiplier-info">
                                <div class="user-level-info">
                                    <el-tag :type="levelTagType">{{ userLevel }}</el-tag>
                                    <div class="multiplier">{{ levelMultiplier }}倍积分</div>
                                </div>
                                <div class="level-description">
                                    {{ levelDescription }}
                                </div>
                                <div class="level-upgrade">
                                    <p>距离下一等级还需 <strong>{{ nextLevelPoints }}</strong> 积分</p>
                                    <el-progress :percentage="levelProgress" :color="levelColor" :stroke-width="10"
                                        :show-text="false"></el-progress>
                                </div>
                            </div>
                        </el-card>
                    </div>

                    <div class="tasks-group">
                        <h3 class="tasks-group-title">
                            <span>积分获取渠道</span>
                            <span class="tasks-desc">多种途径获取更多积分</span>
                        </h3>
                        <el-card v-for="channel in pointChannels" :key="channel.id" class="info-card">
                            <div class="channel-info">
                                <div class="channel-header">
                                    <div class="channel-title">{{ channel.name }}</div>
                                    <div class="channel-points">+{{ channel.points }}</div>
                                </div>
                                <div class="channel-desc">{{ channel.description }}</div>
                                <div class="channel-actions" v-if="channel.actionType">
                                    <el-button type="primary" size="small" @click="goToChannelAction(channel)">
                                        {{ channel.actionText }}
                                    </el-button>
                                </div>
                            </div>
                        </el-card>
                    </div>
                </el-tab-pane>
            </el-tabs>
        </div>

        <!-- 任务详情弹窗 -->
        <el-dialog v-model="taskDetailsVisible" :title="currentTask?.name || '任务详情'" width="500px">
            <div v-if="currentTask" class="task-details">
                <div class="detail-header">
                    <div class="detail-points">+{{ currentTask.points }} 积分</div>
                    <el-tag :type="currentTask.completed ? 'success' : 'info'" effect="dark">
                        {{ currentTask.completed ? '已完成' : '未完成' }}
                    </el-tag>
                </div>

                <div class="detail-section">
                    <h4>任务描述</h4>
                    <p>{{ currentTask.description }}</p>
                </div>

                <div class="detail-section" v-if="currentTask.steps && currentTask.steps.length > 0">
                    <h4>完成步骤</h4>
                    <ol class="task-steps">
                        <li v-for="(step, index) in currentTask.steps" :key="index">{{ step }}</li>
                    </ol>
                </div>

                <div class="detail-section" v-if="currentTask.rules && currentTask.rules.length > 0">
                    <h4>任务规则</h4>
                    <ul class="task-rules">
                        <li v-for="(rule, index) in currentTask.rules" :key="index">{{ rule }}</li>
                    </ul>
                </div>

                <div class="detail-footer">
                    <el-button @click="taskDetailsVisible = false">关闭</el-button>
                    <el-button type="primary" @click="completeTask(currentTask)" :disabled="currentTask.completed">
                        {{ currentTask.completed ? '已完成' : '去完成' }}
                    </el-button>
                </div>
            </div>
        </el-dialog>
    </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
// eslint-disable-next-line no-unused-vars
import api from '@/services/api'

// 任务项组件
const TaskItem = {
    props: {
        task: {
            type: Object,
            required: true
        }
    },
    setup(props, { emit }) {
        const completeTask = () => {
            emit('complete', props.task)
        }

        const viewDetails = () => {
            emit('view-details', props.task)
        }

        return {
            completeTask,
            viewDetails
        }
    },
    template: `
    <div class="task-item">
      <div class="task-info">
        <div class="task-name">{{ task.name }}</div>
        <div class="task-description">{{ task.description }}</div>
        <div class="task-status" v-if="task.progress">
          <span class="progress-text">进度: {{ task.progress.current }}/{{ task.progress.total }}</span>
          <el-progress 
            :percentage="(task.progress.current / task.progress.total) * 100" 
            :stroke-width="5"
            :show-text="false"
          ></el-progress>
        </div>
      </div>
      <div class="task-side">
        <div class="task-points">+{{ task.points }}</div>
        <div class="task-actions">
          <el-button 
            type="text" 
            @click="viewDetails"
          >
            详情
          </el-button>
          <el-button 
            :type="task.completed ? 'success' : 'primary'" 
            :disabled="task.completed" 
            size="small"
            @click="completeTask"
          >
            {{ task.completed ? '已完成' : '去完成' }}
          </el-button>
        </div>
      </div>
    </div>
  `
}

export default {
    name: 'PointsTasksView',
    components: {
        TaskItem
    },
    setup() {
        const router = useRouter()
        const userPoints = ref(2350)
        const activeTab = ref('daily')
        const taskDetailsVisible = ref(false)
        const currentTask = ref(null)

        // 用户会员等级信息
        const userLevel = ref('白银会员')
        const levelMultiplier = ref(1.0)
        const nextLevelPoints = ref(1650)
        const levelProgress = ref(60)

        // 会员等级标签类型
        const levelTagType = computed(() => {
            const types = {
                '普通会员': '',
                '白银会员': 'info',
                '黄金会员': 'warning',
                '白金会员': 'success',
                '钻石会员': 'danger'
            }
            return types[userLevel.value] || ''
        })

        // 会员等级颜色
        const levelColor = computed(() => {
            const colors = {
                '普通会员': '#909399',
                '白银会员': '#A1A1AA',
                '黄金会员': '#F59E0B',
                '白金会员': '#10B981',
                '钻石会员': '#3B82F6'
            }
            return colors[userLevel.value] || '#909399'
        })

        // 会员等级描述
        const levelDescription = computed(() => {
            const descriptions = {
                '普通会员': '正常获取积分，有效期24个月',
                '白银会员': '正常获取积分，有效期24个月，优先办理值机手续',
                '黄金会员': '获取1.2倍积分，有效期36个月，生日双倍积分，优先值机，免费选座',
                '白金会员': '获取1.5倍积分，积分不过期，休息室使用权，优先登机，额外行李额度',
                '钻石会员': '获取2倍积分，积分不过期，全球休息室，专属值机，免费升舱机会'
            }
            return descriptions[userLevel.value] || ''
        })

        // 每日任务
        const dailyTasks = ref([
            {
                id: 1,
                name: '每日签到',
                description: '完成每日签到，连续签到获得额外奖励',
                points: 5,
                completed: false,
                type: 'daily',
                progress: {
                    current: 3,
                    total: 7
                },
                steps: [
                    '登录iFly账户',
                    '在首页或积分中心点击"每日签到"按钮'
                ],
                rules: [
                    '每自然日只能签到一次',
                    '连续7天签到可获得额外30积分奖励',
                    '连续30天签到可获得额外200积分奖励'
                ],
                route: '/check-in'
            },
            {
                id: 2,
                name: '浏览热门航线',
                description: '每日浏览热门航线信息，了解最新机票价格',
                points: 10,
                completed: false,
                type: 'daily',
                steps: [
                    '进入首页热门航线区域',
                    '浏览至少3条热门航线信息'
                ],
                rules: [
                    '每日首次完成可获得积分',
                    '需浏览至少1分钟以上'
                ],
                route: '/'
            },
            {
                id: 3,
                name: '分享航班信息',
                description: '将感兴趣的航班信息分享给好友',
                points: 15,
                completed: false,
                type: 'daily',
                steps: [
                    '查询航班信息',
                    '点击分享按钮分享给好友'
                ],
                rules: [
                    '每日最多可获得3次分享积分奖励',
                    '同一航班分享多次只计一次积分'
                ],
                route: '/flights'
            }
        ])

        // 旅行相关任务
        const travelTasks = ref([
            {
                id: 4,
                name: '航班准点起飞',
                description: '搭乘的航班准点起飞即可获得额外积分奖励',
                points: 50,
                completed: false,
                type: 'travel',
                rules: [
                    '航班须在预定起飞时间15分钟内起飞',
                    '积分将在航班完成后3个工作日内自动发放',
                    '需使用会员账号预订机票'
                ],
                route: '/flights'
            },
            {
                id: 5,
                name: '行程评价',
                description: '对已完成的航班旅程进行评价反馈',
                points: 100,
                completed: false,
                type: 'travel',
                steps: [
                    '进入"我的订单"',
                    '找到已完成的航班',
                    '点击"评价"按钮',
                    '填写航班体验评价（不少于50字）'
                ],
                rules: [
                    '每个航班只能评价一次',
                    '评价需包含实质性内容',
                    '积分将在评价审核通过后发放'
                ],
                route: '/orders'
            },
            {
                id: 6,
                name: '上传登机牌',
                description: '上传本次旅行的登机牌照片',
                points: 30,
                completed: false,
                type: 'travel',
                steps: [
                    '进入"我的订单"',
                    '找到相应航班',
                    '点击"上传登机牌"',
                    '拍照或选择登机牌照片上传'
                ],
                rules: [
                    '需上传清晰完整的登机牌照片',
                    '每个航班只能获得一次积分奖励',
                    '登机牌信息需与订单信息一致'
                ],
                route: '/orders'
            }
        ])

        // 账户相关任务
        const accountTasks = ref([
            {
                id: 7,
                name: '完善个人信息',
                description: '完善个人基本资料获得积分奖励',
                points: 200,
                completed: true,
                type: 'account',
                steps: [
                    '进入"个人中心"',
                    '点击"编辑个人资料"',
                    '完善所有必填信息',
                    '点击"保存"'
                ],
                rules: [
                    '需完成所有必填项',
                    '每个账户仅首次完善可获得积分'
                ],
                route: '/profile'
            },
            {
                id: 8,
                name: '绑定手机号',
                description: '绑定手机号增强账户安全性',
                points: 100,
                completed: false,
                type: 'account',
                steps: [
                    '进入"账户安全"页面',
                    '点击"绑定手机号"',
                    '输入手机号并完成验证'
                ],
                rules: [
                    '每个账户仅首次绑定可获得积分',
                    '需通过验证码验证'
                ],
                route: '/profile/security'
            },
            {
                id: 9,
                name: '设置常用联系人',
                description: '添加至少一位常用联系人',
                points: 50,
                completed: false,
                type: 'account',
                steps: [
                    '进入"常用联系人"页面',
                    '点击"添加联系人"',
                    '填写联系人信息',
                    '点击"保存"'
                ],
                rules: [
                    '联系人信息需真实有效',
                    '至少需添加一位联系人才可获得积分'
                ],
                route: '/contacts'
            },
            {
                id: 10,
                name: '完成实名认证',
                description: '完成账户实名认证，享受更多权益',
                points: 300,
                completed: false,
                type: 'account',
                steps: [
                    '进入"账户安全"页面',
                    '点击"实名认证"',
                    '上传身份证正反面照片',
                    '填写身份证信息',
                    '完成人脸识别验证'
                ],
                rules: [
                    '需上传清晰的身份证照片',
                    '填写的信息需与身份证信息一致',
                    '通过人脸识别验证'
                ],
                route: '/profile/security'
            }
        ])

        // 首次体验任务
        const firstTimeTasks = ref([
            {
                id: 11,
                name: '首次购票',
                description: '首次在iFly预订机票',
                points: 500,
                completed: true,
                type: 'first',
                steps: [
                    '搜索航班',
                    '选择适合的航班',
                    '完成预订并支付'
                ],
                rules: [
                    '账户首次成功预订并支付机票可获得积分',
                    '积分将在支付成功后自动发放'
                ],
                route: '/flights'
            },
            {
                id: 12,
                name: '首次使用在线值机',
                description: '首次使用iFly在线值机服务',
                points: 150,
                completed: false,
                type: 'first',
                steps: [
                    '在航班起飞前24小时内',
                    '进入"在线值机"页面',
                    '选择航班并完成值机'
                ],
                rules: [
                    '账户首次成功使用在线值机服务可获得积分',
                    '需使用会员账号预订的机票'
                ],
                route: '/online-check-in'
            },
            {
                id: 13,
                name: '首次使用App',
                description: '下载并登录iFly移动App',
                points: 200,
                completed: false,
                type: 'first',
                steps: [
                    '扫描二维码下载App',
                    '安装并打开App',
                    '使用会员账号登录'
                ],
                rules: [
                    '账户首次在移动App上登录可获得积分',
                    'App登录需使用与网页端相同的账户'
                ],
                route: '/download'
            },
            {
                id: 14,
                name: '首次参与问卷调查',
                description: '参与iFly用户体验问卷调查',
                points: 100,
                completed: false,
                type: 'first',
                steps: [
                    '进入"用户调查"页面',
                    '选择问卷并填写',
                    '提交完整问卷'
                ],
                rules: [
                    '需完成所有问题',
                    '回答需真实有效',
                    '每次调查最多获得一次积分奖励'
                ],
                route: '/survey'
            }
        ])

        // 积分获取渠道
        const pointChannels = ref([
            {
                id: 1,
                name: '购买机票',
                points: '1积分/1元',
                description: '购买iFly航空机票，每消费1元获得1积分。',
                actionType: 'booking',
                actionText: '预订机票',
                route: '/flights'
            },
            {
                id: 2,
                name: '会员等级积分加速',
                points: '最高2倍',
                description: '根据会员等级获得不同倍率的积分加速，钻石会员可享受2倍积分。',
                actionType: 'level',
                actionText: '查看会员等级',
                route: '/member-benefits'
            },
            {
                id: 3,
                name: '里程兑换积分',
                points: '1000里程=300积分',
                description: '将飞行里程兑换为积分，需在"会员中心"操作。',
                actionType: 'exchange',
                actionText: '兑换积分',
                route: '/points/exchange'
            },
            {
                id: 4,
                name: '参与活动',
                points: '不定额',
                description: '参与iFly官方活动可获得额外积分奖励。',
                actionType: 'promotion',
                actionText: '查看活动',
                route: '/promotions'
            }
        ])

        // 获取用户积分和等级信息
        const fetchUserPointsInfo = () => {
            // 实际项目中应该从API获取用户积分和等级信息
            // try {
            //   const result = await api.points.getUserInfo()
            //   userPoints.value = result.available
            //   userLevel.value = result.level
            //   levelMultiplier.value = result.multiplier
            //   nextLevelPoints.value = result.nextLevelPoints
            //   levelProgress.value = result.levelProgress
            // } catch (error) {
            //   console.error('获取用户积分信息失败:', error)
            //   ElMessage.error('获取用户积分信息失败')
            // }
        }

        // 获取任务列表
        const fetchTasks = () => {
            // 实际项目中应该从API获取任务列表
            // try {
            //   const result = await api.points.getTasks()
            //   dailyTasks.value = result.dailyTasks
            //   travelTasks.value = result.travelTasks
            //   accountTasks.value = result.accountTasks
            //   firstTimeTasks.value = result.firstTimeTasks
            // } catch (error) {
            //   console.error('获取任务列表失败:', error)
            //   ElMessage.error('获取任务列表失败')
            // }
        }

        // 完成任务
        const completeTask = (task) => {
            if (task.completed) return

            // 跳转到对应的任务页面
            if (task.route) {
                router.push(task.route)
            } else {
                // 实际项目中应该调用API完成任务
                // try {
                //   await api.points.completeTask(task.id)
                //   
                //   // 更新任务状态
                //   const updateTask = (taskList) => {
                //     const index = taskList.value.findIndex(t => t.id === task.id)
                //     if (index !== -1) {
                //       taskList.value[index].completed = true
                //     }
                //   }
                //   
                //   updateTask(dailyTasks)
                //   updateTask(travelTasks)
                //   updateTask(accountTasks)
                //   updateTask(firstTimeTasks)
                //   
                //   // 获取最新的积分信息
                //   fetchUserPointsInfo()
                //   
                //   ElMessage.success(`恭喜您完成任务，获得${task.points}积分！`)
                // } catch (error) {
                //   console.error('完成任务失败:', error)
                //   ElMessage.error('完成任务失败，请稍后再试')
                // }

                // 模拟任务完成
                ElMessage.success(`即将前往完成任务，可获得${task.points}积分！`)
            }
        }

        // 查看任务详情
        const viewTaskDetails = (task) => {
            currentTask.value = task
            taskDetailsVisible.value = true
        }

        // 积分获取渠道跳转
        const goToChannelAction = (channel) => {
            if (channel.route) {
                router.push(channel.route)
            }
        }

        // 返回积分中心
        const goBack = () => {
            router.push('/points')
        }

        // 查看积分明细
        const goToHistory = () => {
            router.push('/points/history')
        }

        onMounted(() => {
            fetchUserPointsInfo()
            fetchTasks()
        })

        return {
            userPoints,
            activeTab,
            dailyTasks,
            travelTasks,
            accountTasks,
            firstTimeTasks,
            pointChannels,
            taskDetailsVisible,
            currentTask,
            userLevel,
            levelMultiplier,
            nextLevelPoints,
            levelProgress,
            levelTagType,
            levelColor,
            levelDescription,
            completeTask,
            viewTaskDetails,
            goToChannelAction,
            goBack,
            goToHistory
        }
    }
}
</script>

<style scoped>
.points-tasks {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

.page-header {
    margin-bottom: 20px;
}

.points-balance {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 30px;
    padding: 15px 20px;
    background-color: #f5f7fa;
    border-radius: 8px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
}

.balance-info {
    font-size: 16px;
    color: #606266;
}

.balance-value {
    font-size: 24px;
    font-weight: bold;
    color: #409EFF;
    margin-left: 5px;
}

.tasks-container {
    margin-bottom: 40px;
}

.tasks-group {
    margin-bottom: 30px;
}

.tasks-group-title {
    display: flex;
    align-items: center;
    margin-bottom: 15px;
    font-size: 18px;
    color: #303133;
}

.tasks-desc {
    margin-left: 10px;
    font-size: 14px;
    color: #909399;
    font-weight: normal;
}

.task-card {
    margin-bottom: 15px;
}

/* TaskItem组件样式 */
.task-item {
    display: flex;
    justify-content: space-between;
}

.task-info {
    flex: 1;
    margin-right: 20px;
}

.task-name {
    font-size: 16px;
    font-weight: bold;
    color: #303133;
    margin-bottom: 8px;
}

.task-description {
    font-size: 14px;
    color: #606266;
    margin-bottom: 10px;
}

.task-status {
    margin-top: 10px;
}

.progress-text {
    font-size: 12px;
    color: #909399;
    margin-bottom: 5px;
    display: inline-block;
}

.task-side {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    justify-content: space-between;
}

.task-points {
    font-size: 18px;
    font-weight: bold;
    color: #E6A23C;
    margin-bottom: 15px;
}

.task-actions {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 5px;
}

/* 信息卡片样式 */
.info-card {
    margin-bottom: 15px;
}

/* 积分倍率信息 */
.multiplier-info {
    padding: 10px;
}

.user-level-info {
    display: flex;
    align-items: center;
    margin-bottom: 15px;
}

.multiplier {
    font-size: 18px;
    font-weight: bold;
    margin-left: 15px;
    color: #E6A23C;
}

.level-description {
    color: #606266;
    margin-bottom: 20px;
    font-size: 14px;
}

.level-upgrade {
    margin-top: 15px;
}

.level-upgrade p {
    font-size: 14px;
    color: #606266;
    margin-bottom: 10px;
}

/* 积分获取渠道 */
.channel-info {
    padding: 10px;
}

.channel-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
}

.channel-title {
    font-size: 16px;
    font-weight: bold;
    color: #303133;
}

.channel-points {
    font-size: 16px;
    font-weight: bold;
    color: #E6A23C;
}

.channel-desc {
    font-size: 14px;
    color: #606266;
    margin-bottom: 15px;
}

.channel-actions {
    display: flex;
    justify-content: flex-end;
}

/* 任务详情对话框 */
.detail-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}

.detail-points {
    font-size: 20px;
    font-weight: bold;
    color: #E6A23C;
}

.detail-section {
    margin-bottom: 20px;
}

.detail-section h4 {
    font-size: 16px;
    margin-bottom: 10px;
    color: #303133;
}

.detail-section p {
    color: #606266;
    line-height: 1.6;
}

.task-steps,
.task-rules {
    padding-left: 20px;
    margin: 10px 0;
    color: #606266;
    line-height: 1.8;
}

.detail-footer {
    margin-top: 20px;
    display: flex;
    justify-content: flex-end;
    gap: 10px;
}

@media (max-width: 768px) {
    .task-item {
        flex-direction: column;
    }

    .task-info {
        margin-right: 0;
        margin-bottom: 15px;
    }

    .task-side {
        flex-direction: row;
        align-items: center;
        justify-content: space-between;
    }

    .task-points {
        margin-bottom: 0;
    }

    .user-level-info {
        flex-direction: column;
        align-items: flex-start;
    }

    .multiplier {
        margin-left: 0;
        margin-top: 10px;
    }

    .channel-header {
        flex-direction: column;
        align-items: flex-start;
    }

    .channel-points {
        margin-top: 5px;
    }
}
</style>