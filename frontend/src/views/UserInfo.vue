<template>
  <div class="user-info">
    <el-card shadow="never" style="max-width: 480px">
      <template #header>个人信息</template>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-form-item label="登录账号">
          <el-input :value="form.username" disabled />
        </el-form-item>
        <el-form-item label="用户名" prop="name">
          <el-input v-model="form.name" placeholder="请输入用户名" disabled/>
        </el-form-item>
        <el-form-item label="所属部门">
          <el-input v-model="form.department" placeholder="请输入所属部门" />
        </el-form-item>
        <el-form-item label="联系方式">
          <el-input v-model="form.phone" placeholder="请输入联系方式" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="loading" @click="handleSubmit">保存修改</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getCurrentUser, updateCurrentUser } from '../api/auth'
import { useUserStore } from '../store/user'

const userStore = useUserStore()
const formRef = ref(null)
const loading = ref(false)

const form = ref({
  username: '',
  name: '',
  department: '',
  phone: '',
})

const rules = {
  name: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
}

async function loadUser() {
  const user = await getCurrentUser()
  form.value = { ...user }
}

async function handleSubmit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    const updated = await updateCurrentUser({
      name: form.value.name,
      department: form.value.department,
      phone: form.value.phone,
    })
    userStore.updateUser(updated)
    ElMessage.success('保存成功')
  } finally {
    loading.value = false
  }
}

onMounted(loadUser)
</script>

<style scoped>
.user-info {
  padding: 0;
}
@media (max-width: 768px) {
  :deep(.el-card) {
    max-width: 100% !important;
  }
  :deep(.el-dialog) {
    width: 95% !important;
    margin: 0 auto;
  }
  :deep(.el-form-item__label) {
    font-size: 13px;
  }
}
</style>
