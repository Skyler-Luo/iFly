<template>
    <div class="admin-layout" :class="{ 'sidebar-collapsed': sidebarCollapsed }">
        <AdminNavigation />
        <div class="admin-content">
            <AdminHeader :pageTitle="currentPageTitle" @toggle-sidebar="toggleSidebar" />
            <main class="content-area">
                <slot></slot>
            </main>
            <footer class="admin-footer">
                <div class="copyright">
                    &copy; {{ currentYear }} iFly 航空 · 管理系统 v1.0
                </div>
            </footer>
        </div>
    </div>
</template>

<script>
import AdminNavigation from './AdminNavigation.vue'
import AdminHeader from './AdminHeader.vue'

export default {
    name: 'AdminLayout',
    components: {
        AdminNavigation,
        AdminHeader
    },
    data() {
        return {
            sidebarCollapsed: false,
            currentYear: new Date().getFullYear()
        }
    },
    computed: {
        currentPageTitle() {
            // 获取当前路由对应的标题
            // 在实际应用中可以根据路由名称或路径映射到相应的中文标题
            const routeTitles = {
                'admin-dashboard': '控制面板',
                'admin-flights': '航班管理',
                'admin-flight-passengers': '航班乘客管理',
                'admin-users': '用户管理',
                'admin-orders': '订单管理',
                'admin-flight-analytics': '航班数据分析',
                'admin-revenue': '收入管理',
                'admin-promotions': '优惠管理',
                'admin-settings': '系统设置'
            }

            return routeTitles[this.$route.name] || '管理中心'
        }
    },
    methods: {
        toggleSidebar() {
            this.sidebarCollapsed = !this.sidebarCollapsed
        }
    }
}
</script>

<style scoped>
.admin-layout {
    min-height: 100vh;
    display: flex;
}

.admin-content {
    flex: 1;
    padding-left: 250px;
    transition: padding-left 0.3s;
}

.sidebar-collapsed .admin-content {
    padding-left: 70px;
}

.content-area {
    padding: 80px 20px 20px;
    min-height: calc(100vh - 110px);
}

.admin-footer {
    height: 50px;
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: white;
    color: #777;
    font-size: 14px;
    box-shadow: 0 -1px 2px rgba(0, 0, 0, 0.05);
}

@media (max-width: 768px) {
    .admin-content {
        padding-left: 70px;
    }
}
</style>