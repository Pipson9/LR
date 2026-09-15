import { reactive } from 'vue'

/**
 * 从 JWT 里解析出 payload（不做签名校验，只是拿到 user_id，
 * 真正的权限校验永远在后端做，这里只用于展示）
 */
function parseToken(token) {
  try {
    const payload = token.split('.')[1]
    const json = decodeURIComponent(
      atob(payload.replace(/-/g, '+').replace(/_/g, '/'))
        .split('')
        .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    )
    return JSON.parse(json)
  } catch {
    return null
  }
}

/** 判断 JWT 是否已过期（exp 是秒级时间戳）。解析不出就当已过期，保证安全 */
function tokenExpired(token) {
  const payload = parseToken(token)
  if (!payload) return true // 解析失败：按过期处理，强制重登
  if (!payload.exp) return false // 没有 exp 字段的旧令牌，留给后端校验
  return payload.exp * 1000 < Date.now()
}

export const userStore = reactive({
  token: localStorage.getItem('token') || '',
  user: JSON.parse(localStorage.getItem('user') || 'null'),

  // 令牌为空或已过期，一律视为"未登录"，这样带死令牌的请求就不会再发出去
  get isLogin() {
    return !!this.token && !tokenExpired(this.token)
  },
  get isAdmin() {
    return !!this.user?.is_admin
  },

  setToken(token) {
    this.token = token
    localStorage.setItem('token', token)
  },

  setUser(user) {
    this.user = user
    localStorage.setItem('user', JSON.stringify(user))
  },

  /** 登录成功后：解析令牌拿 user_id，再去后端拉取完整用户信息 */
  async fetchUserInfo(api) {
    const payload = parseToken(this.token)
    if (!payload || !payload.user_id) return null
    const res = await api.get(`/users/${payload.user_id}`)
    this.setUser(res.data)
    return res.data
  },

  logout() {
    this.token = ''
    this.user = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }
})
