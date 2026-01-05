<template>
  <el-menu
    class="header"
    mode="horizontal"
    :ellipsis="false"
    role="navigation"
    aria-label="主导航菜单"
  >
    <el-menu-item index="0" class="logo-item">
      <router-link to="/" aria-label="返回首页">
        <h1>iFly</h1>
      </router-link>
    </el-menu-item>
    <el-menu-item index="1">
      <router-link to="/" aria-label="前往首页">首页</router-link>
    </el-menu-item>
    <el-menu-item index="2" v-if="isLoggedIn">
      <router-link to="/orders">我的订单</router-link>
    </el-menu-item>

    <!-- 管理员菜单 -->
    <el-sub-menu
      index="3"
      v-if="isAdmin"
      class="admin-menu"
      aria-label="管理员菜单"
    >
      <template #title>管理控制台</template>
      <el-menu-item index="3-1">
        <router-link to="/admin">控制台首页</router-link>
      </el-menu-item>
      <el-menu-item index="3-2">
        <router-link to="/admin/flights">航班管理</router-link>
      </el-menu-item>
      <el-menu-item index="3-3">
        <router-link to="/admin/users">用户管理</router-link>
      </el-menu-item>
      <el-menu-item index="3-4">
        <router-link to="/admin/orders">订单管理</router-link>
      </el-menu-item>
      <el-menu-item index="3-5">
        <router-link to="/admin/settings">系统设置</router-link>
      </el-menu-item>
    </el-sub-menu>

    <!-- 未登录状态 -->
    <div class="login-container" v-if="!isLoggedIn">
      <el-button class="login-btn" @click="goToLogin" aria-label="用户登录">
        <div class="btn-content">
          <el-icon>
            <User />
          </el-icon>
          <span>登录</span>
        </div>
      </el-button>
      <el-button
        class="register-btn"
        @click="goToRegister"
        aria-label="用户注册"
      >
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
                <User /> </el-icon
              >个人中心
            </el-dropdown-item>
            <el-dropdown-item command="messages">
              <el-badge
                :value="unreadCount"
                :hidden="unreadCount === 0"
                class="message-badge"
              >
                <el-icon>
                  <Bell /> </el-icon
                >消息中心
              </el-badge>
            </el-dropdown-item>
            <el-dropdown-item command="orders">
              <el-icon>
                <Tickets /> </el-icon
              >我的订单
            </el-dropdown-item>
            <el-dropdown-item v-if="isAdmin" command="admin">
              <el-icon>
                <Setting /> </el-icon
              >管理控制台
            </el-dropdown-item>
            <el-dropdown-item divided command="logout">
              <el-icon>
                <SwitchButton /> </el-icon
              >退出登录
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </el-menu>
</template>

<script>
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import {
  User,
  Plus,
  ArrowDown,
  Tickets,
  SwitchButton,
  Bell,
  Setting
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import api from '@/services/api'
import tokenManager from '@/utils/tokenManager'

export default {
  name: 'AppHeader',
  components: {
    User,
    Plus,
    ArrowDown,
    Tickets,
    SwitchButton,
    Bell,
    Setting
  },
  setup() {
    const router = useRouter()
    const route = useRoute()
    const userName = ref('')
    const userAvatar = ref('')
    const unreadCount = ref(0)
    const userRole = ref('')
    const isLoggedIn = ref(false)

    // 初始化登录状态
    isLoggedIn.value = tokenManager.isAuthenticated()

    const isAdmin = computed(() => {
      return userRole.value === 'admin'
    })

    // 获取未读消息数量
    const fetchUnreadMessages = async () => {
      if (isLoggedIn.value) {
        try {
          const token = tokenManager.getToken()
          if (!token) {
            unreadCount.value = 0
            return
          }
          const response = await api.userMessages.getUnreadCount()
          // API 返回格式为 { count: number }，axios 拦截器可能已解包 data
          unreadCount.value = response?.count ?? response?.data?.count ?? 0
        } catch (error) {
          // 静默处理错误，显示 0
          console.error('获取未读消息数量失败:', error)
          unreadCount.value = 0
        }
      }
    }

    const fetchUserInfo = async () => {
      // 使用 tokenManager 检查认证状态
      const token = tokenManager.getToken()
      if (!token) {
        isLoggedIn.value = false
        return
      }

      isLoggedIn.value = true
      try {
        // 从 tokenManager 获取用户信息
        const user = tokenManager.getUser()
        if (user) {
          userName.value = user.username || '用户'
          userRole.value = user.role || 'user'
        }

        // 尝试从 API 获取最新信息
        try {
          const response = await api.accounts.getProfile()

          // 响应拦截器已解包 data，response 即为用户数据
          if (response) {
            userName.value = response.username || userName.value
            userRole.value = response.role || userRole.value
            userAvatar.value = response.avatar_url || response.avatar || ''
          }
        } catch (error) {
          // 如果是401错误，说明token无效，需要退出登录
          if (error.status === 401) {
            tokenManager.clearToken()
            isLoggedIn.value = false
          }
          // 其他错误静默处理，使用本地存储的基本信息
        }
      } catch {
        // 使用默认值或本地存储的基本信息
      }
    }

    const goToLogin = () => {
      router.push('/login')
    }

    const goToRegister = () => {
      router.push('/register')
    }

    const handleCommand = async command => {
      if (command === 'logout') {
        try {
          const token = tokenManager.getToken()
          if (token) {
            try {
              await api.accounts.logout()
            } catch (apiError) {
              // 忽略 API 错误，继续清除本地状态
              console.warn('登出API调用失败:', apiError)
            }
          }
          // 清除认证信息
          tokenManager.clearToken()
          ElMessage.success('已成功退出登录')
          // 触发登出事件
          window.dispatchEvent(new CustomEvent('user-logout'))
          // 跳转到首页
          router.push('/')
        } catch (error) {
          console.error('登出过程出错:', error)
          // 即使出错也清除本地状态
          tokenManager.clearToken()
          window.dispatchEvent(new CustomEvent('user-logout'))
          router.push('/')
        }
      } else if (command === 'profile') {
        router.push('/profile')
      } else if (command === 'orders') {
        router.push('/orders')
      } else if (command === 'messages') {
        router.push('/notifications')
      } else if (command === 'admin') {
        router.push('/admin')
      }
    }

    // 监听登录事件
    const handleUserLogin = () => {
      isLoggedIn.value = true
      fetchUserInfo()
      fetchUnreadMessages()
    }

    // 监听登出事件
    const handleUserLogout = () => {
      isLoggedIn.value = false
      userName.value = ''
      userAvatar.value = ''
      userRole.value = ''
      unreadCount.value = 0
    }

    // 监听路由变化，重新检查登录状态
    watch(
      () => route.path,
      () => {
        const wasLoggedIn = isLoggedIn.value
        const nowLoggedIn = tokenManager.isAuthenticated()
        if (wasLoggedIn !== nowLoggedIn) {
          isLoggedIn.value = nowLoggedIn
          if (nowLoggedIn) {
            fetchUserInfo()
            fetchUnreadMessages()
          }
        }
      }
    )

    onMounted(() => {
      fetchUserInfo()
      fetchUnreadMessages()
      // 监听登录/登出事件
      window.addEventListener('user-login', handleUserLogin)
      window.addEventListener('user-logout', handleUserLogout)
    })

    // 组件卸载时移除事件监听
    onBeforeUnmount(() => {
      window.removeEventListener('user-login', handleUserLogin)
      window.removeEventListener('user-logout', handleUserLogout)
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
  background: linear-gradient(
    to right,
    rgba(255, 255, 255, 0.9),
    rgba(250, 250, 252, 0.9)
  );
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(0, 201, 255, 0.1);
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
}

:deep(.header.el-menu--horizontal) {
  --el-menu-active-border-bottom-color: transparent;
  --el-menu-hover-border-bottom-color: transparent;
}

:deep(.header.el-menu--horizontal > .el-menu-item),
:deep(.header.el-menu--horizontal > .el-sub-menu) {
  border-bottom: none;
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
  color: #2979ff;
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
  background: linear-gradient(90deg, #2979ff, #00c9ff);
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
  color: #2979ff;
  font-weight: 600;
}

.el-menu-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: radial-gradient(
    circle at center,
    rgba(41, 121, 255, 0.1) 0%,
    transparent 70%
  );
  opacity: 0;
  transition: opacity 0.5s ease;
  z-index: -1;
}

.el-menu-item:hover::before {
  opacity: 1;
}

.logo-item h1 {
  font-family: 'Comic Sans MS', 'Comic Sans', cursive;
  background: linear-gradient(135deg, #2979ff 0%, #00c9ff 50%, #11998e 100%);
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
  content: '';
  position: absolute;
  width: 100%;
  height: 4px;
  bottom: -4px;
  left: 0;
  background: linear-gradient(
    90deg,
    transparent 0%,
    #00c9ff 50%,
    transparent 100%
  );
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
  content: '✈';
  margin-right: 8px;
  font-size: 26px;
  vertical-align: middle;
  -webkit-text-fill-color: #00c9ff;
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

.el-menu--horizontal > .logo-item {
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

/* 管理员菜单 */
.admin-menu :deep(.el-sub-menu__title) {
  font-size: 15px;
  font-weight: 500;
  letter-spacing: 0.5px;
  color: #606266;
  transition: all 0.3s ease;
}

.admin-menu :deep(.el-sub-menu__title:hover) {
  color: #2979ff;
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
  background: linear-gradient(135deg, #2979ff, #00c9ff);
  color: white;
}

.register-btn {
  background: white;
  color: #2979ff;
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
  background: linear-gradient(135deg, #1e69e3, #00b4e6);
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
  background: linear-gradient(
    90deg,
    transparent,
    rgba(255, 255, 255, 0.2),
    transparent
  );
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
  color: #2979ff;
  transition: all 0.3s ease;
}

.user-dropdown-link:hover .user-name {
  color: #1e69e3;
}

.user-dropdown-link .el-icon {
  transition: all 0.3s ease;
  color: #2979ff;
}

.user-dropdown-link:hover .el-icon {
  transform: rotate(180deg);
  color: #1e69e3;
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
  color: #2979ff;
}

.el-dropdown-menu :deep(.el-dropdown-menu__item.is-disabled) {
  color: #c0c4cc;
}

.el-dropdown-menu :deep(.el-dropdown-menu__item--divided) {
  margin-top: 8px;
  border-top: 1px solid rgba(41, 121, 255, 0.1);
  padding-top: 12px;
}

.el-dropdown-menu .el-icon {
  margin-right: 10px;
  font-size: 18px;
  color: #2979ff;
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
