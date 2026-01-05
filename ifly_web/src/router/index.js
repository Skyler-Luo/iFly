import { createRouter, createWebHashHistory } from 'vue-router'

import tokenManager from '@/utils/tokenManager'

// 核心页面直接导入（首屏加载）
import HomeView from '../views/HomeView.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'

// 其他页面使用懒加载
const BookingView = () => import('../views/BookingView.vue')
const FlightResults = () => import('../views/FlightResults.vue')
const OrderDetail = () => import('../views/OrderDetail.vue')
const UserProfileView = () => import('../views/UserProfileView.vue')
const NotificationView = () => import('../views/NotificationView.vue')

// 管理页面懒加载
const AdminDashboardView = () => import('../views/AdminDashboardView.vue')
const AdminFlightsView = () => import('../views/AdminFlightsView.vue')
const AdminUsersView = () => import('../views/AdminUsersView.vue')

// 错误页面懒加载
const ForbiddenView = () => import('../views/error/ForbiddenView.vue')

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView
  },
  {
    path: '/login',
    name: 'login',
    component: LoginView
  },
  {
    path: '/register',
    name: 'register',
    component: RegisterView
  },
  {
    path: '/flights',
    name: 'flights',
    component: FlightResults
  },
  {
    path: '/booking/:flightId',
    name: 'booking',
    component: BookingView
  },
  {
    path: '/orders/:orderId',
    name: 'orderDetail',
    component: OrderDetail
  },
  {
    path: '/orders',
    name: 'orderList',
    component: () =>
      import(/* webpackChunkName: "orders" */ '../views/OrderList.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/payment/:orderId',
    name: 'payment',
    component: () =>
      import(/* webpackChunkName: "payment" */ '../views/PaymentView.vue')
  },
  {
    path: '/checkin',
    name: 'checkin-search',
    component: () =>
      import(/* webpackChunkName: "checkin" */ '../views/CheckinView.vue')
  },
  {
    path: '/checkin/:ticketId',
    name: 'checkin',
    component: () =>
      import(/* webpackChunkName: "checkin" */ '../views/CheckinView.vue')
  },
  {
    path: '/reschedule/:ticketId',
    name: 'reschedule',
    component: () =>
      import(/* webpackChunkName: "reschedule" */ '../views/RescheduleView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/profile',
    name: 'profile',
    component: UserProfileView,
    meta: { requiresAuth: true }
  },
  {
    path: '/notifications',
    name: 'notifications',
    component: NotificationView,
    meta: { requiresAuth: true }
  },
  {
    path: '/flight-status',
    name: 'flightStatus',
    component: () =>
      import(
        /* webpackChunkName: "flightStatus" */ '../views/FlightStatusView.vue'
      )
  },
  // 管理员路由
  {
    path: '/admin',
    name: 'adminDashboard',
    component: AdminDashboardView,
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/flights',
    name: 'adminFlights',
    component: AdminFlightsView,
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/flights/:flightId/passengers',
    name: 'adminFlightPassengers',
    component: () =>
      import(
        /* webpackChunkName: "adminFlightPassengers" */ '../views/AdminFlightPassengersView.vue'
      ),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/flights/:flightId/pricing',
    name: 'adminFlightPricing',
    component: () =>
      import(
        /* webpackChunkName: "adminFlightPricing" */ '../views/AdminFlightPricingView.vue'
      ),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/users',
    name: 'adminUsers',
    component: AdminUsersView,
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/users/:userId/orders',
    name: 'adminUserOrders',
    component: () =>
      import(
        /* webpackChunkName: "adminUserOrders" */ '../views/AdminUserOrdersView.vue'
      ),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/orders',
    name: 'adminOrders',
    component: () =>
      import(
        /* webpackChunkName: "adminOrders" */ '../views/AdminOrdersView.vue'
      ),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/settings',
    name: 'adminSettings',
    component: () =>
      import(
        /* webpackChunkName: "adminSettings" */ '../views/AdminSettingsView.vue'
      ),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  // 新增数据可视化路由
  {
    path: '/admin/visualization',
    name: 'adminVisualization',
    component: () =>
      import(
        /* webpackChunkName: "adminVisualization" */ '../views/AdminDataVisualizationView.vue'
      ),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/business-intelligence',
    name: 'adminBusinessIntelligence',
    component: () =>
      import(
        /* webpackChunkName: "adminBusinessIntelligence" */ '../views/AdminBusinessIntelligenceView.vue'
      ),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/analytics/flights',
    name: 'adminFlightAnalytics',
    component: () =>
      import(
        /* webpackChunkName: "adminFlightAnalytics" */ '../views/AdminFlightAnalyticsView.vue'
      ),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/analytics/revenue',
    name: 'adminRevenueAnalytics',
    component: () =>
      import(
        /* webpackChunkName: "adminRevenueAnalytics" */ '../views/AdminRevenueView.vue'
      ),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/logs',
    name: 'adminSystemLogs',
    component: () =>
      import(
        /* webpackChunkName: "adminSystemLogs" */ '../views/AdminSystemLogsView.vue'
      ),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  // 错误页面路由
  {
    path: '/403',
    name: 'forbidden',
    component: ForbiddenView,
    meta: {
      title: '权限不足',
      description: '您无权访问此页面'
    }
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
  // 每次导航到新页面时滚动到顶部
  scrollBehavior(to, from, savedPosition) {
    // 如果有保存的位置（浏览器后退/前进），恢复到该位置
    if (savedPosition) {
      return savedPosition
    }
    // 否则滚动到页面顶部
    return { top: 0, left: 0 }
  }
})

// 路由守卫 - 使用安全的认证机制
router.beforeEach((to, from, next) => {
  // 检查路由是否需要登录权限
  if (to.matched.some(record => record.meta.requiresAuth)) {
    // 检查用户是否已登录且token未过期
    if (!tokenManager.isAuthenticated()) {
      // 未登录或token已过期，重定向到登录页
      next({
        path: '/login',
        query: { redirect: to.fullPath } // 保存要访问的路径，便于登录后重定向
      })
      return
    }

    // 检查管理员路由权限
    if (to.matched.some(record => record.meta.requiresAdmin)) {
      if (!tokenManager.isAdmin()) {
        // 非管理员用户，重定向到403页面或首页
        next({
          path: '/403',
          query: { message: '权限不足，无法访问管理页面' }
        })
        return
      }
    }

    // 已登录且权限足够，允许访问
    next()
  } else {
    // 不需要登录权限的路由，直接放行
    next()
  }
})

export default router
