<template>
  <div class="room-manage">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>会议室管理</span>
          <el-button type="primary" @click="openDialog()">
            <el-icon><Plus /></el-icon> 新增会议室
          </el-button>
        </div>
      </template>
      <div class="search-bar">
        <el-input v-model="keyword" placeholder="搜索编号/名称" clearable style="width: 260px" @clear="loadData" @keyup.enter="loadData">
          <template #prefix><el-icon><Search /></el-icon></template>
        </el-input>
        <el-button type="primary" @click="loadData">搜索</el-button>
      </div>
      <el-table :data="tableData" v-loading="loading" stripe border>
        <el-table-column prop="room_code" label="会议室编号" width="150" />
        <el-table-column prop="name" label="会议室名称" width="180" />
        <el-table-column prop="remark" label="备注" min-width="200" />
        <el-table-column prop="is_active" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'">
              {{ row.is_active ? '启用' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
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

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑会议室' : '新增会议室'" width="460px" destroy-on-close>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-form-item label="会议室编号">
          <el-input :value="form.room_code || '系统自动生成'" disabled />
        </el-form-item>
        <el-form-item label="会议室名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入会议室名称" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" :rows="3" placeholder="请输入备注" />
        </el-form-item>
        <el-form-item v-if="isEdit" label="状态">
          <el-switch v-model="form.is_active" active-text="启用" inactive-text="停用" />
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
import { getRooms, createRoom, updateRoom, deleteRoom } from '../api/rooms'

const loading = ref(false)
const submitting = ref(false)
const tableData = ref([])
const keyword = ref('')
const dialogVisible = ref(false)
const isEdit = ref(false)
const editId = ref(null)
const formRef = ref(null)

const form = ref({
  room_code: '',
  name: '',
  remark: '',
  is_active: true,
})

const rules = {
  name: [{ required: true, message: '请输入会议室名称', trigger: 'blur' }],
}

async function loadData() {
  loading.value = true
  try {
    tableData.value = await getRooms({ keyword: keyword.value })
  } finally {
    loading.value = false
  }
}

function openDialog(row) {
  if (row) {
    isEdit.value = true
    editId.value = row.id
    form.value = { ...row }
  } else {
    isEdit.value = false
    editId.value = null
    form.value = { room_code: '', name: '', remark: '', is_active: true }
  }
  dialogVisible.value = true
}

async function handleSubmit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    if (isEdit.value) {
      await updateRoom(editId.value, {
        name: form.value.name,
        remark: form.value.remark,
        is_active: form.value.is_active,
      })
      ElMessage.success('修改成功')
    } else {
      await createRoom({ name: form.value.name, remark: form.value.remark })
      ElMessage.success('新增成功')
    }
    dialogVisible.value = false
    loadData()
  } finally {
    submitting.value = false
  }
}

async function handleDelete(id) {
  await deleteRoom(id)
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
