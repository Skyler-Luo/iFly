<template>
    <div class="notification-container">
        <el-card class="notification-card" :body-style="{ padding: '0px' }">
            <template #header>
                <div class="notification-header">
                    <h2><i class="el-icon-bell"></i> 消息中心</h2>
                    <div class="notification-actions">
                        <el-button type="primary" size="small" @click="markAllAsRead" :icon="Check">全部已读</el-button>
                        <el-button type="danger" size="small" @click="deleteSelected" :icon="Delete">删除选中</el-button>
                    </div>
                </div>
            </template>

            <el-tabs v-model="activeTab" class="notification-tabs" type="border-card">
                <el-tab-pane label="全部消息" name="all">
                    <div v-loading="loading" class="tab-content">
                        <message-list :messages="filteredMessages" @select-change="handleSelectChange"
                            @mark-read="handleMarkRead" @delete-message="handleDeleteMessage" />
                    </div>
                </el-tab-pane>
                <el-tab-pane label="系统通知" name="system">
                    <div v-loading="loading" class="tab-content">
                        <message-list :messages="getMessagesByType('system')" @select-change="handleSelectChange"
                            @mark-read="handleMarkRead" @delete-message="handleDeleteMessage" />
                    </div>
                </el-tab-pane>
                <el-tab-pane label="订单更新" name="order">
                    <div v-loading="loading" class="tab-content">
                        <message-list :messages="getMessagesByType('order')" @select-change="handleSelectChange"
                            @mark-read="handleMarkRead" @delete-message="handleDeleteMessage" />
                    </div>
                </el-tab-pane>
                <el-tab-pane label="航班变动" name="flight">
                    <div v-loading="loading" class="tab-content">
                        <message-list :messages="getMessagesByType('flight')" @select-change="handleSelectChange"
                            @mark-read="handleMarkRead" @delete-message="handleDeleteMessage" />
                    </div>
                </el-tab-pane>
            </el-tabs>

            <el-pagination v-if="totalMessages > pageSize" background layout="total, prev, pager, next"
                :total="totalMessages" :page-size="pageSize" :current-page="currentPage"
                @current-change="handlePageChange" class="notification-pagination" />
        </el-card>
    </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import MessageList from '@/components/profile/message/MessageList.vue'
import api from '@/services/api'
import { ElMessage } from 'element-plus'
import { Check, Delete, Bell } from '@element-plus/icons-vue'

export default {
    name: 'NotificationView',
    components: {
        MessageList
    },
    setup() {
        const activeTab = ref('all')
        const messages = ref([])
        const selectedMessages = ref([])
        const loading = ref(false)
        const currentPage = ref(1)
        const pageSize = ref(10)
        const totalMessages = ref(0)

        // 监听标签页变化，重新加载消息
        watch(activeTab, () => {
            currentPage.value = 1
            fetchMessages()
        })

        // 获取消息列表
        const fetchMessages = () => {
            loading.value = true

            // 构建API查询参数
            const params = {
                page: currentPage.value,
                page_size: pageSize.value,
                type: activeTab.value === 'all' ? '' : activeTab.value
            }

            // 调用API获取消息数据
            api.messages.getMessages(params)
                .then(response => {
                    console.log('API 请求参数:', params)
                    console.log('API 响应:', response)
                    if (response.results && response.count !== undefined) {
                        // 转换API返回的消息格式
                        messages.value = response.results.map(msg => ({
                            id: msg.id,
                            type: msg.notif_type || 'system',
                            title: msg.title || '系统通知',
                            content: msg.message || '',
                            isRead: msg.is_read || false,
                            createTime: msg.created_at || new Date().toISOString()
                        }))
                        totalMessages.value = response.count
                    } else if (Array.isArray(response)) {
                        messages.value = response.map(msg => ({
                            id: msg.id,
                            type: msg.notif_type || 'system',
                            title: msg.title || '系统通知',
                            content: msg.message || '',
                            isRead: msg.is_read || false,
                            createTime: msg.created_at || new Date().toISOString()
                        }))
                        totalMessages.value = response.length
                    } else {
                        messages.value = []
                        totalMessages.value = 0
                    }
                    loading.value = false
                })
                .catch(error => {
                    console.error('获取消息列表失败:', error)
                    ElMessage.error('获取消息列表失败，请稍后重试')
                    messages.value = []
                    totalMessages.value = 0
                    loading.value = false
                })
        }

        // 根据类型过滤消息
        const getMessagesByType = (type) => {
            return messages.value.filter(msg => msg.type === type)
        }

        // 当前标签页显示的消息
        const filteredMessages = computed(() => {
            if (activeTab.value === 'all') {
                return messages.value
            } else {
                return getMessagesByType(activeTab.value)
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
                const newReadStatus = !message.isRead

                api.messages.markAsRead(messageId, newReadStatus)
                    .then(() => {
                        message.isRead = newReadStatus
                        ElMessage({
                            message: `已标记为${message.isRead ? '已读' : '未读'}`,
                            type: 'success',
                            duration: 2000
                        })
                    })
                    .catch(error => {
                        console.error('操作失败:', error)
                        ElMessage.error('操作失败，请稍后重试')
                    })
            }
        }

        // 处理删除消息
        const handleDeleteMessage = (messageId) => {
            api.messages.deleteMessage(messageId)
                .then(() => {
                    const index = messages.value.findIndex(msg => msg.id === messageId)
                    if (index !== -1) {
                        messages.value.splice(index, 1)
                        ElMessage({
                            message: '删除成功',
                            type: 'success',
                            duration: 2000
                        })
                        totalMessages.value -= 1
                    }
                })
                .catch(error => {
                    console.error('删除失败:', error)
                    ElMessage.error('删除失败，请稍后重试')
                })
        }

        // 标记所有消息为已读
        const markAllAsRead = () => {
            if (messages.value.length === 0) {
                ElMessage.warning('没有可标记的消息')
                return
            }

            api.messages.markAllAsRead()
                .then(() => {
                    messages.value = messages.value.map(msg => ({ ...msg, isRead: true }))
                    ElMessage({
                        message: '已全部标记为已读',
                        type: 'success',
                        duration: 2000
                    })
                })
                .catch(error => {
                    console.error('操作失败:', error)
                    ElMessage.error('操作失败，请稍后重试')
                })
        }

        // 删除选中消息
        const deleteSelected = () => {
            if (selectedMessages.value.length === 0) {
                ElMessage.warning('请先选择要删除的消息')
                return
            }

            api.messages.deleteMultiple(selectedMessages.value)
                .then(() => {
                    const selectedIds = selectedMessages.value
                    messages.value = messages.value.filter(msg => !selectedIds.includes(msg.id))
                    selectedMessages.value = []
                    totalMessages.value -= selectedIds.length
                    ElMessage({
                        message: `成功删除 ${selectedIds.length} 条消息`,
                        type: 'success',
                        duration: 2000
                    })
                })
                .catch(error => {
                    console.error('删除失败:', error)
                    ElMessage.error('删除失败，请稍后重试')
                })
        }

        onMounted(() => {
            fetchMessages()
        })

        return {
            activeTab,
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
            deleteSelected,
            // 图标
            Check,
            Delete,
            Bell
        }
    }
}
</script>

<style scoped>
.notification-container {
    max-width: 1200px;
    margin: 20px auto;
    padding: 0 20px;
}

.notification-card {
    border-radius: 12px;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
    overflow: hidden;
    transition: all 0.3s ease;
}

.notification-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

.notification-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 20px;
    background: linear-gradient(135deg, #409EFF, #53a8ff);
    color: #fff;
    border-radius: 8px 8px 0 0;
}

.notification-header h2 {
    margin: 0;
    display: flex;
    align-items: center;
    font-size: 22px;
}

.notification-header h2 i {
    margin-right: 10px;
    font-size: 24px;
}

.notification-actions {
    display: flex;
    gap: 12px;
}

.notification-tabs {
    margin-bottom: 0;
}

.tab-content {
    min-height: 300px;
    padding: 16px;
}

.notification-pagination {
    margin: 0;
    padding: 16px;
    text-align: center;
    background-color: #f7f9fc;
    border-top: 1px solid #ebeef5;
}

/* 响应式调整 */
@media screen and (max-width: 768px) {
    .notification-container {
        padding: 0 10px;
    }

    .notification-header {
        flex-direction: column;
        align-items: flex-start;
        gap: 10px;
    }

    .notification-actions {
        width: 100%;
        justify-content: flex-end;
    }
}

/* 添加过渡动画 */
.el-tab-pane {
    animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(10px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }
}
</style>