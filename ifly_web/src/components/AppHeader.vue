<template>
    <el-menu class="header" mode="horizontal" :ellipsis="false">
        <el-menu-item index="0" class="logo-item">
            <router-link to="/">
                <h1>iFly</h1>
            </router-link>
        </el-menu-item>
        <el-menu-item index="1">
            <router-link to="/">首页</router-link>
        </el-menu-item>
        <el-menu-item index="2">
            <router-link to="/promotions">优惠活动</router-link>
        </el-menu-item>
        <el-menu-item index="3" v-if="isLoggedIn">
            <router-link to="/orders">我的订单</router-link>
        </el-menu-item>
        <el-menu-item index="4">
            <router-link to="/help">帮助中心</router-link>
        </el-menu-item>

        <!-- 管理员菜单 -->
        <el-sub-menu index="5" v-if="isAdmin" class="admin-menu">
            <template #title>管理控制台</template>
            <el-menu-item index="5-1">
                <router-link to="/admin">控制台首页</router-link>
            </el-menu-item>
            <el-menu-item index="5-2">
                <router-link to="/admin/flights">航班管理</router-link>
            </el-menu-item>
            <el-menu-item index="5-3">
                <router-link to="/admin/users">用户管理</router-link>
            </el-menu-item>
            <el-menu-item index="5-4">
                <router-link to="/admin/orders">订单管理</router-link>
            </el-menu-item>
            <el-menu-item index="5-5">
                <router-link to="/admin/promotions">优惠活动管理</router-link>
            </el-menu-item>
            <el-menu-item index="5-6">
                <router-link to="/admin/settings">系统设置</router-link>
            </el-menu-item>
        </el-sub-menu>

        <!-- 未登录状态 -->
        <div class="login-container" v-if="!isLoggedIn">
            <el-button class="login-btn" @click="goToLogin">
                <div class="btn-content">
                    <el-icon>
                        <User />
                    </el-icon>
                    <span>登录</span>
                </div>
            </el-button>
            <el-button class="register-btn" @click="goToRegister">
                <div class="btn-content">
                    <el-icon>
                        <Plus />
                    </el-icon>
                    <span>注册</span>
                </div>
            </el-button>
        </div>

        <!-- 已登录状态 -->
        <div class="user-container" v-else>
            <el-dropdown trigger="hover" @command="handleCommand">
                <div class="user-dropdown-link">
                    <el-avatar :size="32" :src="userAvatar" class="user-avatar" />
                    <span class="user-name">{{ userName }}</span>
                    <el-icon class="el-icon--right"><arrow-down /></el-icon>
                </div>
                <template #dropdown>
                    <el-dropdown-menu>
                        <el-dropdown-item command="profile">
                            <el-icon>
                                <User />
                            </el-icon>个人中心
                        </el-dropdown-item>
                        <el-dropdown-item command="messages">
                            <el-badge :value="unreadCount" :hidden="unreadCount === 0" class="message-badge">
                                <el-icon>
                                    <Bell />
                                </el-icon>消息中心
                            </el-badge>
                        </el-dropdown-item>
                        <el-dropdown-item command="orders">
                            <el-icon>
                                <Tickets />
                            </el-icon>我的订单
                        </el-dropdown-item>
                        <el-dropdown-item command="points">
                            <el-icon>
                                <Trophy />
                            </el-icon>积分中心
                        </el-dropdown-item>
                        <el-dropdown-item command="promotions">
                            <el-icon>
                                <Discount />
                            </el-icon>优惠活动
                        </el-dropdown-item>
                        <el-dropdown-item command="help">
                            <el-icon>
                                <QuestionFilled />
                            </el-icon>帮助中心
                        </el-dropdown-item>
                        <el-dropdown-item v-if="isAdmin" command="admin">
                            <el-icon>
                                <Setting />
                            </el-icon>管理控制台
                        </el-dropdown-item>
                        <el-dropdown-item divided command="logout">
                            <el-icon>
                                <SwitchButton />
                            </el-icon>退出登录
                        </el-dropdown-item>
                    </el-dropdown-menu>
                </template>
            </el-dropdown>
        </div>
    </el-menu>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { User, Plus, ArrowDown, Tickets, SwitchButton, Bell, Discount, Trophy, Setting, QuestionFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

export default {
    name: 'AppHeader',
    components: {
        User,
        Plus,
        ArrowDown,
        Tickets,
        SwitchButton,
        Bell,
        Discount,
        Trophy,
        Setting,
        QuestionFilled
    },
    setup() {
        const router = useRouter()
        const userName = ref('')
        const userAvatar = ref('')
        const unreadCount = ref(0)
        const userRole = ref('')
        const isLoggedIn = ref(false)

        // 初始化登录状态
        isLoggedIn.value = !!localStorage.getItem('token')

        const isAdmin = computed(() => {
            return userRole.value === 'admin'
        })

        // 获取未读消息数量
        const fetchUnreadMessages = async () => {
            if (isLoggedIn.value) {
                try {
                    // 由于API不存在，直接使用模拟数据
                    unreadCount.value = 0;
                    console.log('使用模拟的未读消息数量:', unreadCount.value);
                } catch (error) {
                    console.error('获取未读消息数量失败:', error);
                    unreadCount.value = 0;
                }
            }
        }

        const fetchUserInfo = async () => {
            // 先检查是否有token，没有则直接返回，不尝试请求API
            const token = localStorage.getItem('token');
            if (!token) {
                isLoggedIn.value = false;
                return;
            }

            isLoggedIn.value = true;
            try {
                // 从本地存储获取基本信息
                userName.value = localStorage.getItem('username') || '用户'
                userRole.value = localStorage.getItem('role') || 'user'

                // 使用axios直接请求而不是通过API服务
                try {
                    const response = await axios.get('http://127.0.0.1:8000/api/accounts/profile/', {
                        headers: {
                            'Authorization': `Token ${token}`
                        }
                    });

                    if (response.data) {
                        userName.value = response.data.username || userName.value
                        userRole.value = response.data.role || userRole.value
                        userAvatar.value = response.data.avatar || ''
                    }
                } catch (error) {
                    // 如果是401错误，说明token无效，需要退出登录
                    if (error.response && error.response.status === 401) {
                        console.log('Token无效，已自动退出登录');
                        localStorage.removeItem('token');
                        localStorage.removeItem('user_id');
                        localStorage.removeItem('username');
                        localStorage.removeItem('role');
                        isLoggedIn.value = false;
                    } else {
                        console.error('获取用户信息失败:', error);
                    }
                }
            } catch (error) {
                console.error('获取用户信息处理失败:', error)
                // 使用默认值或本地存储的基本信息
            }
        }

        const goToLogin = () => {
            router.push('/login')
        }

        const goToRegister = () => {
            router.push('/register')
        }

        const handleCommand = async (command) => {
            if (command === 'logout') {
                try {
                    await axios.post('http://127.0.0.1:8000/api/accounts/logout/', null, {
                        headers: {
                            'Authorization': `Token ${localStorage.getItem('token')}`
                        }
                    })
                    // 清除本地存储的token和用户信息
                    localStorage.removeItem('token')
                    localStorage.removeItem('user_id')
                    localStorage.removeItem('username')
                    localStorage.removeItem('role')
                    ElMessage.success('已成功退出登录')
                    // 跳转到首页
                    router.push('/')
                } catch (error) {
                    console.error('退出登录失败:', error)
                    ElMessage.error('退出登录失败，请重试')
                }
            } else if (command === 'profile') {
                router.push('/profile')
            } else if (command === 'orders') {
                router.push('/orders')
            } else if (command === 'messages') {
                router.push('/notifications')
            } else if (command === 'points') {
                router.push('/points')
            } else if (command === 'promotions') {
                router.push('/promotions')
            } else if (command === 'help') {
                router.push('/help')
            } else if (command === 'admin') {
                router.push('/admin')
            }
        }

        onMounted(() => {
            fetchUserInfo()
            fetchUnreadMessages()
        })

        return {
            userName,
            userAvatar,
            isLoggedIn,
            isAdmin,
            unreadCount,
            goToLogin,
            goToRegister,
            handleCommand
        }
    }
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Righteous&display=swap');

/* 移除所有元素获取焦点时的轮廓 */
:deep(*) {
    outline: none !important;
}

:deep(.el-dropdown-menu__item:focus),
:deep(.el-dropdown-menu__item:active),
:deep(.el-menu-item:focus),
:deep(.el-menu-item:active),
:deep(.el-sub-menu__title:focus),
:deep(.el-sub-menu__title:active),
.user-dropdown-link:focus,
.user-dropdown-link:active {
    outline: none !important;
    border-color: transparent !important;
    box-shadow: none !important;
}

.header {
    width: 100%;
    height: 60px;
    line-height: 60px;
    box-shadow: 0 1px 5px rgba(0, 0, 0, 0.1);
    overflow: visible;
    background: linear-gradient(to right, rgba(255, 255, 255, 0.9), rgba(250, 250, 252, 0.9));
    backdrop-filter: blur(10px);
    border-bottom: 1px solid rgba(0, 201, 255, 0.1);
}

/* 美化菜单项 */
.el-menu-item {
    padding: 0 24px;
    transition: all 0.3s cubic-bezier(0.25, 0.8, 0.5, 1);
    position: relative;
    overflow: hidden;
}

.el-menu-item a {
    font-size: 15px;
    font-weight: 500;
    letter-spacing: 0.5px;
    color: #606266;
    text-decoration: none;
    display: block;
    transition: all 0.3s ease;
}

.el-menu-item:hover a {
    color: #2979FF;
    transform: translateY(-2px);
    text-shadow: 0 2px 4px rgba(41, 121, 255, 0.2);
}

.el-menu-item::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 50%;
    width: 0;
    height: 3px;
    background: linear-gradient(90deg, #2979FF, #00C9FF);
    transition: all 0.3s ease;
    transform: translateX(-50%);
    border-radius: 3px;
    opacity: 0;
}

.el-menu-item:hover::after {
    width: 60%;
    opacity: 1;
}

.el-menu-item.is-active::after {
    width: 70%;
    opacity: 1;
}

.el-menu-item.is-active a {
    color: #2979FF;
    font-weight: 600;
}

.el-menu-item::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: radial-gradient(circle at center, rgba(41, 121, 255, 0.1) 0%, transparent 70%);
    opacity: 0;
    transition: opacity 0.5s ease;
    z-index: -1;
}

.el-menu-item:hover::before {
    opacity: 1;
}

.logo-item h1 {
    font-family: 'Righteous', cursive;
    background: linear-gradient(135deg, #2979FF 0%, #00C9FF 50%, #11998e 100%);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-size: 36px;
    font-weight: normal;
    margin: 0;
    letter-spacing: 3px;
    text-shadow: 0 0 5px rgba(0, 201, 255, 0.3), 0 0 10px rgba(0, 201, 255, 0.2);
    position: relative;
    transition: all 0.5s ease;
    transform: perspective(800px) rotateX(8deg);
    animation: float 6s ease-in-out infinite;
}

.message-badge {
    display: flex;
    align-items: center;
}

@keyframes float {
    0% {
        transform: perspective(800px) rotateX(8deg) translateY(0px);
    }

    50% {
        transform: perspective(800px) rotateX(8deg) translateY(-6px);
    }

    100% {
        transform: perspective(800px) rotateX(8deg) translateY(0px);
    }
}

.logo-item h1::after {
    content: "";
    position: absolute;
    width: 100%;
    height: 4px;
    bottom: -4px;
    left: 0;
    background: linear-gradient(90deg, transparent 0%, #00C9FF 50%, transparent 100%);
    transform: scaleX(0.5);
    opacity: 0.7;
    transform-origin: center;
    transition: transform 0.5s ease, opacity 0.5s ease;
    border-radius: 4px;
    filter: blur(2px);
}

.logo-item:hover h1::after {
    transform: scaleX(1);
    opacity: 1;
}

.logo-item:hover h1 {
    letter-spacing: 4px;
}

.logo-item h1::before {
    content: "✈";
    margin-right: 8px;
    font-size: 26px;
    vertical-align: middle;
    -webkit-text-fill-color: #00C9FF;
    display: inline-block;
    filter: drop-shadow(0 0 2px rgba(0, 201, 255, 0.7));
    animation: fly 3s ease-in-out infinite;
}

@keyframes fly {
    0% {
        transform: translateY(0) rotate(0deg);
    }

    50% {
        transform: translateY(-3px) rotate(5deg);
    }

    100% {
        transform: translateY(0) rotate(0deg);
    }
}

.el-menu--horizontal>.logo-item {
    margin-right: auto;
    padding-left: 30px;
    height: 60px;
    line-height: 60px;
}

.login-container,
.user-container {
    display: flex;
    align-items: center;
    padding-right: 20px;
    gap: 16px;
}

.el-menu-item,
.el-sub-menu__title {
    height: 60px;
    line-height: 60px;
}

/* 管理员菜单美化 */
.admin-menu {
    background-color: #2979FF;
    color: white;
    font-weight: bold;
    border-radius: 4px;
    margin-top: 5px;
    box-shadow: 0 4px 12px rgba(41, 121, 255, 0.3);
    overflow: hidden;
}

.admin-menu :deep(.el-sub-menu__title) {
    color: white;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}

.admin-menu :deep(.el-sub-menu__title:hover) {
    background-color: #1E69E3;
    opacity: 0.9;
    transform: translateY(-1px);
}

.admin-menu :deep(.el-sub-menu__title::before) {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
    transition: left 0.6s ease;
}

.admin-menu :deep(.el-sub-menu__title:hover::before) {
    left: 100%;
}

/* 登录和注册按钮样式 */
.login-btn,
.register-btn {
    border: none;
    height: 36px;
    border-radius: 18px;
    padding: 0 20px;
    font-size: 14px;
    font-weight: 500;
    letter-spacing: 0.5px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
    box-shadow: 0 3px 6px rgba(0, 0, 0, 0.1);
    line-height: 1;
}

.login-btn {
    background: linear-gradient(135deg, #2979FF, #00C9FF);
    color: white;
}

.register-btn {
    background: white;
    color: #2979FF;
    border: 1px solid rgba(41, 121, 255, 0.3);
}

.login-btn:hover,
.register-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.15);
}

.login-btn:active,
.register-btn:active {
    transform: translateY(1px);
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.login-btn:hover {
    background: linear-gradient(135deg, #1E69E3, #00B4E6);
}

.register-btn:hover {
    background: rgba(41, 121, 255, 0.05);
    border-color: rgba(41, 121, 255, 0.5);
}

.btn-content {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
}

.login-btn .el-icon,
.register-btn .el-icon {
    margin-right: 6px;
    font-size: 16px;
}

.login-btn span,
.register-btn span {
    font-size: 14px;
}

.login-btn::before,
.register-btn::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
    transition: left 0.6s ease;
}

.login-btn:hover::before,
.register-btn:hover::before {
    left: 100%;
}

/* 用户下拉菜单样式 */
.user-dropdown-link {
    display: flex;
    align-items: center;
    cursor: pointer;
    padding: 0 12px;
    height: 40px;
    border-radius: 20px;
    transition: all 0.3s ease;
    background-color: rgba(41, 121, 255, 0.08);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    border: none;
}

.user-dropdown-link:hover {
    background-color: rgba(41, 121, 255, 0.15);
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(41, 121, 255, 0.15);
}

.user-avatar {
    margin-right: 10px;
    border: 2px solid #fff;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
    transition: all 0.3s ease;
}

.user-dropdown-link:hover .user-avatar {
    box-shadow: 0 3px 8px rgba(41, 121, 255, 0.3);
    transform: scale(1.05);
}

.user-name {
    font-size: 14px;
    margin-right: 6px;
    max-width: 100px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    font-weight: 500;
    color: #2979FF;
    transition: all 0.3s ease;
}

.user-dropdown-link:hover .user-name {
    color: #1E69E3;
}

.user-dropdown-link .el-icon {
    transition: all 0.3s ease;
    color: #2979FF;
}

.user-dropdown-link:hover .el-icon {
    transform: rotate(180deg);
    color: #1E69E3;
}

.el-dropdown-menu {
    padding: 8px 0;
    border-radius: 12px;
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.12), 0 3px 6px rgba(0, 0, 0, 0.08);
    border: none;
    min-width: 160px;
}

.el-dropdown-menu :deep(.el-dropdown-menu__item) {
    padding: 10px 16px;
    font-size: 14px;
    display: flex;
    align-items: center;
    line-height: 1.5;
    transition: all 0.3s ease;
}

.el-dropdown-menu :deep(.el-dropdown-menu__item:hover) {
    background-color: rgba(41, 121, 255, 0.08);
    color: #2979FF;
}

.el-dropdown-menu :deep(.el-dropdown-menu__item.is-disabled) {
    color: #C0C4CC;
}

.el-dropdown-menu :deep(.el-dropdown-menu__item--divided) {
    margin-top: 8px;
    border-top: 1px solid rgba(41, 121, 255, 0.1);
    padding-top: 12px;
}

.el-dropdown-menu .el-icon {
    margin-right: 10px;
    font-size: 18px;
    color: #2979FF;
}

@media (max-width: 768px) {

    .login-btn span,
    .register-btn span,
    .user-name {
        display: none;
    }

    .login-container,
    .user-container {
        padding-right: 10px;
    }

    .login-btn,
    .register-btn {
        padding: 0 12px;
    }

    .login-btn .el-icon,
    .register-btn .el-icon {
        margin-right: 0;
    }
}
</style>