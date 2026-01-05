<template>
    <div class="message-detail-container">
        <div class="message-header">
            <h3>{{ message.title }}</h3>
            <span class="message-time">{{ message.createTime }}</span>
        </div>

        <div class="message-info">
            <el-tag :type="getTagType(message.type)" size="small">
                {{ getTypeName(message.type) }}
            </el-tag>
        </div>

        <div class="message-content">
            {{ message.content }}
        </div>

        <div v-if="hasRelatedAction" class="message-actions">
            <el-button type="primary" size="small" @click="handleAction">
                {{ actionText }}
            </el-button>
        </div>
    </div>
</template>

<script>
import { computed } from 'vue'
import { useRouter } from 'vue-router'

export default {
    name: 'MessageDetail',
    props: {
        message: {
            type: Object,
            required: true,
            default: () => ({})
        }
    },
    setup(props) {
        const router = useRouter()

        // 获取消息类型名称
        const getTypeName = (type) => {
            const typeMap = {
                'system': '系统通知',
                'order': '订单更新',
                'flight': '航班变动'
            }
            return typeMap[type] || '其他'
        }

        // 获取标签类型
        const getTagType = (type) => {
            const typeMap = {
                'system': 'info',
                'order': 'success',
                'flight': 'warning'
            }
            return typeMap[type] || 'info'
        }

        // 是否有相关操作
        const hasRelatedAction = computed(() => {
            return ['order', 'flight'].includes(props.message.type)
        })

        // 操作按钮文本
        const actionText = computed(() => {
            if (props.message.type === 'order') {
                return '查看订单'
            } else if (props.message.type === 'flight') {
                return '查看航班'
            }
            return '查看详情'
        })

        // 处理相关操作
        const handleAction = () => {
            if (props.message.type === 'order') {
                router.push('/orders')
            } else if (props.message.type === 'flight') {
                router.push('/flights')
            }
        }

        return {
            getTypeName,
            getTagType,
            hasRelatedAction,
            actionText,
            handleAction
        }
    }
}
</script>

<style scoped>
.message-detail-container {
    padding: 20px;
}

.message-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
    border-bottom: 1px solid #EBEEF5;
    padding-bottom: 15px;
}

.message-header h3 {
    margin: 0;
    font-size: 18px;
}

.message-time {
    color: #909399;
    font-size: 14px;
}

.message-info {
    margin-bottom: 20px;
}

.message-content {
    line-height: 1.8;
    margin-bottom: 30px;
    white-space: pre-line;
    color: #303133;
}

.message-actions {
    text-align: right;
    margin-top: 20px;
    padding-top: 15px;
    border-top: 1px solid #EBEEF5;
}
</style>