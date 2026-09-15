<template>
  <el-card shadow="never">
    <template #header>
      <div class="card-header">
        <div class="left">
          <el-input
            v-model="keyword"
            placeholder="按商品名称搜索（当前页）"
            clearable
            style="width: 240px"
            :prefix-icon="Search"
          />
        </div>
        <el-button v-if="userStore.isAdmin" type="primary" :icon="Plus" @click="openDialog()">
          新增商品
        </el-button>
      </div>
    </template>

    <el-table :data="filteredProducts" v-loading="loading" empty-text="暂无商品">
      <el-table-column prop="id" label="ID" width="70" />
      <el-table-column prop="name" label="商品名称" min-width="180" show-overflow-tooltip />
      <el-table-column prop="price" label="价格（元）" width="120" sortable>
        <template #default="{ row }">￥{{ row.price.toFixed(2) }}</template>
      </el-table-column>
      <el-table-column prop="stock" label="库存" width="100" sortable>
        <template #default="{ row }">
          <el-tag :type="row.stock === 0 ? 'danger' : row.stock < 10 ? 'warning' : 'info'" effect="plain" size="small">
            {{ row.stock }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="is_active" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'info'" size="small">
            {{ row.is_active ? '在售' : '下架' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column v-if="userStore.isAdmin" label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button text type="primary" size="small" @click="openDialog(row)">编辑</el-button>
          <el-button text type="danger" size="small" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页：后端接口支持 page / page_size -->
    <div class="pagination">
      <el-pagination
        v-model:current-page="page"
        v-model:page-size="pageSize"
        :page-sizes="[5, 10, 20, 50]"
        :total="total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="loadProducts"
        @current-change="loadProducts"
      />
    </div>

    <!-- 新增/编辑弹窗（仅管理员可见按钮） -->
    <el-dialog
      v-model="dialogVisible"
      :title="editingId ? '编辑商品' : '新增商品'"
      width="460px"
      destroy-on-close
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-form-item label="商品名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入商品名称" maxlength="100" />
        </el-form-item>
        <el-form-item label="价格（元）" prop="price">
          <el-input-number v-model="form.price" :min="0.01" :precision="2" :step="1" style="width: 100%" />
        </el-form-item>
        <el-form-item label="库存" prop="stock">
          <el-input-number v-model="form.stock" :min="0" :step="1" style="width: 100%" />
        </el-form-item>
        <el-form-item label="是否在售">
          <el-switch v-model="form.is_active" active-text="在售" inactive-text="下架" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </el-card>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Plus } from '@element-plus/icons-vue'
import { getProducts, createProduct, updateProduct, deleteProduct } from '../api'
import { userStore } from '../stores/user'

const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const editingId = ref(null)
const formRef = ref()

const products = ref([])
const keyword = ref('')
const page = ref(1)
const pageSize = ref(10)
// 后端接口没有返回总数，这里用一个简化处理：如果当前页返回条数等于 page_size，就认为可能还有下一页
const total = computed(() => {
  const loaded = (page.value - 1) * pageSize.value + products.value.length
  return products.value.length === pageSize.value ? loaded + 1 : loaded
})

const filteredProducts = computed(() => {
  if (!keyword.value) return products.value
  const kw = keyword.value.toLowerCase()
  return products.value.filter((p) => p.name.toLowerCase().includes(kw))
})

const form = reactive({ name: '', price: 1, stock: 0, is_active: true })
const rules = {
  name: [
    { required: true, message: '请输入商品名称', trigger: 'blur' },
    { min: 1, max: 100, message: '长度需在 100 字以内', trigger: 'blur' }
  ],
  price: [{ required: true, message: '请输入价格', trigger: 'blur' }],
  stock: [{ required: true, message: '请输入库存', trigger: 'blur' }]
}

async function loadProducts() {
  loading.value = true
  try {
    const res = await getProducts({ page: page.value, page_size: pageSize.value })
    products.value = res.data
  } finally {
    loading.value = false
  }
}

function openDialog(row) {
  editingId.value = row?.id ?? null
  Object.assign(form, {
    name: row?.name ?? '',
    price: row?.price ?? 1,
    stock: row?.stock ?? 0,
    is_active: row?.is_active ?? true
  })
  dialogVisible.value = true
}

async function handleSubmit() {
  await formRef.value.validate()
  submitting.value = true
  try {
    if (editingId.value) {
      await updateProduct(editingId.value, { ...form })
      ElMessage.success('修改成功')
    } else {
      await createProduct({ ...form })
      ElMessage.success('新增成功')
    }
    dialogVisible.value = false
    loadProducts()
  } catch {
    // 拦截器已提示
  } finally {
    submitting.value = false
  }
}

function handleDelete(row) {
  ElMessageBox.confirm(`确定要删除商品「${row.name}」吗？`, '删除确认', {
    type: 'warning',
    confirmButtonText: '删除',
    cancelButtonText: '取消'
  })
    .then(async () => {
      await deleteProduct(row.id)
      ElMessage.success('删除成功')
      // 如果删的是当前页最后一条且不是第一页，回退一页
      if (products.value.length === 1 && page.value > 1) page.value -= 1
      loadProducts()
    })
    .catch(() => {})
}

onMounted(loadProducts)
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.pagination {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}
</style>
