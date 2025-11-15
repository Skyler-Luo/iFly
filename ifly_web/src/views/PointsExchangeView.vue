<template>
    <div class="points-exchange">
        <div class="page-header">
            <el-page-header @back="goBack" content="积分兑换商城"></el-page-header>
        </div>

        <div class="points-balance">
            <div class="balance-info">
                <span>当前可用积分：</span>
                <span class="balance-value">{{ userPoints }}</span>
            </div>
            <el-button @click="goToHistory" size="small">查看积分明细</el-button>
        </div>

        <div class="exchange-filter">
            <el-tabs v-model="activeCategory" @tab-click="handleCategoryChange">
                <el-tab-pane v-for="category in categories" :key="category.value" :label="category.label"
                    :name="category.value">
                </el-tab-pane>
            </el-tabs>

            <div class="filter-actions">
                <el-select v-model="sortBy" placeholder="排序方式" size="large">
                    <el-option label="默认排序" value="default"></el-option>
                    <el-option label="积分从低到高" value="points-asc"></el-option>
                    <el-option label="积分从高到低" value="points-desc"></el-option>
                    <el-option label="热门优先" value="popularity"></el-option>
                    <el-option label="最新上架" value="newest"></el-option>
                </el-select>
            </div>
        </div>

        <div v-loading="loading" class="exchange-content">
            <el-empty v-if="filteredItems.length === 0" description="暂无符合条件的兑换商品"></el-empty>

            <el-row v-else :gutter="20">
                <el-col v-for="item in filteredItems" :key="item.id" :xs="24" :sm="12" :md="8" :lg="6">
                    <el-card class="exchange-card" shadow="hover">
                        <div class="card-img">
                            <img :src="item.image" :alt="item.name">
                            <div v-if="item.isHot" class="hot-tag">热门</div>
                            <div v-if="item.isNew" class="new-tag">新品</div>
                            <div v-if="item.isLimited" class="limited-tag">限量</div>
                        </div>
                        <div class="card-content">
                            <h3 class="card-title">{{ item.name }}</h3>
                            <div class="card-desc">{{ item.description }}</div>
                            <div class="card-points">{{ item.points }} 积分</div>
                            <div class="card-actions">
                                <el-button type="primary" :disabled="userPoints < item.points"
                                    @click="openExchangeDialog(item)">
                                    立即兑换
                                </el-button>
                            </div>
                            <div v-if="item.stock !== null" class="card-stock"
                                :class="{ 'low-stock': item.stock < 10 }">
                                库存: {{ item.stock }}
                            </div>
                        </div>
                    </el-card>
                </el-col>
            </el-row>
        </div>

        <div class="pagination-container" v-if="totalItems > pageSize">
            <el-pagination v-model:current-page="currentPage" v-model:page-size="pageSize"
                :page-sizes="[12, 24, 48, 96]" :layout="'total, sizes, prev, pager, next, jumper'" :total="totalItems"
                @size-change="handleSizeChange" @current-change="handleCurrentChange" />
        </div>

        <!-- 兑换确认对话框 -->
        <el-dialog v-model="confirmDialogVisible" :title="currentItem?.name" width="600px">
            <div v-if="currentItem" class="exchange-dialog-content">
                <img :src="currentItem.image" class="dialog-image">
                <div class="dialog-info">
                    <div class="dialog-points">
                        所需积分：<span class="point-value">{{ currentItem.points }}</span>
                    </div>

                    <div class="dialog-balance">
                        兑换后剩余：<span class="balance-value">{{ userPoints - currentItem.points }}</span>
                    </div>

                    <div v-if="currentItem.rules && currentItem.rules.length > 0" class="dialog-rules">
                        <h4>兑换规则</h4>
                        <ul>
                            <li v-for="(rule, index) in currentItem.rules" :key="index">{{ rule }}</li>
                        </ul>
                    </div>

                    <template v-if="currentItem.needsAddress">
                        <h4>收货信息</h4>
                        <el-form ref="addressForm" :model="addressForm" :rules="addressRules" label-width="80px"
                            class="address-form">
                            <el-form-item label="收货人" prop="name">
                                <el-input v-model="addressForm.name" />
                            </el-form-item>

                            <el-form-item label="手机号" prop="phone">
                                <el-input v-model="addressForm.phone" />
                            </el-form-item>

                            <el-form-item label="详细地址" prop="address">
                                <el-input v-model="addressForm.address" type="textarea" :rows="2" />
                            </el-form-item>
                        </el-form>
                    </template>

                    <template v-if="currentItem.type === 'coupon'">
                        <h4>使用说明</h4>
                        <p class="coupon-tips">兑换成功后，优惠券将自动添加到您的账户中，预订机票时可直接使用。</p>
                    </template>

                    <div class="dialog-actions">
                        <el-button @click="confirmDialogVisible = false">取消</el-button>
                        <el-button type="primary" :disabled="userPoints < currentItem.points" @click="confirmExchange"
                            :loading="exchangeLoading">
                            确认兑换
                        </el-button>
                    </div>

                    <div v-if="userPoints < currentItem.points" class="points-not-enough">
                        <el-alert title="积分不足" type="warning" :closable="false" show-icon>
                            您的积分不足，还差 {{ currentItem.points - userPoints }} 积分
                        </el-alert>
                    </div>
                </div>
            </div>
        </el-dialog>

        <!-- 兑换成功对话框 -->
        <el-dialog v-model="successDialogVisible" title="兑换成功" width="400px" :show-close="false"
            :close-on-click-modal="false" :close-on-press-escape="false">
            <div class="success-dialog-content">
                <el-icon class="success-icon">
                    <CircleCheck />
                </el-icon>
                <h3 class="success-title">恭喜，兑换成功！</h3>
                <p class="success-message">{{ successMessage }}</p>

                <div class="success-actions">
                    <el-button @click="goToHistory">查看积分明细</el-button>
                    <el-button type="primary" @click="closeSuccessDialog">确定</el-button>
                </div>
            </div>
        </el-dialog>
    </div>
</template>

<script>
import { ref, computed, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { CircleCheck } from '@element-plus/icons-vue'
// eslint-disable-next-line no-unused-vars
import api from '@/services/api'

export default {
    name: 'PointsExchangeView',
    components: {
        CircleCheck
    },
    setup() {
        const router = useRouter()
        const loading = ref(false)
        const userPoints = ref(2350)
        const activeCategory = ref('all')
        const sortBy = ref('default')
        const currentPage = ref(1)
        const pageSize = ref(12)
        const confirmDialogVisible = ref(false)
        const successDialogVisible = ref(false)
        const currentItem = ref(null)
        const exchangeLoading = ref(false)
        const successMessage = ref('')

        // 表单相关
        const addressForm = reactive({
            name: '',
            phone: '',
            address: ''
        })

        const addressRules = {
            name: [
                { required: true, message: '请输入收货人姓名', trigger: 'blur' },
                { min: 2, max: 20, message: '长度在 2 到 20 个字符', trigger: 'blur' }
            ],
            phone: [
                { required: true, message: '请输入手机号码', trigger: 'blur' },
                { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码', trigger: 'blur' }
            ],
            address: [
                { required: true, message: '请输入详细地址', trigger: 'blur' },
                { min: 5, max: 100, message: '长度在 5 到 100 个字符', trigger: 'blur' }
            ]
        }

        // 商品分类
        const categories = [
            { value: 'all', label: '全部商品' },
            { value: 'flight', label: '航班服务' },
            { value: 'lounge', label: '贵宾休息室' },
            { value: 'coupon', label: '优惠券' },
            { value: 'baggage', label: '行李礼遇' },
            { value: 'goods', label: '实物礼品' }
        ]

        // 兑换商品数据
        const exchangeItems = ref([
            {
                id: 1,
                name: '经济舱升级商务舱',
                description: '使用积分将您的经济舱机票升级为商务舱，享受更舒适的旅行体验。',
                points: 2000,
                image: 'https://picsum.photos/id/250/600/400',
                category: 'flight',
                isHot: true,
                isNew: false,
                isLimited: false,
                stock: null,
                type: 'upgrade',
                needsAddress: false,
                rules: [
                    '仅适用于iFly航空运营的航班',
                    '升舱需提前至少24小时申请',
                    '升舱需视座位情况而定',
                    '每次升舱仅适用于单程航班'
                ]
            },
            {
                id: 2,
                name: '额外行李额10kg',
                description: '用积分兑换额外的托运行李额度，增加10公斤的行李额。',
                points: 1000,
                image: 'https://picsum.photos/id/46/600/400',
                category: 'baggage',
                isHot: false,
                isNew: false,
                isLimited: false,
                stock: null,
                type: 'baggage',
                needsAddress: false,
                rules: [
                    '需提前至少48小时申请',
                    '仅适用于iFly航空运营的航班',
                    '不可与其他行李额度优惠同时使用'
                ]
            },
            {
                id: 3,
                name: '国内机场贵宾休息室',
                description: '兑换国内机场贵宾休息室使用权，享受候机时的优质服务与舒适环境。',
                points: 1500,
                image: 'https://picsum.photos/id/390/600/400',
                category: 'lounge',
                isHot: true,
                isNew: false,
                isLimited: false,
                stock: null,
                type: 'lounge',
                needsAddress: false,
                rules: [
                    '可在国内指定机场的合作贵宾休息室使用',
                    '休息时间不超过3小时',
                    '需提前至少12小时预约'
                ]
            },
            {
                id: 4,
                name: '100元机票优惠券',
                description: '兑换100元机票优惠券，可直接抵扣机票金额。',
                points: 800,
                image: 'https://picsum.photos/id/36/600/400',
                category: 'coupon',
                isHot: false,
                isNew: false,
                isLimited: false,
                stock: null,
                type: 'coupon',
                needsAddress: false,
                rules: [
                    '单笔订单满500元可用',
                    '有效期为兑换后60天',
                    '不可与其他优惠券叠加使用'
                ]
            },
            {
                id: 5,
                name: '国际机场贵宾休息室',
                description: '兑换国际机场贵宾休息室使用权，享受候机时的优质服务与舒适环境。',
                points: 2500,
                image: 'https://picsum.photos/id/380/600/400',
                category: 'lounge',
                isHot: false,
                isNew: true,
                isLimited: false,
                stock: null,
                type: 'lounge',
                needsAddress: false,
                rules: [
                    '可在国际指定机场的合作贵宾休息室使用',
                    '休息时间不超过4小时',
                    '需提前至少24小时预约',
                    '每年最多可兑换4次'
                ]
            },
            {
                id: 6,
                name: '机场接送机服务',
                description: '享受从家到机场或从机场到目的地的专车接送服务。',
                points: 3000,
                image: 'https://picsum.photos/id/183/600/400',
                category: 'flight',
                isHot: true,
                isNew: false,
                isLimited: false,
                stock: null,
                type: 'service',
                needsAddress: false,
                rules: [
                    '单程30公里内免费，超出部分需额外付费',
                    '需提前至少24小时预约',
                    '接送服务仅限国内主要城市'
                ]
            },
            {
                id: 7,
                name: '便携式旅行箱',
                description: '时尚轻便的20寸旅行箱，是您短途旅行的理想伴侣。',
                points: 5000,
                image: 'https://picsum.photos/id/96/600/400',
                category: 'goods',
                isHot: false,
                isNew: true,
                isLimited: true,
                stock: 15,
                type: 'goods',
                needsAddress: true,
                rules: [
                    '限量供应，先兑先得',
                    '颜色随机，不支持指定',
                    '预计发货时间为兑换后7个工作日内'
                ]
            },
            {
                id: 8,
                name: '旅行颈枕套装',
                description: '舒适的记忆棉颈枕搭配眼罩和耳塞，让您的旅途更加舒适。',
                points: 2000,
                image: 'https://picsum.photos/id/131/600/400',
                category: 'goods',
                isHot: false,
                isNew: false,
                isLimited: false,
                stock: 50,
                type: 'goods',
                needsAddress: true,
                rules: [
                    '颜色随机，不支持指定',
                    '预计发货时间为兑换后5个工作日内'
                ]
            },
            {
                id: 9,
                name: '手提行李免费托运',
                description: '将一件手提行李额外免费托运，不占用您的普通托运行李额度。',
                points: 500,
                image: 'https://picsum.photos/id/152/600/400',
                category: 'baggage',
                isHot: false,
                isNew: false,
                isLimited: false,
                stock: null,
                type: 'baggage',
                needsAddress: false,
                rules: [
                    '手提行李重量不超过10kg',
                    '尺寸需符合航空公司规定的手提行李标准',
                    '需提前至少12小时申请'
                ]
            },
            {
                id: 10,
                name: '200元机票优惠券',
                description: '兑换200元机票优惠券，可直接抵扣机票金额。',
                points: 1600,
                image: 'https://picsum.photos/id/40/600/400',
                category: 'coupon',
                isHot: true,
                isNew: false,
                isLimited: false,
                stock: null,
                type: 'coupon',
                needsAddress: false,
                rules: [
                    '单笔订单满1000元可用',
                    '有效期为兑换后60天',
                    '不可与其他优惠券叠加使用'
                ]
            },
            {
                id: 11,
                name: '商务头等舱优先登机',
                description: '享受与商务舱、头等舱旅客一同优先登机的特权。',
                points: 800,
                image: 'https://picsum.photos/id/316/600/400',
                category: 'flight',
                isHot: false,
                isNew: true,
                isLimited: false,
                stock: null,
                type: 'service',
                needsAddress: false,
                rules: [
                    '仅适用于iFly航空运营的航班',
                    '需提前至少6小时申请',
                    '每次仅对应单次航班'
                ]
            },
            {
                id: 12,
                name: '50元机场餐饮券',
                description: '可在指定机场餐饮店使用的代金券，让您的候机时光更加愉悦。',
                points: 400,
                image: 'https://picsum.photos/id/292/600/400',
                category: 'coupon',
                isHot: false,
                isNew: false,
                isLimited: false,
                stock: null,
                type: 'coupon',
                needsAddress: false,
                rules: [
                    '可在指定机场的合作餐饮店使用',
                    '有效期为兑换后30天',
                    '不设最低消费限制',
                    '不可兑换现金，不设找零'
                ]
            }
        ])

        // 根据筛选条件过滤商品
        const filteredItems = computed(() => {
            let result = [...exchangeItems.value]

            // 按分类筛选
            if (activeCategory.value !== 'all') {
                result = result.filter(item => item.category === activeCategory.value)
            }

            // 按排序条件排序
            switch (sortBy.value) {
                case 'points-asc':
                    result.sort((a, b) => a.points - b.points)
                    break
                case 'points-desc':
                    result.sort((a, b) => b.points - a.points)
                    break
                case 'popularity':
                    result.sort((a, b) => {
                        if (a.isHot && !b.isHot) return -1
                        if (!a.isHot && b.isHot) return 1
                        return 0
                    })
                    break
                case 'newest':
                    result.sort((a, b) => {
                        if (a.isNew && !b.isNew) return -1
                        if (!a.isNew && b.isNew) return 1
                        return 0
                    })
                    break
                default:
                    // 默认排序，热门和新品靠前
                    result.sort((a, b) => {
                        if (a.isHot && !b.isHot) return -1
                        if (!a.isHot && b.isHot) return 1
                        if (a.isNew && !b.isNew) return -1
                        if (!a.isNew && b.isNew) return 1
                        return 0
                    })
            }

            // 计算分页
            const startIndex = (currentPage.value - 1) * pageSize.value
            const endIndex = startIndex + pageSize.value

            return result.slice(startIndex, endIndex)
        })

        const totalItems = computed(() => {
            if (activeCategory.value === 'all') {
                return exchangeItems.value.length
            } else {
                return exchangeItems.value.filter(item => item.category === activeCategory.value).length
            }
        })

        // 处理分类变更
        const handleCategoryChange = () => {
            currentPage.value = 1
            fetchExchangeItems()
        }

        // 处理每页显示数量变化
        const handleSizeChange = (size) => {
            pageSize.value = size
            fetchExchangeItems()
        }

        // 处理页码变化
        const handleCurrentChange = (page) => {
            currentPage.value = page
        }

        // 获取兑换商品列表
        const fetchExchangeItems = () => {
            loading.value = true

            // 模拟API请求延迟
            setTimeout(() => {
                // 实际项目中应该从API获取数据
                // try {
                //   const params = {
                //     category: activeCategory.value,
                //     sortBy: sortBy.value,
                //     page: currentPage.value,
                //     pageSize: pageSize.value
                //   }
                //   const result = await api.points.getExchangeItems(params)
                //   exchangeItems.value = result.items
                //   totalItems.value = result.total
                // } catch (error) {
                //   console.error('获取兑换商品失败:', error)
                //   ElMessage.error('获取兑换商品失败')
                // }

                loading.value = false
            }, 500)
        }

        // 打开兑换确认对话框
        const openExchangeDialog = (item) => {
            currentItem.value = item
            confirmDialogVisible.value = true

            // 重置地址表单
            if (item.needsAddress) {
                addressForm.name = ''
                addressForm.phone = ''
                addressForm.address = ''
            }
        }

        // 确认兑换
        const confirmExchange = async () => {
            // 检查积分是否足够
            if (userPoints.value < currentItem.value.points) {
                ElMessage.warning('积分不足，无法兑换')
                return
            }

            // 如果需要地址，检查地址表单
            if (currentItem.value.needsAddress) {
                const addressFormEl = document.querySelector('.address-form')
                if (!addressFormEl) return

                // 验证表单
                const valid = await new Promise(resolve => {
                    const formRef = addressFormEl.__vueParentComponent.proxy.$refs.addressForm
                    formRef.validate((valid) => {
                        resolve(valid)
                    })
                })

                if (!valid) {
                    ElMessage.warning('请正确填写收货信息')
                    return
                }
            }

            // 设置加载状态
            exchangeLoading.value = true

            // 模拟API请求
            setTimeout(() => {
                // 实际项目中应该调用API进行兑换
                // try {
                //   const params = {
                //     itemId: currentItem.value.id,
                //     address: currentItem.value.needsAddress ? addressForm : null
                //   }
                //   await api.points.exchange(params)
                //   
                //   // 更新用户积分
                //   userPoints.value -= currentItem.value.points
                //   
                //   // 显示成功对话框
                //   confirmDialogVisible.value = false
                //   
                //   // 根据不同商品类型设置成功消息
                //   setSuccessMessage(currentItem.value)
                //   
                //   successDialogVisible.value = true
                // } catch (error) {
                //   console.error('兑换失败:', error)
                //   ElMessage.error('兑换失败，请稍后重试')
                // }

                // 模拟兑换成功
                userPoints.value -= currentItem.value.points

                // 显示成功对话框
                confirmDialogVisible.value = false

                // 根据不同商品类型设置成功消息
                setSuccessMessage(currentItem.value)

                successDialogVisible.value = true
                exchangeLoading.value = false
            }, 1500)
        }

        // 设置成功消息
        const setSuccessMessage = (item) => {
            if (item.type === 'coupon') {
                successMessage.value = '优惠券已添加到您的账户，可在订单预订时直接使用。'
            } else if (item.type === 'goods') {
                successMessage.value = '实物礼品将在7个工作日内发出，请保持联系方式畅通。'
            } else if (item.type === 'lounge') {
                successMessage.value = '休息室使用权已添加到您的账户，请在使用前24小时进行预约。'
            } else if (item.type === 'upgrade') {
                successMessage.value = '升舱权益已添加到您的账户，可在订单管理中使用。'
            } else if (item.type === 'baggage') {
                successMessage.value = '额外行李权益已添加到您的账户，可在值机时直接使用。'
            } else {
                successMessage.value = '兑换成功！感谢您使用iFly会员积分服务。'
            }
        }

        // 关闭成功对话框
        const closeSuccessDialog = () => {
            successDialogVisible.value = false
            fetchExchangeItems() // 刷新商品列表
        }

        // 返回积分中心
        const goBack = () => {
            router.push('/points')
        }

        // 查看积分明细
        const goToHistory = () => {
            router.push('/points/history')
        }

        // 在组件挂载时获取积分信息和商品列表
        onMounted(() => {
            // 获取用户积分
            // async function fetchUserPoints() {
            //   try {
            //     const result = await api.points.getUserPoints()
            //     userPoints.value = result.available
            //   } catch (error) {
            //     console.error('获取用户积分失败:', error)
            //     ElMessage.error('获取用户积分失败')
            //   }
            // }

            // fetchUserPoints()
            fetchExchangeItems()
        })

        return {
            userPoints,
            activeCategory,
            categories,
            sortBy,
            loading,
            currentPage,
            pageSize,
            totalItems,
            filteredItems,
            confirmDialogVisible,
            successDialogVisible,
            currentItem,
            addressForm,
            addressRules,
            exchangeLoading,
            successMessage,
            handleCategoryChange,
            handleSizeChange,
            handleCurrentChange,
            openExchangeDialog,
            confirmExchange,
            goBack,
            goToHistory,
            closeSuccessDialog
        }
    }
}
</script>

<style scoped>
.points-exchange {
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

.exchange-filter {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 20px;
}

.filter-actions {
    display: flex;
    align-items: center;
}

.exchange-content {
    min-height: 400px;
}

.exchange-card {
    height: 100%;
    margin-bottom: 20px;
    transition: transform 0.3s, box-shadow 0.3s;
    overflow: hidden;
}

.exchange-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 15px 30px rgba(0, 0, 0, 0.1);
}

.card-img {
    position: relative;
    height: 200px;
    overflow: hidden;
}

.card-img img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform 0.5s;
}

.exchange-card:hover .card-img img {
    transform: scale(1.1);
}

.hot-tag,
.new-tag,
.limited-tag {
    position: absolute;
    top: 10px;
    right: 10px;
    padding: 5px 10px;
    color: white;
    border-radius: 4px;
    font-size: 12px;
    font-weight: bold;
    z-index: 1;
}

.hot-tag {
    background-color: #F56C6C;
}

.new-tag {
    background-color: #67C23A;
}

.limited-tag {
    background-color: #E6A23C;
}

.card-content {
    padding: 15px;
    position: relative;
}

.card-title {
    font-size: 16px;
    margin: 0 0 10px;
    color: #303133;
    font-weight: bold;
}

.card-desc {
    font-size: 14px;
    color: #606266;
    margin-bottom: 15px;
    height: 40px;
    overflow: hidden;
    text-overflow: ellipsis;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
}

.card-points {
    font-size: 18px;
    color: #E6A23C;
    font-weight: bold;
    margin-bottom: 15px;
}

.card-actions {
    text-align: center;
}

.card-stock {
    margin-top: 10px;
    font-size: 12px;
    color: #909399;
    text-align: right;
}

.low-stock {
    color: #F56C6C;
}

.pagination-container {
    margin-top: 30px;
    display: flex;
    justify-content: center;
}

/* 对话框样式 */
.exchange-dialog-content {
    display: flex;
    flex-direction: column;
}

.dialog-image {
    width: 100%;
    max-height: 250px;
    object-fit: cover;
    border-radius: 8px;
    margin-bottom: 20px;
}

.dialog-points,
.dialog-balance {
    font-size: 16px;
    margin-bottom: 15px;
    color: #606266;
}

.point-value {
    font-size: 20px;
    font-weight: bold;
    color: #E6A23C;
}

.balance-value {
    font-size: 20px;
    font-weight: bold;
    color: #409EFF;
}

.dialog-rules {
    margin-bottom: 20px;
}

.dialog-rules h4,
.dialog-info h4 {
    font-size: 16px;
    margin: 15px 0 10px;
    color: #303133;
}

.dialog-rules ul {
    padding-left: 20px;
    margin: 10px 0;
    color: #606266;
}

.dialog-rules li {
    margin-bottom: 8px;
}

.address-form {
    margin-top: 15px;
}

.coupon-tips {
    color: #606266;
    line-height: 1.6;
    margin-top: 5px;
}

.dialog-actions {
    margin-top: 20px;
    display: flex;
    justify-content: flex-end;
    gap: 10px;
}

.points-not-enough {
    margin-top: 15px;
}

/* 成功对话框样式 */
.success-dialog-content {
    text-align: center;
    padding: 20px 0;
}

.success-icon {
    font-size: 60px;
    color: #67C23A;
    margin-bottom: 20px;
}

.success-title {
    font-size: 20px;
    margin: 0 0 15px;
    color: #303133;
}

.success-message {
    color: #606266;
    margin-bottom: 20px;
}

.success-actions {
    display: flex;
    justify-content: center;
    gap: 15px;
}

@media (min-width: 768px) {
    .exchange-dialog-content {
        flex-direction: row;
    }

    .dialog-image {
        width: 40%;
        max-height: 300px;
        margin-right: 20px;
        margin-bottom: 0;
    }

    .dialog-info {
        flex: 1;
    }
}

@media (max-width: 767px) {
    .exchange-filter {
        flex-direction: column;
        align-items: stretch;
    }

    .filter-actions {
        margin-top: 15px;
        justify-content: flex-end;
    }
}
</style>