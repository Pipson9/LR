<template>
  <el-card shadow="never">
    <template #header>
      <div class="card-header">
        <div class="left">
          <el-select v-model="statusFilter" placeholder="按状态筛选" clearable style="width: 160px">
            <el-option v-for="(v, k) in ORDER_STATUS" :key="k" :label="v.text" :value="k" />
          </el-select>
        </div>
        <el-button type="primary" :icon="Plus" @click="openCreate">创建订单</el-button>
      </div>
    </template>

    <el-table :data="filteredOrders" v-loading="loading" empty-text="暂无订单">
      <el-table-column prop="order_id" label="ID" width="70" />
      <el-table-column prop="order_no" label="订单号" min-width="200" show-overflow-tooltip />
      <el-table-column prop="user_id" label="用户ID" width="90">
        <template #default="{ row }">
          <el-tag size="small" effect="plain">{{ row.user_id }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="amount" label="金额" width="120" sortable>
        <template #default="{ row }">￥{{ row.amount.toFixed(2) }}</template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="110">
        <template #default="{ row }">
          <el-tag :type="orderStatusType(row.status)" size="small">{{ orderStatusText(row.status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="220" fixed="right">
        <template #default="{ row }">
          <template v-if="userStore.isAdmin">
            <el-button text type="primary" size="small" @click="openStatusDialog(row)">改状态</el-button>
            <el-button text type="danger" size="small" @click="handleDelete(row)">删除</el-button>
          </template>
          <el-tag v-else size="small" type="info" effect="plain">
            {{ row.user_id === userStore.user?.id ? '我的订单' : '' }}
          </el-tag>
        </template>
      </el-table-column>
    </el-table>

    <!-- 创建订单弹窗（登录用户都可以下单） -->
    <el-dialog v-model="createVisible" title="创建订单" width="460px" destroy-on-close>
      <el-alert
        type="info"
        :closable="false"
        show-icon
        title="订单归属人取自登录令牌，状态由服务端强制为「待支付」"
        style="margin-bottom: 16px"
      />
      <el-form ref="createFormRef" :model="createForm" :rules="createRules" label-width="90px">
        <el-form-item label="订单号" prop="order_no">
          <el-input v-model="createForm.order_no" placeholder="订单号">
            <template #append>
              <el-button @click="createForm.order_no = genOrderNo()">生成</el-button>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item label="金额（元）" prop="amount">
          <el-input-number v-model="createForm.amount" :min="0.01" :precision="2" :step="10" style="width: 100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleCreate">提交订单</el-button>
      </template>
    </el-dialog>

    <!-- 修改状态弹窗（仅管理员） -->
    <el-dialog v-model="statusVisible" title="修改订单状态" width="420px" destroy-on-close>
      <p class="status-tip">订单号：{{ editingOrder?.order_no }}</p>
      <el-select v-model="newStatus" style="width: 100%" size="large">
        <el-option v-for="(v, k) in ORDER_STATUS" :key="k" :label="v.text" :value="k" />
      </el-select>
      <template #footer>
        <el-button @click="statusVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleStatusUpdate">确定</el-button>
      </template>
    </el-dialog>
  </el-card>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { getOrders, createOrder, updateOrder, deleteOrder } from '../api'
import { userStore } from '../stores/user'

const ORDER_STATUS = {
  pending: { text: '待支付', type: 'warning' },
  paid: { text: '已支付', type: 'success' },
  shipped: { text: '已发货', type: 'primary' },
  completed: { text: '已完成', type: 'success' },
  cancelled: { text: '已取消', type: 'info' }
}
const orderStatusText = (s) => ORDER_STATUS[s]?.text || s
const orderStatusType = (s) => ORDER_STATUS[s]?.type || 'info'

const loading = ref(false)
const submitting = ref(false)
const orders = ref([])
const statusFilter = ref('')

// 后端会把普通用户的查询自动限制为"只能看自己的订单"，管理员能看到全部
const filteredOrders = computed(() =>
  statusFilter.value ? orders.value.filter((o) => o.status === statusFilter.value) : orders.value
)

// ---- 创建订单 ----
const createVisible = ref(false)
const createFormRef = ref()
const createForm = reactive({ order_no: '', amount: 100 })
const createRules = {
  order_no: [{ required: true, message: '请填写或生成订单号', trigger: 'blur' }],
  amount: [{ required: true, message: '请输入金额', trigger: 'blur' }]
}

function genOrderNo() {
  const now = new Date()
  const pad = (n) => String(n).padStart(2, '0')
  return `ORD${now.getFullYear()}${pad(now.getMonth() + 1)}${pad(now.getDate())}${pad(now.getHours())}${pad(now.getMinutes())}${pad(now.getSeconds())}${Math.floor(Math.random() * 1000)}`
}

function openCreate() {
  createForm.order_no = genOrderNo()
  createForm.amount = 100
  createVisible.value = true
}

async function handleCreate() {
  await createFormRef.value.validate()
  submitting.value = true
  try {
    await createOrder({ order_no: createForm.order_no, amount: createForm.amount })
    ElMessage.success('下单成功，订单状态为待支付')
    createVisible.value = false
    loadOrders()
  } catch {
  } finally {
    submitting.value = false
  }
}

// ---- 管理员改状态 / 删除 ----
const statusVisible = ref(false)
const editingOrder = ref(null)
const newStatus = ref('pending')

function openStatusDialog(row) {
  editingOrder.value = row
  newStatus.value = row.status
  statusVisible.value = true
}

async function handleStatusUpdate() {
  submitting.value = true
  try {
    await updateOrder(editingOrder.value.order_id, { status: newStatus.value })
    ElMessage.success('状态修改成功')
    statusVisible.value = false
    loadOrders()
  } catch {
  } finally {
    submitting.value = false
  }
}

function handleDelete(row) {
  ElMessageBox.confirm(`确定要删除订单「${row.order_no}」吗？`, '删除确认', {
    type: 'warning',
    confirmButtonText: '删除',
    cancelButtonText: '取消'
  })
    .then(async () => {
      await deleteOrder(row.order_id)
      ElMessage.success('删除成功')
      loadOrders()
    })
    .catch(() => {})
}

async function loadOrders() {
  loading.value = true
  try {
    const res = await getOrders()
    orders.value = res.data
  } finally {
    loading.value = false
  }
}

onMounted(loadOrders)
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.status-tip {
  margin-bottom: 12px;
  color: #606266;
  font-size: 14px;
}
</style>
