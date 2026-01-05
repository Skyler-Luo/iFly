<template>
    <div class="user-profile-container">
        <el-card class="profile-card">
            <template #header>
                <div class="profile-header">
                    <h2>个人中心</h2>
                </div>
            </template>

            <el-tabs v-model="activeTab" class="profile-tabs">
                <el-tab-pane label="个人信息" name="info">
                    <user-info-tab :user="user" @update-success="loadUserProfile" />
                </el-tab-pane>
                <el-tab-pane label="常用乘客" name="passengers">
                    <passenger-list-tab />
                </el-tab-pane>
                <el-tab-pane label="我的订单" name="orders">
                    <order-history-tab />
                </el-tab-pane>
                <el-tab-pane label="我的机票" name="tickets">
                    <ticket-list-tab />
                </el-tab-pane>
                <el-tab-pane label="消息中心" name="messages">
                    <message-center-tab />
                </el-tab-pane>
                <el-tab-pane label="账户安全" name="security">
                    <security-tab />
                </el-tab-pane>
            </el-tabs>
        </el-card>
    </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import api from '@/services/api'
import UserInfoTab from '@/components/profile/UserInfoTab.vue'
import PassengerListTab from '@/components/profile/PassengerListTab.vue'
import OrderHistoryTab from '@/components/profile/OrderHistoryTab.vue'
import TicketListTab from '@/components/profile/TicketListTab.vue'
import SecurityTab from '@/components/profile/SecurityTab.vue'
import MessageCenterTab from '@/components/profile/MessageCenterTab.vue'

export default {
    name: 'UserProfileView',
    components: {
        UserInfoTab,
        PassengerListTab,
        OrderHistoryTab,
        TicketListTab,
        SecurityTab,
        MessageCenterTab
    },
    setup() {
        const router = useRouter()
        const activeTab = ref('info')
        const user = ref({})
        const loading = ref(false)

        const loadUserProfile = async () => {
            loading.value = true

            try {
                const response = await api.auth.getProfile()
                const data = response.data || response
                user.value = {
                    id: data.id,
                    username: data.username,
                    email: data.email,
                    real_name: data.real_name || '',
                    phone: data.phone || '',
                    id_card: data.id_card || '',
                    gender: data.gender || '',
                    address: data.address || '',
                    avatar: data.avatar || ''
                }
            } catch (error) {
                console.error('获取用户信息失败:', error)
                // 如果获取失败，尝试从本地存储获取
                try {
                    const userStr = localStorage.getItem('user')
                    if (userStr) {
                        user.value = JSON.parse(userStr)
                    } else {
                        ElMessage.error('获取用户信息失败，请重新登录')
                        router.push('/login')
                    }
                } catch (e) {
                    ElMessage.error('获取用户信息失败，请重新登录')
                    router.push('/login')
                }
            } finally {
                loading.value = false
            }
        }

        onMounted(() => {
            // 根据URL参数设置激活的标签
            const tab = router.currentRoute.value.query.tab
            if (tab && ['info', 'passengers', 'orders', 'tickets', 'messages', 'security'].includes(tab)) {
                activeTab.value = tab
            }

            loadUserProfile()
        })

        return {
            activeTab,
            user,
            loading,
            loadUserProfile
        }
    }
}
</script>

<style scoped>
.user-profile-container {
    width: 100%;
    padding: 20px 40px;
    box-sizing: border-box;
}

.profile-card {
    border-radius: 8px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.profile-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.profile-tabs {
    margin-top: 20px;
}

.profile-tabs :deep(.el-tabs__content) {
    padding: 20px 0;
}
</style>