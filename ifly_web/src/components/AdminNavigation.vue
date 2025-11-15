<template>
    <div class="admin-navigation">
        <div class="admin-logo">
            <img src="../assets/logo.png" alt="iFly Logo" />
            <span>iFly 管理中心</span>
        </div>

        <nav class="nav-menu">
            <router-link to="/admin/dashboard" class="nav-item" active-class="active">
                <i class="fas fa-tachometer-alt"></i>
                <span>控制面板</span>
            </router-link>

            <router-link to="/admin/flights" class="nav-item" active-class="active">
                <i class="fas fa-plane"></i>
                <span>航班管理</span>
            </router-link>

            <router-link to="/admin/users" class="nav-item" active-class="active">
                <i class="fas fa-users"></i>
                <span>用户管理</span>
            </router-link>

            <router-link to="/admin/orders" class="nav-item" active-class="active">
                <i class="fas fa-shopping-cart"></i>
                <span>订单管理</span>
            </router-link>

            <router-link to="/admin/flight-analytics" class="nav-item" active-class="active">
                <i class="fas fa-chart-line"></i>
                <span>航班分析</span>
            </router-link>

            <router-link to="/admin/revenue" class="nav-item" active-class="active">
                <i class="fas fa-money-bill-wave"></i>
                <span>收入管理</span>
            </router-link>

            <router-link to="/admin/promotions" class="nav-item" active-class="active">
                <i class="fas fa-tags"></i>
                <span>优惠管理</span>
            </router-link>

            <router-link to="/admin/settings" class="nav-item" active-class="active">
                <i class="fas fa-cogs"></i>
                <span>系统设置</span>
            </router-link>
        </nav>

        <div class="admin-info">
            <div class="admin-avatar">
                <img src="../assets/admin-avatar.jpg" alt="Admin" />
            </div>
            <div class="admin-details">
                <div class="admin-name">管理员</div>
                <div class="admin-role">超级管理员</div>
            </div>
            <div class="admin-actions">
                <button class="action-button">
                    <i class="fas fa-sign-out-alt"></i>
                </button>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: 'AdminNavigation'
}
</script>

<style scoped>
.admin-navigation {
    background-color: #2c3e50;
    color: white;
    width: 250px;
    height: 100vh;
    display: flex;
    flex-direction: column;
    position: fixed;
    left: 0;
    top: 0;
}

.admin-logo {
    padding: 20px;
    display: flex;
    align-items: center;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.admin-logo img {
    width: 40px;
    height: 40px;
    margin-right: 10px;
}

.admin-logo span {
    font-size: 18px;
    font-weight: bold;
}

.nav-menu {
    flex: 1;
    padding: 20px 0;
    overflow-y: auto;
}

.nav-item {
    display: flex;
    align-items: center;
    padding: 15px 20px;
    color: rgba(255, 255, 255, 0.7);
    text-decoration: none;
    transition: all 0.3s;
}

.nav-item:hover {
    background-color: rgba(255, 255, 255, 0.1);
    color: white;
}

.nav-item.active {
    background-color: #3f51b5;
    color: white;
    border-left: 4px solid #ff9800;
}

.nav-item i {
    margin-right: 15px;
    width: 20px;
    text-align: center;
}

.admin-info {
    padding: 15px 20px;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
    display: flex;
    align-items: center;
}

.admin-avatar {
    width: 40px;
    height: 40px;
    overflow: hidden;
    border-radius: 50%;
    margin-right: 10px;
}

.admin-avatar img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.admin-details {
    flex: 1;
}

.admin-name {
    font-weight: bold;
}

.admin-role {
    font-size: 12px;
    color: rgba(255, 255, 255, 0.7);
}

.admin-actions {
    display: flex;
}

.action-button {
    background: none;
    border: none;
    color: rgba(255, 255, 255, 0.7);
    cursor: pointer;
    font-size: 16px;
    padding: 5px;
    transition: all 0.3s;
}

.action-button:hover {
    color: white;
}

@media (max-width: 768px) {
    .admin-navigation {
        width: 70px;
    }

    .admin-logo span,
    .nav-item span,
    .admin-details {
        display: none;
    }

    .admin-logo {
        justify-content: center;
    }

    .admin-logo img {
        margin-right: 0;
    }

    .nav-item {
        justify-content: center;
        padding: 15px 0;
    }

    .nav-item i {
        margin-right: 0;
        font-size: 18px;
    }

    .admin-info {
        justify-content: center;
        padding: 15px 0;
    }

    .admin-avatar {
        margin-right: 0;
    }
}
</style>