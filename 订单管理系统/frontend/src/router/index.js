import { createRouter, createWebHistory } from 'vue-router'
import { userStore } from '../stores/user'

const routes = [
  { path: '/login', name: 'Login', component: () => import('../views/Login.vue'), meta: { title: '登录' } },
  { path: '/register', name: 'Register', component: () => import('../views/Register.vue'), meta: { title: '注册' } },
  {
    path: '/',
    component: () => import('../views/Layout.vue'),
    redirect: '/dashboard',
    children: [
      { path: 'dashboard', name: 'Dashboard', component: () => import('../views/Dashboard.vue'), meta: { title: '首页' } },
      { path: 'products', name: 'Products', component: () => import('../views/Products.vue'), meta: { title: '商品管理' } },
      { path: 'orders', name: 'Orders', component: () => import('../views/Orders.vue'), meta: { title: '订单管理' } },
      { path: 'coupons', name: 'Coupons', component: () => import('../views/Coupons.vue'), meta: { title: '优惠券' } },
      { path: 'users', name: 'Users', component: () => import('../views/Users.vue'), meta: { title: '用户管理', admin: true } },
      { path: 'profile', name: 'Profile', component: () => import('../views/Profile.vue'), meta: { title: '个人中心' } }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 全局路由守卫：未登录 → 登录页；管理员页面权限拦截
router.beforeEach((to) => {
  document.title = to.meta.title ? `${to.meta.title} - 订单管理系统` : '订单管理系统'

  if (to.path === '/login' || to.path === '/register') return true

  // 令牌失效（为空或已过期）：清掉本地残留后回登录页
  if (!userStore.isLogin) {
    if (userStore.token) userStore.logout()
    return '/login'
  }
  if (to.meta.admin && !userStore.isAdmin) {
    return '/dashboard'
  }
  return true
})

export default router
