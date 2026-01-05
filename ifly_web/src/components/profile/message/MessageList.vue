<template>
  <div class="message-list-container">
    <div class="message-list">
      <div v-if="messages.length === 0" class="no-messages">
        <el-empty description="暂无消息" :image-size="120">
          <template #image>
            <i class="el-icon-message"></i>
          </template>
        </el-empty>
      </div>
      <el-checkbox-group v-model="selectedMessages" @change="handleSelectionChange" v-else>
        <transition-group name="message-list" tag="div">
          <div v-for="message in messages" :key="message.id" :class="['message-item', { 'unread': !message.isRead }]">
            <div class="message-header">
              <el-checkbox :label="message.id"></el-checkbox>
              <div class="message-title">
                <span class="title-text">{{ message.title }}</span>
                <el-tag v-if="!message.isRead" size="small" type="danger" class="unread-tag">未读</el-tag>
              </div>
              <div class="message-actions">
                <el-tooltip :content="message.isRead ? '标为未读' : '标为已读'" placement="top">
                  <el-button size="small" circle type="primary" plain @click.stop="handleMarkRead(message)">
                    <i :class="message.isRead ? 'el-icon-message' : 'el-icon-message-solid'"></i>
                  </el-button>
                </el-tooltip>
                <el-tooltip content="删除消息" placement="top">
                  <el-button size="small" circle type="danger" plain @click.stop="handleDelete(message)">
                    <i class="el-icon-delete"></i>
                  </el-button>
                </el-tooltip>
              </div>
            </div>
            <div class="message-content">
              {{ message.content }}
            </div>
            <div class="message-footer">
              <el-tag :type="getMessageTagType(message.type)" size="small" effect="light" class="message-type-tag">
                {{ getMessageTypeText(message.type) }}
              </el-tag>
              <span class="message-time">{{ formatTime(message.createTime) }}</span>
            </div>
          </div>
        </transition-group>
      </el-checkbox-group>
    </div>
  </div>
</template>

<script>
import { ref, watch } from 'vue';
import { ElMessageBox } from 'element-plus';

export default {
  name: 'MessageList',
  props: {
    messages: {
      type: Array,
      required: true
    }
  },
  setup(props, { emit }) {
    const selectedMessages = ref([]);

    // 当消息列表变化时，清空选择项
    watch(
      () => props.messages,
      () => {
        selectedMessages.value = [];
      }
    );

    // 处理选择变化
    const handleSelectionChange = (selected) => {
      emit('select-change', selected);
    };

    // 处理标记已读/未读
    const handleMarkRead = (message) => {
      emit('mark-read', message.id);
    };

    // 处理删除消息
    const handleDelete = (message) => {
      ElMessageBox.confirm('确定要删除这条消息吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        emit('delete-message', message.id);
      }).catch(() => { });
    };

    // 格式化时间显示
    const formatTime = (timeString) => {
      if (!timeString) return '';

      const date = new Date(timeString);
      const now = new Date();
      const diff = now - date;

      // 如果小于1天，显示x小时前
      if (diff < 24 * 60 * 60 * 1000) {
        const hours = Math.floor(diff / (60 * 60 * 1000));
        if (hours === 0) {
          const minutes = Math.floor(diff / (60 * 1000));
          return minutes === 0 ? '刚刚' : `${minutes}分钟前`;
        }
        return `${hours}小时前`;
      }

      // 如果小于7天，显示x天前
      if (diff < 7 * 24 * 60 * 60 * 1000) {
        const days = Math.floor(diff / (24 * 60 * 60 * 1000));
        return `${days}天前`;
      }

      // 否则显示完整日期
      return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
    };

    // 获取消息类型的友好显示文本
    const getMessageTypeText = (type) => {
      const typeMap = {
        'system': '系统通知',
        'order': '订单更新',
        'flight': '航班变动',
        'payment': '支付通知',
        'refund': '退款通知'
      };
      return typeMap[type] || '系统通知';
    };

    // 获取消息类型对应的标签样式
    const getMessageTagType = (type) => {
      const typeMap = {
        'system': 'info',
        'order': 'success',
        'flight': 'warning',
        'payment': 'primary',
        'refund': ''
      };
      return typeMap[type] || 'info';
    };

    return {
      selectedMessages,
      handleSelectionChange,
      handleMarkRead,
      handleDelete,
      formatTime,
      getMessageTypeText,
      getMessageTagType
    };
  }
};
</script>

<style scoped>
.message-list-container {
  width: 100%;
}

.message-list {
  width: 100%;
}

.no-messages {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  color: #909399;
}

.no-messages i {
  font-size: 60px;
  margin-bottom: 16px;
  color: #c0c4cc;
}

.message-list-move {
  transition: transform 0.5s ease;
}

.message-item {
  padding: 20px;
  border: none;
  border-radius: 8px;
  margin-bottom: 16px;
  background-color: #fff;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.message-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 4px;
  height: 100%;
  background-color: #dcdfe6;
  transition: background-color 0.3s;
}

.message-item.unread::before {
  background-color: #409EFF;
}

.message-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.12);
}

.message-item.unread {
  background-color: #f0f9ff;
}

.message-header {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
}

.message-title {
  flex: 1;
  display: flex;
  align-items: center;
  margin-left: 10px;
  font-weight: 600;
  font-size: 15px;
  color: #303133;
}

.unread-tag {
  margin-left: 10px;
  font-size: 12px;
}

.message-actions {
  display: flex;
  gap: 8px;
}

.message-content {
  margin-left: 30px;
  margin-bottom: 16px;
  line-height: 1.6;
  color: #606266;
  white-space: pre-wrap;
  word-break: break-word;
  font-size: 14px;
  padding: 6px 0;
  border-bottom: 1px dashed #ebeef5;
}

.message-footer {
  display: flex;
  justify-content: space-between;
  margin-left: 30px;
  font-size: 12px;
  color: #909399;
  align-items: center;
}

.message-type-tag {
  border-radius: 12px;
  padding: 0 8px;
  height: 22px;
  line-height: 20px;
}

.message-time {
  font-size: 12px;
  color: #909399;
}

/* 响应式调整 */
@media screen and (max-width: 768px) {
  .message-item {
    padding: 15px;
  }

  .message-header {
    flex-wrap: wrap;
  }

  .message-actions {
    margin-top: 10px;
    margin-left: 30px;
  }

  .message-title {
    width: 100%;
  }
}
</style>