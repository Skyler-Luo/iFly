<template>
    <div class="promotion-detail">
        <div v-if="loading" class="loading-container">
            <el-skeleton :rows="10" animated />
        </div>

        <div v-else-if="promotion" class="promotion-content">
            <div class="promotion-header">
                <el-page-header @back="goBack" :content="promotion.title" />
            </div>

            <div class="promotion-banner">
                <img :src="promotion.image" :alt="promotion.title">
            </div>

            <div class="promotion-info">
                <div class="promotion-title-box">
                    <h1>{{ promotion.title }}</h1>
                    <div class="promotion-tags">
                        <el-tag v-if="promotion.isLimited" type="warning">限时特惠</el-tag>
                        <el-tag v-if="promotion.isMember" type="primary">会员专享</el-tag>
                        <el-tag v-if="isEndingSoon(promotion)" type="danger">即将结束</el-tag>
                    </div>
                    <div class="promotion-period">
                        活动期限：{{ promotion.startDate }} 至 {{ promotion.endDate }}
                    </div>
                </div>

                <el-divider />

                <div class="promotion-description">
                    <h2>活动详情</h2>
                    <p>{{ promotion.fullDescription || promotion.description }}</p>
                </div>

                <div v-if="promotion.rules" class="promotion-rules">
                    <h2>活动规则</h2>
                    <el-card shadow="hover">
                        <ul>
                            <li v-for="(rule, index) in promotion.rules" :key="index">{{ rule }}</li>
                        </ul>
                    </el-card>
                </div>

                <div v-if="promotion.couponCode" class="promotion-coupon">
                    <h2>优惠码</h2>
                    <el-card shadow="hover" class="coupon-card">
                        <div class="coupon-content">
                            <div class="coupon-code">
                                {{ promotion.couponCode }}
                            </div>
                            <el-button type="primary" @click="copyCode(promotion.couponCode)">复制优惠码</el-button>
                        </div>
                        <div class="coupon-tip">
                            预订时使用此优惠码可享受特别折扣
                        </div>
                    </el-card>
                </div>

                <div v-if="relatedPromotions.length > 0" class="related-promotions">
                    <h2>相关活动推荐</h2>
                    <div class="related-list">
                        <el-card v-for="promo in relatedPromotions" :key="promo.id" shadow="hover" class="related-card"
                            @click="viewPromotion(promo.id)">
                            <img :src="promo.image" :alt="promo.title">
                            <div class="related-info">
                                <h3>{{ promo.title }}</h3>
                                <p>{{ promo.description }}</p>
                            </div>
                        </el-card>
                    </div>
                </div>

                <div class="promotion-actions">
                    <el-button type="primary" size="large" @click="usePromotion">立即使用</el-button>
                    <el-button size="large" @click="sharePromotion">分享活动</el-button>
                </div>
            </div>
        </div>

        <el-empty v-else description="未找到该优惠活动"></el-empty>
    </div>
</template>

<script>
import { ElMessage } from 'element-plus'
// eslint-disable-next-line no-unused-vars
import api from '@/services/api'

export default {
    name: 'PromotionDetailView',
    data() {
        return {
            loading: true,
            promotion: null,
            relatedPromotions: []
        }
    },
    methods: {
        async fetchPromotionDetail() {
            this.loading = true

            try {
                // 实际项目中应该从API获取数据
                // const result = await api.promotions.getById(this.$route.params.id)
                // this.promotion = result

                // 由于没有实际API，这里用模拟数据
                setTimeout(() => {
                    const promotionId = parseInt(this.$route.params.id)

                    const promotions = [
                        {
                            id: 1,
                            title: '暑假特惠',
                            description: '暑期学生订票享受八折优惠，提前预订立享折上折！',
                            fullDescription: '2023年暑期特惠活动，面向全国在校学生推出的专属优惠。凡是在6月1日至8月31日期间，预订7月1日至9月10日的航班，凭有效学生证即可享受机票价格8折优惠。若提前15天预订，还可额外享受5%的折扣。\n\n此活动专为在校学生设计，旨在减轻暑期出行的经济负担。学生须在预订时提供有效学生证信息，并在值机时出示学生证原件进行验证。此优惠不可与其他促销活动、优惠券或折扣码叠加使用。',
                            image: 'https://picsum.photos/id/380/1200/400',
                            startDate: '2023-06-01',
                            endDate: '2023-08-31',
                            isLimited: true,
                            isMember: false,
                            type: 'seasonal',
                            discountRate: 20,
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
                            image: 'https://picsum.photos/id/401/1200/400',
                            startDate: '2023-05-15',
                            endDate: '2023-12-31',
                            isLimited: false,
                            isMember: true,
                            type: 'member',
                            discountRate: 10,
                            rules: [
                                '新会员优惠仅适用于注册后30天内的首次预订',
                                '双倍积分将在航班起飞后15个工作日内自动添加到会员账户',
                                '会员等级以预订时的等级为准'
                            ]
                        }
                    ]

                    this.promotion = promotions.find(p => p.id === promotionId)

                    // 获取相关推荐的活动
                    if (this.promotion) {
                        this.relatedPromotions = promotions
                            .filter(p => p.id !== this.promotion.id)
                            .slice(0, 3)
                    }

                    this.loading = false
                }, 800)

            } catch (error) {
                console.error('获取活动详情失败:', error)
                ElMessage.error('获取活动详情失败')
                this.loading = false
            }
        },
        goBack() {
            this.$router.push('/promotions')
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
        usePromotion() {
            // 根据优惠活动类型执行不同操作
            if (this.promotion.type === 'route') {
                // 跳转到航班搜索页面并应用优惠码
                this.$router.push({
                    path: '/',
                    query: { promoCode: this.promotion.couponCode }
                })
            } else if (this.promotion.type === 'points') {
                // 跳转到积分兑换页面
                this.$router.push('/profile?tab=points')
            } else {
                // 默认跳转到首页
                this.$router.push('/')
            }
        },
        sharePromotion() {
            // 实际应用中这里可以集成分享API
            const url = window.location.href

            // 模拟分享操作
            ElMessage.success('分享链接已复制到剪贴板')
            navigator.clipboard.writeText(url).catch(() => { })
        },
        viewPromotion(id) {
            // 跳转到其他优惠活动详情页
            this.$router.push(`/promotions/${id}`)
        },
        isEndingSoon(promo) {
            const now = new Date()
            const end = new Date(promo.endDate)
            const daysLeft = Math.ceil((end - now) / (1000 * 60 * 60 * 24))
            return daysLeft <= 7 && daysLeft >= 0
        }
    },
    created() {
        this.fetchPromotionDetail()
    },
    watch: {
        '$route.params.id': {
            handler() {
                this.fetchPromotionDetail()
            },
            immediate: true
        }
    }
}
</script>

<style scoped>
.promotion-detail {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

.loading-container {
    padding: 40px 0;
}

.promotion-header {
    margin-bottom: 20px;
}

.promotion-banner {
    margin-bottom: 30px;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.promotion-banner img {
    width: 100%;
    max-height: 400px;
    object-fit: cover;
}

.promotion-title-box {
    margin-bottom: 20px;
}

.promotion-title-box h1 {
    font-size: 28px;
    color: #303133;
    margin: 0 0 15px;
}

.promotion-tags {
    margin-bottom: 15px;
}

.promotion-tags .el-tag {
    margin-right: 10px;
}

.promotion-period {
    color: #909399;
    font-size: 14px;
}

.promotion-description,
.promotion-rules,
.promotion-coupon,
.related-promotions {
    margin-bottom: 30px;
}

.promotion-description h2,
.promotion-rules h2,
.promotion-coupon h2,
.related-promotions h2 {
    font-size: 20px;
    color: #303133;
    margin: 0 0 15px;
}

.promotion-description p {
    color: #606266;
    line-height: 1.8;
    white-space: pre-line;
}

.promotion-rules ul {
    padding-left: 20px;
    color: #606266;
    line-height: 1.8;
}

.promotion-rules li {
    margin-bottom: 10px;
}

.coupon-card {
    background: linear-gradient(135deg, #f5f7fa 0%, #e4e7ed 100%);
}

.coupon-content {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 15px;
}

.coupon-code {
    font-family: monospace;
    font-size: 24px;
    font-weight: bold;
    color: #409eff;
    letter-spacing: 2px;
}

.coupon-tip {
    color: #909399;
    font-size: 14px;
}

.related-list {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 20px;
}

.related-card {
    height: 100%;
    cursor: pointer;
    transition: transform 0.3s;
}

.related-card:hover {
    transform: translateY(-5px);
}

.related-card img {
    width: 100%;
    height: 150px;
    object-fit: cover;
}

.related-info {
    padding: 15px;
}

.related-info h3 {
    font-size: 16px;
    margin: 0 0 10px;
    color: #303133;
}

.related-info p {
    font-size: 14px;
    color: #606266;
    overflow: hidden;
    text-overflow: ellipsis;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
}

.promotion-actions {
    display: flex;
    justify-content: center;
    gap: 20px;
    margin-top: 40px;
}

@media (max-width: 768px) {
    .promotion-actions {
        flex-direction: column;
    }
}
</style>