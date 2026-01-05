<template>
  <div class="forbidden-container">
    <el-result
      icon="warning"
      title="403"
      sub-title="抱歉，您无权访问此页面"
    >
      <template #extra>
        <div class="error-actions">
          <el-button type="primary" @click="goHome" size="large">
            <el-icon><HomeFilled /></el-icon>
            返回首页
          </el-button>
          <el-button @click="goBack" size="large">
            <el-icon><Back /></el-icon>
            返回上页
          </el-button>
        </div>
      </template>
    </el-result>

    <!-- 错误详情 -->
    <div class="error-details" v-if="errorMessage">
      <el-card>
        <h4>详细信息</h4>
        <p>{{ errorMessage }}</p>
        
        <div class="suggestions">
          <h5>可能的解决方案：</h5>
          <ul>
            <li>检查您是否已正确登录</li>
            <li>确认您的账户具有相应权限</li>
            <li>联系管理员获取访问权限</li>
          </ul>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { HomeFilled, Back } from '@element-plus/icons-vue'

export default {
  name: 'ForbiddenView',
  components: {
    HomeFilled,
    Back
  },
  setup() {
    const router = useRouter()
    const route = useRoute()
    
    const errorMessage = ref('')
    
    onMounted(() => {
      // 从路由参数获取错误信息
      errorMessage.value = route.query.message || ''
      
      // 记录访问日志
      console.warn('403 Forbidden:', {
        path: route.path,
        query: route.query,
        timestamp: new Date().toISOString()
      })
    })
    
    const goHome = () => {
      router.push('/')
    }
    
    const goBack = () => {
      // 如果有历史记录就返回，否则去首页
      if (window.history.length > 1) {
        router.go(-1)
      } else {
        router.push('/')
      }
    }
    
    return {
      errorMessage,
      goHome,
      goBack
    }
  }
}
</script>

<style scoped>
.forbidden-container {
  min-height: 60vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 40px 20px;
}

.error-actions {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
  justify-content: center;
}

.error-details {
  margin-top: 40px;
  max-width: 600px;
  width: 100%;
}

.error-details h4 {
  color: #409eff;
  margin-bottom: 16px;
}

.error-details p {
  color: #606266;
  margin-bottom: 24px;
  line-height: 1.6;
}

.suggestions h5 {
  color: #303133;
  margin-bottom: 12px;
}

.suggestions ul {
  color: #606266;
  margin-bottom: 24px;
  padding-left: 20px;
}

.suggestions li {
  margin-bottom: 8px;
  line-height: 1.5;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .forbidden-container {
    padding: 20px 16px;
  }
  
  .error-actions {
    flex-direction: column;
    align-items: center;
  }
  
  .error-actions .el-button {
    width: 200px;
  }
}

/* 无障碍支持 */
@media (prefers-reduced-motion: reduce) {
  * {
    animation: none !important;
    transition: none !important;
  }
}
</style>
