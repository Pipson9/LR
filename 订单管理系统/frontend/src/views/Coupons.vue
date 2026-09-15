<template>
  <el-card shadow="never">
    <template #header>
      <div class="card-header">
        <div class="left">
          <el-select v-model="statusFilter" placeholder="按状态筛选" clearable style="width: 160px">
            <el-option label="生效中" value="active" />
            <el-option label="已停用" value="inactive" />
          </el-select>
        </div>
        <el-button v-if="userStore.isAdmin" type="primary" :icon="Plus" @click="openCreate">
          发放优惠券
        </el-button>
      </div>
    </template>

    <el-row :gutter="16" v-loading="loading">
      <el-col v-for="coupon in filteredCoupons" :key="coupon.id" :xs="24" :sm="12" :md="8" :lg="6" class="coupon-col">
        <el-card shadow="hover" class="coupon-card" :class="{ disabled: coupon.status !== 'active' }">
          <div class="coupon-body">
            <div class="coupon-left">
              <div class="amount">
                <span class="rmb">￥</span>{{ coupon.discount_amount }}
              </div>
              <div class="min">满 {{ coupon.min_amount }} 可用</div>
            </div>
            <div class="coupon-right">
              <div class="name" :title="coupon.name">{{ coupon.name }}</div>
              <div class="code">兑换码：{{ coupon.code }}</div>
              <div class="count">
                <el-progress
                  :percentage="useRate(coupon)"
                  :stroke-width="8"
                  :status="useRate(coupon) >= 100 ? 'exception' : undefined"
                />
                <span class="count-text">已领 {{ coupon.used_count }}/{{ coupon.total_count }}</span>
              </div>
              <div class="time">{{ shortTime(coupon.start_time) }} ~ {{ shortTime(coupon.end_time) }}</div>
            </div>
          </div>
          <div class="coupon-footer">
            <el-tag :type="coupon.status === 'active' ? 'success' : 'info'" size="small">
              {{ coupon.status === 'active' ? '生效中' : '已停用' }}
            </el-tag>
            <div v-if="userStore.isAdmin" class="btns">
              <el-button text type="primary" size="small" @click="openEdit(coupon)">编辑</el-button>
              <el-button text type="danger" size="small" @click="handleDelete(coupon)">删除</el-button>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col v-if="!loading && filteredCoupons.length === 0" :span="24">
        <el-empty description="暂无优惠券" />
      </el-col>
    </el-row>

    <!-- 发券弹窗（仅管理员） -->
    <el-dialog v-model="createVisible" title="发放优惠券" width="500px" destroy-on-close>
      <el-form ref="createFormRef" :model="createForm" :rules="createRules" label-width="100px">
        <el-form-item label="券名称" prop="name">
          <el-input v-model="createForm.name" placeholder="如：满100减20" maxlength="100" />
        </el-form-item>
        <el-form-item label="兑换码" prop="code">
          <el-input v-model="createForm.code" placeholder="如：SAVE20">
            <template #append>
              <el-button @click="createForm.code = genCode()">随机</el-button>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item label="优惠金额" prop="discount_amount">
          <el-input-number v-model="createForm.discount_amount" :min="0.01" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item label="使用门槛" prop="min_amount">
          <el-input-number v-model="createForm.min_amount" :min="0" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item label="发放总量" prop="total_count">
          <el-input-number v-model="createForm.total_count" :min="1" :step="10" style="width: 100%" />
        </el-form-item>
        <el-form-item label="生效时间" prop="range">
          <el-date-picker
            v-model="createForm.range"
            type="datetimerange"
            range-separator="至"
            start-placeholder="开始时间"
            end-placeholder="结束时间"
            value-format="YYYY-MM-DDTHH:mm:ss"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleCreate">确定发放</el-button>
      </template>
    </el-dialog>

    <!-- 编辑弹窗（仅管理员：名称/金额/门槛/状态） -->
    <el-dialog v-model="editVisible" title="编辑优惠券" width="460px" destroy-on-close>
      <el-form :model="editForm" label-width="100px">
        <el-form-item label="券名称">
          <el-input v-model="editForm.name" maxlength="100" />
        </el-form-item>
        <el-form-item label="优惠金额">
          <el-input-number v-model="editForm.discount_amount" :min="0.01" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item label="使用门槛">
          <el-input-number v-model="editForm.min_amount" :min="0" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item label="状态">
          <el-radio-group v-model="editForm.status">
            <el-radio value="active">生效中</el-radio>
            <el-radio value="inactive">停用</el-radio>
          </el-radio-group>
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
import { Plus } from '@element-plus/icons-vue'
import { getCoupons, createCoupon, updateCoupon, deleteCoupon } from '../api'
import { userStore } from '../stores/user'

const loading = ref(false)
const submitting = ref(false)
const coupons = ref([])
const statusFilter = ref('')

const filteredCoupons = computed(() =>
  statusFilter.value ? coupons.value.filter((c) => c.status === statusFilter.value) : coupons.value
)

const useRate = (c) => (c.total_count ? Math.round((c.used_count / c.total_count) * 100) : 0)
const shortTime = (t) => (t ? String(t).replace('T', ' ').slice(0, 16) : '')

// ---- 创建 ----
const createVisible = ref(false)
const createFormRef = ref()
const createForm = reactive({
  name: '',
  code: '',
  discount_amount: 20,
  min_amount: 100,
  total_count: 100,
  range: []
})

const createRules = {
  name: [
    { required: true, message: '请输入券名称', trigger: 'blur' },
    { min: 1, max: 100, message: '长度需在 100 字以内', trigger: 'blur' }
  ],
  code: [{ required: true, message: '请输入兑换码', trigger: 'blur' }],
  discount_amount: [{ required: true, message: '请输入优惠金额', trigger: 'blur' }],
  total_count: [{ required: true, message: '请输入发放总量', trigger: 'blur' }],
  range: [
    {
      required: true,
      validator: (rule, value, callback) => {
        if (!value || value.length !== 2) callback(new Error('请选择生效时间范围'))
        else callback()
      },
      trigger: 'change'
    }
  ]
}

function genCode() {
  return 'SAVE' + Math.random().toString(36).slice(2, 8).toUpperCase()
}

function openCreate() {
  Object.assign(createForm, {
    name: '',
    code: genCode(),
    discount_amount: 20,
    min_amount: 100,
    total_count: 100,
    range: []
  })
  createVisible.value = true
}

async function handleCreate() {
  await createFormRef.value.validate()
  submitting.value = true
  try {
    await createCoupon({
      name: createForm.name,
      code: createForm.code,
      discount_amount: createForm.discount_amount,
      min_amount: createForm.min_amount,
      total_count: createForm.total_count,
      start_time: createForm.range[0],
      end_time: createForm.range[1]
    })
    ElMessage.success('发放成功')
    createVisible.value = false
    loadCoupons()
  } catch {
  } finally {
    submitting.value = false
  }
}

// ---- 编辑 / 删除 ----
const editVisible = ref(false)
const editingId = ref(null)
const editForm = reactive({ name: '', discount_amount: 0, min_amount: 0, status: 'active' })

function openEdit(row) {
  editingId.value = row.id
  Object.assign(editForm, {
    name: row.name,
    discount_amount: row.discount_amount,
    min_amount: row.min_amount,
    status: row.status
  })
  editVisible.value = true
}

async function handleEdit() {
  submitting.value = true
  try {
    await updateCoupon(editingId.value, { ...editForm })
    ElMessage.success('保存成功')
    editVisible.value = false
    loadCoupons()
  } catch {
  } finally {
    submitting.value = false
  }
}

function handleDelete(row) {
  ElMessageBox.confirm(`确定要删除优惠券「${row.name}」吗？`, '删除确认', {
    type: 'warning',
    confirmButtonText: '删除',
    cancelButtonText: '取消'
  })
    .then(async () => {
      await deleteCoupon(row.id)
      ElMessage.success('删除成功')
      loadCoupons()
    })
    .catch(() => {})
}

async function loadCoupons() {
  loading.value = true
  try {
    const res = await getCoupons()
    coupons.value = res.data
  } finally {
    loading.value = false
  }
}

onMounted(loadCoupons)
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.coupon-col {
  margin-bottom: 16px;
}

.coupon-card.disabled {
  opacity: 0.6;
}

.coupon-body {
  display: flex;
  gap: 14px;
}

.coupon-left {
  width: 110px;
  flex-shrink: 0;
  text-align: center;
  padding: 8px 0;
  border-right: 1px dashed #dcdfe6;
}

.coupon-left .amount {
  color: #f56c6c;
  font-size: 26px;
  font-weight: 700;
}

.coupon-left .rmb {
  font-size: 14px;
}

.coupon-left .min {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.coupon-right {
  flex: 1;
  min-width: 0;
}

.coupon-right .name {
  font-weight: 600;
  color: #303133;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.coupon-right .code {
  font-size: 12px;
  color: #909399;
  margin: 4px 0;
}

.count-text {
  font-size: 12px;
  color: #909399;
}

.coupon-right .time {
  font-size: 12px;
  color: #909399;
  margin-top: 6px;
}

.coupon-footer {
  margin-top: 12px;
  padding-top: 10px;
  border-top: 1px solid #f0f2f5;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
