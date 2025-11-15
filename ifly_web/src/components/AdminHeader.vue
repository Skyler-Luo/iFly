<template>
    <div class="admin-header">
        <div class="left-section">
            <button class="toggle-menu" @click="toggleSidebar">
                <i class="fas fa-bars"></i>
            </button>
            <div class="page-title">{{ pageTitle }}</div>
        </div>

        <div class="right-section">
            <div class="header-search">
                <input type="text" placeholder="搜索..." />
                <i class="fas fa-search"></i>
            </div>

            <div class="header-actions">
                <div class="action-item notifications" @click="toggleNotifications">
                    <i class="fas fa-bell"></i>
                    <div v-if="unreadNotifications" class="badge">{{ unreadNotifications }}</div>

                    <div class="dropdown-menu notifications-menu" v-show="showNotifications">
                        <div class="dropdown-header">
                            <span>通知</span>
                            <button class="mark-all-read" @click.stop="markAllAsRead">全部已读</button>
                        </div>
                        <div class="dropdown-body">
                            <div v-if="notifications.length === 0" class="empty-state">
                                暂无通知
                            </div>
                            <div v-else class="notification-list">
                                <div v-for="notification in notifications" :key="notification.id"
                                    class="notification-item" :class="{ 'unread': !notification.read }"
                                    @click="readNotification(notification)">
                                    <div class="notification-icon" :class="'type-' + notification.type">
                                        <i :class="getNotificationIcon(notification.type)"></i>
                                    </div>
                                    <div class="notification-content">
                                        <div class="notification-text">{{ notification.message }}</div>
                                        <div class="notification-time">{{ notification.time }}</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="dropdown-footer">
                            <button class="view-all" @click="viewAllNotifications">查看全部</button>
                        </div>
                    </div>
                </div>

                <div class="action-item admin-dropdown" @click="toggleUserMenu">
                    <div class="admin-name">管理员</div>
                    <i class="fas fa-chevron-down"></i>

                    <div class="dropdown-menu user-menu" v-show="showUserMenu">
                        <router-link to="/admin/profile" class="dropdown-item">
                            <i class="fas fa-user"></i> 个人资料
                        </router-link>
                        <router-link to="/admin/settings" class="dropdown-item">
                            <i class="fas fa-cog"></i> 设置
                        </router-link>
                        <div class="dropdown-divider"></div>
                        <button class="dropdown-item" @click="logout">
                            <i class="fas fa-sign-out-alt"></i> 退出登录
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: 'AdminHeader',
    props: {
        pageTitle: {
            type: String,
            default: '管理中心'
        }
    },
    data() {
        return {
            showNotifications: false,
            showUserMenu: false,
            notifications: [
                {
                    id: 1,
                    type: 'alert',
                    message: '系统检测到异常访问，请及时查看',
                    time: '10分钟前',
                    read: false
                },
                {
                    id: 2,
                    type: 'info',
                    message: '今日有5个新用户注册',
                    time: '1小时前',
                    read: false
                },
                {
                    id: 3,
                    type: 'success',
                    message: '备份任务已完成',
                    time: '2小时前',
                    read: true
                }
            ]
        }
    },
    computed: {
        unreadNotifications() {
            return this.notifications.filter(n => !n.read).length
        }
    },
    methods: {
        toggleSidebar() {
            this.$emit('toggle-sidebar')
        },
        toggleNotifications() {
            this.showNotifications = !this.showNotifications
            if (this.showUserMenu) this.showUserMenu = false
        },
        toggleUserMenu() {
            this.showUserMenu = !this.showUserMenu
            if (this.showNotifications) this.showNotifications = false
        },
        getNotificationIcon(type) {
            const icons = {
                'alert': 'fas fa-exclamation-triangle',
                'info': 'fas fa-info-circle',
                'success': 'fas fa-check-circle'
            }
            return icons[type] || 'fas fa-bell'
        },
        markAllAsRead() {
            this.notifications.forEach(notification => {
                notification.read = true
            })
        },
        readNotification(notification) {
            notification.read = true
            // 在实际应用中，这里应该导航到对应的页面或打开详情
            console.log('查看通知:', notification)
        },
        viewAllNotifications() {
            // 导航到通知页面
            console.log('查看全部通知')
            this.showNotifications = false
        },
        logout() {
            // 实际应用中，这里应该调用登出API
            console.log('退出登录')
            // this.$router.push('/login')
        }
    },
    mounted() {
        // 点击外部关闭下拉菜单
        document.addEventListener('click', (e) => {
            const notificationsArea = document.querySelector('.notifications')
            const userMenuArea = document.querySelector('.admin-dropdown')

            if (notificationsArea && !notificationsArea.contains(e.target)) {
                this.showNotifications = false
            }

            if (userMenuArea && !userMenuArea.contains(e.target)) {
                this.showUserMenu = false
            }
        })
    }
}
</script>

<style scoped>
.admin-header {
    height: 60px;
    background-color: white;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 20px;
    position: fixed;
    top: 0;
    right: 0;
    left: 250px;
    z-index: 100;
}

.left-section {
    display: flex;
    align-items: center;
}

.toggle-menu {
    background: none;
    border: none;
    width: 40px;
    height: 40px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    margin-right: 15px;
    color: #555;
    transition: all 0.3s;
}

.toggle-menu:hover {
    background-color: #f5f5f5;
    color: #333;
}

.page-title {
    font-size: 18px;
    font-weight: 500;
    color: #333;
}

.right-section {
    display: flex;
    align-items: center;
}

.header-search {
    position: relative;
    margin-right: 20px;
}

.header-search input {
    border: none;
    background-color: #f5f5f5;
    border-radius: 20px;
    padding: 8px 35px 8px 15px;
    font-size: 14px;
    width: 200px;
    transition: all 0.3s;
}

.header-search input:focus {
    width: 250px;
    outline: none;
    box-shadow: 0 0 0 2px rgba(63, 81, 181, 0.2);
}

.header-search i {
    position: absolute;
    right: 12px;
    top: 50%;
    transform: translateY(-50%);
    color: #777;
}

.header-actions {
    display: flex;
    align-items: center;
}

.action-item {
    position: relative;
    margin-left: 15px;
}

.notifications {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    color: #555;
    transition: all 0.3s;
}

.notifications:hover {
    background-color: #f5f5f5;
    color: #333;
}

.badge {
    position: absolute;
    top: 3px;
    right: 3px;
    background-color: #f44336;
    color: white;
    font-size: 10px;
    width: 16px;
    height: 16px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
}

.admin-dropdown {
    display: flex;
    align-items: center;
    cursor: pointer;
    padding: 5px 10px;
    border-radius: 20px;
    transition: all 0.3s;
}

.admin-dropdown:hover {
    background-color: #f5f5f5;
}

.admin-name {
    margin-right: 5px;
    font-weight: 500;
}

.dropdown-menu {
    position: absolute;
    top: 100%;
    right: 0;
    background-color: white;
    border-radius: 4px;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
    margin-top: 10px;
    min-width: 220px;
    z-index: 1000;
}

.dropdown-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 15px;
    border-bottom: 1px solid #f0f0f0;
}

.dropdown-header span {
    font-weight: bold;
    font-size: 16px;
}

.mark-all-read {
    background: none;
    border: none;
    color: #3f51b5;
    cursor: pointer;
    font-size: 14px;
}

.dropdown-body {
    max-height: 300px;
    overflow-y: auto;
}

.empty-state {
    padding: 30px 15px;
    text-align: center;
    color: #999;
}

.notification-list {
    padding: 10px 0;
}

.notification-item {
    padding: 12px 15px;
    display: flex;
    align-items: center;
    cursor: pointer;
    transition: background-color 0.3s;
}

.notification-item:hover {
    background-color: #f9f9f9;
}

.notification-item.unread {
    background-color: #f0f7ff;
}

.notification-icon {
    width: 30px;
    height: 30px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 10px;
}

.type-alert {
    background-color: rgba(244, 67, 54, 0.1);
    color: #f44336;
}

.type-info {
    background-color: rgba(33, 150, 243, 0.1);
    color: #2196f3;
}

.type-success {
    background-color: rgba(76, 175, 80, 0.1);
    color: #4caf50;
}

.notification-content {
    flex: 1;
}

.notification-text {
    font-size: 14px;
    margin-bottom: 5px;
}

.notification-time {
    font-size: 12px;
    color: #999;
}

.dropdown-footer {
    padding: 10px 15px;
    text-align: center;
    border-top: 1px solid #f0f0f0;
}

.view-all {
    background: none;
    border: none;
    color: #3f51b5;
    cursor: pointer;
    font-weight: 500;
}

.dropdown-item {
    padding: 12px 15px;
    display: flex;
    align-items: center;
    color: #333;
    text-decoration: none;
    transition: background-color 0.3s;
}

.dropdown-item:hover {
    background-color: #f5f5f5;
}

.dropdown-item i {
    width: 20px;
    margin-right: 10px;
}

.dropdown-divider {
    height: 1px;
    background-color: #f0f0f0;
    margin: 5px 0;
}

@media (max-width: 768px) {
    .admin-header {
        left: 70px;
    }

    .header-search {
        display: none;
    }

    .admin-name {
        display: none;
    }
}
</style>