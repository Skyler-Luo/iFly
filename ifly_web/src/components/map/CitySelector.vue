<template>
  <div class="popular-cities">
    <h4>热门城市</h4>
    
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <el-icon class="is-loading"><Loading /></el-icon>
      <span>加载中...</span>
    </div>
    
    <!-- 错误状态 -->
    <div v-else-if="error" class="error-state">
      <span>{{ error }}</span>
      <el-button type="primary" size="small" @click="fetchCities">重试</el-button>
    </div>
    
    <!-- 空数据状态 -->
    <div v-else-if="popularCities.length === 0" class="empty-state">
      <span>暂无城市数据</span>
    </div>
    
    <!-- 城市列表 -->
    <div v-else class="city-chips">
      <el-tag 
        v-for="city in popularCities" 
        :key="city.name" 
        @click="$emit('city-selected', city)" 
        class="city-tag"
        :effect="city.selected ? 'dark' : 'plain'"
      >
        {{ city.name }}
      </el-tag>
    </div>
  </div>
</template>

<script>
import { Loading } from '@element-plus/icons-vue'
import api from '@/services/api'

export default {
  name: 'CitySelector',
  components: {
    Loading
  },
  props: {
    selectedFromCity: String,
    selectedToCity: String
  },
  data() {
    return {
      popularCities: [],
      loading: false,
      error: null
    }
  },
  mounted() {
    this.fetchCities()
  },
  watch: {
    selectedFromCity() {
      this.updateCitySelection()
    },
    selectedToCity() {
      this.updateCitySelection()
    }
  },
  methods: {
    async fetchCities() {
      this.loading = true
      this.error = null
      
      try {
        const response = await api.core.getCities()
        const cities = response.results || response || []
        
        // 转换为组件需要的格式
        this.popularCities = cities
          .filter(city => city.latitude && city.longitude)
          .map(city => ({
            name: city.name,
            code: city.code || '',
            coords: [parseFloat(city.latitude), parseFloat(city.longitude)],
            selected: false
          }))
        
        // 更新选中状态
        this.updateCitySelection()
      } catch (err) {
        console.error('获取城市数据失败:', err)
        this.error = err.message || '获取城市数据失败'
      } finally {
        this.loading = false
      }
    },
    
    updateCitySelection() {
      this.popularCities.forEach(city => {
        city.selected = city.name === this.selectedFromCity || city.name === this.selectedToCity
      })
    },
    
    resetSelection() {
      this.popularCities.forEach(city => {
        city.selected = false
      })
    }
  }
}
</script>

<style scoped>
.popular-cities {
  margin-top: 20px;
  padding: 16px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.popular-cities h4 {
  margin: 0 0 12px 0;
  color: #1890ff;
  font-size: 16px;
}

.city-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.city-tag {
  cursor: pointer;
  transition: all 0.2s ease;
}

.city-tag:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.loading-state,
.error-state,
.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 20px;
  color: #909399;
}

.loading-state .el-icon {
  font-size: 18px;
  color: #1890ff;
}

.error-state {
  color: #f56c6c;
}

.is-loading {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>
