<template>
  <div class="message-center-container">
    <div class="message-header">
      <h3>消息中心</h3>
      <div class="message-actions">
        <el-button type="primary" size="small" @click="markAllAsRead">全部已读</el-button>
        <el-button type="danger" size="small" @click="deleteSelected">删除选中</el-button>
      </div>
    </div>

    <el-tabs v-model="activeMessageTab" class="message-tabs">
      <el-tab-pane label="全部消息" name="all">
        <message-list :messages="filteredMessages" @select-change="handleSelectChange" @mark-read="handleMarkRead"
          @delete-message="handleDeleteMessage" />
      </el-tab-pane>
      <el-tab-pane label="系统通知" name="system">
        <message-list :messages="getMessagesByType('system')" @select-change="handleSelectChange"
          @mark-read="handleMarkRead" @delete-message="handleDeleteMessage" />
      </el-tab-pane>
      <el-tab-pane label="订单更新" name="order">
        <message-list :messages="getMessagesByType('order')" @select-change="handleSelectChange"
          @mark-read="handleMarkRead" @delete-message="handleDeleteMessage" />
      </el-tab-pane>
      <el-tab-pane label="航班变动" name="flight">
        <message-list :messages="getMessagesByType('flight')" @select-change="handleSelectChange"
          @mark-read="handleMarkRead" @delete-message="handleDeleteMessage" />
      </el-tab-pane>
    </el-tabs>

    <el-pagination v-if="totalMessages > pageSize" background layout="prev, pager, next" :total="totalMessages"
      :page-size="pageSize" :current-page="currentPage" @current-change="handlePageChange" class="message-pagination" />
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import MessageList from './message/MessageList.vue'
// import api from '@/services/api' // 暂时不使用API

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
    const currentPage = ref(1)
    const pageSize = ref(10)
    const totalMessages = ref(0)

    // 获取消息列表
    const fetchMessages = () => {
      loading.value = true

      // 使用模拟数据（因为API尚未接入）
      setTimeout(() => {
        // 模拟消息数据
        const mockMessages = [
          {
            id: 1,
            type: 'system',
            title: '系统升级通知',
            content: '亲爱的用户，我们将于2023年6月15日凌晨2:00-4:00进行系统升级，期间可能影响部分功能使用。',
            isRead: false,
            createTime: '2023-06-10 10:30:00'
          },
          {
            id: 2,
            type: 'order',
            title: '订单支付成功',
            content: '您的订单 ORD20230605001 已支付成功，感谢您的购买！',
            isRead: true,
            createTime: '2023-06-05 14:25:00'
          },
          {
            id: 3,
            type: 'flight',
            title: '航班时间变更',
            content: '您预订的 CA1234 航班起飞时间已变更为2023年7月1日 10:30，请及时查看详情。',
            isRead: false,
            createTime: '2023-06-01 09:15:00'
          },
          {
            id: 4,
            type: 'system',
            title: '账户安全提醒',
            content: '我们检测到您的账户在新设备上登录，如非本人操作，请立即修改密码。',
            isRead: false,
            createTime: '2023-05-28 22:10:00'
          },
          {
            id: 5,
            type: 'order',
            title: '退票申请已受理',
            content: '您的退票申请已受理，退款将在3-7个工作日内退回原支付账户。',
            isRead: true,
            createTime: '2023-05-20 16:40:00'
          },
          {
            id: 6,
            type: 'flight',
            title: '值机提醒',
            content: '您预订的 MU5678 航班已开放在线值机，请提前办理值机手续。',
            isRead: false,
            createTime: '2023-05-15 08:00:00'
          },
          {
            id: 7,
            type: 'system',
            title: '会员积分更新',
            content: '恭喜您！您的会员积分已更新，当前积分为1250分。',
            isRead: true,
            createTime: '2023-05-10 12:20:00'
          },
          {
            id: 8,
            type: 'order',
            title: '订单即将出行提醒',
            content: '您的航班将于明天出发，请提前做好出行准备。',
            isRead: false,
            createTime: '2023-05-05 18:30:00'
          },
          {
            id: 9,
            type: 'flight',
            title: '航班取消通知',
            content: '很抱歉，由于天气原因，您预订的 CZ8765 航班已取消，请查看短信了解详情。',
            isRead: false,
            createTime: '2023-05-01 07:45:00'
          },
          {
            id: 10,
            type: 'system',
            title: '节日优惠活动',
            content: '五一假期特惠，全场机票8折起，活动时间：4月25日-5月5日。',
            isRead: true,
            createTime: '2023-04-25 09:00:00'
          },
          {
            id: 11,
            type: 'order',
            title: '行程单已生成',
            content: '您的电子行程单已生成，可在"我的订单"中查看和下载。',
            isRead: false,
            createTime: '2023-04-20 14:15:00'
          },
          {
            id: 12,
            type: 'flight',
            title: '登机口变更',
            content: '您的航班登机口已变更为T2-C12，请注意登机时间。',
            isRead: true,
            createTime: '2023-04-15 16:50:00'
          }
        ]

        messages.value = mockMessages
        totalMessages.value = mockMessages.length
        loading.value = false
      }, 500)

      /* 实际API调用代码（暂时注释掉）
      try {
        const params = {
          page: currentPage.value,
          pageSize: pageSize.value,
          type: activeMessageTab.value === 'all' ? '' : activeMessageTab.value
        }
        const response = await api.messages.getMessages(params)
        messages.value = response.data
        totalMessages.value = response.total
      } catch (error) {
        console.error('获取消息列表失败:', error)
        ElMessage.error('获取消息列表失败，请稍后重试')
      } finally {
        loading.value = false
      }
      */
    }

    // 根据类型过滤消息
    const getMessagesByType = (type) => {
      return messages.value.filter(msg => msg.type === type)
    }

    // 当前标签页显示的消息
    const filteredMessages = computed(() => {
      if (activeMessageTab.value === 'all') {
        return messages.value
      } else {
        return getMessagesByType(activeMessageTab.value)
      }
    })

    // 处理页码变化
    const handlePageChange = (page) => {
      currentPage.value = page
      fetchMessages()
    }

    // 处理选中消息变化
    const handleSelectChange = (selected) => {
      selectedMessages.value = selected
    }

    // 处理标记消息已读/未读
    const handleMarkRead = (messageId) => {
      const message = messages.value.find(msg => msg.id === messageId)
      if (message) {
        message.isRead = !message.isRead

        /* 实际API调用代码（暂时注释掉）
        try {
          await api.messages.markAsRead(messageId, !message.isRead)
          ElMessage.success(`已标记为${message.isRead ? '已读' : '未读'}`)
        } catch (error) {
          console.error('操作失败:', error)
          ElMessage.error('操作失败，请稍后重试')
        }
        */
      }
    }

    // 处理删除消息
    const handleDeleteMessage = (messageId) => {
      const index = messages.value.findIndex(msg => msg.id === messageId)
      if (index !== -1) {
        messages.value.splice(index, 1)

        /* 实际API调用代码（暂时注释掉）
        try {
          await api.messages.deleteMessage(messageId)
          ElMessage.success('删除成功')
        } catch (error) {
          console.error('删除失败:', error)
          ElMessage.error('删除失败，请稍后重试')
        }
        */
      }
    }

    // 标记所有消息为已读
    const markAllAsRead = () => {
      // 实际应用中应该调用API
      messages.value = messages.value.map(msg => ({ ...msg, isRead: true }))

      /* 实际API调用代码（暂时注释掉）
      try {
        await api.messages.markAllAsRead()
        ElMessage.success('已将所有消息标记为已读')
        fetchMessages()
      } catch (error) {
        console.error('操作失败:', error)
        ElMessage.error('操作失败，请稍后重试')
      }
      */
    }

    // 删除选中消息
    const deleteSelected = () => {
      if (selectedMessages.value.length === 0) {
        // ElMessage.warning('请先选择要删除的消息')
        return
      }

      // 实际应用中应该调用API
      const selectedIds = selectedMessages.value
      messages.value = messages.value.filter(msg => !selectedIds.includes(msg.id))
      selectedMessages.value = []

      /* 实际API调用代码（暂时注释掉）
      try {
        await api.messages.deleteMessages(selectedMessages.value)
        ElMessage.success('删除成功')
        fetchMessages()
      } catch (error) {
        console.error('删除失败:', error)
        ElMessage.error('删除失败，请稍后重试')
      }
      */
    }

    onMounted(() => {
      fetchMessages()
    })

    return {
      activeMessageTab,
      messages,
      selectedMessages,
      loading,
      currentPage,
      pageSize,
      totalMessages,
      filteredMessages,
      getMessagesByType,
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
}
</style>