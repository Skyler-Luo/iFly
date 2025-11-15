<template>
    <div class="promotions">
        <div class="promotions-header">
            <h2 class="section-title">最新优惠活动</h2>
            <router-link to="/promotions" class="view-all">查看全部</router-link>
        </div>
        <p class="section-subtitle">限时特惠，把握机会享受超值折扣</p>

        <!-- 加载状态 -->
        <div v-if="loading" class="loading-state">
            <el-skeleton :rows="3" animated />
        </div>

        <!-- 错误状态 -->
        <div v-else-if="error" class="error-state">
            <el-empty description="暂时无法获取优惠活动信息" :image-size="200">
                <el-button type="primary" @click="fetchPromotions">重试</el-button>
            </el-empty>
        </div>

        <!-- 有数据显示轮播图 -->
        <el-carousel v-else :interval="4000" type="card" height="320px">
            <el-carousel-item v-for="promo in promotions" :key="promo.id">
                <el-card class="promo-card" shadow="hover">
                    <img :src="promo.image" :alt="promo.title" class="promo-image">
                    <div class="promo-content">
                        <h3>{{ promo.title }}</h3>
                        <p>{{ promo.description }}</p>
                        <div class="promo-button-container">
                            <router-link :to="`/promotions/${promo.id}`" class="promo-link">
                                <el-button type="primary">查看详情</el-button>
                            </router-link>
                        </div>
                    </div>
                </el-card>
            </el-carousel-item>
        </el-carousel>
    </div>
</template>

<script>
import api from '@/services/api'

export default {
    name: 'PromotionCarousel',
    data() {
        return {
            promotions: [],
            loading: false,
            error: false
        }
    },
    created() {
        this.fetchPromotions()
    },
    methods: {
        async fetchPromotions() {
            this.loading = true
            this.error = false
            try {
                // 从API获取促销活动数据
                const result = await api.promotions.getList()
                console.log('获取到促销数据:', result);

                // 确保result是数组，即使是空数组
                const promoData = Array.isArray(result) ? result : [];

                // 处理API返回的数据
                if (promoData.length > 0) {
                    this.promotions = promoData.map(promo => ({
                        id: promo.id,
                        title: promo.title,
                        description: promo.description,
                        image: promo.image || `https://picsum.photos/id/${300 + parseInt(promo.id)}/600/300`
                    }))
                } else {
                    // 如果API没有返回数据，使用模拟数据
                    console.warn('没有找到促销活动数据，使用模拟数据')
                    this.promotions = [
                        {
                            id: 1,
                            title: "新用户专享优惠",
                            description: "新注册用户首次预订享受85折优惠，最高减免300元",
                            image: "https://picsum.photos/id/301/600/300"
                        },
                        {
                            id: 2,
                            title: "春节回家特惠",
                            description: "春节期间预订指定航线，享受9折优惠，还有额外行李额度",
                            image: "https://picsum.photos/id/302/600/300"
                        },
                        {
                            id: 3,
                            title: "商务舱限时特惠",
                            description: "指定国际航线商务舱8.5折起，含专属值机通道和贵宾休息室",
                            image: "https://picsum.photos/id/303/600/300"
                        },
                        {
                            id: 4,
                            title: "周二特惠日",
                            description: "每周二预订，所有航线额外95折优惠，可与其他优惠叠加",
                            image: "https://picsum.photos/id/304/600/300"
                        }
                    ]
                }
            } catch (error) {
                console.error('获取促销活动数据失败:', error)

                // 判断错误类型并提供适当的信息
                if (error.response) {
                    console.error(`服务器响应错误: ${error.response.status}`);
                } else if (error.request) {
                    console.error('没有收到服务器响应');
                } else {
                    console.error('请求配置错误:', error.message);
                }

                // 使用模拟数据代替显示错误
                console.warn('使用模拟数据替代')
                this.promotions = [
                    {
                        id: 1,
                        title: "新用户专享优惠",
                        description: "新注册用户首次预订享受85折优惠，最高减免300元",
                        image: "https://picsum.photos/id/301/600/300"
                    },
                    {
                        id: 2,
                        title: "春节回家特惠",
                        description: "春节期间预订指定航线，享受9折优惠，还有额外行李额度",
                        image: "https://picsum.photos/id/302/600/300"
                    },
                    {
                        id: 3,
                        title: "商务舱限时特惠",
                        description: "指定国际航线商务舱8.5折起，含专属值机通道和贵宾休息室",
                        image: "https://picsum.photos/id/303/600/300"
                    },
                    {
                        id: 4,
                        title: "周二特惠日",
                        description: "每周二预订，所有航线额外95折优惠，可与其他优惠叠加",
                        image: "https://picsum.photos/id/304/600/300"
                    }
                ]
                this.error = false // 使用模拟数据不显示错误
            } finally {
                this.loading = false
            }
        }
    }
}
</script>

<style scoped>
.promotions {
    margin: 40px 0;
}

.promotions-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    padding: 0 20px;
}

.loading-state,
.error-state {
    min-height: 320px;
    padding: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
}

/* 使用全局标题样式 */

.view-all {
    color: #409EFF;
    text-decoration: none;
    font-size: 14px;
    transition: all 0.3s;
    padding: 8px 15px;
    border-radius: 20px;
    background-color: rgba(64, 158, 255, 0.1);
}

.view-all:hover {
    color: #66b1ff;
    background-color: rgba(64, 158, 255, 0.2);
}

.promo-card {
    height: 100%;
    overflow: hidden;
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    display: flex;
    flex-direction: column;
}

.promo-image {
    width: 100%;
    height: 170px;
    object-fit: cover;
    transition: transform 0.5s ease;
}

.promo-content {
    padding: 15px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    height: calc(100% - 170px);
}

.promo-content h3 {
    margin-bottom: 10px;
    color: #303133;
    font-size: 1.2em;
}

.promo-content p {
    margin-bottom: 15px;
    color: #606266;
    line-height: 1.5;
    flex-grow: 1;
    max-height: 60px;
    overflow: hidden;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    line-clamp: 2;
    -webkit-box-orient: vertical;
}

.promo-button-container {
    margin-top: 10px;
    display: flex;
    justify-content: flex-end;
    height: 36px;
    position: relative;
}

.promo-link {
    text-decoration: none;
    z-index: 10;
    position: relative;
}

.promo-card .el-button {
    position: relative;
    z-index: 10;
    transform: translateZ(0);
}

:deep(.el-carousel__mask) {
    opacity: 0.3;
}

:deep(.el-carousel--card .el-carousel__item) {
    border-radius: 12px;
}

:deep(.el-button--primary) {
    background: linear-gradient(135deg, #42a5f5, #1976d2);
    border: none;
    box-shadow: 0 2px 8px rgba(25, 118, 210, 0.3);
    padding: 10px 20px;
    font-weight: 500;
}

:deep(.el-button--primary:hover) {
    background: linear-gradient(135deg, #64b5f6, #2196f3);
    box-shadow: 0 4px 12px rgba(33, 150, 243, 0.4);
}

.section-subtitle {
    text-align: center;
    color: #909399;
    margin-bottom: 30px;
}
</style>