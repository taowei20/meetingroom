<template>
  <div class="user-manage">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>用户管理</span>
          <div class="header-btns">
            <el-button @click="handleDownloadTemplate">
              <el-icon><Download /></el-icon> 导入模板
            </el-button>
            <el-button type="success" @click="importDialogVisible = true">
              <el-icon><Upload /></el-icon> 批量导入
            </el-button>
            <el-button type="primary" @click="openDialog()">
              <el-icon><Plus /></el-icon> 新增用户
            </el-button>
          </div>
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
      <div class="pagination-wrap">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="loadData"
          @current-change="loadData"
        />
      </div>
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

    <el-dialog v-model="importDialogVisible" title="批量导入用户" width="480px" destroy-on-close>
      <div class="import-tips">
        <p><strong>导入说明：</strong></p>
        <ul>
          <li>请先下载导入模板，按模板格式填写数据</li>
          <li>Excel文件需包含表头行，数据从第2行开始</li>
          <li>登录账号重复的用户将自动跳过</li>
          <li>密码列留空则默认使用 <code>123456</code></li>
        </ul>
      </div>
      <el-upload
        ref="importUploadRef"
        :auto-upload="false"
        :limit="1"
        accept=".xlsx,.xls"
        :on-change="handleImportFileChange"
        :on-exceed="handleImportExceed"
        drag
      >
        <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
        <div class="el-upload__text">将Excel文件拖到此处，或<em>点击上传</em></div>
        <template #tip>
          <div class="el-upload__tip">仅支持 .xlsx 格式文件</div>
        </template>
      </el-upload>
      <template #footer>
        <el-button @click="importDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="importing" @click="handleImport">开始导入</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, Search, Download, Upload, UploadFilled } from '@element-plus/icons-vue'
import { getUsers, createUser, updateUser, deleteUser, downloadUserImportTemplate, importUsers } from '../api/users'

const loading = ref(false)
const submitting = ref(false)
const tableData = ref([])
const keyword = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const dialogVisible = ref(false)
const isEdit = ref(false)
const editId = ref(null)
const formRef = ref(null)

const importDialogVisible = ref(false)
const importing = ref(false)
const importFile = ref(null)
const importUploadRef = ref(null)

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
    const res = await getUsers({ keyword: keyword.value, page: currentPage.value, page_size: pageSize.value })
    tableData.value = res.items
    total.value = res.total
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

async function handleDownloadTemplate() {
  try {
    const response = await downloadUserImportTemplate()
    if (!response.ok) {
      ElMessage.error('下载失败')
      return
    }
    const blob = await response.blob()
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = '用户导入模板.xlsx'
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  } catch {
    ElMessage.error('下载失败')
  }
}

function handleImportFileChange(file) {
  importFile.value = file.raw
}

function handleImportExceed() {
  ElMessage.warning('只能上传一个文件，请先移除已选文件')
}

async function handleImport() {
  if (!importFile.value) {
    ElMessage.warning('请先选择文件')
    return
  }
  importing.value = true
  try {
    const formData = new FormData()
    formData.append('file', importFile.value)
    const res = await importUsers(formData)
    ElMessage.success(res.message)
    if (res.errors && res.errors.length > 0) {
      console.warn('导入详情:', res.errors)
    }
    importDialogVisible.value = false
    importFile.value = null
    importUploadRef.value?.clearFiles()
    loadData()
  } catch (e) {
    const msg = e.response?.data?.error || '导入失败'
    ElMessage.error(msg)
  } finally {
    importing.value = false
  }
}

onMounted(loadData)
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.header-btns {
  display: flex;
  gap: 8px;
}
.search-bar {
  display: flex;
  gap: 10px;
  margin-bottom: 16px;
}
.pagination-wrap {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}
.import-tips {
  margin-bottom: 16px;
  font-size: 13px;
  color: #606266;
  line-height: 1.8;
}
.import-tips ul {
  margin: 4px 0 0 0;
  padding-left: 20px;
}
.import-tips code {
  background: #f5f5f5;
  padding: 1px 4px;
  border-radius: 3px;
  font-size: 12px;
  color: #e6a23c;
}
</style>
