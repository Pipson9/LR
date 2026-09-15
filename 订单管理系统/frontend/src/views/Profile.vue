<template>
  <el-row :gutter="20" v-loading="loading">
    <!-- 左侧：个人信息 -->
    <el-col :span="8">
      <el-card shadow="hover">
        <template #header><span>个人信息</span></template>
        <div class="profile-body">
          <el-avatar :size="90" :src="userStore.user?.avatar || ''">
            {{ userStore.user?.username?.charAt(0)?.toUpperCase() }}
          </el-avatar>
          <h3>{{ userStore.user?.username }}</h3>
          <p class="email">{{ userStore.user?.email }}</p>
          <div class="tags">
            <el-tag :type="userStore.user?.is_admin ? 'danger' : 'info'" :effect="userStore.user?.is_admin ? 'dark' : 'plain'">
              {{ userStore.user?.is_admin ? '管理员' : '普通用户' }}
            </el-tag>
            <el-tag :type="userStore.user?.is_active ? 'success' : 'danger'">
              {{ userStore.user?.is_active ? '账号正常' : '已禁用' }}
            </el-tag>
          </div>
          <el-divider />
          <div class="info-item"><span>用户 ID</span><b>{{ userStore.user?.id }}</b></div>
          <div class="info-item"><span>用户名</span><b>{{ userStore.user?.username }}</b></div>
          <div class="info-item"><span>邮箱</span><b>{{ userStore.user?.email }}</b></div>
        </div>
      </el-card>
    </el-col>

    <!-- 右侧：头像上传 -->
    <el-col :span="16">
      <el-card shadow="hover">
        <template #header><span>修改头像</span></template>
        <el-upload
          class="avatar-uploader"
          :show-file-list="false"
          :http-request="doUpload"
          accept="image/jpeg,image/png,image/webp,image/gif,image/bmp"
          drag
        >
          <div class="upload-area">
            <el-icon :size="48" color="#c0c4cc"><Plus /></el-icon>
            <div class="upload-text">点击或拖拽图片到这里上传</div>
            <div class="upload-tip">支持 jpg / png / webp / gif / bmp，不超过 2MB</div>
          </div>
        </el-upload>
        <el-alert
          type="info"
          :closable="false"
          show-icon
          title="上传成功后，页面顶部的头像会立即更新"
          style="margin-top: 16px"
        />
      </el-card>
    </el-col>
  </el-row>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { uploadAvatar } from '../api'
import request from '../api/request'
import { userStore } from '../stores/user'

const loading = ref(false)

async function doUpload({ file }) {
  if (file.size > 2 * 1024 * 1024) {
    ElMessage.error('图片不能超过 2MB')
    return
  }
  const formData = new FormData()
  formData.append('file', file)
  try {
    const res = await uploadAvatar(userStore.user.id, formData)
    userStore.setUser(res.data)
    ElMessage.success('头像上传成功')
  } catch {
    // 拦截器已提示
  }
}

onMounted(() => {
  // 每次进入页面刷新一次个人信息（比如管理员在别处改过资料）
  loading.value = true
  userStore
    .fetchUserInfo(request)
    .catch(() => {})
    .finally(() => {
      loading.value = false
    })
})
</script>

<style scoped>
.profile-body {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 8px 0;
}

.profile-body h3 {
  color: #303133;
}

.email {
  color: #909399;
  font-size: 13px;
  margin-top: -2px;
}

.tags {
  display: flex;
  gap: 8px;
}

.info-item {
  width: 100%;
  display: flex;
  justify-content: space-between;
  font-size: 14px;
  color: #606266;
  padding: 6px 0;
}

.info-item b {
  color: #303133;
}

.avatar-uploader :deep(.el-upload-dragger) {
  padding: 40px 20px;
}

.upload-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.upload-text {
  color: #606266;
  font-size: 14px;
}

.upload-tip {
  color: #909399;
  font-size: 12px;
}
</style>
