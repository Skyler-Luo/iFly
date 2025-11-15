<template>
    <div class="promotion-center">
        <div class="page-header">
            <h1>优惠活动中心</h1>
            <p>发现更多专属优惠，为您的旅行省钱</p>
        </div>

        <!-- 活动分类导航 -->
        <div class="category-nav">
            <el-tabs v-model="activeCategory" @tab-click="handleCategoryChange">
                <el-tab-pane label="全部活动" name="all"></el-tab-pane>
                <el-tab-pane label="限时特惠" name="limited"></el-tab-pane>
                <el-tab-pane label="会员专享" name="member"></el-tab-pane>
                <el-tab-pane label="航线优惠" name="routes"></el-tab-pane>
                <el-tab-pane label="积分兑换" name="points"></el-tab-pane>
            </el-tabs>
        </div>

        <!-- 活动筛选器 -->
        <div class="filter-bar">
            <el-select v-model="sortBy" placeholder="排序方式" size="small">
                <el-option label="最新发布" value="newest"></el-option>
                <el-option label="即将结束" value="ending-soon"></el-option>
                <el-option label="折扣力度" value="discount"></el-option>
            </el-select>
        </div>

        <!-- 加载状态显示 -->
        <div v-if="loading" class="loading-container">
            <el-skeleton :rows="3" animated />
        </div>

        <!-- 优惠活动列表 -->
        <div v-else class="promotion-list">
            <transition-group name="fade">
                <el-card v-for="promo in filteredPromotions" :key="promo.id" class="promo-card" shadow="hover">
                    <div class="promo-card-content">
                        <div class="promo-image">
                            <img :src="promo.image" :alt="promo.title">
                            <div v-if="promo.isLimited" class="promo-tag limited">限时</div>
                            <div v-if="promo.isMember" class="promo-tag member">会员专享</div>
                        </div>
                        <div class="promo-info">
                            <h3>{{ promo.title }}</h3>
                            <p class="promo-description">{{ promo.description }}</p>
                            <div class="promo-meta">
                                <span class="promo-period">活动期限: {{ promo.startDate }} - {{ promo.endDate }}</span>
                                <span v-if="isEndingSoon(promo)" class="ending-soon">即将结束</span>
                            </div>
                            <div class="promo-actions">
                                <el-button type="primary" @click="viewPromoDetails(promo)">查看详情</el-button>
                                <el-button v-if="promo.canShare" @click="sharePromotion(promo)">分享</el-button>
                            </div>
                        </div>
                    </div>
                </el-card>
            </transition-group>
        </div>

        <!-- 空状态 -->
        <el-empty v-if="filteredPromotions.length === 0 && !loading" description="暂无符合条件的优惠活动"></el-empty>

        <!-- 优惠活动详情对话框 -->
        <el-dialog v-model="dialogVisible" :title="currentPromo.title" width="60%" custom-class="promo-dialog">
            <div v-if="currentPromo.id" class="promo-details">
                <img :src="currentPromo.image" :alt="currentPromo.title" class="detail-image">
                <div class="detail-content">
                    <h3>{{ currentPromo.title }}</h3>
                    <div class="detail-meta">
                        <span class="detail-period">活动期限: {{ currentPromo.startDate }} - {{ currentPromo.endDate
                            }}</span>
                    </div>
                    <div class="detail-description">
                        <h4>活动详情</h4>
                        <p>{{ currentPromo.fullDescription || currentPromo.description }}</p>
                    </div>
                    <div v-if="currentPromo.rules" class="detail-rules">
                        <h4>活动规则</h4>
                        <ul>
                            <li v-for="(rule, index) in currentPromo.rules" :key="index">{{ rule }}</li>
                        </ul>
                    </div>
                    <div v-if="currentPromo.couponCode" class="detail-coupon">
                        <h4>优惠码</h4>
                        <div class="coupon-code">
                            <span>{{ currentPromo.couponCode }}</span>
                            <el-button size="small" @click="copyCode(currentPromo.couponCode)">复制</el-button>
                        </div>
                    </div>
                    <div class="detail-actions">
                        <el-button type="primary" @click="usePromotion(currentPromo)">立即使用</el-button>
                    </div>
                </div>
            </div>
        </el-dialog>
    </div>
</template>

<script>
import { ElMessage } from 'element-plus'
// eslint-disable-next-line no-unused-vars
import api from '@/services/api'

export default {
    name: 'PromotionCenterView',
    data() {
        return {
            loading: true,
            promotions: [],
            activeCategory: 'all',
            sortBy: 'newest',
            dialogVisible: false,
            currentPromo: {}
        }
    },
    computed: {
        filteredPromotions() {
            // 根据分类筛选
            let result = [...this.promotions]

            if (this.activeCategory !== 'all') {
                switch (this.activeCategory) {
                    case 'limited':
                        result = result.filter(p => p.isLimited)
                        break
                    case 'member':
                        result = result.filter(p => p.isMember)
                        break
                    case 'routes':
                        result = result.filter(p => p.type === 'route')
                        break
                    case 'points':
                        result = result.filter(p => p.type === 'points')
                        break
                }
            }

            // 根据排序方式排序
            switch (this.sortBy) {
                case 'newest':
                    result.sort((a, b) => new Date(b.startDate) - new Date(a.startDate))
                    break
                case 'ending-soon':
                    result.sort((a, b) => new Date(a.endDate) - new Date(b.endDate))
                    break
                case 'discount':
                    result.sort((a, b) => b.discountRate - a.discountRate)
                    break
            }

            return result
        }
    },
    methods: {
        async fetchPromotions() {
            this.loading = true
            try {
                // 实际项目中应该从API获取数据
                // const result = await api.promotions.getAll()
                // this.promotions = result

                // 由于没有实际API，这里用模拟数据
                setTimeout(() => {
                    this.promotions = [
                        {
                            id: 1,
                            title: '暑假特惠',
                            description: '暑期学生订票享受八折优惠，提前预订立享折上折！',
                            fullDescription: '2023年暑期特惠活动，面向全国在校学生推出的专属优惠。凡是在6月1日至8月31日期间，预订7月1日至9月10日的航班，凭有效学生证即可享受机票价格8折优惠。若提前15天预订，还可额外享受5%的折扣。',
                            image: 'https://picsum.photos/id/380/600/300',
                            startDate: '2023-06-01',
                            endDate: '2023-08-31',
                            isLimited: true,
                            isMember: false,
                            type: 'seasonal',
                            discountRate: 20,
                            canShare: true,
                            couponCode: 'SUMMER2023',
                            rules: [
                                '须持有效学生证',
                                '提前15天预订可享受额外5%折扣',
                                '不可与其他优惠同时使用',
                                '每位学生限购4张机票'
                            ]
                        },
                        {
                            id: 2,
                            title: '会员福利',
                            description: '新注册会员首单立减100元，老会员专享积分双倍！',
                            fullDescription: '为回馈新老会员的支持，推出会员专享福利活动。新注册会员首次预订机票即可立减100元；金卡及以上会员预订任意航线，可获得双倍积分奖励，积分可用于兑换机票、升舱或兑换合作伙伴礼品。',
                            image: 'https://picsum.photos/id/401/600/300',
                            startDate: '2023-05-15',
                            endDate: '2023-12-31',
                            isLimited: false,
                            isMember: true,
                            type: 'member',
                            discountRate: 10,
                            canShare: true,
                            rules: [
                                '新会员优惠仅适用于注册后30天内的首次预订',
                                '双倍积分将在航班起飞后15个工作日内自动添加到会员账户',
                                '会员等级以预订时的等级为准'
                            ]
                        },
                        {
                            id: 3,
                            title: '早鸟计划',
                            description: '提前30天预订国际航班，最高可享7折优惠！',
                            fullDescription: '国际航线早鸟计划，提前30天预订指定国际航班，即可享受7折优惠。此优惠适用于亚洲、欧洲、北美等多条国际航线，数量有限，先到先得。',
                            image: 'https://picsum.photos/id/450/600/300',
                            startDate: '2023-07-01',
                            endDate: '2023-09-30',
                            isLimited: true,
                            isMember: false,
                            type: 'route',
                            discountRate: 30,
                            canShare: true,
                            couponCode: 'EARLYBIRD30',
                            rules: [
                                '须提前30天预订',
                                '适用于指定国际航线',
                                '每条航线优惠座位数量有限',
                                '改签将收取差价和手续费'
                            ]
                        },
                        {
                            id: 4,
                            title: '积分兑换特惠',
                            description: '积分兑换机票低至6折，还有多重好礼等你来换！',
                            fullDescription: '限时积分兑换特惠活动，会员可用积分兑换指定航线机票，兑换折扣低至6折。此外，还可使用积分兑换酒店住宿、租车服务和品牌商品等多种权益。',
                            image: 'https://picsum.photos/id/424/600/300',
                            startDate: '2023-08-01',
                            endDate: '2023-10-15',
                            isLimited: true,
                            isMember: true,
                            type: 'points',
                            discountRate: 40,
                            canShare: false,
                            rules: [
                                '兑换请登录会员中心或通过APP操作',
                                '兑换机票需提前7天操作',
                                '积分兑换的机票不可退改签',
                                '实际所需积分以兑换时系统显示为准'
                            ]
                        },
                        {
                            id: 5,
                            title: '周末特惠',
                            description: '周末出行更划算，精选国内热门航线8.5折起！',
                            fullDescription: '每周五至周日出发的国内热门航线特惠活动，提前预订可享受8.5折优惠。包括北京-上海、广州-深圳、成都-重庆等多条热门航线。',
                            image: 'https://picsum.photos/id/410/600/300',
                            startDate: '2023-07-15',
                            endDate: '2023-09-15',
                            isLimited: false,
                            isMember: false,
                            type: 'route',
                            discountRate: 15,
                            canShare: true,
                            couponCode: 'WEEKEND15',
                            rules: [
                                '适用于每周五、六、日出发的指定航班',
                                '须提前7天预订',
                                '不适用于法定节假日',
                                '每人每周限购2张'
                            ]
                        }
                    ]
                    this.loading = false
                }, 800)
            } catch (error) {
                console.error('获取优惠活动失败:', error)
                ElMessage.error('获取优惠活动列表失败')
                this.loading = false
            }
        },
        handleCategoryChange() {
            // 切换分类时可以做一些额外处理
            console.log('Category changed to:', this.activeCategory)
        },
        viewPromoDetails(promo) {
            this.currentPromo = { ...promo }
            this.dialogVisible = true
        },
        usePromotion(promo) {
            // 根据优惠活动类型执行不同操作
            if (promo.type === 'route') {
                // 跳转到航班搜索页面并应用优惠码
                this.$router.push({
                    path: '/',
                    query: { promoCode: promo.couponCode }
                })
            } else if (promo.type === 'points') {
                // 跳转到积分兑换页面
                this.$router.push('/profile?tab=points')
            } else {
                // 默认跳转到首页
                this.$router.push('/')
            }
            this.dialogVisible = false
        },
        sharePromotion(promo) {
            // 实际应用中这里可以集成分享API
            const shareText = `${promo.title} - ${promo.description}`;
            console.log('分享活动:', shareText);
            ElMessage.success('分享链接已复制到剪贴板')
        },
        copyCode(code) {
            navigator.clipboard.writeText(code).then(() => {
                ElMessage({
                    message: '优惠码已复制到剪贴板',
                    type: 'success'
                })
            }).catch(() => {
                ElMessage.error('复制失败，请手动复制')
            })
        },
        isEndingSoon(promo) {
            const now = new Date()
            const end = new Date(promo.endDate)
            const daysLeft = Math.ceil((end - now) / (1000 * 60 * 60 * 24))
            return daysLeft <= 7 && daysLeft >= 0
        }
    },
    created() {
        this.fetchPromotions()
    }
}
</script>

<style scoped>
.promotion-center {
    padding: 20px;
    max-width: 1200px;
    margin: 0 auto;
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

.page-header p {
    color: #606266;
    font-size: 16px;
}

.category-nav {
    margin-bottom: 20px;
}

.filter-bar {
    display: flex;
    justify-content: flex-end;
    margin-bottom: 20px;
}

.promotion-list {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
    gap: 20px;
}

.promo-card {
    height: 100%;
    transition: transform 0.3s;
}

.promo-card:hover {
    transform: translateY(-5px);
}

.promo-card-content {
    display: flex;
    flex-direction: column;
    height: 100%;
}

.promo-image {
    position: relative;
    height: 180px;
    overflow: hidden;
}

.promo-image img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform 0.3s;
}

.promo-card:hover .promo-image img {
    transform: scale(1.05);
}

.promo-tag {
    position: absolute;
    top: 10px;
    right: 10px;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 12px;
    color: white;
    font-weight: bold;
}

.promo-tag.limited {
    background-color: #e6a23c;
}

.promo-tag.member {
    background-color: #409eff;
}

.promo-info {
    padding: 20px;
    flex-grow: 1;
    display: flex;
    flex-direction: column;
}

.promo-info h3 {
    margin: 0 0 10px;
    font-size: 18px;
    color: #303133;
}

.promo-description {
    margin-bottom: 15px;
    color: #606266;
    flex-grow: 1;
}

.promo-meta {
    margin-bottom: 15px;
    font-size: 14px;
    color: #909399;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.ending-soon {
    color: #f56c6c;
    font-weight: bold;
}

.promo-actions {
    margin-top: auto;
}

/* 详情对话框样式 */
.promo-details {
    display: flex;
    flex-direction: column;
}

.detail-image {
    width: 100%;
    max-height: 300px;
    object-fit: cover;
    margin-bottom: 20px;
}

.detail-content h3 {
    margin: 0 0 15px;
    font-size: 22px;
    color: #303133;
}

.detail-meta {
    margin-bottom: 20px;
    color: #909399;
}

.detail-description,
.detail-rules {
    margin-bottom: 20px;
}

.detail-description h4,
.detail-rules h4,
.detail-coupon h4 {
    margin: 0 0 10px;
    font-size: 16px;
    color: #303133;
}

.detail-description p {
    line-height: 1.6;
    color: #606266;
}

.detail-rules ul {
    padding-left: 20px;
    color: #606266;
}

.detail-rules li {
    margin-bottom: 5px;
}

.coupon-code {
    display: flex;
    align-items: center;
    background: #f5f7fa;
    padding: 10px 15px;
    border-radius: 4px;
    margin-bottom: 20px;
}

.coupon-code span {
    font-family: monospace;
    font-size: 16px;
    font-weight: bold;
    color: #409eff;
    margin-right: 15px;
}

.detail-actions {
    margin-top: 20px;
}

.loading-container {
    padding: 20px;
}

/* 动画效果 */
.fade-enter-active,
.fade-leave-active {
    transition: opacity 0.5s;
}

.fade-enter-from,
.fade-leave-to {
    opacity: 0;
}

@media (min-width: 768px) {
    .promo-details {
        flex-direction: row;
    }

    .detail-image {
        width: 40%;
        margin-right: 30px;
        margin-bottom: 0;
    }

    .detail-content {
        flex: 1;
    }
}
</style>