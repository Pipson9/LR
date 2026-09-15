import axios from 'axios'
import { ElMessage } from 'element-plus'
import { userStore } from '../stores/user'
import router from '../router'

const request = axios.create({
  baseURL: '/api',
  timeout: 10000
})

// 请求拦截器：自动带上登录令牌
request.interceptors.request.use((config) => {
  if (userStore.token) {
    config.headers.Authorization = `Bearer ${userStore.token}`
  }
  return config
})

// 响应拦截器：统一错误提示；401 一律踢回登录页
request.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error.response?.status
    const detail = error.response?.data?.detail

    let message = '请求失败，请稍后重试'
    if (typeof detail === 'string') message = detail
    else if (Array.isArray(detail)) {
      // FastAPI 参数校验错误
      message = detail[0]?.msg || '参数错误'
    } else if (error.message.includes('timeout')) {
      message = '请求超时，请检查后端是否已启动'
    } else if (!error.response) {
      message = '无法连接到服务器，请确认后端已启动（127.0.0.1:8000）'
    }

    if (status === 401) {
      // 登录接口自身的 401 = 用户名/密码错误，展示真实原因，不要提示"登录已过期"
      // 其它接口 401 = 令牌失效/未登录 → 清状态并踢回登录页
      const isLoginApi = (error.config?.url === '/login' || error.config?.url?.startsWith('/login'))
      if (isLoginApi) {
        ElMessage.error(message || '用户名或密码错误')
      } else {
        userStore.logout()
        ElMessage.error('登录已过期，请重新登录')
        if (router.currentRoute.value.path !== '/login') {
          router.push('/login')
        }
      }
    } else {
      ElMessage.error(message)
    }
    return Promise.reject(error)
  }
)

export default request
