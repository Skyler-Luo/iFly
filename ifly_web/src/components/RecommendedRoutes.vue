<template>
  <div class="recommended-routes">
    <h3 class="section-title">{{ title }}</h3>
    <p class="section-subtitle">{{ subtitle }}</p>
    
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <el-skeleton :rows="3" animated />
    </div>
    
    <!-- 有数据时显示航线卡片 -->
    <el-row v-else-if="recommendations.length > 0" :gutter="20">
      <el-col
        v-for="route in recommendations"
        :key="route.route"
        :xs="24"
        :sm="12"
        :md="8"
      >
        <el-card class="route-card" shadow="hover" @click="selectRoute(route)">
          <div class="route-info">
            <span class="city departure">{{ route.departure_city }}</span>
            <div class="route-arrow">
              <el-icon><Right /></el-icon>
            </div>
            <span class="city arrival">{{ route.arrival_city }}</span>
          </div>
          <div class="route-meta">
            <span v-if="route.predicted_score !== undefined" class="score">
              <span class="score-label">推荐指数:</span>
              <el-rate
                :model-value="scoreToStars(route.predicted_score)"
                disabled
                :max="5"
                :colors="['#f7ba2a', '#f7ba2a', '#f7ba2a']"
              />
            </span>
            <span v-if="route.booking_count" class="booking-count">
              <el-icon><Ticket /></el-icon>
              {{ route.booking_count }} 人已预订
            </span>
          </div>
          <div class="route-reason">
            <el-icon><InfoFilled /></el-icon>
            {{ route.reason }}
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 无数据时显示空状态 -->
    <div v-else class="empty-state">
      <el-empty description="暂无推荐航线">
        <template #image>
          <el-icon class="empty-icon"><Plane /></el-icon>
        </template>
        <p class="empty-tip">航线数据正在准备中，敬请期待</p>
      </el-empty>
    </div>
  </div>
</template>

<script>
import { Right, Ticket, InfoFilled, Promotion as Plane } from '@element-plus/icons-vue'
import api from '@/services/api'

export default {
  name: 'RecommendedRoutes',
  components: {
    Right,
    Ticket,
    InfoFilled,
    Plane
  },
  props: {
    limit: {
      type: Number,
      default: 6
    }
  },
  data() {
    return {
      recommendations: [],
      recommendationType: '',
      loading: false
    }
  },
  computed: {
    title() {
      return this.recommendationType === 'collaborative'
        ? '为您推荐的航线'
        : '热门航线推荐'
    },
    subtitle() {
      return this.recommendationType === 'collaborative'
        ? '基于您的出行偏好，为您精选以下航线'
        : '发现最受欢迎的航线目的地'
    }
  },
  mounted() {
    this.fetchRecommendations()
  },
  methods: {
    async fetchRecommendations() {
      this.loading = true
      try {
        const response = await api.recommendations.getRouteRecommendations({
          limit: this.limit
        })
        this.recommendations = response.recommendations || []
        this.recommendationType = response.recommendation_type || 'popular'
      } catch (error) {
        console.error('获取推荐航线失败:', error)
        this.recommendations = []
      } finally {
        this.loading = false
      }
    },
    selectRoute(route) {
      this.$emit('route-selected', {
        from: route.departure_city,
        to: route.arrival_city
      })
      // 跳转到航班搜索页面
      this.$router.push({
        path: '/flights',
        query: {
          from: route.departure_city,
          to: route.arrival_city
        }
      })
    },
    scoreToStars(score) {
      // 将 0-1 的评分转换为 0-5 的星级，支持半星
      return Math.round(score * 5 * 2) / 2
    }
  }
}
</script>

<style scoped>
.recommended-routes {
  margin: 0;
  max-width: 100%;
  padding: 0;
  background-color: transparent;
  border-radius: 0;
}

.section-title {
  text-align: center;
  margin-bottom: 15px;
  font-size: 2em;
  color: #003b7a;
  font-weight: 600;
}

.section-subtitle {
  text-align: center;
  font-size: 15px;
  color: #666;
  margin-bottom: 30px;
}

.route-card {
  cursor: pointer;
  margin-bottom: 20px;
  border-radius: 12px;
  transition: all 0.3s ease;
  border: 1px solid #e8eaf6;
  background: linear-gradient(135deg, #fafbff 0%, #f3f5fc 100%);
}

.route-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 25px rgba(92, 107, 192, 0.2);
  border-color: #7986cb;
}

.route-info {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 15px;
  margin-bottom: 15px;
}

.city {
  font-size: 1.3em;
  font-weight: 600;
  color: #3f51b5;
}

.route-arrow {
  display: flex;
  align-items: center;
  color: #7986cb;
  font-size: 1.2em;
}

.route-meta {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-bottom: 12px;
  font-size: 0.9em;
  color: #666;
}

.route-meta span {
  display: flex;
  align-items: center;
  gap: 5px;
}

.score {
  display: flex;
  align-items: center;
  gap: 8px;
}

.score-label {
  color: #666;
}

.score .el-rate {
  height: 20px;
}

.booking-count .el-icon {
  color: #5c6bc0;
}

.route-reason {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-size: 0.85em;
  color: #888;
  padding-top: 12px;
  border-top: 1px solid #e8eaf6;
}

.route-reason .el-icon {
  color: #5c6bc0;
}

@media (max-width: 768px) {
  .section-title {
    font-size: 1.6em;
  }

  .city {
    font-size: 1.1em;
  }

  .route-meta {
    flex-direction: column;
    gap: 8px;
  }
}

/* 空状态样式 */
.empty-state {
  padding: 40px 20px;
  text-align: center;
}

.empty-icon {
  font-size: 64px;
  color: #c0c4cc;
}

.empty-tip {
  margin-top: 10px;
  font-size: 14px;
  color: #909399;
}

/* 加载状态样式 */
.loading-state {
  padding: 30px;
}
</style>
