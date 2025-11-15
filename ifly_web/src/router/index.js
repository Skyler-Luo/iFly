import { createRouter, createWebHashHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import FlightResults from '../views/FlightResults.vue'
import BookingView from '../views/BookingView.vue'
import OrderDetail from '../views/OrderDetail.vue'
import UserProfileView from '../views/UserProfileView.vue'
import NotificationView from '../views/NotificationView.vue'
import HelpCenterView from '../views/HelpCenterView.vue'
import PromotionCenterView from '../views/PromotionCenterView.vue'
import PromotionDetailView from '../views/PromotionDetailView.vue'
import PointsCenterView from '../views/PointsCenterView.vue'
import PointsHistoryView from '../views/PointsHistoryView.vue'
import PointsExchangeView from '../views/PointsExchangeView.vue'
import PointsTasksView from '../views/PointsTasksView.vue'
import AdminDashboardView from '../views/AdminDashboardView.vue'
import AdminFlightsView from '../views/AdminFlightsView.vue'
import AdminUsersView from '../views/AdminUsersView.vue'
import AdminPromotionsView from '../views/AdminPromotionsView.vue'
import DebugView from '../views/Debug.vue'

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
    component: () => import(/* webpackChunkName: "orders" */ '../views/OrderList.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/payment/:orderId',
    name: 'payment',
    component: () => import(/* webpackChunkName: "payment" */ '../views/PaymentView.vue')
  },
  {
    path: '/checkin/:ticketId',
    name: 'checkin',
    component: () => import(/* webpackChunkName: "checkin" */ '../views/CheckinView.vue')
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
    path: '/help',
    name: 'helpCenter',
    component: HelpCenterView
  },
  {
    path: '/help/category/:categoryId',
    name: 'helpCategory',
    component: () => import(/* webpackChunkName: "helpCategory" */ '../views/HelpCenterView.vue')
  },
  {
    path: '/flight-status',
    name: 'flightStatus',
    component: () => import(/* webpackChunkName: "flightStatus" */ '../views/FlightStatusView.vue')
  },
  {
    path: '/promotions',
    name: 'promotions',
    component: PromotionCenterView
  },
  {
    path: '/promotions/:id',
    name: 'promotionDetail',
    component: PromotionDetailView
  },
  {
    path: '/points',
    name: 'pointsCenter',
    component: PointsCenterView,
    meta: { requiresAuth: true }
  },
  {
    path: '/points/history',
    name: 'pointsHistory',
    component: PointsHistoryView,
    meta: { requiresAuth: true }
  },
  {
    path: '/points/exchange',
    name: 'pointsExchange',
    component: PointsExchangeView,
    meta: { requiresAuth: true }
  },
  {
    path: '/points/tasks',
    name: 'pointsTasks',
    component: PointsTasksView,
    meta: { requiresAuth: true }
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
    component: () => import(/* webpackChunkName: "adminFlightPassengers" */ '../views/AdminFlightPassengersView.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/flights/:flightId/pricing',
    name: 'adminFlightPricing',
    component: () => import(/* webpackChunkName: "adminFlightPricing" */ '../views/AdminFlightPricingView.vue'),
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
    component: () => import(/* webpackChunkName: "adminUserOrders" */ '../views/AdminUserOrdersView.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/promotions',
    name: 'adminPromotions',
    component: AdminPromotionsView,
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/promotions/:promoId/usage',
    name: 'adminPromotionUsage',
    component: () => import(/* webpackChunkName: "adminPromotionUsage" */ '../views/AdminPromotionUsageView.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/orders',
    name: 'adminOrders',
    component: () => import(/* webpackChunkName: "adminOrders" */ '../views/AdminOrdersView.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/settings',
    name: 'adminSettings',
    component: () => import(/* webpackChunkName: "adminSettings" */ '../views/AdminSettingsView.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  // 新增数据可视化路由
  {
    path: '/admin/visualization',
    name: 'adminVisualization',
    component: () => import(/* webpackChunkName: "adminVisualization" */ '../views/AdminDataVisualizationView.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/business-intelligence',
    name: 'adminBusinessIntelligence',
    component: () => import(/* webpackChunkName: "adminBusinessIntelligence" */ '../views/AdminBusinessIntelligenceView.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/analytics/flights',
    name: 'adminFlightAnalytics',
    component: () => import(/* webpackChunkName: "adminFlightAnalytics" */ '../views/AdminFlightAnalyticsView.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/analytics/revenue',
    name: 'adminRevenueAnalytics',
    component: () => import(/* webpackChunkName: "adminRevenueAnalytics" */ '../views/AdminRevenueView.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/logs',
    name: 'adminSystemLogs',
    component: () => import(/* webpackChunkName: "adminSystemLogs" */ '../views/AdminSystemLogsView.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  // 添加调试页面路由
  {
    path: '/debug',
    name: 'debug',
    component: DebugView
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

// 全局前置守卫
// 暂时注释掉登录检测，因为还没有接入API
/*
router.beforeEach((to, from, next) => {
  // 检查路由是否需要登录权限
  if (to.matched.some(record => record.meta.requiresAuth)) {
    // 检查用户是否已登录
    if (!localStorage.getItem('token')) {
      // 未登录，重定向到登录页
      next({
        path: '/login',
        query: { redirect: to.fullPath } // 保存要访问的路径，便于登录后重定向
      })
    } else {
      // 已登录，允许访问
      next()
    }
  } else {
    // 不需要登录权限的路由，直接放行
    next()
  }
})
*/

// 临时放行所有路由
router.beforeEach((to, from, next) => {
  next()
})

export default router
