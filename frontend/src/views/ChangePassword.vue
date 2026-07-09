<template>
  <div class="change-password">
    <el-card shadow="never" style="max-width: 480px">
      <template #header>修改密码</template>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-form-item label="旧密码" prop="old_password">
          <el-input v-model="form.old_password" type="password" show-password placeholder="请输入旧密码" />
        </el-form-item>
        <el-form-item label="新密码" prop="new_password">
          <el-input v-model="form.new_password" type="password" show-password placeholder="请输入新密码（至少4位）" />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirm_password">
          <el-input v-model="form.confirm_password" type="password" show-password placeholder="请再次输入新密码" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="loading" @click="handleSubmit">确认修改</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { changePassword } from '../api/auth'
import { useUserStore } from '../store/user'
import { useRouter } from 'vue-router'

const userStore = useUserStore()
const router = useRouter()
const formRef = ref(null)
const loading = ref(false)

const form = ref({ old_password: '', new_password: '', confirm_password: '' })

const rules = {
  old_password: [{ required: true, message: '请输入旧密码', trigger: 'blur' }],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 4, message: '密码长度不能少于4位', trigger: 'blur' },
  ],
  confirm_password: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== form.value.new_password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur',
    },
  ],
}

async function handleSubmit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    await changePassword({
      old_password: form.value.old_password,
      new_password: form.value.new_password,
    })
    ElMessage.success('密码修改成功，请重新登录')
    userStore.logout()
    router.push('/login')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.change-password {
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
