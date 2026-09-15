<template>
  <el-card shadow="never">
    <template #header>
      <div class="card-header">
        <span>用户列表（仅管理员可见）</span>
        <el-input
          v-model="keyword"
          placeholder="搜索用户名/邮箱"
          clearable
          style="width: 240px"
          :prefix-icon="Search"
        />
      </div>
    </template>

    <el-table :data="filteredUsers" v-loading="loading" empty-text="暂无用户">
      <el-table-column prop="id" label="ID" width="70" />
      <el-table-column label="头像" width="80">
        <template #default="{ row }">
          <el-avatar :size="36" :src="row.avatar || ''">
            {{ row.username?.charAt(0)?.toUpperCase() }}
          </el-avatar>
        </template>
      </el-table-column>
      <el-table-column prop="username" label="用户名" min-width="140">
        <template #default="{ row }">
          <span>{{ row.username }}</span>
          <el-tag v-if="row.id === userStore.user?.id" size="small" type="primary" effect="plain" style="margin-left: 6px">我</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="email" label="邮箱" min-width="200" show-overflow-tooltip />
      <el-table-column prop="is_active" label="状态" width="90">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">
            {{ row.is_active ? '正常' : '已禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="is_admin" label="角色" width="90">
        <template #default="{ row }">
          <el-tag :type="row.is_admin ? 'danger' : 'info'" size="small" :effect="row.is_admin ? 'dark' : 'plain'">
            {{ row.is_admin ? '管理员' : '普通用户' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="140" fixed="right">
        <template #default="{ row }">
          <el-button text type="primary" size="small" @click="openEdit(row)">编辑</el-button>
          <el-button text type="danger" size="small" :disabled="row.id === userStore.user?.id" @click="handleDelete(row)">
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>
    <div class="tip">提示：不能删除自己；新注册用户默认是普通用户且处于启用状态。</div>

    <!-- 编辑弹窗 -->
    <el-dialog v-model="editVisible" title="编辑用户" width="460px" destroy-on-close>
      <el-form :model="editForm" label-width="90px">
        <el-form-item label="用户名">
          <el-input v-model="editForm.username" maxlength="500" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="editForm.email" />
        </el-form-item>
        <el-form-item label="是否启用">
          <el-switch v-model="editForm.is_active" active-text="启用" inactive-text="禁用" />
        </el-form-item>
        <el-form-item label="管理员">
          <el-switch v-model="editForm.is_admin" active-text="是" inactive-text="否" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleEdit">保存</el-button>
      </template>
    </el-dialog>
  </el-card>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import { getUsers, updateUser, deleteUser } from '../api'
import { userStore } from '../stores/user'

const loading = ref(false)
const submitting = ref(false)
const users = ref([])
const keyword = ref('')

const filteredUsers = computed(() => {
  if (!keyword.value) return users.value
  const kw = keyword.value.toLowerCase()
  return users.value.filter(
    (u) => u.username.toLowerCase().includes(kw) || u.email.toLowerCase().includes(kw)
  )
})

const editVisible = ref(false)
const editingId = ref(null)
const editForm = reactive({ username: '', email: '', is_active: true, is_admin: false })

function openEdit(row) {
  editingId.value = row.id
  Object.assign(editForm, {
    username: row.username,
    email: row.email,
    is_active: row.is_active,
    is_admin: row.is_admin
  })
  editVisible.value = true
}

async function handleEdit() {
  submitting.value = true
  try {
    await updateUser(editingId.value, { ...editForm })
    ElMessage.success('保存成功')
    editVisible.value = false
    loadUsers()
  } catch {
  } finally {
    submitting.value = false
  }
}

function handleDelete(row) {
  ElMessageBox.confirm(`确定要删除用户「${row.username}」吗？此操作不可恢复！`, '删除确认', {
    type: 'warning',
    confirmButtonText: '删除',
    cancelButtonText: '取消'
  })
    .then(async () => {
      await deleteUser(row.id)
      ElMessage.success('删除成功')
      loadUsers()
    })
    .catch(() => {})
}

async function loadUsers() {
  loading.value = true
  try {
    const res = await getUsers()
    users.value = res.data
  } finally {
    loading.value = false
  }
}

onMounted(loadUsers)
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.tip {
  margin-top: 12px;
  font-size: 13px;
  color: #909399;
}
</style>
