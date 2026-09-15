import request from './request'

// 注意：后端的路由都注册在带尾斜杠的路径上（如 @router.get("/") + prefix="/products" → /products/），
// 请求不带尾斜杠的 /products 会被 FastAPI 307 重定向，而重定向会丢失 Authorization 请求头 → 401。
// 所以"列表/创建"这类打到根路径的接口必须带尾斜杠；带 /{id} 的接口不受影响。

// ============ 认证 & 验证码 ============

// 获取图形验证码（登录前就能访问，无需令牌）
export const getCaptcha = () => request.get('/captcha')

// 登录：后端是 OAuth2 表单格式，必须用 URLSearchParams 提交
export function login({ username, password, code, captchaId }) {
  const form = new URLSearchParams()
  form.append('username', username)
  form.append('password', password)
  form.append('code', code)
  form.append('captcha_id', captchaId)
  return request.post('/login', form, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
  })
}

// 注册（开放接口）
export const register = (data) => request.post('/users/', data)

// ============ 用户管理 ============
export const getUsers = () => request.get('/users/')
export const getUser = (id) => request.get(`/users/${id}`)
export const updateUser = (id, data) => request.patch(`/users/${id}`, data)
export const deleteUser = (id) => request.delete(`/users/${id}`)
export const uploadAvatar = (id, formData) =>
  request.post(`/users/${id}/avatar`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })

// ============ 商品管理 ============
export const getProducts = (params) => request.get('/products/', { params })
export const getProduct = (id) => request.get(`/products/${id}`)
export const createProduct = (data) => request.post('/products/', data)
export const updateProduct = (id, data) => request.patch(`/products/${id}`, data)
export const deleteProduct = (id) => request.delete(`/products/${id}`)

// ============ 订单管理 ============
export const getOrders = () => request.get('/orders/')
export const getOrder = (id) => request.get(`/orders/${id}`)
export const createOrder = (data) => request.post('/orders/', data)
export const updateOrder = (id, data) => request.patch(`/orders/${id}`, data)
export const deleteOrder = (id) => request.delete(`/orders/${id}`)

// ============ 优惠券管理 ============
export const getCoupons = () => request.get('/coupons/')
export const createCoupon = (data) => request.post('/coupons/', data)
export const updateCoupon = (id, data) => request.patch(`/coupons/${id}`, data)
export const deleteCoupon = (id) => request.delete(`/coupons/${id}`)
