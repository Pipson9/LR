<template>
  <div class="login-page">
    <div class="login-card">
      <h2 class="title">订单管理系统</h2>
      <p class="subtitle">Vue3 + FastAPI 前后端分离示例</p>

      <el-form ref="formRef" :model="form" :rules="rules" size="large" @keyup.enter="handleLogin">
        <el-form-item prop="username">
          <el-input v-model="form.username" placeholder="用户名" :prefix-icon="User" />
        </el-form-item>

        <el-form-item prop="password">
          <el-input v-model="form.password" type="password" placeholder="密码" show-password :prefix-icon="Lock" />
        </el-form-item>

        <el-form-item prop="code">
          <div class="captcha-row">
            <el-input v-model="form.code" placeholder="验证码" :prefix-icon="Key" maxlength="4" />
            <img v-if="captchaImage" :src="captchaImage" class="captcha-img" title="点击刷新" @click="loadCaptcha" />
            <div v-else class="captcha-img captcha-placeholder" @click="loadCaptcha">点击获取</div>
          </div>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" class="login-btn" :loading="loading" @click="handleLogin">
            登 录
          </el-button>
        </el-form-item>
      </el-form>

      <div class="footer-links">
        还没有账号？
        <router-link to="/register">立即注册</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock, Key } from '@element-plus/icons-vue'
import { getCaptcha, login } from '../api'
import request from '../api/request'
import { userStore } from '../stores/user'

const router = useRouter()
const formRef = ref()
const loading = ref(false)
const captchaImage = ref('')
const captchaId = ref('')

const form = reactive({ username: '', password: '', code: '' })

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
  code: [{ required: true, message: '请输入验证码', trigger: 'blur' }]
}

async function loadCaptcha() {
  try {
    const res = await getCaptcha()
    captchaId.value = res.data.captcha_id
    captchaImage.value = res.data.image
  } catch {
    captchaImage.value = ''
  }
}

async function handleLogin() {
  await formRef.value.validate()
  loading.value = true
  try {
    const res = await login({
      username: form.username,
      password: form.password,
      code: form.code,
      captchaId: captchaId.value
    })
    userStore.setToken(res.data.access_token)
    await userStore.fetchUserInfo(request)
    ElMessage.success(`欢迎回来，${userStore.user?.username || form.username}！`)
    router.push('/')
  } catch {
    // 验证码是一次性的，无论登录成败都要刷新
    form.code = ''
    loadCaptcha()
  } finally {
    loading.value = false
  }
}

onMounted(loadCaptcha)
</script>

<style scoped>
.login-page {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-card {
  width: 400px;
  padding: 40px 36px 24px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.title {
  text-align: center;
  color: #303133;
  margin-bottom: 6px;
}

.subtitle {
  text-align: center;
  color: #909399;
  font-size: 13px;
  margin-bottom: 28px;
}

.captcha-row {
  display: flex;
  gap: 10px;
  width: 100%;
  align-items: center;
}

.captcha-img {
  height: 40px;
  width: 120px;
  border-radius: 6px;
  cursor: pointer;
  border: 1px solid #dcdfe6;
  flex-shrink: 0;
}

.captcha-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  color: #909399;
  background: #f5f7fa;
}

.login-btn {
  width: 100%;
}

.footer-links {
  text-align: center;
  font-size: 14px;
  color: #909399;
}

.footer-links a {
  color: #409eff;
  text-decoration: none;
}
</style>
