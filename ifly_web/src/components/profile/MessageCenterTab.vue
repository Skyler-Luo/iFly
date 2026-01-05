<template>
  <div class="message-center-container">
    <div class="message-header">
      <h3>消息中心</h3>
      <div class="message-actions">
        <el-button type="primary" size="small" @click="markAllAsRead" :loading="markingAllRead">全部已读</el-button>
        <el-button type="danger" size="small" @click="deleteSelected" :loading="deleting" :disabled="selectedMessages.length === 0">删除选中</el-button>
      </div>
    </div>

    <el-tabs v-model="activeMessageTab" class="message-tabs" @tab-change="handleTabChange">
      <el-tab-pane label="全部消息" name="all">
        <div v-loading="loading">
          <message-list 
            :messages="messages" 
            @select-change="handleSelectChange" 
            @mark-read="handleMarkRead"
            @delete-message="handleDeleteMessage" 
          />
        </div>
      </el-tab-pane>
      <el-tab-pane label="系统通知" name="system">
        <div v-loading="loading">
          <message-list 
            :messages="messages" 
            @select-change="handleSelectChange"
            @mark-read="handleMarkRead" 
            @delete-message="handleDeleteMessage" 
          />
        </div>
      </el-tab-pane>
      <el-tab-pane label="订单更新" name="order">
        <div v-loading="loading">
          <message-list 
            :messages="messages" 
            @select-change="handleSelectChange"
            @mark-read="handleMarkRead" 
            @delete-message="handleDeleteMessage" 
          />
        </div>
      </el-tab-pane>
      <el-tab-pane label="航班变动" name="flight">
        <div v-loading="loading">
          <message-list 
            :messages="messages" 
            @select-change="handleSelectChange"
            @mark-read="handleMarkRead" 
            @delete-message="handleDeleteMessage" 
          />
        </div>
      </el-tab-pane>
    </el-tabs>

    <!-- 分页 -->
    <el-pagination 
      v-if="totalMessages > pageSize" 
      background 
      layout="prev, pager, next" 
      :total="totalMessages"
      :page-size="pageSize" 
      :current-page="currentPage" 
      @current-change="handlePageChange" 
      class="message-pagination" 
    />
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import MessageList from './message/MessageList.vue'
import api from '@/services/api'

export default {
  name: 'MessageCenterTab',
  components: {
    MessageList
  },
  setup() {
    const activeMessageTab = ref('all')
    const messages = ref([])
    const selectedMessages = ref([])
    const loading = ref(false)
    const markingAllRead = ref(false)
    const deleting = ref(false)
    const currentPage = ref(1)
    const pageSize = ref(10)
    const totalMessages = ref(0)

    // 获取消息列表
    const fetchMessages = async () => {
      loading.value = true
      try {
        const params = {
          page: currentPage.value,
          page_size: pageSize.value
        }
        // 如果不是"全部"标签，添加类型筛选
        if (activeMessageTab.value !== 'all') {
          params.type = activeMessageTab.value
        }
        
        const response = await api.userMessages.getMessages(params)
        
        // 处理分页响应数据
        if (response.results) {
          // DRF 分页格式
          messages.value = response.results.map(msg => ({
            id: msg.id,
            type: msg.type,
            title: msg.title,
            content: msg.content,
            isRead: msg.is_read,
            createTime: msg.created_at
          }))
          totalMessages.value = response.count || 0
        } else if (Array.isArray(response)) {
          // 非分页格式
          messages.value = response.map(msg => ({
            id: msg.id,
            type: msg.type,
            title: msg.title,
            content: msg.content,
            isRead: msg.is_read,
            createTime: msg.created_at
          }))
          totalMessages.value = response.length
        }
      } catch (error) {
        console.error('获取消息列表失败:', error)
        ElMessage.error('获取消息列表失败，请稍后重试')
        messages.value = []
        totalMessages.value = 0
      } finally {
        loading.value = false
      }
    }

    // 处理标签页切换
    const handleTabChange = () => {
      currentPage.value = 1
      selectedMessages.value = []
      fetchMessages()
    }

    // 处理页码变化
    const handlePageChange = (page) => {
      currentPage.value = page
      selectedMessages.value = []
      fetchMessages()
    }

    // 处理选中消息变化
    const handleSelectChange = (selected) => {
      selectedMessages.value = selected
    }

    // 处理标记消息已读/未读
    const handleMarkRead = async (messageId) => {
      const message = messages.value.find(msg => msg.id === messageId)
      if (!message) return
      
      const newReadStatus = !message.isRead
      try {
        await api.userMessages.markAsRead(messageId, newReadStatus)
        message.isRead = newReadStatus
        ElMessage.success(`已标记为${newReadStatus ? '已读' : '未读'}`)
      } catch (error) {
        console.error('操作失败:', error)
        ElMessage.error('操作失败，请稍后重试')
      }
    }

    // 处理删除消息
    const handleDeleteMessage = async (messageId) => {
      try {
        await api.userMessages.deleteMessage(messageId)
        const index = messages.value.findIndex(msg => msg.id === messageId)
        if (index !== -1) {
          messages.value.splice(index, 1)
          totalMessages.value--
        }
        ElMessage.success('删除成功')
      } catch (error) {
        console.error('删除失败:', error)
        ElMessage.error('删除失败，请稍后重试')
      }
    }

    // 标记所有消息为已读
    const markAllAsRead = async () => {
      markingAllRead.value = true
      try {
        await api.userMessages.markAllAsRead()
        messages.value = messages.value.map(msg => ({ ...msg, isRead: true }))
        ElMessage.success('已将所有消息标记为已读')
      } catch (error) {
        console.error('操作失败:', error)
        ElMessage.error('操作失败，请稍后重试')
      } finally {
        markingAllRead.value = false
      }
    }

    // 删除选中消息
    const deleteSelected = async () => {
      if (selectedMessages.value.length === 0) {
        ElMessage.warning('请先选择要删除的消息')
        return
      }

      deleting.value = true
      try {
        await api.userMessages.deleteMultiple(selectedMessages.value)
        ElMessage.success('删除成功')
        selectedMessages.value = []
        // 重新获取消息列表
        fetchMessages()
      } catch (error) {
        console.error('删除失败:', error)
        ElMessage.error('删除失败，请稍后重试')
      } finally {
        deleting.value = false
      }
    }

    onMounted(() => {
      fetchMessages()
    })

    return {
      activeMessageTab,
      messages,
      selectedMessages,
      loading,
      markingAllRead,
      deleting,
      currentPage,
      pageSize,
      totalMessages,
      handleTabChange,
      handlePageChange,
      handleSelectChange,
      handleMarkRead,
      handleDeleteMessage,
      markAllAsRead,
      deleteSelected
    }
  }
}
</script>

<style scoped>
.message-center-container {
  padding: 10px 0;
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.message-header h3 {
  margin: 0;
}

.message-actions {
  display: flex;
  gap: 10px;
}

.message-tabs {
  margin-bottom: 20px;
}

.message-pagination {
  margin-top: 20px;
  text-align: center;
  display: flex;
  justify-content: center;
}
</style>
