<template>
  <div class="user-manage">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>用户管理</span>
          <el-button type="primary" @click="openDialog()">
            <el-icon><Plus /></el-icon> 新增用户
          </el-button>
        </div>
      </template>
      <div class="search-bar">
        <el-input v-model="keyword" placeholder="搜索用户名/姓名/部门" clearable style="width: 260px" @clear="loadData" @keyup.enter="loadData">
          <template #prefix><el-icon><Search /></el-icon></template>
        </el-input>
        <el-button type="primary" @click="loadData">搜索</el-button>
      </div>
      <el-table :data="tableData" v-loading="loading" stripe border>
        <el-table-column prop="username" label="登录账号" width="140" />
        <el-table-column prop="name" label="用户名" width="120" />
        <el-table-column prop="department" label="所属部门" width="150" />
        <el-table-column prop="phone" label="联系方式" width="140" />
        <el-table-column prop="is_admin" label="角色" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_admin ? 'danger' : 'info'">
              {{ row.is_admin ? '管理员' : '普通用户' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" width="90">
          <template #default="{ row }">
            <el-switch v-model="row.is_active" @change="handleToggleActive(row)" :disabled="row.username === 'admin'" />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="140" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openDialog(row)">编辑</el-button>
            <el-popconfirm title="确定要删除吗？" @confirm="handleDelete(row.id)">
              <template #reference>
                <el-button size="small" type="danger">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑用户' : '新增用户'" width="460px" destroy-on-close>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-form-item label="登录账号" prop="username">
          <el-input v-model="form.username" :disabled="isEdit" placeholder="请输入登录账号" />
        </el-form-item>
        <el-form-item label="用户名" prop="name">
          <el-input v-model="form.name" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="所属部门" prop="department">
          <el-input v-model="form.department" placeholder="请输入所属部门" />
        </el-form-item>
        <el-form-item label="联系方式" prop="phone">
          <el-input v-model="form.phone" placeholder="请输入联系方式" />
        </el-form-item>
        <el-form-item label="角色">
          <el-switch v-model="form.is_admin" active-text="管理员" inactive-text="普通用户" />
        </el-form-item>
        <el-form-item label="密码" :prop="isEdit ? '' : 'password'">
          <el-input v-model="form.password" type="password" show-password :placeholder="isEdit ? '留空则不修改' : '请输入密码（默认123456）'" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, Search } from '@element-plus/icons-vue'
import { getUsers, createUser, updateUser, deleteUser } from '../api/users'

const loading = ref(false)
const submitting = ref(false)
const tableData = ref([])
const keyword = ref('')
const dialogVisible = ref(false)
const isEdit = ref(false)
const editId = ref(null)
const formRef = ref(null)

const form = ref({
  username: '',
  name: '',
  department: '',
  phone: '',
  is_admin: false,
  is_active: true,
  password: '',
})

const rules = {
  username: [{ required: true, message: '请输入登录账号', trigger: 'blur' }],
  name: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

async function loadData() {
  loading.value = true
  try {
    tableData.value = await getUsers({ keyword: keyword.value })
  } finally {
    loading.value = false
  }
}

function openDialog(row) {
  if (row) {
    isEdit.value = true
    editId.value = row.id
    form.value = { ...row, password: '' }
  } else {
    isEdit.value = false
    editId.value = null
    form.value = { username: '', name: '', department: '', phone: '', is_admin: false, is_active: true, password: '' }
  }
  dialogVisible.value = true
}

async function handleToggleActive(row) {
  try {
    await updateUser(row.id, { is_active: row.is_active })
    ElMessage.success(row.is_active ? '已启用' : '已禁用')
  } catch (e) {
    row.is_active = !row.is_active
  }
}

async function handleSubmit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    if (isEdit.value) {
      const data = { ...form.value }
      if (!data.password) delete data.password
      await updateUser(editId.value, data)
      ElMessage.success('修改成功')
    } else {
      await createUser(form.value)
      ElMessage.success('新增成功')
    }
    dialogVisible.value = false
    loadData()
  } finally {
    submitting.value = false
  }
}

async function handleDelete(id) {
  await deleteUser(id)
  ElMessage.success('删除成功')
  loadData()
}

onMounted(loadData)
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.search-bar {
  display: flex;
  gap: 10px;
  margin-bottom: 16px;
}
</style>
