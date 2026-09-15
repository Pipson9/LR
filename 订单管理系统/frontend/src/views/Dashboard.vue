<template>
  <div v-loading="loading">
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stat-row">
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-icon" style="background: #e8f4ff"><el-icon :size="28" color="#409eff"><Goods /></el-icon></div>
            <div>
              <div class="stat-value">{{ stats.products }}</div>
              <div class="stat-label">在售商品</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-icon" style="background: #fdf0e6"><el-icon :size="28" color="#e6a23c"><Document /></el-icon></div>
            <div>
              <div class="stat-value">{{ stats.orders }}</div>
              <div class="stat-label">我的订单</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-icon" style="background: #f0f9eb"><el-icon :size="28" color="#67c23a"><CircleCheck /></el-icon></div>
            <div>
              <div class="stat-value">{{ stats.paidOrders }}</div>
              <div class="stat-label">已完成支付</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-icon" style="background: #fef0f0"><el-icon :size="28" color="#f56c6c"><Ticket /></el-icon></div>
            <div>
              <div class="stat-value">{{ stats.coupons }}</div>
              <div class="stat-label">可用优惠券</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <!-- 最近订单 -->
      <el-col :span="14">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>最近订单</span>
              <el-button text type="primary" @click="$router.push('/orders')">查看全部</el-button>
            </div>
          </template>
          <el-table :data="recentOrders" size="default" empty-text="暂无订单">
            <el-table-column prop="order_no" label="订单号" min-width="160" />
            <el-table-column prop="amount" label="金额" width="110">
              <template #default="{ row }">￥{{ row.amount.toFixed(2) }}</template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="orderStatusType(row.status)" size="small">{{ orderStatusText(row.status) }}</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <!-- 欢迎信息 -->
      <el-col :span="10">
        <el-card shadow="hover" class="welcome-card">
          <template #header><span>欢迎</span></template>
          <div class="welcome-body">
            <el-avatar :size="64" :src="userStore.user?.avatar || ''">
              {{ userStore.user?.username?.charAt(0)?.toUpperCase() }}
            </el-avatar>
            <h3>{{ userStore.user?.username }}</h3>
            <p class="email">{{ userStore.user?.email }}</p>
            <el-tag v-if="userStore.isAdmin" type="danger" effect="dark">管理员</el-tag>
            <el-tag v-else type="info">普通用户</el-tag>
            <p class="tip">这是一套 Vue3 + FastAPI 的前后端分离订单管理系统示例</p>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref, computed } from 'vue'
import { getProducts, getOrders, getCoupons } from '../api'
import { userStore } from '../stores/user'

const loading = ref(false)
const orders = ref([])
const stats = reactive({ products: 0, orders: 0, paidOrders: 0, coupons: 0 })

const recentOrders = computed(() => orders.value.slice(0, 6))

const ORDER_STATUS = {
  pending: { text: '待支付', type: 'warning' },
  paid: { text: '已支付', type: 'success' },
  shipped: { text: '已发货', type: 'primary' },
  completed: { text: '已完成', type: 'success' },
  cancelled: { text: '已取消', type: 'info' }
}
const orderStatusText = (s) => ORDER_STATUS[s]?.text || s
const orderStatusType = (s) => ORDER_STATUS[s]?.type || 'info'

onMounted(async () => {
  loading.value = true
  try {
    // 三个请求互不依赖，并行发出
    const [productsRes, ordersRes, couponsRes] = await Promise.all([
      getProducts({ page: 1, page_size: 100 }),
      getOrders(),
      getCoupons()
    ])
    stats.products = productsRes.data.filter((p) => p.is_active).length
    orders.value = ordersRes.data
    stats.orders = ordersRes.data.length
    stats.paidOrders = ordersRes.data.filter((o) => ['paid', 'shipped', 'completed'].includes(o.status)).length
    stats.coupons = couponsRes.data.filter((c) => c.status === 'active').length
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.stat-row {
  margin-bottom: 20px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-value {
  font-size: 26px;
  font-weight: 700;
  color: #303133;
}

.stat-label {
  font-size: 13px;
  color: #909399;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.welcome-body {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  padding: 10px 0;
}

.welcome-body h3 {
  color: #303133;
}

.email {
  color: #909399;
  font-size: 13px;
  margin: -4px 0 2px;
}

.tip {
  margin-top: 10px;
  font-size: 13px;
  color: #909399;
  text-align: center;
}
</style>
